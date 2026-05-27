from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from jobs_ai.models import JobRecord
from jobs_ai.submitters.base import SubmissionResult


@dataclass(frozen=True)
class FormSelectors:
    name: Optional[str] = None
    email: Optional[str] = None
    resume: Optional[str] = None
    cover_letter: Optional[str] = None
    submit: Optional[str] = None


class PlaywrightFormSubmitter:
    """Configurable submitter for approved, stable application forms."""

    def __init__(self, selectors: FormSelectors, headless: bool = False) -> None:
        self.selectors = selectors
        self.headless = headless

    async def submit(self, job: JobRecord) -> SubmissionResult:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return SubmissionResult(
                submitted=False,
                status="failed",
                message="Install the automation extra and Playwright browsers to use this submitter.",
                opened_url=str(job.url),
            )

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            await page.goto(str(job.url), wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_load_state("networkidle", timeout=15000)
            await browser.close()

        return SubmissionResult(
            submitted=False,
            status="review_required",
            message=(
                "Opened the form with Playwright. Add platform-specific selector filling "
                "before enabling final submit clicks."
            ),
            opened_url=str(job.url),
        )
