"""Shared plumbing for job sources: HTTP session, retries, normalised records."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter

try:  # urllib3 v1/v2 compatibility
    from urllib3.util.retry import Retry
except ImportError:  # pragma: no cover
    Retry = None  # type: ignore

from ..text import clean_html_text, safe_company_name

logger = logging.getLogger("careeros.sources")

USER_AGENT = "CareerOS/3.0 (+job search assistant)"
DEFAULT_TIMEOUT = (10, 25)  # (connect, read)

__all__ = [
    "SourceResult",
    "build_session",
    "make_job",
    "parse_date",
    "days_since",
    "http_error_message",
]


@dataclass
class SourceResult:
    """Outcome of one source call — never raises, always inspectable."""

    source: str
    jobs: List[Dict] = field(default_factory=list)
    error: Optional[str] = None
    skipped: bool = False
    elapsed_ms: int = 0

    @property
    def ok(self) -> bool:
        return self.error is None and not self.skipped

    @property
    def count(self) -> int:
        return len(self.jobs)


def build_session(retries: int = 2) -> requests.Session:
    """A session with sane retry/backoff behaviour for flaky job APIs."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9,ro;q=0.8",
    })
    if Retry is not None:
        retry = Retry(
            total=retries,
            connect=retries,
            read=retries,
            backoff_factor=0.6,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "POST"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
    return session


_DATE_FORMATS = (
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d.%m.%Y",
)


def parse_date(value: object) -> Optional[datetime]:
    """Best-effort parsing of the many date formats job boards emit."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+0000"
    text = re.sub(r"([+-]\d{2}):(\d{2})$", r"\1\2", text)

    for fmt in _DATE_FORMATS:
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    # Relative forms: "3 days ago", "acum 2 zile", "today"
    lowered = text.lower()
    if any(word in lowered for word in ("today", "azi", "just now", "acum")):
        match = re.search(r"(\d+)\s*(day|zi|zile|hour|ora|ore)", lowered)
        if match and match.group(2).startswith(("day", "zi")):
            from datetime import timedelta
            return datetime.now(timezone.utc) - timedelta(days=int(match.group(1)))
        return datetime.now(timezone.utc)
    match = re.search(r"(\d+)\s*(day|days|zi|zile)\s*(ago|in urma)?", lowered)
    if match:
        from datetime import timedelta
        return datetime.now(timezone.utc) - timedelta(days=int(match.group(1)))
    return None


def days_since(value: object) -> Optional[int]:
    parsed = parse_date(value)
    if parsed is None:
        return None
    delta = datetime.now(timezone.utc) - parsed
    return max(0, delta.days)


def make_job(
    *,
    title: str,
    company: object,
    location: object,
    description: str,
    url: str,
    source: str,
    salary_text: str = "",
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None,
    salary_currency: Optional[str] = None,
    category: str = "",
    posted_at: object = None,
    remote: bool = False,
    extra: Optional[Dict] = None,
) -> Dict:
    """Build the canonical job record every part of the app consumes."""
    posted = parse_date(posted_at)
    job = {
        "title": str(title or "").strip() or "Job title not available",
        "company": {"display_name": safe_company_name(company)},
        "location": {"display_name": str(location or "").strip()},
        "description": description or "",
        "description_text": clean_html_text(description)[:6000],
        "redirect_url": str(url or "").strip(),
        "salary_text": str(salary_text or "").strip(),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": salary_currency,
        "source": source,
        "category": {"label": str(category or "")},
        "posted_at": posted.isoformat() if posted else "",
        "age_days": days_since(posted) if posted else None,
        "remote": bool(remote),
    }
    if extra:
        job.update(extra)
    return job


def http_error_message(source: str, status: int, body: str = "") -> str:
    """Turn an HTTP status into an actionable message for the user."""
    hints = {
        400: "bad request — check the search parameters",
        401: "authentication failed — verify the API key in Secrets",
        403: "access denied — the key may lack permission or the IP is blocked",
        404: "endpoint not found — the API may have moved",
        410: "endpoint retired",
        429: "rate limit reached — wait a minute and try again",
        500: "the provider had a server error",
        502: "bad gateway at the provider",
        503: "the provider is temporarily unavailable",
        504: "the provider timed out",
    }
    hint = hints.get(status, "unexpected response")
    snippet = clean_html_text(body)[:160]
    tail = f" — {snippet}" if snippet else ""
    return f"{source}: HTTP {status} ({hint}){tail}"
