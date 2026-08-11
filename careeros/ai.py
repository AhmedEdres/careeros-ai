"""Claude-powered analysis, cover letters and CV bullet tailoring.

The HTTP API is called directly with ``requests`` so the app has no hard
dependency on the ``anthropic`` SDK (which was missing from requirements.txt
and made every analysis fail in production).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests

from .matching import MatchResult
from .profile import Profile
from .text import clean_html_text, safe_company_name, truncate

__all__ = ["AIClient", "AIResult", "DEFAULT_MODEL", "MODELS"]

DEFAULT_MODEL = "claude-3-5-haiku-20241022"
MODELS = {
    "Fast & cheap (Haiku 3.5)": "claude-3-5-haiku-20241022",
    "Best quality (Sonnet 4)": "claude-sonnet-4-20250514",
}
API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"


@dataclass
class AIResult:
    text: str = ""
    error: Optional[str] = None
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def ok(self) -> bool:
        return self.error is None and bool(self.text)


class AIClient:
    """Thin, dependency-free Anthropic Messages API client."""

    def __init__(self, api_key: str = "", model: str = DEFAULT_MODEL, timeout: int = 60):
        self.api_key = (api_key or "").strip()
        self.model = model or DEFAULT_MODEL
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    # -- low level ---------------------------------------------------------
    def complete(self, prompt: str, max_tokens: int = 700, system: str = "") -> AIResult:
        if not self.enabled:
            return AIResult(error="Claude API key not configured — add CLAUDE_API_KEY to Secrets.")

        payload: Dict[str, object] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            payload["system"] = system

        try:
            response = requests.post(
                API_URL,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": API_VERSION,
                    "content-type": "application/json",
                },
                data=json.dumps(payload),
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout:
            return AIResult(error="Claude request timed out — try again.")
        except requests.exceptions.RequestException as exc:
            return AIResult(error=f"Claude connection error: {exc}")

        if response.status_code == 401:
            return AIResult(error="Claude rejected the API key (401). Check CLAUDE_API_KEY.")
        if response.status_code == 429:
            return AIResult(error="Claude rate limit reached — wait a moment and retry.")
        if response.status_code >= 400:
            detail = ""
            try:
                detail = response.json().get("error", {}).get("message", "")
            except ValueError:
                detail = response.text[:200]
            return AIResult(error=f"Claude API error {response.status_code}: {detail}")

        try:
            data = response.json()
            blocks = data.get("content") or []
            text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
            usage = data.get("usage") or {}
            return AIResult(
                text=text.strip(),
                model=data.get("model", self.model),
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
            )
        except (ValueError, AttributeError) as exc:
            return AIResult(error=f"Could not parse the Claude response: {exc}")

    # -- prompts -----------------------------------------------------------
    @staticmethod
    def _profile_block(profile: Profile) -> str:
        highlights = "\n".join(f"- {h}" for h in profile.highlights)
        return (
            f"- Name: {profile.name}\n"
            f"- Based in: {profile.location}, {profile.country} (full work authorisation)\n"
            f"- Experience: {profile.experience_years}+ years in operations, client management, "
            f"financial compliance, tax, accounting, collections, B2B\n"
            f"- Languages: Arabic ({profile.arabic_level}), English ({profile.english_level}), "
            f"Romanian ({profile.romanian_level})\n"
            f"- Education: {profile.education}\n"
            f"- Target salary: {profile.target_salary_min:,}-{profile.target_salary_max:,} RON/month\n"
            f"{highlights}"
        )

    @staticmethod
    def _job_block(job: Dict, match: MatchResult, description_limit: int = 2500) -> str:
        description = clean_html_text(job.get("description", ""))
        return (
            f"Title: {job.get('title', 'Unknown')}\n"
            f"Company: {safe_company_name(job.get('company'))}\n"
            f"Location: {(job.get('location') or {}).get('display_name', 'Unknown')}\n"
            f"Source: {job.get('source', '')}\n"
            f"Salary (as published): {job.get('salary_text') or 'not specified'}\n"
            f"Posted: {job.get('posted_at') or 'unknown'}\n"
            f"Description:\n{truncate(description, description_limit)}"
        )

    def analyze_job(self, job: Dict, match: MatchResult, profile: Profile) -> AIResult:
        prompt = f"""You are {profile.name}'s career advisor in the Romanian/EU job market.

