"""Text normalisation and matching helpers.

Pure functions only — no Streamlit imports, so this module is unit-testable
and can be reused outside the UI.
"""

from __future__ import annotations

import hashlib
import html
import re
import unicodedata
from functools import lru_cache
from typing import Iterable, Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

__all__ = [
    "normalize_text",
    "clean_html_text",
    "safe_company_name",
    "normalize_location",
    "is_romania_location",
    "valid_url",
    "canonical_url",
    "text_hash",
    "contains_phrase",
    "contains_any",
    "matched_phrases",
    "truncate",
]

_WHITESPACE_RE = re.compile(r"\s+")
_TAG_RE = re.compile(r"<[^>]*>")
_SCRIPT_RE = re.compile(r"<(script|style)\b.*?</\1>", re.IGNORECASE | re.DOTALL)
_BLOCK_BREAK_RE = re.compile(
    r"</(p|div|li|ul|ol|tr|h[1-6])>|<br\s*/?>", re.IGNORECASE
)
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")

# Tracking parameters stripped when canonicalising URLs for dedup.
_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_id", "utm_name", "ref", "referer", "referrer", "source", "medium",
    "fbclid", "gclid", "msclkid", "mc_cid", "mc_eid", "trk", "trkCampaign",
    "sid", "cid", "aid", "affid", "aff_id", "campaign", "gh_src",
}


def normalize_text(text: object) -> str:
    """Lowercase, strip accents and collapse whitespace.

    ``Timișoara`` -> ``timisoara`` so Romanian diacritics never break matching.
    """
    value = str(text or "")
    # Romanian comma-below characters decompose inconsistently; map them first.
    value = value.translate(
        str.maketrans({
            "ș": "s", "Ș": "S", "ş": "s", "Ş": "S",
            "ț": "t", "Ț": "T", "ţ": "t", "Ţ": "T",
            "ă": "a", "Ă": "A", "â": "a", "Â": "A",
            "î": "i", "Î": "I",
        })
    )
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    return _WHITESPACE_RE.sub(" ", value).strip().lower()


def clean_html_text(text: object) -> str:
    """Strip HTML to readable plain text, preserving block boundaries."""
    value = str(text or "")
    value = _SCRIPT_RE.sub(" ", value)
    value = _BLOCK_BREAK_RE.sub("\n", value)
    value = _TAG_RE.sub(" ", value)
    value = html.unescape(value)
    # &nbsp; unescapes to U+00A0, which is not matched by \s in some contexts
    # and shows up as a stray character in the UI.
    value = value.replace("\u00a0", " ").replace("\u200b", "")
    # Collapse spaces but keep single newlines so descriptions stay readable.
    value = re.sub(r"[ \t\r\f\v]+", " ", value)
    value = re.sub(r"\n\s*\n\s*", "\n\n", value)
    value = re.sub(r" *\n *", "\n", value)
    return value.strip()


def safe_company_name(company: object) -> str:
    """Company names arrive as a string or as ``{"display_name": ...}``."""
    if isinstance(company, dict):
        name = company.get("display_name") or company.get("name") or ""
        return str(name).strip() or "Company not listed"
    return str(company or "").strip() or "Company not listed"


def normalize_location(location: object, default: str = "Timisoara, Romania") -> str:
    """Make a location string API-friendly (adds the country when obvious)."""
    value = str(location or "").strip()
    if not value:
        return default
    normalized = normalize_text(value)
    if normalized in {"timisoara", "timis", "timisoara romania", "timis romania"}:
        return "Timisoara, Romania"
    romanian_cities = {
        "timisoara", "timis", "bucharest", "bucuresti", "cluj", "cluj-napoca",
        "iasi", "brasov", "constanta", "oradea", "sibiu", "arad", "craiova",
    }
    if "romania" not in normalized and normalized in romanian_cities:
        return f"{value}, Romania"
    return value


def is_romania_location(location: object) -> bool:
    text = normalize_text(location)
    return contains_any(
        text,
        ["romania", "timisoara", "timis", "bucharest", "bucuresti",
         "cluj", "iasi", "brasov", "constanta", "arad", "sibiu", "oradea"],
    )


def valid_url(url: object) -> bool:
    try:
        parsed = urlparse(str(url or ""))
    except (ValueError, AttributeError):
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def canonical_url(url: object) -> str:
    """Normalise a URL for deduplication.

    Drops tracking parameters, the fragment, ``www.`` and a trailing slash so
    the same posting shared by two aggregators collapses into one entry.
    """
    raw = str(url or "").strip()
    if not raw:
        return ""
    try:
        parsed = urlparse(raw)
    except ValueError:
        return raw.lower()
    if not parsed.netloc:
        return raw.lower()

    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    netloc = re.sub(r":(80|443)$", "", netloc)

    query_pairs = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=False)
        if key.lower() not in _TRACKING_PARAMS
    ]
    query = urlencode(sorted(query_pairs))

    path = parsed.path.rstrip("/") or "/"
    return urlunparse(("https", netloc, path, "", query, "")).lower()


def text_hash(text: object) -> str:
    """Stable hash of the alphanumeric skeleton of a string."""
    cleaned = _NON_ALNUM_RE.sub("", normalize_text(text))
    return hashlib.md5(cleaned.encode("utf-8")).hexdigest()


@lru_cache(maxsize=4096)
def _phrase_pattern(phrase: str) -> Optional[re.Pattern]:
    """Compile a whole-word regex for a phrase (cached).

    Word boundaries stop the classic false positives: ``eu`` matching
    *Deutschland*, ``risk`` matching *asterisk*, ``sap`` matching *sapient*.
    """
    normalized = normalize_text(phrase)
    if not normalized:
        return None
    # Allow any run of non-alphanumerics between words: "back office" also
    # matches "back-office" and "back  office".
    tokens = [re.escape(tok) for tok in re.split(r"[^a-z0-9]+", normalized) if tok]
    if not tokens:
        return None
    body = r"[^a-z0-9]{0,3}".join(tokens)
    return re.compile(rf"(?<![a-z0-9]){body}(?![a-z0-9])")


def contains_phrase(text: str, phrase: str) -> bool:
    """Whole-word containment check on already normalised text."""
    pattern = _phrase_pattern(phrase)
    if pattern is None:
        return False
    return pattern.search(text) is not None


def contains_any(text: str, phrases: Iterable[str]) -> bool:
    return any(contains_phrase(text, phrase) for phrase in phrases)


def matched_phrases(text: str, phrases: Iterable[str]) -> list:
    return [phrase for phrase in phrases if contains_phrase(text, phrase)]


def truncate(text: str, limit: int, suffix: str = "…") -> str:
    value = str(text or "")
    if len(value) <= limit:
        return value
    cut = value[:limit].rsplit(" ", 1)[0]
    return f"{cut}{suffix}"
