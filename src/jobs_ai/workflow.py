from __future__ import annotations

import math
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

    def _analyzer(self):
        return analyzer_for(self.settings) if self.settings.openai_api_key else HeuristicAnalyzer()

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

    async def auto_discover_jobs(self, limit: Optional[int] = None) -> list[JobRecord]:
        resume = self.resume_store.read()
        if not resume:
            raise ValueError(
                "No resume found. Add CV files to "
                f"{self.settings.app_cv_directory} or {self.settings.app_resume_path} first."
            )
        limit = limit or self.settings.job_search_limit
        profile = self._analyzer().build_candidate_profile(resume)
        queries = _clean_queries(profile.search_queries) or _clean_queries(
            [self.settings.job_search_query]
        )
        per_query_limit = max(5, math.ceil(limit / max(len(queries), 1)))
        found: dict[int, JobRecord] = {}
        for query in queries[:6]:
            jobs = await self.search_jobs(query=query, location="Spain", limit=per_query_limit)
            for job in jobs:
                found[job.id] = job
            if len(found) >= limit:
                break

        self.db.add_log(
            "info",
            "lucai_auto_discovery_completed",
            f"LucAI generated {len(queries[:6])} search queries and found {len(found)} matching jobs.",
            metadata={
                "profile_summary": profile.summary,
                "target_titles": profile.target_titles,
                "core_skills": profile.core_skills,
                "queries": queries[:6],
                "configured_platforms": [
                    {
                        "platform": connection.platform,
                        "search_enabled": connection.search_enabled,
                        "apply_enabled": connection.apply_enabled,
                        "status": connection.status,
                    }
                    for connection in self.db.list_platform_connections()
                    if connection.search_enabled or connection.apply_enabled
                ],
            },
        )
        return list(found.values())[:limit]

    async def analyze_job(self, job_id: int) -> JobRecord:
        job = self._require_job(job_id)
        resume_document = self.resume_store.select_for_language(job.language)
        if not resume_document:
            raise ValueError(
                "No resume found. Add CV files to "
                f"{self.settings.app_cv_directory} or {self.settings.app_resume_path} first."
            )
        analyzer = self._analyzer()
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

    def chat_with_lucai(self, message: str) -> str:
        resume = self.resume_store.read()
        if not resume:
            raise ValueError(
                "No resume found. Add CV files to "
                f"{self.settings.app_cv_directory} or {self.settings.app_resume_path} first."
            )
        answer = self._analyzer().chat(resume=resume, jobs=self.db.list_jobs(), message=message)
        self.db.add_log("info", "lucai_chat", "LucAI answered a chat message.")
        return answer

    def _require_job(self, job_id: int) -> JobRecord:
        job = self.db.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} was not found.")
        return job


def _clean_queries(queries: list[str]) -> list[str]:
    cleaned = []
    seen = set()
    for query in queries:
        value = " ".join(query.split())
        if len(value) < 3:
            continue
        key = value.lower()
        if key not in seen:
            cleaned.append(value)
            seen.add(key)
    return cleaned
