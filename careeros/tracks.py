"""Career-track configuration for matching engine v4.

Tracks change *how* a job is scored, not only which queries are sent. Each
track has a 100-point weight table, skill-group multipliers and a Romanian
pressure factor: Arabic is worth 30 points on the Arabic track and 8 on
Logistics; a Bucharest finance role is far more Romanian-dependent than a
remote Arabic desk.
"""

from __future__ import annotations

from typing import Dict, Mapping

__all__ = [
    "TRACK_FULL",
    "TRACK_FINANCE",
    "TRACK_OPERATIONS",
    "TRACK_SUPPORT",
    "TRACK_ARABIC",
    "TRACK_LOGISTICS",
    "TRACK_CUSTOM",
    "ALL_TRACKS",
    "DEFAULT_TRACK",
    "TRACK_WEIGHTS",
    "TRACK_SKILL_MULTIPLIERS",
    "TRACK_RO_PRESSURE",
    "LOGISTICS_ALLOWED_TITLES",
    "resolve_track",
    "track_weights",
    "skill_multiplier",
    "romanian_pressure",
    "dimension_max",
]

TRACK_FULL = "🔥 Full Career Scan (recommended)"
TRACK_FINANCE = "💰 Finance & Compliance"
TRACK_OPERATIONS = "⚙️ Operations & Back Office"
TRACK_SUPPORT = "📞 Customer Support & BPO"
TRACK_ARABIC = "🗣️ Arabic-Speaking Roles"
TRACK_LOGISTICS = "🏭 Logistics & Production"
TRACK_CUSTOM = "📝 Custom keywords"

ALL_TRACKS = (
    TRACK_FULL,
    TRACK_FINANCE,
    TRACK_OPERATIONS,
    TRACK_SUPPORT,
    TRACK_ARABIC,
    TRACK_LOGISTICS,
    TRACK_CUSTOM,
)

DEFAULT_TRACK = TRACK_FULL

# Titles that look "wrong-track" on an office search but are in-scope for
# Logistics & Production (Timisoara manufacturing / warehouse market).
LOGISTICS_ALLOWED_TITLES = {
    "operator cnc",
    "cnc operator",
    "mechanic",
}

# Base evidence scale used by the v3 dimension functions. Track tables
# rescale these onto their own 100-point budget.
BASE_DIMENSION_MAX: Dict[str, int] = {
    "location": 20,
    "skills": 25,
    "arabic": 15,
    "english": 10,
    "experience": 10,
    "salary": 10,
    "education": 5,
    "relevance": 5,
}

TRACK_WEIGHTS: Dict[str, Dict[str, int]] = {
    TRACK_FULL: dict(BASE_DIMENSION_MAX),
    TRACK_CUSTOM: dict(BASE_DIMENSION_MAX),
    TRACK_FINANCE: {
        "location": 14,
        "skills": 24,
        "arabic": 8,
        "english": 12,
        "experience": 12,
        "salary": 10,
        "education": 12,
        "relevance": 8,
    },
    TRACK_OPERATIONS: {
        "location": 18,
        "skills": 28,
        "arabic": 10,
        "english": 10,
        "experience": 12,
        "salary": 10,
        "education": 4,
        "relevance": 8,
    },
    TRACK_SUPPORT: {
        "location": 16,
        "skills": 26,
        "arabic": 16,
        "english": 14,
        "experience": 10,
        "salary": 10,
        "education": 0,
        "relevance": 8,
    },
    TRACK_ARABIC: {
        "location": 12,
        "skills": 18,
        "arabic": 30,
        "english": 12,
        "experience": 8,
        "salary": 8,
        "education": 2,
        "relevance": 10,
    },
    TRACK_LOGISTICS: {
        "location": 20,
        "skills": 30,
        "arabic": 8,
        "english": 8,
        "experience": 12,
        "salary": 10,
        "education": 4,
        "relevance": 8,
    },
}

