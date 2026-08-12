"""CareerOS AI — job search, matching and application assistant.

The package holds all business logic (pure Python, unit-tested) while
``app.py`` contains only the Streamlit presentation layer.
"""

__version__ = "4.0.0"

from .profile import DEFAULT_PROFILE, Profile
from .matching import MatchResult, calculate_match, hard_filter_job, priority_band
from .tracks import (
    ALL_TRACKS,
    DEFAULT_TRACK,
    TRACK_ARABIC,
    TRACK_CUSTOM,
    TRACK_FINANCE,
    TRACK_FULL,
    TRACK_LOGISTICS,
    TRACK_OPERATIONS,
    TRACK_SUPPORT,
)
from .salary import SalaryInfo, format_salary, parse_salary
from .search import (
    CAREER_PRESETS,
    SearchReport,
    SearchRequest,
    build_search_queries,
    deduplicate_jobs,
    run_search,
    score_and_filter,
)
from .tracker import Application, ApplicationStore, STATUS_FLOW

__all__ = [
    "__version__",
    "Profile",
    "DEFAULT_PROFILE",
    "MatchResult",
    "calculate_match",
    "hard_filter_job",
    "priority_band",
    "SalaryInfo",
    "parse_salary",
    "format_salary",
    "CAREER_PRESETS",
    "SearchRequest",
    "SearchReport",
    "build_search_queries",
    "deduplicate_jobs",
    "run_search",
    "score_and_filter",
    "Application",
    "ApplicationStore",
    "STATUS_FLOW",
    "ALL_TRACKS",
    "DEFAULT_TRACK",
    "TRACK_FULL",
    "TRACK_FINANCE",
    "TRACK_OPERATIONS",
    "TRACK_SUPPORT",
    "TRACK_ARABIC",
    "TRACK_LOGISTICS",
    "TRACK_CUSTOM",
]
