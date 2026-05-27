const state = {
  jobs: [],
  logs: [],
  selectedJobId: null,
  lang: localStorage.getItem("lucai.lang") || "en",
  theme: localStorage.getItem("lucai.theme") || "light",
};

const els = {
  languageSelect: document.querySelector("#languageSelect"),
  themeSelect: document.querySelector("#themeSelect"),
  queryInput: document.querySelector("#queryInput"),
  locationInput: document.querySelector("#locationInput"),
  limitInput: document.querySelector("#limitInput"),
  searchButton: document.querySelector("#searchButton"),
  autoDiscoverButton: document.querySelector("#autoDiscoverButton"),
  chatMessages: document.querySelector("#chatMessages"),
  chatInput: document.querySelector("#chatInput"),
  chatSendButton: document.querySelector("#chatSendButton"),
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
  discoverySummary: document.querySelector("#discoverySummary"),
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
  platformCards: document.querySelector("#platformCards"),
};

const I18N = {
  en: {
    accounts: "Accounts",
    advancedSearch: "Advanced manual search",
    answers: "Answers",
    applyEnabled: "Prepare applications",
    brandSubtitle: "Autopilot for focused applications",
    chatGreeting: "Hi, I am LucAI. I can find roles, explain matches, and help with applications.",
    chatPlaceholder: "Talk to LucAI...",
    cvFiles: "{count} CV file(s): {files}",
    cvFallback: "No CV files found in the configured directory. Fallback editor content will be used.",
    cvSource: "CV Source",
    cvUsedAnalyze: "CV used: analyze this role to select the closest language match.",
    cvUsedName: "CV used: {name}",
    dashboard: "Dashboard",
    dark: "Dark",
    description: "Description",
    discovered: "Discovered",
    discoveryFound: "LucAI found {count} matching role(s). Showing newest matches first.",
    discoveryNone: "LucAI did not find new matching roles with the current filters.",
    discoverySummaryDefault: "Run LucAI to refresh this list from your CV.",
    emptyCopy: "Run automatic discovery, select a match, then tailor the CV and answers for that role.",
    emptyTitle: "Start with LucAI",
    failed: "Failed",
    findMatches: "Find Matches With LucAI",
    jobSearchCompleted: "Job search completed.",
    keyRequirements: "Key Requirements",
    language: "Language",
    light: "Light",
    location: "Location",
    logs: "Logs",
    lucaiAutoUser: "LucAI, find roles automatically from my CV.",
    lucaiFoundChat: "I found {count} compatible role(s) after analyzing your CV and applying your preferences.",
    lucaiFindCopy: "CV-first discovery with your Spain remote, hybrid, and onsite rules applied automatically.",
    lucaiFindTitle: "Let LucAI find the matches",
    manualReviewEnabled: "Manual review enabled",
    autoSubmitEnabled: "Auto-submit enabled",
    autoSubmitDisabled: "Auto-submit disabled",
    match: "match",
    matchAnalysis: "Match Analysis",
    matchedRoles: "Matched Roles",
    matchSummaryEmpty: "Analyze this role to generate match details.",
    maxRoles: "Max roles to review",
    notes: "Notes",
    noTailored: "No tailored CV generated yet.",
    openLogin: "Open Login",
    openPosting: "Open Posting",
    overview: "Overview",
    password: "Password",
    passwordSaved: "Saved password",
    pipeline: "Pipeline",
    platformLogins: "Platform Logins",
    platformNote: "Configure local credentials and choose where LucAI may search or prepare applications. Some platforms require MFA, CAPTCHA, or manual confirmation before any application can be sent.",
    platformSaved: "Platform settings saved.",
    platforms: "Platforms",
    primaryWorkflow: "Primary workflow",
    review: "Review",
    roles: "roles",
    resume: "Resume",
    savePlatform: "Save {name}",
    saveResume: "Save Resume",
    resumeSaved: "Resume saved.",
    search: "Search",
    searchEnabled: "Search jobs",
    searchJobs: "Search Jobs",
    send: "Send",
    skip: "Skip",
    strategy: "strategy",
    submitMarkReviewed: "Submit / Mark Reviewed",
    submitted: "Submitted",
    applicationMoved: "Application moved to review/submission workflow.",
    jobSkipped: "Job skipped.",
    tailorPacket: "Tailor Packet",
    tailoredGenerated: "Tailored CV and answers generated.",
    theme: "Theme",
    username: "Email / username",
  },
  "pt-BR": {
    accounts: "Contas",
    advancedSearch: "Busca manual avançada",
    answers: "Respostas",
    applyEnabled: "Preparar candidaturas",
    brandSubtitle: "Piloto automático para candidaturas focadas",
    chatGreeting: "Olá, sou o LucAI. Posso procurar vagas, explicar matches e ajudar com candidaturas.",
    chatPlaceholder: "Fale com o LucAI...",
    cvFiles: "{count} CV(s): {files}",
    cvFallback: "Nenhum CV encontrado na pasta configurada. O conteúdo do editor será usado como fallback.",
    cvSource: "Fonte do CV",
    cvUsedAnalyze: "CV usado: analise esta vaga para selecionar o idioma mais próximo.",
    cvUsedName: "CV usado: {name}",
    dashboard: "Dashboard",
    dark: "Escuro",
    description: "Descrição",
    discovered: "Descobertas",
    discoveryFound: "LucAI encontrou {count} vaga(s) compatíveis. Mostrando os matches mais recentes primeiro.",
    discoveryNone: "LucAI não encontrou novas vagas compatíveis com os filtros atuais.",
    discoverySummaryDefault: "Rode o LucAI para atualizar esta lista a partir do seu CV.",
    emptyCopy: "Rode a descoberta automática, selecione um match e depois adapte o CV e as respostas para a vaga.",
    emptyTitle: "Comece com o LucAI",
    failed: "Falhas",
    findMatches: "Encontrar matches com LucAI",
    jobSearchCompleted: "Busca de vagas concluída.",
    keyRequirements: "Requisitos principais",
    language: "Idioma",
    light: "Claro",
    location: "Localização",
    logs: "Logs",
    lucaiAutoUser: "LucAI, procure vagas automaticamente com base no meu CV.",
    lucaiFoundChat: "Encontrei {count} vaga(s) compatíveis depois de analisar o teu CV e aplicar as tuas preferências.",
    lucaiFindCopy: "Descoberta baseada no CV com as tuas regras para remoto, híbrido e presencial na Espanha.",
    lucaiFindTitle: "Deixe o LucAI encontrar os matches",
    manualReviewEnabled: "Revisão manual ativada",
    autoSubmitEnabled: "Autoenvio ativado",
    autoSubmitDisabled: "Autoenvio desativado",
    match: "match",
    matchAnalysis: "Análise de match",
    matchedRoles: "Vagas compatíveis",
    matchSummaryEmpty: "Analise esta vaga para gerar detalhes do match.",
    maxRoles: "Máximo de vagas",
    notes: "Notas",
    noTailored: "Nenhum CV adaptado gerado ainda.",
    openLogin: "Abrir login",
    openPosting: "Abrir vaga",
    overview: "Resumo",
    password: "Senha",
    passwordSaved: "Senha salva",
    pipeline: "Pipeline",
    platformLogins: "Logins de plataformas",
    platformNote: "Configure credenciais locais e escolha onde o LucAI pode pesquisar ou preparar candidaturas. Algumas plataformas exigem MFA, CAPTCHA ou confirmação manual antes de qualquer candidatura.",
    platformSaved: "Configurações da plataforma salvas.",
    platforms: "Plataformas",
    primaryWorkflow: "Fluxo principal",
    review: "Revisão",
    roles: "vagas",
    resume: "CV",
    savePlatform: "Salvar {name}",
    saveResume: "Salvar CV",
    resumeSaved: "CV salvo.",
    search: "Busca",
    searchEnabled: "Pesquisar vagas",
    searchJobs: "Pesquisar vagas",
    send: "Enviar",
    skip: "Pular",
    strategy: "estratégia",
    submitMarkReviewed: "Enviar / Marcar revisada",
    submitted: "Enviadas",
    applicationMoved: "Candidatura movida para revisão/envio.",
    jobSkipped: "Vaga pulada.",
    tailorPacket: "Adaptar candidatura",
    tailoredGenerated: "CV e respostas adaptados.",
    theme: "Tema",
    username: "Email / usuário",
  },
  "es-ES": {
    accounts: "Cuentas",
    advancedSearch: "Búsqueda manual avanzada",
    answers: "Respuestas",
    applyEnabled: "Preparar candidaturas",
    brandSubtitle: "Piloto automático para candidaturas enfocadas",
    chatGreeting: "Hola, soy LucAI. Puedo buscar ofertas, explicar matches y ayudarte con candidaturas.",
    chatPlaceholder: "Habla con LucAI...",
    cvFiles: "{count} CV(s): {files}",
    cvFallback: "No se encontraron CVs en la carpeta configurada. Se usará el contenido del editor como alternativa.",
    cvSource: "Fuente del CV",
    cvUsedAnalyze: "CV usado: analiza esta oferta para seleccionar el idioma más cercano.",
    cvUsedName: "CV usado: {name}",
    dashboard: "Panel",
    dark: "Oscuro",
    description: "Descripción",
    discovered: "Descubiertas",
    discoveryFound: "LucAI encontró {count} oferta(s) compatibles. Mostrando los matches más recientes primero.",
    discoveryNone: "LucAI no encontró nuevas ofertas compatibles con los filtros actuales.",
    discoverySummaryDefault: "Ejecuta LucAI para actualizar esta lista desde tu CV.",
    emptyCopy: "Ejecuta la búsqueda automática, selecciona un match y adapta el CV y las respuestas para esa oferta.",
    emptyTitle: "Empieza con LucAI",
    failed: "Fallidas",
    findMatches: "Encontrar matches con LucAI",
    jobSearchCompleted: "Búsqueda de ofertas completada.",
    keyRequirements: "Requisitos clave",
    language: "Idioma",
    light: "Claro",
    location: "Ubicación",
    logs: "Logs",
    lucaiAutoUser: "LucAI, busca ofertas automáticamente según mi CV.",
    lucaiFoundChat: "Encontré {count} oferta(s) compatibles después de analizar tu CV y aplicar tus preferencias.",
    lucaiFindCopy: "Búsqueda basada en CV con tus reglas para remoto, híbrido y presencial en España.",
    lucaiFindTitle: "Deja que LucAI encuentre los matches",
    manualReviewEnabled: "Revisión manual activada",
    autoSubmitEnabled: "Autoenvío activado",
    autoSubmitDisabled: "Autoenvío desactivado",
    match: "match",
    matchAnalysis: "Análisis de match",
    matchedRoles: "Ofertas compatibles",
    matchSummaryEmpty: "Analiza esta oferta para generar detalles del match.",
    maxRoles: "Máximo de ofertas",
    notes: "Notas",
    noTailored: "Aún no se ha generado un CV adaptado.",
    openLogin: "Abrir login",
    openPosting: "Abrir oferta",
    overview: "Resumen",
    password: "Contraseña",
    passwordSaved: "Contraseña guardada",
    pipeline: "Pipeline",
    platformLogins: "Logins de plataformas",
    platformNote: "Configura credenciales locales y elige dónde LucAI puede buscar o preparar candidaturas. Algunas plataformas requieren MFA, CAPTCHA o confirmación manual antes de enviar cualquier candidatura.",
    platformSaved: "Configuración de plataforma guardada.",
    platforms: "Plataformas",
    primaryWorkflow: "Flujo principal",
    review: "Revisión",
    roles: "ofertas",
    resume: "CV",
    savePlatform: "Guardar {name}",
    saveResume: "Guardar CV",
    resumeSaved: "CV guardado.",
    search: "Búsqueda",
    searchEnabled: "Buscar ofertas",
    searchJobs: "Buscar ofertas",
    send: "Enviar",
    skip: "Saltar",
    strategy: "estrategia",
    submitMarkReviewed: "Enviar / Marcar revisada",
    submitted: "Enviadas",
    applicationMoved: "Candidatura movida a revisión/envío.",
    jobSkipped: "Oferta omitida.",
    tailorPacket: "Adaptar candidatura",
    tailoredGenerated: "CV y respuestas adaptadas.",
    theme: "Tema",
    username: "Email / usuario",
  },
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

function t(key, params = {}) {
  const template = I18N[state.lang]?.[key] || I18N.en[key] || key;
  return Object.entries(params).reduce(
    (text, [name, value]) => text.replaceAll(`{${name}}`, value),
    template,
  );
}

function applyLocale() {
  document.documentElement.lang = state.lang;
  els.languageSelect.value = state.lang;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.placeholder = t(node.dataset.i18nPlaceholder);
  });
  renderSettingsFromState();
  renderJobs();
  renderSelectedJob();
}

