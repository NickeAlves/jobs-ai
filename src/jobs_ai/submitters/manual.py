from __future__ import annotations

from jobs_ai.models import JobRecord
from jobs_ai.submitters.base import SubmissionResult


class ManualReviewSubmitter:
    async def submit(self, job: JobRecord) -> SubmissionResult:
        return SubmissionResult(
            submitted=False,
            status="review_required",
            message=(
                "Manual review is required. Open the original posting, verify the tailored "
                "resume and answers, then submit on the job platform."
            ),
            opened_url=str(job.url),
        )
