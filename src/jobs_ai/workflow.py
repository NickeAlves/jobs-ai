from __future__ import annotations

import os
from typing import Optional

from jobs_ai.ai import HeuristicAnalyzer, analyzer_for
from jobs_ai.config import Settings
from jobs_ai.db import Database
from jobs_ai.job_sources.remotive import RemotiveSource
from jobs_ai.job_sources.sample import SampleSource
from jobs_ai.models import ApplicationStatus, JobRecord
from jobs_ai.preferences import apply_preferences
from jobs_ai.resume import ResumeStore
from jobs_ai.submitters.manual import ManualReviewSubmitter


class ApplicationWorkflow:
    def __init__(self, settings: Settings, db: Database, resume_store: ResumeStore) -> None:
        self.settings = settings
        self.db = db
        self.resume_store = resume_store

    async def search_jobs(
        self, query: Optional[str] = None, location: Optional[str] = None, limit: Optional[int] = None
    ) -> list[JobRecord]:
        query = query or self.settings.job_search_query
        location = location or self.settings.job_search_location
        limit = limit or self.settings.job_search_limit
        source = RemotiveSource()
        try:
            openings = await source.search(query=query, location=location, limit=limit)
        except Exception as exc:
            self.db.add_log(
                "warning",
                "job_search_fallback",
                f"Remotive search failed, using sample data: {exc}",
                metadata={"query": query, "location": location},
            )
            openings = await SampleSource().search(query=query, location=location, limit=limit)

        evaluated = [apply_preferences(opening) for opening in openings]
        matching = [opening for opening in evaluated if opening.preference_match]
        skipped_count = len(evaluated) - len(matching)
        ids = [self.db.upsert_job(opening) for opening in matching]
        self.db.add_log(
            "info",
            "job_search_completed",
            f"Discovered or refreshed {len(ids)} matching job openings.",
            metadata={
                "query": query,
                "location": location,
                "limit": limit,
                "skipped_by_preferences": skipped_count,
            },
        )
        return [job for job in self.db.list_jobs() if job.id in ids]

    async def analyze_job(self, job_id: int) -> JobRecord:
        job = self._require_job(job_id)
        resume_document = self.resume_store.select_for_language(job.language)
        if not resume_document:
            raise ValueError(
                "No resume found. Add CV files to "
                f"{self.settings.app_cv_directory} or {self.settings.app_resume_path} first."
            )
        analyzer = analyzer_for(self.settings) if os.getenv("OPENAI_API_KEY") else HeuristicAnalyzer()
        try:
            result = analyzer.analyze(resume_document.content, job)
        except Exception as exc:
            self.db.add_log(
                "error",
                "ai_analysis_failed",
                f"OpenAI analysis failed: {exc}",
                job_id=job_id,
            )
            raise

        self.db.save_analysis(
            job_id=job_id,
            match_score=result.match_score,
            match_summary=result.match_summary,
            requirements=result.key_requirements,
            tailored_resume=result.tailored_resume_markdown,
            selected_resume_name=resume_document.name,
            answers=[answer.model_dump() for answer in result.application_answers],
        )
        self.db.add_log(
            "info",
            "job_analyzed",
            f"Generated tailored resume and answers for {job.title} at {job.company}.",
            job_id=job_id,
            metadata={
                "match_score": result.match_score,
                "job_language": job.language,
                "selected_resume": resume_document.name,
                "selected_resume_language": resume_document.language,
                "work_mode": job.work_mode,
                "preference_reason": job.preference_reason,
                "strengths": result.strengths_to_emphasize,
                "gaps_or_risks": result.gaps_or_risks,
            },
        )
        return self._require_job(job_id)

    async def submit_job(self, job_id: int) -> JobRecord:
        job = self._require_job(job_id)
        if not job.tailored_resume:
            raise ValueError("Analyze and tailor this job before submission.")

        if self.settings.app_require_manual_review or not self.settings.app_auto_submit_enabled:
            submitter = ManualReviewSubmitter()
        else:
            submitter = ManualReviewSubmitter()

        result = await submitter.submit(job)
        status = (
            ApplicationStatus.SUBMITTED
            if result.submitted
            else ApplicationStatus.REVIEW_REQUIRED
            if result.status == "review_required"
            else ApplicationStatus.FAILED
        )
        self.db.update_status(job_id, status)
        self.db.add_log(
            "info" if status != ApplicationStatus.FAILED else "error",
            "submission_attempted",
            result.message,
            job_id=job_id,
            metadata=result.model_dump(),
        )
        return self._require_job(job_id)

    def skip_job(self, job_id: int) -> JobRecord:
        self._require_job(job_id)
        self.db.update_status(job_id, ApplicationStatus.SKIPPED)
        self.db.add_log("info", "job_skipped", "Job marked as skipped.", job_id=job_id)
        return self._require_job(job_id)

    def _require_job(self, job_id: int) -> JobRecord:
        job = self.db.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} was not found.")
        return job
