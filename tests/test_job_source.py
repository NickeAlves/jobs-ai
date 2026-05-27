from jobs_ai.job_sources.remotive import _clean_html


def test_clean_html_preserves_readable_text():
    html = "<p>Hello&nbsp;<strong>Python</strong></p><ul><li>FastAPI</li></ul>"

    cleaned = _clean_html(html)

    assert "Hello Python" in cleaned
    assert "FastAPI" in cleaned
    assert "<" not in cleaned
