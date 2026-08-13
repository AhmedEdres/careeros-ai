"""Hipo.ro source adapter for Romanian job discovery.

Hipo is a useful Romanian-market source because it exposes a large local
catalog with Timisoara, remote/hybrid and salary metadata. This adapter is
HTTP-first and reuses the existing Selenium fallback used by the Romanian
board collector; it never logs in, solves CAPTCHAs, or submits applications.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from ..text import clean_html_text, normalize_text
from .base import DEFAULT_TIMEOUT, SourceResult, build_session, make_job
from .romania_boards import _get_html


_HIPO_JOB_RE = re.compile(r"/locuri-de-munca/locuri_de_munca/\d+/", re.IGNORECASE)
_DATE_RE = re.compile(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b")
_LOCATION_TOKENS = (
    "timisoara", "timișoara", "bucharest", "bucuresti", "cluj", "iasi",
    "brasov", "arad", "sibiu", "oradea", "constanta", "remote", "hybrid",
    "job national", "job national",
)


def _slug(value: str) -> str:
    text = normalize_text(value)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "jobs"


def _text(node) -> str:
    if not node:
        return ""
    return clean_html_text(node.get_text(" ", strip=True))


def _absolute(url: str, base: str = "https://www.hipo.ro") -> str:
    from urllib.parse import urljoin
    return urljoin(base, str(url or "").strip()).split("?")[0]


def _salary_text(blob: str) -> str:
    text = clean_html_text(blob)
    patterns = (
        r"\d[\d\s.,]*\s*(?:-|–|—|to)\s*\d[\d\s.,]*\s*(?:ron|lei|eur|€)\s*(?:net|brut)?",
        r"\d[\d\s.,]*\s*(?:ron|lei|eur|€)\s*(?:net|brut)?\s*(?:/\s*(?:luna|month|an|year))?",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            value_text = match.group(0)
            nums = re.findall(r"\d[\d\s.,]*\d|\d", value_text)
            try:
                numeric = float(nums[0].replace(".", "").replace(",", "").replace(" ", "")) if nums else 0
            except ValueError:
                numeric = 0
            norm = normalize_text(value_text)
            if ("ron" in norm or "lei" in norm) and numeric < 1500:
                continue
            if "eur" in norm and numeric < 300:
                continue
            return value_text
    return ""


def _search_url(keywords: str, location: str) -> str:
    slug = quote(_slug(keywords), safe="-")
    loc = normalize_text(location or "romania")
    if loc in {"timisoara", "timișoara", "timis"}:
        return f"https://www.hipo.ro/locuri-de-munca/cautajob/Toate-Domeniile/Timisoara/{slug}"
    if loc and loc not in {"romania", "all"}:
        return f"https://www.hipo.ro/locuri-de-munca/cautajob/Toate-Domeniile/{quote(_slug(location), safe='-')}/{slug}"
    return f"https://www.hipo.ro/locuri-de-munca/cautajob/Toate-Domeniile/Toate-Orasele/{slug}"


def _container(link):
    """Choose a compact card-like ancestor instead of the entire page."""
    node = link
    for _ in range(6):
        node = getattr(node, "parent", None)
        if not node:
            break
        text = _text(node)
        if 20 <= len(text) <= 2200:
            return node
    return link.parent


def _company(card, title: str) -> str:
    title_n = normalize_text(title)
    if "jobs from hipo" in title_n:
        at = re.search(r"@\s*([^|]+)$", title)
        return at.group(1).strip() if at else ""
    selectors = (
        "[class*=company]", "[class*=employer]", "[class*=firma]",
        "h3", "h4", "strong",
    )
    for selector in selectors:
        for node in card.select(selector):
            value = _text(node)
            if value and normalize_text(value) != normalize_text(title) and "jobs from hipo" not in normalize_text(value):
                return value
    # Hipo cards often put the employer in a sibling link. Prefer a short
    # non-navigation-looking anchor rather than guessing from arbitrary text.
    for node in card.find_all("a", href=True):
        value = _text(node)
        href = str(node.get("href", ""))
        if value and normalize_text(value) != normalize_text(title) and "/locuri-de-munca/" not in href:
            return value
    return ""


def _location(card, fallback: str) -> str:
    blob = _text(card)
    low_blob = normalize_text(blob)
    for token in _LOCATION_TOKENS:
        token_n = normalize_text(token)
        if re.search(rf"(?<![a-z]){re.escape(token_n)}(?![a-z])", low_blob):
            pretty = "Timișoara" if token_n in {"timisoara", "timișoara"} else token.title()
            if "hybrid" in low_blob:
                return f"Hybrid / {pretty}"
            if "remote" in low_blob:
                return f"Remote / {pretty}"
            return pretty
    return fallback or "Romania"


def _parse(html: str, limit: int, fallback_location: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs: List[Dict] = []
    seen = set()

    # Stable job-detail URL pattern observed on Hipo, e.g.
    # /locuri-de-munca/locuri_de_munca/269980/AUMOVIO-Romania/Privacy-Compliance-Officer...
    for link in soup.find_all("a", href=True):
        href = str(link.get("href", ""))
        if not _HIPO_JOB_RE.search(href):
            continue
        url = _absolute(href)
        if url in seen:
            continue
        title = _text(link)
        title = _DATE_RE.sub("", title).strip()
        title = re.sub(r"\s+Jobs from Hipo.*$", "", title, flags=re.IGNORECASE).strip()
        if not title or len(title) > 220:
            continue
        card = _container(link)
        card_text = _text(card)
        company = _company(card, title)
        location = _location(card, fallback_location)
        salary = _salary_text(card_text)
        date_match = _DATE_RE.search(card_text)
        remote = any(token in normalize_text(card_text) for token in ("remote", "hybrid"))
        seen.add(url)
        jobs.append(make_job(
            title=title,
            company=company,
            location=location,
            description=card_text[:6000],
            url=url,
            source="Hipo",
            salary_text=salary,
            salary_currency="ron" if salary and any(x in normalize_text(salary) for x in ("ron", "lei")) else None,
            posted_at=date_match.group(0) if date_match else None,
            remote=remote,
        ))
        if len(jobs) >= limit:
            break
    return jobs


def _detail(session: requests.Session, job: Dict) -> str:
    url = job.get("redirect_url", "")
    if not url:
        return ""
    try:
        response = session.get(url, timeout=DEFAULT_TIMEOUT, headers={
            "User-Agent": "Mozilla/5.0 (CareerOS/5.0)",
            "Accept-Language": "ro-RO,ro;q=0.9,en;q=0.8",
        })
        if response.status_code != 200:
            return ""
        soup = BeautifulSoup(response.text or "", "html.parser")
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()
        return _text(soup.body)[:14000] if soup.body else ""
    except requests.RequestException:
        return ""


def fetch_hipo(
    keywords: str,
    location: str = "Timisoara",
    limit: int = 20,
    session: Optional[requests.Session] = None,
    **_,
) -> SourceResult:
    """Fetch query-aware Hipo results, then enrich a small top slice."""
    source = "Hipo"
    session = session or build_session()
    url = _search_url(keywords, location)
    html, error = _get_html(session, url)
    if not html:
        return SourceResult(source=source, error=f"Hipo: {error or 'no usable HTML returned'}")

    jobs = _parse(html, max(limit * 2, limit), location)
    # Detail pages are where Hipo exposes the useful language, experience,
    # salary and responsibility text. Enrich only the first few to keep the
    # source fast and respectful.
    for job in jobs[: min(10, len(jobs))]:
        detail = _detail(session, job)
        if detail:
            job["description"] = detail
            job["description_text"] = detail[:8000]
            if not job.get("salary_text"):
                job["salary_text"] = _salary_text(detail)

    return SourceResult(source=source, jobs=jobs[:limit])


__all__ = ["fetch_hipo"]
