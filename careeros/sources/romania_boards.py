"""Public Romanian job-board collector for CareerOS.

Inspired by the source-specific parsing approach of the public
``romania_it_job_scraper`` project, but kept as an isolated CareerOS provider.
It tries normal HTTP first and uses Selenium only as an optional fallback when
an installed browser is needed for a dynamic page. It never logs in, solves
CAPTCHAs, or submits applications.
"""

from __future__ import annotations

import concurrent.futures
import re
from html import unescape
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

from ..text import clean_html_text, normalize_text
from .base import DEFAULT_TIMEOUT, SourceResult, build_session, make_job

SOURCE_LABELS = {"ejobs": "eJobs", "bestjobs": "BestJobs", "linkedin": "LinkedIn"}


def _slug(value: str) -> str:
    text = normalize_text(value)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "romania"


def _headers() -> Dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
    }


def _fetch_http(session: requests.Session, url: str) -> Tuple[str, str]:
    try:
        response = session.get(url, headers=_headers(), timeout=DEFAULT_TIMEOUT, allow_redirects=True)
        if response.status_code != 200:
            return "", f"HTTP {response.status_code}"
        text = response.text or ""
        marker = normalize_text(text[:5000])
        if any(x in marker for x in ("captcha", "verify you are human", "access denied", "robot check")):
            return "", "anti-bot/challenge page"
        return text, ""
    except requests.RequestException as exc:
        return "", str(exc)


