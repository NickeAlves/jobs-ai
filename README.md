# Jobs AI

Jobs AI is a Python web application for discovering job openings, matching them to your real resume, generating tailored resumes and application answers with the OpenAI API, and tracking the application lifecycle in a modern dashboard.

The app is intentionally conservative about submission automation. It supports a manual review step by default and uses submitter adapters for platform-specific automation, because job boards differ heavily in terms, markup, authentication, CAPTCHAs, and allowed automation.

## Features

- Resume loading from `/documents/cv/` first, falling back to `data/resume.md` or upload/paste through the UI.
- Job discovery through modular providers, with a Remotive public API provider included.
- Preference filtering for remote roles available to Spain, hybrid roles in Madrid/Burgos/Valladolid/Bilbao/Miranda de Ebro, and onsite roles in Madrid/Burgos/Valladolid/Bilbao.
- Job language detection so tailored resumes and answers are generated in the posting language.
- AI job matching, requirement analysis, resume tailoring, and application question answers.
- SQLite-backed dashboard with discovered jobs, statuses, logs, generated resumes, answers, and history.
- Optional manual review before submission, enabled by default.
- Submitter abstraction for resilient platform-specific automation. A safe manual submitter is included; a Playwright form submitter scaffold is provided for approved platforms.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,automation]"
cp .env.example .env
mkdir -p data
# Preferred: put your CV files in /documents/cv/
# Fallback:
$EDITOR data/resume.md
uvicorn jobs_ai.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

Your API key should stay in `.env` or your shell environment as `OPENAI_API_KEY`. Do not paste it into the browser UI.

## Typical Workflow

1. Add your CV files to `/documents/cv/`, or use `data/resume.md` as a fallback.
2. Set `JOB_SEARCH_QUERY`, `JOB_SEARCH_LOCATION`, and `JOB_SEARCH_LIMIT`.
3. Click **Search Jobs** in the UI. Jobs outside your location/work-mode preferences are skipped.
4. Open a job and click **Analyze & Tailor**.
5. Review the tailored resume and generated answers.
6. Click **Submit / Mark Reviewed**. With default settings this records a manual-review status and opens the original posting for final submission.

## Auto-Submission

Universal auto-apply is not reliable or appropriate across all platforms. This project uses submitter adapters instead:

- `ManualReviewSubmitter`: safe default, logs the action and keeps the user in control.
- `PlaywrightFormSubmitter`: configurable browser automation scaffold for platforms where you have permission and stable selectors.

Enable automation only after reviewing a platform's rules:

```bash
APP_REQUIRE_MANUAL_REVIEW=false
APP_AUTO_SUBMIT_ENABLED=true
```

Then implement or configure a platform adapter under `src/jobs_ai/submitters/`.

## OpenAI API

The app uses the OpenAI Python SDK and the Responses API with structured Pydantic outputs for reliable parsing. The SDK reads `OPENAI_API_KEY` from the environment. The default model is configurable with `OPENAI_MODEL`.

## Development

```bash
python -m pytest
python -m ruff check .
```