function applyTheme() {
  document.documentElement.dataset.theme = state.theme;
  els.themeSelect.value = state.theme;
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
  renderPlatforms(data.platforms || []);
  renderJobs();
  if (!state.selectedJobId && state.jobs.length) {
    state.selectedJobId = state.jobs[0].id;
  }
  renderSelectedJob();
}

async function loadPlatforms() {
  const data = await api("/api/platforms");
  renderPlatforms(data.platforms || []);
}

async function loadResume() {
  const data = await api("/api/resume");
  els.resumeEditor.value = data.content;
  els.resumePath.textContent = data.cv_directory || data.path;
  els.cvDocuments.textContent = data.documents?.length
    ? t("cvFiles", {
        count: data.documents.length,
        files: data.documents.map((doc) => `${doc.name} (${doc.language})`).join(", "),
      })
    : t("cvFallback");
}

function renderStats(stats) {
  els.totalJobs.textContent = stats.total_jobs;
  els.submittedApps.textContent = stats.submitted_applications;
  els.reviewRequired.textContent = stats.review_required;
  els.failedApps.textContent = stats.failed;
}

function renderSettings(settings) {
  state.settings = settings;
  els.queryInput.value ||= settings.default_query;
  els.locationInput.value ||= settings.default_location;
  els.limitInput.value ||= settings.default_limit;
  renderSettingsFromState();
}