CANDIDATE PROFILE:
{self._profile_block(profile)}

JOB POSTING:
{self._job_block(job, match)}

LOCAL MATCHING ENGINE (score {match.score}/100, confidence {match.confidence}):
Dimensions: {json.dumps(match.dimensions)}
Strengths: {'; '.join(match.reasons[:8]) or 'none detected'}
Warnings: {'; '.join(match.warnings[:6]) or 'none detected'}

Reply in EXACTLY this format, no preamble:

VERDICT: 🔥 APPLY NOW / ⚠️ APPLY WITH CAUTION / ❌ SKIP — [max 12 words]

FIT CHECK:
🟢/🟡/🔴 Career fit: [one line]
🟢/🟡/🔴 Language: [one line about Arabic/English vs Romanian {profile.romanian_level}]
🟢/🟡/🔴 Location: [one line]
🟢/🟡/🔴 Seniority & salary: [one line]

BIGGEST RISK: [one line]

HOW TO POSITION YOURSELF: [two short bullets with concrete wording {profile.name} should use]

Be concrete and honest. If the role is a poor fit, say so plainly."""
        return self.complete(prompt, max_tokens=700)

    def cover_letter(self, job: Dict, match: MatchResult, profile: Profile, tone: str = "professional") -> AIResult:
        prompt = f"""Write a cover letter for {profile.name} applying to this role.

CANDIDATE PROFILE:
{self._profile_block(profile)}

JOB POSTING:
{self._job_block(job, match, description_limit=2000)}

REQUIREMENTS:
- Tone: {tone}. Language: English (the posting language).
- Maximum 220 words, 3 short paragraphs, no clichés like "I am writing to apply".
- Open with the single strongest match between his background and this role.
- Mention Arabic only if it adds value for this employer.
- Address the Romanian language gap ONLY if the posting requires Romanian, and frame it honestly (currently {profile.romanian_level}, actively learning).
- End with a specific, confident call to action.
- Output only the letter body — no subject line, no placeholders like [Company]."""
        return self.complete(prompt, max_tokens=800)

    def cv_bullets(self, job: Dict, match: MatchResult, profile: Profile) -> AIResult:
        prompt = f"""Tailor {profile.name}'s CV for this specific job.

CANDIDATE PROFILE:
{self._profile_block(profile)}

JOB POSTING:
{self._job_block(job, match, description_limit=2000)}

Produce:

KEYWORDS TO ADD (for ATS): [comma-separated list of 8-12 exact terms from the posting he can honestly claim]

REWRITTEN BULLETS: [4 CV bullets, each starting with a strong verb, each containing a number or measurable outcome, each mirroring the posting's vocabulary]

WHAT TO DE-EMPHASISE: [one line]

Only claim experience supported by his real profile above."""
        return self.complete(prompt, max_tokens=800)

    def interview_prep(self, job: Dict, match: MatchResult, profile: Profile) -> AIResult:
        prompt = f"""Prepare {profile.name} for an interview for this role.

CANDIDATE PROFILE:
{self._profile_block(profile)}

JOB POSTING:
{self._job_block(job, match, description_limit=1800)}

Produce:

5 LIKELY QUESTIONS: [numbered, specific to this role — include the obvious hard one about his career transition or Romanian level]

STRONGEST ANSWER ANGLE: [3 bullets: which stories from his background to use]

3 QUESTIONS TO ASK THEM: [numbered, showing genuine research]

Keep every line short and usable as notes."""
        return self.complete(prompt, max_tokens=900)
