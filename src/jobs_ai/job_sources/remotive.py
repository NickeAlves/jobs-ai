from __future__ import annotations

import html
import re

import httpx

from jobs_ai.models import JobOpening


class RemotiveSource:
    name = "remotive"
    api_url = "https://remotive.com/api/remote-jobs"

    async def search(self, query: str, location: str, limit: int) -> list[JobOpening]:
        params = {"search": query, "limit": limit}
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(self.api_url, params=params)
            response.raise_for_status()
        payload = response.json()
        jobs = payload.get("jobs", [])[:limit]
        return [self._normalize(job) for job in jobs]

    def _normalize(self, job: dict) -> JobOpening:
        description = _clean_html(job.get("description") or "")
        tags = [str(tag) for tag in job.get("tags") or []]
        return JobOpening(
            external_id=str(job.get("id")),
            source=self.name,
            title=job.get("title") or "Untitled role",
            company=job.get("company_name") or "Unknown company",
            location=job.get("candidate_required_location") or "Remote",
            url=job.get("url") or job.get("job_url") or "https://remotive.com",
            description=description,
            salary=job.get("salary") or "",
            tags=tags,
        )


def _clean_html(value: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", value, flags=re.I)
    text = re.sub(r"</(p|li|h[1-6])>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text).replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()