def _fetch_selenium(url: str) -> str:
    """Optional dynamic-page fallback; normal installs do not need Selenium."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except Exception:
        return ""
    driver = None
    try:
        options = Options()
        for arg in ("--headless=new", "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage", "--window-size=1920,1080"):
            options.add_argument(arg)
        options.add_argument(f"--user-agent={_headers()['User-Agent']}")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        WebDriverWait(driver, 12).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        return driver.page_source or ""
    except Exception:
        return ""
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def _get_html(session: requests.Session, url: str) -> Tuple[str, str]:
    html, error = _fetch_http(session, url)
    if html:
        return html, ""
    browser_html = _fetch_selenium(url)
    if browser_html:
        return browser_html, ""
    return "", error or "no usable HTML returned"


def _text(node) -> str:
    return clean_html_text(node.get_text(" ", strip=True)) if node else ""


def _absolute(url: str, base: str) -> str:
    return urljoin(base, unescape(str(url or "")).strip()).split("?")[0]


def _salary_text(blob: str) -> str:
    text = clean_html_text(blob)
    for pattern in (
        r"\d[\d\s.,]*\s*(?:-|–|—|to)\s*\d[\d\s.,]*\s*(?:ron|lei|eur|€)",
        r"\d[\d\s.,]*\s*(?:ron|lei|eur|€)\s*(?:net|brut)?",
        r"(?:salary|salariu)\s*[:\-]?\s*\d[\d\s.,]*",
    ):
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return ""


def _detail_description(session: requests.Session, url: str) -> str:
    if not url:
        return ""
    html, _ = _fetch_http(session, url)
    if not html:
        html = _fetch_selenium(url)
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    candidates = []
    for selector in ("article", "main", "[class*=description]", "[class*=job-description]"):
        candidates.extend(soup.select(selector))
    text = max((_text(n) for n in candidates), key=len, default="") if candidates else _text(soup.body)
    return text[:12000]


def _enrich(session: requests.Session, jobs: List[Dict], max_details: int = 12) -> None:
    targets = [j for j in jobs if j.get("redirect_url")][:max_details]
    if not targets:
        return
    def worker(job: Dict) -> Tuple[Dict, str]:
        return job, _detail_description(session, job.get("redirect_url", ""))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for job, desc in executor.map(worker, targets):
            if desc:
                job["description"] = desc
                job["description_text"] = desc[:6000]
                if not job.get("salary_text"):
                    job["salary_text"] = _salary_text(desc)


def _parse_ejobs(html: str, limit: int, base: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs: List[Dict] = []
    for heading in soup.select("h2.job-card-content-middle__title"):
        link = heading.find("a", href=True)
        if not link:
            continue
        parent = heading.parent
        title = _text(heading)
        company = _text(parent.select_one("h3")) if parent else ""
        location = _text(parent.select_one("div.job-card-content-middle__info")) if parent else ""
        url = _absolute(link.get("href"), base)
        blob = _text(parent)
        if title and url:
            jobs.append(make_job(title=title, company=company, location=location or "Romania", description=blob, url=url, source="eJobs", salary_text=_salary_text(blob)))
        if len(jobs) >= limit:
            break
    return jobs


def _parse_bestjobs(html: str, limit: int, base: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs: List[Dict] = []
    seen = set()
    for link in soup.select("a.absolute.inset-0.z-1"):
        url = _absolute(link.get("href"), base)
        parent = link.find_parent("div")
        if not parent or not url or url in seen:
            continue
        title_node = parent.select_one("h2.line-clamp-2") or parent.select_one("h2")
        title = _text(title_node)
        if not title:
            continue
        company = _text(parent.select_one("div.text-ink-medium"))
        location = _text(parent.select_one("div.relative.z-2"))
        blob = _text(parent)
        seen.add(url)
        jobs.append(make_job(title=title, company=company, location=location or "Romania", description=blob, url=url, source="BestJobs", salary_text=_salary_text(blob)))
        if len(jobs) >= limit:
            break
    if not jobs:
        for heading in soup.select("h2"):
            title = _text(heading)
            link = heading.find_parent("a", href=True) or heading.find("a", href=True)
            if not title or not link:
                continue
            url = _absolute(link.get("href"), base)
            blob = _text(heading.parent)
            jobs.append(make_job(title=title, company="", location="Romania", description=blob, url=url, source="BestJobs", salary_text=_salary_text(blob)))
            if len(jobs) >= limit:
                break
    return jobs


def _parse_linkedin(html: str, limit: int, base: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.base-card") or soup.select("li.result-card")
    jobs: List[Dict] = []
    seen = set()
    for card in cards:
        link = card.select_one("a.base-card__full-link") or card.find("a", href=True)
        title_node = card.select_one("h3.base-search-card__title")
        if not link or not title_node:
            continue
        title = _text(title_node)
        url = _absolute(link.get("href"), base)
        if not title or not url or url in seen:
            continue
        company = _text(card.select_one("h4.base-search-card__subtitle"))
        location = _text(card.select_one("span.job-search-card__location")) or "Romania"
        blob = _text(card)
        seen.add(url)
        jobs.append(make_job(title=title, company=company, location=location, description=blob, url=url, source="LinkedIn", salary_text=_salary_text(blob)))
        if len(jobs) >= limit:
            break
    return jobs


def _search_url(source: str, keywords: str, location: str) -> str:
    query = _slug(keywords)
    loc = _slug(location or "romania")
    if source == "ejobs":
        return f"https://www.ejobs.ro/locuri-de-munca/{loc}/{query}"
    if source == "bestjobs":
        return f"https://www.bestjobs.eu/locuri-de-munca-in-{loc}/{query}"
    return "https://www.linkedin.com/jobs/search/?keywords=" + quote_plus(keywords) + "&location=" + quote_plus(location or "Romania")


def _parse(source: str, html: str, limit: int) -> List[Dict]:
    if source == "ejobs":
        return _parse_ejobs(html, limit, "https://www.ejobs.ro")
    if source == "bestjobs":
        return _parse_bestjobs(html, limit, "https://www.bestjobs.eu")
    return _parse_linkedin(html, limit, "https://www.linkedin.com")


def fetch_romania_boards(keywords: str, location: str = "Timisoara", limit: int = 20, session: Optional[requests.Session] = None, **_) -> SourceResult:
    """Fetch a bounded, query-aware sample from eJobs, BestJobs and LinkedIn."""
    source = "Romania Boards"
    session = session or build_session()
    queries = [q.strip() for q in re.split(r"\s*\|\s*", keywords or "") if q.strip()][:6]
    if not queries:
        queries = ["operations"]
    per_query = max(4, min(10, limit // max(1, len(queries))))
    all_jobs: List[Dict] = []
    errors: List[str] = []

    for query in queries:
        for board in ("ejobs", "bestjobs", "linkedin"):
            url = _search_url(board, query, location)
            html, error = _get_html(session, url)
            if not html:
                errors.append(f"{SOURCE_LABELS[board]}: {error}")
                continue
            try:
                all_jobs.extend(_parse(board, html, per_query))
            except Exception as exc:
                errors.append(f"{SOURCE_LABELS[board]}: parser error — {exc}")

    _enrich(session, all_jobs, max_details=min(24, max(12, limit)))

    unique: Dict[Tuple[str, str], Dict] = {}
    for job in all_jobs:
        company = str((job.get("company") or {}).get("display_name", ""))
        key = (normalize_text(job.get("title", "")), normalize_text(company))
        if key != ("", ""):
            unique.setdefault(key, job)
    jobs = list(unique.values())[: max(limit * 2, limit)]
    if not jobs and errors:
        return SourceResult(source=source, error="; ".join(dict.fromkeys(errors))[:900])
    if errors:
        return SourceResult(source=source, jobs=jobs, error="Partial source issues: " + "; ".join(dict.fromkeys(errors))[:700])
    return SourceResult(source=source, jobs=jobs)
