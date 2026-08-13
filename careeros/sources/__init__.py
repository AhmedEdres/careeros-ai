"""Job source adapters."""

from .base import SourceResult, build_session, days_since, make_job, parse_date
from .providers import PROVIDERS, ProviderSpec, fetch_source
from .romania_boards import fetch_romania_boards

# Add the Romanian board collector without disturbing the existing API
# providers. It uses the same ProviderSpec/SourceResult contract.
PROVIDERS["romania_boards"] = ProviderSpec(
    "romania_boards",
    "🇷🇴 eJobs + BestJobs + LinkedIn",
    "Romania Boards",
    fetch_romania_boards,
    default_on=True,
    supports_location=True,
    client_side_filter=True,
    help_text="Public Romania-board discovery with HTTP-first parsing and optional Selenium fallback.",
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