_UNITY = {
    "operations_support": 1.0,
    "finance_compliance": 1.0,
    "logistics": 1.0,
    "production": 1.0,
    "tools": 1.0,
    "languages_market": 1.0,
}

TRACK_SKILL_MULTIPLIERS: Dict[str, Dict[str, float]] = {
    TRACK_FULL: dict(_UNITY),
    TRACK_CUSTOM: dict(_UNITY),
    TRACK_FINANCE: {
        "operations_support": 0.8,
        "finance_compliance": 1.6,
        "logistics": 0.5,
        "production": 0.3,
        "tools": 1.1,
        "languages_market": 0.8,
    },
    TRACK_OPERATIONS: {
        "operations_support": 1.4,
        "finance_compliance": 1.0,
        "logistics": 0.9,
        "production": 0.6,
        "tools": 1.1,
        "languages_market": 0.9,
    },
    TRACK_SUPPORT: {
        "operations_support": 1.5,
        "finance_compliance": 0.6,
        "logistics": 0.5,
        "production": 0.3,
        "tools": 1.0,
        "languages_market": 1.3,
    },
    TRACK_ARABIC: {
        "operations_support": 1.2,
        "finance_compliance": 0.7,
        "logistics": 0.4,
        "production": 0.2,
        "tools": 0.9,
        "languages_market": 1.8,
    },
    TRACK_LOGISTICS: {
        "operations_support": 0.55,
        "finance_compliance": 0.5,
        "logistics": 1.6,
        "production": 1.5,
        "tools": 1.1,
        "languages_market": 0.4,
    },
}

# Baseline Romanian-dependence of the *role family*. Location then scales it:
# Bucharest finance → 1.35, remote Arabic desk → 0.5.
TRACK_RO_PRESSURE: Dict[str, float] = {
    TRACK_FULL: 1.0,
    TRACK_CUSTOM: 1.0,
    TRACK_FINANCE: 1.15,
    TRACK_OPERATIONS: 1.0,
    TRACK_SUPPORT: 0.8,
    TRACK_ARABIC: 0.55,
    TRACK_LOGISTICS: 0.9,
}


def resolve_track(track: str | None) -> str:
    if track and track in TRACK_WEIGHTS:
        return track
    return DEFAULT_TRACK


def track_weights(track: str | None) -> Dict[str, int]:
    return dict(TRACK_WEIGHTS[resolve_track(track)])


def dimension_max(track: str | None, dim: str) -> int:
    return track_weights(track).get(dim, BASE_DIMENSION_MAX.get(dim, 10))


def skill_multiplier(track: str | None, group: str) -> float:
    table = TRACK_SKILL_MULTIPLIERS.get(resolve_track(track), _UNITY)
    return float(table.get(group, 1.0))


def romanian_pressure(
    track: str | None,
    location_text: str = "",
    remote_class: str = "not_remote",
) -> float:
    """How hard Romanian weighs for this (track × location) pair.

    Explicit values from the v4 spec: a Bucharest finance role is 1.35×;
    a remote Arabic-speaking desk is 0.5×.
    """
    from .text import contains_any, normalize_text

    resolved = resolve_track(track)
    loc = normalize_text(location_text)
    remote = remote_class or "not_remote"

    if resolved == TRACK_ARABIC and remote in {
        "remote_eu", "remote_country", "excellent", "good",
    }:
        return 0.5
    if resolved == TRACK_FINANCE and contains_any(loc, ["bucharest", "bucuresti"]):
        return 1.35
    if contains_any(loc, ["bucharest", "bucuresti", "cluj"]) and resolved != TRACK_ARABIC:
        return round(TRACK_RO_PRESSURE[resolved] * 1.17, 2)

    base = TRACK_RO_PRESSURE[resolved]
    if remote in {"remote_eu", "excellent"}:
        return round(base * 0.7, 2)
    return base
