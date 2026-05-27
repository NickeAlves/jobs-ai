const state = {
  jobs: [],
  logs: [],
  selectedJobId: null,
};

const els = {
  queryInput: document.querySelector("#queryInput"),
  locationInput: document.querySelector("#locationInput"),
  limitInput: document.querySelector("#limitInput"),
  searchButton: document.querySelector("#searchButton"),
  saveResumeButton: document.querySelector("#saveResumeButton"),
  resumeEditor: document.querySelector("#resumeEditor"),
  resumePath: document.querySelector("#resumePath"),
  cvDocuments: document.querySelector("#cvDocuments"),
  totalJobs: document.querySelector("#totalJobs"),
  submittedApps: document.querySelector("#submittedApps"),
  reviewRequired: document.querySelector("#reviewRequired"),
  failedApps: document.querySelector("#failedApps"),
  settingsPill: document.querySelector("#settingsPill"),
  jobCount: document.querySelector("#jobCount"),
  jobsList: document.querySelector("#jobsList"),
  emptyState: document.querySelector("#emptyState"),
  jobDetail: document.querySelector("#jobDetail"),
  detailStatus: document.querySelector("#detailStatus"),
  detailTitle: document.querySelector("#detailTitle"),
  detailMeta: document.querySelector("#detailMeta"),
  detailPrefs: document.querySelector("#detailPrefs"),
  detailUrl: document.querySelector("#detailUrl"),
  analyzeButton: document.querySelector("#analyzeButton"),
  submitButton: document.querySelector("#submitButton"),
  skipButton: document.querySelector("#skipButton"),
  matchScore: document.querySelector("#matchScore"),
  matchSummary: document.querySelector("#matchSummary"),
  selectedResume: document.querySelector("#selectedResume"),
  requirementsList: document.querySelector("#requirementsList"),
  tailoredResume: document.querySelector("#tailoredResume"),
  answersList: document.querySelector("#answersList"),
  jobDescription: document.querySelector("#jobDescription"),
  logsList: document.querySelector("#logsList"),
  toast: document.querySelector("#toast"),
};

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

function showToast(message) {
  els.toast.textContent = message;
  els.toast.classList.remove("hidden");
  window.setTimeout(() => els.toast.classList.add("hidden"), 4200);
}

function setBusy(button, busy) {
  button.disabled = busy;
  button.dataset.originalText ||= button.textContent;
  button.textContent = busy ? "Working..." : button.dataset.originalText;
}

async function loadDashboard() {
  const data = await api("/api/dashboard");
  state.jobs = data.jobs;
  state.logs = data.logs;
  renderStats(data.stats);
  renderSettings(data.settings);
  renderJobs();
  if (!state.selectedJobId && state.jobs.length) {
    state.selectedJobId = state.jobs[0].id;
  }
  renderSelectedJob();
}

async function loadResume() {
  const data = await api("/api/resume");
  els.resumeEditor.value = data.content;
  els.resumePath.textContent = data.cv_directory || data.path;
  els.cvDocuments.textContent = data.documents?.length
    ? `${data.documents.length} CV file(s): ${data.documents.map((doc) => `${doc.name} (${doc.language})`).join(", ")}`
    : "No CV files found in the configured directory. Fallback editor content will be used.";
}

function renderStats(stats) {
  els.totalJobs.textContent = stats.total_jobs;
  els.submittedApps.textContent = stats.submitted_applications;
  els.reviewRequired.textContent = stats.review_required;
  els.failedApps.textContent = stats.failed;
}

function renderSettings(settings) {
  els.queryInput.value ||= settings.default_query;
  els.locationInput.value ||= settings.default_location;
  els.limitInput.value ||= settings.default_limit;
  els.settingsPill.textContent = settings.require_manual_review
    ? "Manual review enabled"
    : settings.auto_submit_enabled
      ? "Auto-submit enabled"
      : "Auto-submit disabled";
}

function renderJobs() {
  els.jobCount.textContent = `${state.jobs.length} roles`;
  els.jobsList.innerHTML = "";
  for (const job of state.jobs) {
    const item = document.createElement("button");
    item.className = `job-item ${job.id === state.selectedJobId ? "active" : ""}`;
    item.innerHTML = `
      <span class="status">${job.status}</span>
      <h3>${escapeHtml(job.title)}</h3>
      <p>${escapeHtml(job.company)} · ${escapeHtml(job.location || "Remote")}</p>
      <p>${escapeHtml(job.work_mode)} · ${escapeHtml(job.language)} · ${job.match_score ?? "-"} match score</p>
    `;
    item.addEventListener("click", () => {
      state.selectedJobId = job.id;
      renderJobs();
      renderSelectedJob();
    });
    els.jobsList.appendChild(item);
  }
}

