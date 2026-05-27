from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, Field, HttpUrl


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ApplicationStatus(str, Enum):
    DISCOVERED = "discovered"
    ANALYZED = "analyzed"
    REVIEW_REQUIRED = "review_required"
    SUBMITTED = "submitted"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkMode(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    UNKNOWN = "unknown"


class JobOpening(BaseModel):
    external_id: str
    source: str
    title: str
    company: str
    location: str = ""
    url: Union[HttpUrl, str]
    description: str
    salary: str = ""
    tags: list[str] = Field(default_factory=list)
    language: str = "unknown"
    work_mode: WorkMode = WorkMode.UNKNOWN
    preference_match: bool = True
    preference_reason: str = ""
    discovered_at: str = Field(default_factory=utc_now)


class JobRecord(JobOpening):
    id: int
    status: ApplicationStatus = ApplicationStatus.DISCOVERED
    match_score: Optional[int] = None
    match_summary: str = ""
    requirements: list[str] = Field(default_factory=list)
    tailored_resume: str = ""
    selected_resume_name: str = ""
    answers: list["ApplicationAnswer"] = Field(default_factory=list)
    submitted_at: Optional[str] = None
    updated_at: str = Field(default_factory=utc_now)


class ApplicationAnswer(BaseModel):
    question: str
    answer: str
    confidence: str = "medium"


class AnalysisResult(BaseModel):
    match_score: int = Field(ge=0, le=100)
    match_summary: str
    key_requirements: list[str]
    strengths_to_emphasize: list[str]
    gaps_or_risks: list[str]
    tailored_resume_markdown: str
    application_answers: list[ApplicationAnswer]


class ResumeDocument(BaseModel):
    name: str
    path: str
    language: str = "unknown"
    content: str


class LogRecord(BaseModel):
    id: int
    job_id: Optional[int] = None
    level: str
    event: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class DashboardStats(BaseModel):
    total_jobs: int
    submitted_applications: int
    review_required: int
    failed: int
