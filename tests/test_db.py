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


def test_platform_connection_round_trip(tmp_path):
    db = Database(tmp_path / "jobs.sqlite3")
    db.initialize()

    platforms = db.list_platform_connections()
    assert {platform.platform for platform in platforms} >= {"infojobs", "linkedin", "indeed"}

    saved = db.save_platform_connection(
        "infojobs",
        username="me@example.com",
        password="secret",
        search_enabled=True,
        apply_enabled=True,
        notes="Use manual review.",
    )

    assert saved.platform == "infojobs"
    assert saved.username == "me@example.com"
    assert saved.has_password is True
    assert saved.apply_enabled is True
    assert db.get_platform_connection_secret("infojobs")["password"] == "secret"