function renderSettingsFromState() {
  const settings = state.settings;
  if (!settings) return;
  els.settingsPill.textContent = settings.require_manual_review
    ? t("manualReviewEnabled")
    : settings.auto_submit_enabled
      ? t("autoSubmitEnabled")
      : t("autoSubmitDisabled");
}

function setDiscoverySummary(message) {
  els.discoverySummary.textContent = message;
}

function renderJobs() {
  els.jobCount.textContent = `${state.jobs.length} ${t("roles")}`;
  els.jobsList.innerHTML = "";
  for (const job of state.jobs) {
    const item = document.createElement("button");
    item.className = `job-item ${job.id === state.selectedJobId ? "active" : ""}`;
    item.innerHTML = `
      <div class="job-meta-row">
        <span class="status">${escapeHtml(job.status)}</span>
        <span class="meta-chip">${job.match_score ?? "-"} ${t("match")}</span>
      </div>
      <h3>${escapeHtml(job.title)}</h3>
      <p>${escapeHtml(job.company)} · ${escapeHtml(job.location || "Remote")}</p>
      <div class="job-meta-row">
        <span class="meta-chip">${escapeHtml(job.work_mode)}</span>
        <span class="meta-chip">${escapeHtml(job.language)}</span>
      </div>
    `;
    item.addEventListener("click", () => {
      state.selectedJobId = job.id;
      renderJobs();
      renderSelectedJob();
    });
    els.jobsList.appendChild(item);
  }
}

