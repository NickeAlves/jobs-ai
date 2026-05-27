from __future__ import annotations

from typing import Protocol
from typing import Optional

from pydantic import BaseModel

from jobs_ai.models import JobRecord


class SubmissionResult(BaseModel):
    submitted: bool
    status: str
    message: str
    opened_url: Optional[str] = None


class Submitter(Protocol):
    async def submit(self, job: JobRecord) -> SubmissionResult:
        """Submit or prepare a job application."""
