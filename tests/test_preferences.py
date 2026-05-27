from jobs_ai.models import JobOpening, WorkMode
from jobs_ai.preferences import apply_preferences, detect_language


def test_remote_spain_matches_preferences():
    job = apply_preferences(
        JobOpening(
            external_id="remote-es",
            source="test",
            title="Backend Engineer",
            company="Acme",
            location="Spain",
            url="https://example.com",
            description="Remote role for a Python engineer.",
        )
    )

    assert job.preference_match is True
    assert job.work_mode == WorkMode.REMOTE


def test_remote_brazil_is_filtered_out():
    job = apply_preferences(
        JobOpening(
            external_id="remote-br",
            source="test",
            title="Backend Engineer",
            company="Acme",
            location="Brazil",
            url="https://example.com",
            description="Remote role for a Python engineer.",
        )
    )

    assert job.preference_match is False
    assert job.work_mode == WorkMode.REMOTE


def test_hybrid_miranda_de_ebro_matches_preferences():
    job = apply_preferences(
        JobOpening(
            external_id="hybrid-miranda",
            source="test",
            title="Ingeniero Python",
            company="Acme",
            location="Miranda de Ebro",
            url="https://example.com",
            description="Trabajo híbrido con experiencia en Python.",
        )
    )

    assert job.preference_match is True
    assert job.work_mode == WorkMode.HYBRID


def test_language_detection_prefers_spanish():
    assert detect_language("Buscamos experiencia con Python y requisitos de backend remoto") == "es"