function renderPlatforms(platforms) {
  if (!els.platformCards) return;
  els.platformCards.innerHTML = "";
  for (const platform of platforms) {
    const card = document.createElement("article");
    card.className = "platform-card";
    card.innerHTML = `
      <div class="platform-card-header">
        <div>
          <span class="eyebrow">${escapeHtml(platform.status)}</span>
          <h3>${escapeHtml(platform.display_name)}</h3>
        </div>
        <a class="link-button" href="${escapeHtml(platform.login_url)}" target="_blank" rel="noreferrer">${t("openLogin")}</a>
      </div>
      <p>${escapeHtml(platform.notes)}</p>
      <label>
        ${t("username")}
        <input data-field="username" value="${escapeHtml(platform.username)}" autocomplete="username" />
      </label>
      <label>
        ${t("password")}
        <input data-field="password" type="password" placeholder="${platform.has_password ? t("passwordSaved") : t("password")}" autocomplete="current-password" />
      </label>
      <div class="toggle-row">
        <label><input data-field="search_enabled" type="checkbox" ${platform.search_enabled ? "checked" : ""} /> ${t("searchEnabled")}</label>
        <label><input data-field="apply_enabled" type="checkbox" ${platform.apply_enabled ? "checked" : ""} /> ${t("applyEnabled")}</label>
      </div>
      <label>
        ${t("notes")}
        <textarea data-field="notes">${escapeHtml(platform.notes || "")}</textarea>
      </label>
      <button class="primary" data-platform="${escapeHtml(platform.platform)}">${t("savePlatform", { name: escapeHtml(platform.display_name) })}</button>
    `;
    card.querySelector("button[data-platform]").addEventListener("click", () =>
      savePlatform(platform.platform, card),
    );
    els.platformCards.appendChild(card);
  }
}

