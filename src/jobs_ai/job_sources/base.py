from __future__ import annotations

from typing import Protocol

from jobs_ai.models import JobOpening


class JobSource(Protocol):
    name: str

    async def search(self, query: str, location: str, limit: int) -> list[JobOpening]:
        """Search for jobs and return normalized openings."""
