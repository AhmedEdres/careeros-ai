"""Job source adapters."""

from typing import List, Optional

from .base import SourceResult, build_session, days_since, make_job, parse_date
from .providers import PROVIDERS, ProviderSpec, fetch_source
from .romania_boards import fetch_romania_boards
from .hipo import fetch_hipo
from .anofm import fetch_anofm

PROVIDERS["romania_boards"] = ProviderSpec(
    "romania_boards",
    "🇷🇴 eJobs + BestJobs + LinkedIn",
    "Romania Boards",
    fetch_romania_boards,
    default_on=True,
    supports_location=True,
    client_side_filter=False,
    help_text="Public Romania-board discovery with HTTP-first parsing and optional Selenium fallback.",
)

PROVIDERS["hipo"] = ProviderSpec(
    "hipo",
    "🇷🇴 Hipo — Romania",
    "Hipo",
    fetch_hipo,
    default_on=True,
    supports_location=True,
    client_side_filter=False,
    help_text="Romanian job board with local, remote/hybrid and salary-rich listings.",
)

_ANOFM_ALIASES = {
    "production": ("productie", "operator productie", "muncitor productie", "asamblare", "montaj"),
    "warehouse": ("depozit", "gestionar", "lucrator depozit", "magazioner", "manipulant marfuri"),
    "logistics": ("logistica", "gestionar", "expeditor", "transport", "distributie"),
    "customer support": ("suport clienti", "relatii cu clientii", "serviciu clienti", "operator call center"),
    "customer service": ("serviciu clienti", "relatii cu clientii", "suport clienti"),
    "back office": ("activitati de birou", "operator calculator"),
    "operations": ("operational", "operatiuni", "coordonator", "activitati operationale"),
    "accounting": ("contabil", "contabilitate", "economist", "facturare"),
    "finance": ("financiar", "finante", "economist", "contabilitate"),
    "tax": ("fiscal", "fiscala", "taxe", "impozite"),
    "compliance": ("conformitate", "control intern", "reglementare"),
    "legal": ("juridic", "consilier juridic", "asistent juridic"),
    "arabic": ("araba", "limba araba"),
    "quality": ("calitate", "inspector calitate", "control calitate"),
}


def _anofm_phrases(phrases: Optional[List[str]]) -> List[str]:
    base = [p for p in (phrases or []) if p and p.strip()]
    expanded = list(base)
    for phrase in base:
        normalized = phrase.lower()
        for key, aliases in _ANOFM_ALIASES.items():
            if key in normalized:
                expanded.extend(aliases)
    seen = set()
    result = []
    for phrase in expanded:
        marker = " ".join(phrase.lower().split())
        if marker and marker not in seen:
            seen.add(marker)
            result.append(phrase)
    return result


def _fetch_anofm_for_candidate(*args, **kwargs):
    kwargs["phrases"] = _anofm_phrases(kwargs.get("phrases"))
    return fetch_anofm(*args, **kwargs)


# ANOFM / Mediere is a first-class public Romanian source. It is fetched once
# per search (not once per expanded query) and filtered locally.
PROVIDERS["anofm"] = ProviderSpec(
    "anofm",
    "🇷🇴 ANOFM — Mediere",
    "ANOFM / Mediere",
    _fetch_anofm_for_candidate,
    default_on=True,
    supports_location=True,
    client_side_filter=True,
    help_text="Official Romanian public job postings; no API key. Structured requirements are preserved for realistic matching.",
)

__all__ = [
    "SourceResult",
    "build_session",
    "days_since",
    "make_job",
    "parse_date",
    "PROVIDERS",
    "ProviderSpec",
    "fetch_source",
]
