from __future__ import annotations

import json
import re

from openai import OpenAI

from jobs_ai.config import Settings
from jobs_ai.models import AnalysisResult, ApplicationAnswer, JobRecord


SYSTEM_PROMPT = """
You are an expert job-application assistant.
You must never invent jobs, degrees, dates, certifications, metrics, employers, or skills.
You may rewrite, reorganize, and emphasize only information that is genuinely present in the resume.
If the resume has a gap against the job requirements, call it out in gaps_or_risks.
Return application answers that are truthful, concise, and ready for review.
Pay close attention to the job language. Generate the tailored resume and answers in the
same language as the job posting unless the job explicitly requests another language.
"""


class AIAnalyzer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI()

    def analyze(self, resume: str, job: JobRecord) -> AnalysisResult:
        prompt = f"""
Resume:
{resume}

Job:
Title: {job.title}
Company: {job.company}
Location: {job.location}
Detected job language: {job.language}
Detected work mode: {job.work_mode}
Preference match reason: {job.preference_reason}
Salary: {job.salary}
Description:
{job.description}

Tasks:
1. Score how well the real resume matches this role from 0 to 100.
2. Extract the most important requirements.
3. Identify real resume strengths to emphasize.
4. Identify gaps or risks without being harsh.
5. Generate a tailored resume in Markdown using only truthful resume content.
6. Generate answers in the job posting language for likely application questions, such as motivation, fit,
   salary note if present, availability if inferable, and work authorization only
   if explicitly present in the resume.
"""
        response = self.client.responses.parse(
            model=self.settings.openai_model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            text_format=AnalysisResult,
        )
        return response.output_parsed


class HeuristicAnalyzer:
    """Fallback analyzer for local development without an API key."""

    def analyze(self, resume: str, job: JobRecord) -> AnalysisResult:
        resume_terms = set(_keywords(resume))
        job_terms = set(_keywords(job.title + " " + job.description + " " + " ".join(job.tags)))
        overlap = sorted(resume_terms & job_terms)
        score = min(95, max(20, int((len(overlap) / max(len(job_terms), 1)) * 100) + 25))
        requirements = _sentences(job.description)[:8] or [job.title]
        language_note = {
            "es": "Responde en español.",
            "en": "Respond in English.",
            "pt": "Responda em português.",
        }.get(job.language, "Use the job posting language.")
        summary = (
            f"Heuristic match based on overlapping terms: {', '.join(overlap[:12])}."
            if overlap
            else "Heuristic match only; run with OPENAI_API_KEY for detailed analysis."
        )
        tailored = (
            f"# Tailored Resume Draft\n\n{resume}\n\n"
            "## Emphasis Notes\n\n"
            + "\n".join(f"- Emphasize experience related to {term}." for term in overlap[:8])
            + f"\n\nLanguage instruction: {language_note}"
        )
        return AnalysisResult(
            match_score=score,
            match_summary=summary,
            key_requirements=requirements,
            strengths_to_emphasize=overlap[:10],
            gaps_or_risks=["Use OpenAI analysis for a reliable gap assessment."],
            tailored_resume_markdown=tailored,
            application_answers=[
                ApplicationAnswer(
                    question="Why are you interested in this role?",
                    answer=(
                        f"I am interested in the {job.title} role at {job.company} because it "
                        "aligns with the experience and skills reflected in my resume."
                    ),
                    confidence="low",
                )
            ],
        )


def analyzer_for(settings: Settings):
    try:
        return AIAnalyzer(settings)
    except Exception:
        return HeuristicAnalyzer()


def analysis_to_json(result: AnalysisResult) -> str:
    return json.dumps(result.model_dump(), indent=2)


def _keywords(text: str) -> list[str]:
    stop = {
        "and",
        "the",
        "with",
        "for",
        "that",
        "this",
        "you",
        "are",
        "from",
        "will",
        "your",
        "our",
        "have",
        "has",
        "job",
        "role",
    }
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{2,}", text.lower())
    return [word for word in words if word not in stop]


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip())
    return [part[:240] for part in parts if len(part) > 20]
