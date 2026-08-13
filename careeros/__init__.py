"""CareerOS AI — job search, matching and application assistant."""

__version__ = "4.3.0"

from .profile import DEFAULT_PROFILE, Profile
from . import matching as _matching
from .matching import MatchResult, calculate_match as _calculate_match_v4, hard_filter_job as _hard_filter_job_v4, priority_band
from .matching import blend_scores
from .role_intelligence import wrap_matching

# B2 is a usable working level. Do not reject a job merely because an ad says
# "fluent English" or mentions C1 as a preferred/alternative qualification.
# Reject only when the posting explicitly requires a level above the candidate's
# configured English level. This is intentionally narrow to avoid false
# negatives in international Romanian roles.
_matching.ENGLISH_ABOVE_B2 = [
    "english c1 required", "english c2 required",
    "c1 english required", "c2 english required",
    "english required c1", "english required c2",
    "c1 level english required", "c2 level english required",
    "english at c1 level required", "english at c2 level required",
    "english proficiency c1 required", "english proficiency c2 required",
    "english c1 proficiency required", "english c2 proficiency required",
    "native english required", "native-level english required",
    "native level english required", "english mother tongue required",
    "english c1 mandatory", "english c2 mandatory",
    "c1 english mandatory", "c2 english mandatory",
]

# Keep the proven v4 engine intact and add the semantic guardrail layer.
hard_filter_job, calculate_match = wrap_matching(
    _hard_filter_job_v4, _calculate_match_v4, blend_scores
)
_matching.hard_filter_job = hard_filter_job
_matching.calculate_match = calculate_match

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