async function savePlatform(platform, card) {
  const field = (name) => card.querySelector(`[data-field="${name}"]`);
  const password = field("password").value;
  const button = card.querySelector("button[data-platform]");
  setBusy(button, true);
  try {
    const data = await api(`/api/platforms/${platform}`, {
      method: "POST",
      body: JSON.stringify({
        username: field("username").value,
        password: password || null,
        search_enabled: field("search_enabled").checked,
        apply_enabled: field("apply_enabled").checked,
        notes: field("notes").value,
      }),
    });
    renderPlatforms(data.platforms || []);
    showToast(t("platformSaved"));
  } catch (error) {
    showToast(error.message);
  } finally {
    setBusy(button, false);
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
    `conic-gradient(var(--brand) ${degrees}deg, var(--brand-soft) 0deg)`;
  els.matchSummary.textContent = job.match_summary || t("matchSummaryEmpty");
  els.selectedResume.textContent = job.selected_resume_name
    ? t("cvUsedName", { name: job.selected_resume_name })
    : t("cvUsedAnalyze");
  els.requirementsList.innerHTML = (job.requirements || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
  els.tailoredResume.textContent = job.tailored_resume || t("noTailored");
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

function applyDiscoveryResponse(data) {
  applyWorkflowResponse(data);
  if (data.jobs?.length) {
    state.selectedJobId = data.jobs[0].id;
    renderJobs();
    renderSelectedJob();
    els.jobsList.scrollTop = 0;
    setDiscoverySummary(t("discoveryFound", { count: data.jobs.length }));
  } else {
    setDiscoverySummary(t("discoveryNone"));
  }
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
    applyDiscoveryResponse(data);
    showToast(t("jobSearchCompleted"));
  } catch (error) {
    showToast(error.message);
  } finally {
    setBusy(els.searchButton, false);
  }
});

els.autoDiscoverButton.addEventListener("click", async () => {
  setBusy(els.autoDiscoverButton, true);
  try {
    addChatMessage("user", t("lucaiAutoUser"));
    const data = await api("/api/jobs/auto-discover", {
      method: "POST",
      body: JSON.stringify({ limit: Number(els.limitInput.value || 25) }),
    });
    applyDiscoveryResponse(data);
    addChatMessage("agent", t("lucaiFoundChat", { count: data.jobs.length }));
    showToast(t("discoveryFound", { count: data.jobs.length }));
  } catch (error) {
    addChatMessage("agent", error.message);
    showToast(error.message);
  } finally {
    setBusy(els.autoDiscoverButton, false);
  }
});

els.saveResumeButton.addEventListener("click", async () => {
  setBusy(els.saveResumeButton, true);
  try {
    await api("/api/resume", {
      method: "POST",
      body: JSON.stringify({ content: els.resumeEditor.value }),
    });
    showToast(t("resumeSaved"));
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
    showToast(t("tailoredGenerated"));
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
    showToast(t("applicationMoved"));
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
  showToast(t("jobSkipped"));
});

els.chatSendButton.addEventListener("click", sendChatMessage);
els.chatInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") sendChatMessage();
});

async function sendChatMessage() {
  const message = els.chatInput.value.trim();
  if (!message) return;
  els.chatInput.value = "";
  addChatMessage("user", message);
  setBusy(els.chatSendButton, true);
  try {
    const data = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    if (data.logs) state.logs = data.logs;
    addChatMessage("agent", data.answer);
    renderSelectedJob();
  } catch (error) {
    addChatMessage("agent", error.message);
    showToast(error.message);
  } finally {
    setBusy(els.chatSendButton, false);
  }
}

function addChatMessage(sender, message) {
  const item = document.createElement("div");
  item.className = `chat-message ${sender === "user" ? "user" : "agent"}`;
  item.textContent = message;
  els.chatMessages.appendChild(item);
  els.chatMessages.scrollTop = els.chatMessages.scrollHeight;
}

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((item) => item.classList.add("hidden"));
    tab.classList.add("active");
    document.querySelector(`#tab-${tab.dataset.tab}`).classList.remove("hidden");
  });
});

els.languageSelect.addEventListener("change", () => {
  state.lang = els.languageSelect.value;
  localStorage.setItem("lucai.lang", state.lang);
  applyLocale();
  loadResume().catch((error) => showToast(error.message));
});

els.themeSelect.addEventListener("change", () => {
  state.theme = els.themeSelect.value;
  localStorage.setItem("lucai.theme", state.theme);
  applyTheme();
});

document.querySelectorAll(".nav-button").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".nav-button").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".view").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    document.querySelector(`#${button.dataset.view}`).classList.add("active");
    if (button.dataset.view === "platformsView") loadPlatforms().catch((error) => showToast(error.message));
  });
});

applyTheme();
applyLocale();
Promise.all([loadDashboard(), loadResume(), loadPlatforms()]).catch((error) => showToast(error.message));
