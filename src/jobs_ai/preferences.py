from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from jobs_ai.models import JobOpening, WorkMode


REMOTE_ALLOWED_REGIONS = (
    "spain",
    "espana",
    "españa",
    "europe",
    "emea",
    "worldwide",
    "anywhere",
    "global",
    "remote",
)

HYBRID_ALLOWED_LOCATIONS = (
    "madrid",
    "burgos",
    "castilla y leon",
    "castilla leon",
    "valladolid",
    "bilbao",
    "pais vasco",
    "país vasco",
    "miranda de ebro",
)

ONSITE_ALLOWED_LOCATIONS = (
    "madrid",
    "burgos",
    "castilla y leon",
    "castilla leon",
    "valladolid",
    "bilbao",
    "pais vasco",
    "país vasco",
)


@dataclass(frozen=True)
class PreferenceDecision:
    work_mode: WorkMode
    language: str
    matches: bool
    reason: str


def apply_preferences(opening: JobOpening) -> JobOpening:
    decision = evaluate_preferences(opening)
    opening.work_mode = decision.work_mode
    opening.language = decision.language
    opening.preference_match = decision.matches
    opening.preference_reason = decision.reason
    return opening


def evaluate_preferences(opening: JobOpening) -> PreferenceDecision:
    searchable = " ".join(
        [opening.title, opening.company, opening.location, opening.description, " ".join(opening.tags)]
    )
    text = _normalize(searchable)
    location = _normalize(opening.location)
    mode = detect_work_mode(text, location)
    language = detect_language(opening.title + "\n" + opening.description)

    if mode == WorkMode.REMOTE:
        matches = any(region in location for region in REMOTE_ALLOWED_REGIONS) or any(
            region in text for region in ("spain", "espana", "españa")
        )
        reason = (
            "Remote role available for Spain/Europe/worldwide."
            if matches
            else "Remote role does not clearly include Spain eligibility."
        )
        return PreferenceDecision(mode, language, matches, reason)

    if mode == WorkMode.HYBRID:
        matches = any(place in location or place in text for place in HYBRID_ALLOWED_LOCATIONS)
        reason = (
            "Hybrid role in an allowed city/province."
            if matches
            else "Hybrid role outside the allowed locations."
        )
        return PreferenceDecision(mode, language, matches, reason)

    if mode == WorkMode.ONSITE:
        matches = any(place in location or place in text for place in ONSITE_ALLOWED_LOCATIONS)
        reason = (
            "Onsite role in an allowed city/province."
            if matches
            else "Onsite role outside the allowed locations."
        )
        return PreferenceDecision(mode, language, matches, reason)

    matches = any(place in location or place in text for place in HYBRID_ALLOWED_LOCATIONS)
    reason = (
        "Work mode unknown, but location is in your allowed regions."
        if matches
        else "Work mode and location do not clearly match your preferences."
    )
    return PreferenceDecision(mode, language, matches, reason)


def detect_work_mode(text: str, location: str) -> WorkMode:
    if _has_any(text, ("hybrid", "hibrido", "híbrido")):
        return WorkMode.HYBRID
    if _has_any(text, ("onsite", "on-site", "presencial", "office-based", "in office")):
        return WorkMode.ONSITE
    if _has_any(location + " " + text[:1200], ("remote", "remoto", "work from anywhere")):
        return WorkMode.REMOTE
    return WorkMode.UNKNOWN


def detect_language(text: str) -> str:
    normalized = _normalize(text[:5000])
    spanish_hits = len(
        re.findall(
            r"\b(el|la|los|las|de|del|para|con|experiencia|remoto|hibrido|presencial|requisitos)\b",
            normalized,
        )
    )
    portuguese_hits = len(
        re.findall(r"\b(vaga|remoto|experiencia|voce|você|para|com|requisitos|brasil)\b", normalized)
    )
    english_hits = len(
        re.findall(r"\b(the|and|with|experience|remote|hybrid|requirements|responsibilities)\b", normalized)
    )
    scores = {"es": spanish_hits, "pt": portuguese_hits, "en": english_hits}
    language, score = max(scores.items(), key=lambda item: item[1])
    return language if score > 0 else "unknown"


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def _normalize(value: str) -> str:
    lowered = value.lower()
    without_accents = unicodedata.normalize("NFKD", lowered).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", without_accents)
