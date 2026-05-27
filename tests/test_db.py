from jobs_ai.db import Database
from jobs_ai.models import ApplicationStatus, JobOpening


def test_job_lifecycle_round_trip(tmp_path):
    db = Database(tmp_path / "jobs.sqlite3")
    db.initialize()
    job_id = db.upsert_job(
        JobOpening(
            external_id="1",
            source="test",
            title="Python Engineer",
            company="Acme",
            location="Remote",
            url="https://example.com/job",
            description="Build APIs.",
            tags=["python"],
        )
    )

    db.save_analysis(
        job_id,
        match_score=88,
        match_summary="Strong match.",
        requirements=["Python"],
        tailored_resume="# Resume",
        selected_resume_name="cv-en.pdf",
        answers=[{"question": "Why?", "answer": "Because.", "confidence": "medium"}],
    )
    db.update_status(job_id, ApplicationStatus.REVIEW_REQUIRED)

    job = db.get_job(job_id)

    assert job is not None
    assert job.match_score == 88
    assert job.status == ApplicationStatus.REVIEW_REQUIRED
    assert job.answers[0].question == "Why?"
