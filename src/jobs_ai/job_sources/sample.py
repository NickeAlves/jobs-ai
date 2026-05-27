from __future__ import annotations

from jobs_ai.models import JobOpening


class SampleSource:
    name = "sample"

    async def search(self, query: str, location: str, limit: int) -> list[JobOpening]:
        return [
            JobOpening(
                external_id="sample-python-ai-engineer",
                source=self.name,
                title="Python AI Engineer",
                company="Example Labs",
                location=location or "Remote",
                url="https://example.com/jobs/python-ai-engineer",
                description=(
                    "Build Python services that integrate LLM APIs, process documents, "
                    "orchestrate background workflows, and ship reliable user-facing tools. "
                    "Experience with FastAPI, automation, observability, and secure API-key "
                    "handling is preferred."
                ),
                salary="",
                tags=["python", "fastapi", "openai", "automation"],
            )
        ][:limit]