function renderSelectedJob() {
  const job = state.jobs.find((item) => item.id === state.selectedJobId);
  els.emptyState.classList.toggle("hidden", Boolean(job));
  els.jobDetail.classList.toggle("hidden", !job);
  if (!job) return;

  els.detailStatus.textContent = job.status;
  els.detailTitle.textContent = job.title;
  els.detailMeta.textContent = `${job.company} · ${job.location || "Remote"} · ${job.salary || "Salary not listed"}`;
  els.detailPrefs.textContent =
    `${job.work_mode} · language: ${job.language} · ${job.preference_reason || "Preference checked"}`;
  els.detailUrl.href = job.url;
  els.matchScore.textContent = job.match_score ?? "-";
  const degrees = Math.max(0, Math.min(100, job.match_score || 0)) * 3.6;
  document.querySelector(".score-ring").style.background =
    `conic-gradient(var(--accent) ${degrees}deg, var(--accent-soft) 0deg)`;
  els.matchSummary.textContent = job.match_summary || "Analyze this role to generate match details.";
  els.selectedResume.textContent = job.selected_resume_name
    ? `CV used: ${job.selected_resume_name}`
    : "CV used: analyze this role to select the closest language match.";
  els.requirementsList.innerHTML = (job.requirements || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
  els.tailoredResume.textContent = job.tailored_resume || "No tailored resume generated yet.";
  els.jobDescription.textContent = job.description;
  els.answersList.innerHTML = (job.answers || [])
    .map(
      (answer) => `
        <article class="answer">
          <h3>${escapeHtml(answer.question)}</h3>
          <p>${escapeHtml(answer.answer)}</p>
          <small>Confidence: ${escapeHtml(answer.confidence)}</small>
        </article>
      `,
    )
    .join("");
  renderLogs(job.id);
}

function renderLogs(jobId) {
  const logs = state.logs.filter((log) => !log.job_id || log.job_id === jobId).slice(0, 80);
  els.logsList.innerHTML = logs
    .map(
      (log) => `
        <article class="log-row">
          <p><strong>${escapeHtml(log.event)}</strong> · ${escapeHtml(log.level)}</p>
          <p>${escapeHtml(log.message)}</p>
          <small>${escapeHtml(log.created_at)}</small>
        </article>
      `,
    )
    .join("");
}

function mergeJob(job) {
  const index = state.jobs.findIndex((item) => item.id === job.id);
  if (index >= 0) state.jobs[index] = job;
  else state.jobs.unshift(job);
}

function applyWorkflowResponse(data) {
  if (data.jobs) state.jobs = data.jobs.concat(state.jobs.filter((job) => !data.jobs.some((j) => j.id === job.id)));
  if (data.job) mergeJob(data.job);
  if (data.logs) state.logs = data.logs;
  if (data.stats) renderStats(data.stats);
  renderJobs();
  renderSelectedJob();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

els.searchButton.addEventListener("click", async () => {
  setBusy(els.searchButton, true);
  try {
    const data = await api("/api/jobs/search", {
      method: "POST",
      body: JSON.stringify({
        query: els.queryInput.value,
        location: els.locationInput.value,
        limit: Number(els.limitInput.value || 25),
      }),
    });
    applyWorkflowResponse(data);
    showToast("Job search completed.");
  } catch (error) {
    showToast(error.message);
  } finally {
    setBusy(els.searchButton, false);
  }
});

els.saveResumeButton.addEventListener("click", async () => {
  setBusy(els.saveResumeButton, true);
  try {
    await api("/api/resume", {
      method: "POST",
      body: JSON.stringify({ content: els.resumeEditor.value }),
    });
    showToast("Resume saved.");
  } catch (error) {
    showToast(error.message);
  } finally {
    setBusy(els.saveResumeButton, false);
  }
});

els.analyzeButton.addEventListener("click", async () => {
  if (!state.selectedJobId) return;
  setBusy(els.analyzeButton, true);
  try {
    const data = await api(`/api/jobs/${state.selectedJobId}/analyze`, { method: "POST" });
    applyWorkflowResponse(data);
    showToast("Tailored resume and answers generated.");
  } catch (error) {
    showToast(error.message);
  } finally {
    setBusy(els.analyzeButton, false);
  }
});

els.submitButton.addEventListener("click", async () => {
  if (!state.selectedJobId) return;
  setBusy(els.submitButton, true);
  try {
    const data = await api(`/api/jobs/${state.selectedJobId}/submit`, { method: "POST" });
    applyWorkflowResponse(data);
    const job = state.jobs.find((item) => item.id === state.selectedJobId);
    if (job?.url) window.open(job.url, "_blank", "noreferrer");
    showToast("Application moved to review/submission workflow.");
  } catch (error) {
    showToast(error.message);
  } finally {
    setBusy(els.submitButton, false);
  }
});

els.skipButton.addEventListener("click", async () => {
  if (!state.selectedJobId) return;
  const data = await api(`/api/jobs/${state.selectedJobId}/skip`, { method: "POST" });
  applyWorkflowResponse(data);
  showToast("Job skipped.");
});

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((item) => item.classList.add("hidden"));
    tab.classList.add("active");
    document.querySelector(`#tab-${tab.dataset.tab}`).classList.remove("hidden");
  });
});

Promise.all([loadDashboard(), loadResume()]).catch((error) => showToast(error.message));
