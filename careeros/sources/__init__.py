"""Job source adapters."""

from .base import SourceResult, build_session, days_since, make_job, parse_date
from .providers import PROVIDERS, ProviderSpec, fetch_source
from .romania_boards import fetch_romania_boards
from .hipo import fetch_hipo

# Romanian local-board coverage. Keep these adapters behind the same
# ProviderSpec/SourceResult contract so the search engine and UI remain
# unchanged while source coverage grows.
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
