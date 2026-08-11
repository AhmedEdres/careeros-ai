"""Salary text parsing and normalisation to monthly RON.

Job boards publish salary as free text ("3.500 - 5.000 RON/luna", "€45,000 a
year", "$25 per hour"). The original app only scored salaries coming from
Adzuna's structured fields, so ~everything scored 0/10. This module extracts a
monthly RON range from free text so the salary dimension actually works.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Tuple

from .text import normalize_text

__all__ = ["SalaryInfo", "parse_salary", "to_monthly_ron", "format_salary"]

# Indicative FX rates -> RON. Kept deliberately conservative and centralised;
# they only influence ranking, never a hard filter.
FX_TO_RON = {
    "ron": 1.0,
    "eur": 4.98,
    "usd": 4.60,
    "gbp": 5.85,
    "chf": 5.35,
    "pln": 1.17,
    "huf": 0.0125,
    "bgn": 2.55,
    "czk": 0.20,
}

_CURRENCY_ALIASES = {
    "ron": "ron", "lei": "ron", "leu": "ron", "rol": "ron",
    "eur": "eur", "euro": "eur", "euros": "eur", "€": "eur",
    "usd": "usd", "dollar": "usd", "dollars": "usd", "$": "usd", "us$": "usd",
    "gbp": "gbp", "pound": "gbp", "pounds": "gbp", "£": "gbp",
    "chf": "chf", "pln": "pln", "zl": "pln", "zloty": "pln",
    "huf": "huf", "ft": "huf", "bgn": "bgn", "czk": "czk",
}

# Multipliers converting a period to "per month".
_PERIOD_MULTIPLIERS = {
    "hour": 160.0,      # ~40h/week
    "day": 21.0,
    "week": 4.33,
    "month": 1.0,
    "year": 1 / 12,
}

_PERIOD_PATTERNS = [
    (r"\b(per|an|a|/)\s*(hour|hr|h)\b|\bhourly\b|/\s*h\b|\bpe\s+ora\b", "hour"),
    (r"\b(per|a|/)\s*day\b|\bdaily\b|\bpe\s+zi\b", "day"),
    (r"\b(per|a|/)\s*week\b|\bweekly\b|\bpe\s+saptamana\b", "week"),
    (r"\b(per|a|/)\s*(month|mo|mth)\b|\bmonthly\b|\b(pe\s+)?luna\b|\blunar\b|/\s*luna\b", "month"),
    (r"\b(per|a|/)\s*(year|yr|annum|an)\b|\bannual(ly)?\b|\bp\.?a\.?\b|\bpe\s+an\b", "year"),
]

# 1.500,50 / 1,500.50 / 1500 / 1 500
_NUMBER_RE = re.compile(r"\d[\d\s.,]*\d|\d")
_K_SUFFIX_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*k\b")

# Numbers that are never salaries: working hours, holiday days, percentages,
# required years of experience, team sizes.
_NOISE_RE = re.compile(
    r"\d+(?:[.,]\d+)?\s*(?:%|percent|"
    r"hours?\s*(?:per|a|/)\s*week|hours?\s*/\s*week|h\s*/\s*week|"
    r"ore\s*(?:pe|/)\s*saptamana|"
    r"days?\s*(?:of\s+)?(?:holiday|vacation|leave|off|remote)|"
    r"zile\s+(?:de\s+)?concediu|"
    r"years?\s+(?:of\s+)?experience|ani\s+experienta|"
    r"people|employees|colleagues|angajati)"
)


@dataclass(frozen=True)
class SalaryInfo:
    """Parsed salary, normalised to gross monthly RON when possible."""

    raw: str = ""
    currency: Optional[str] = None
    period: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    monthly_ron_min: Optional[float] = None
    monthly_ron_max: Optional[float] = None

    @property
    def has_value(self) -> bool:
        return self.monthly_ron_min is not None or self.monthly_ron_max is not None

    @property
    def monthly_ron_mid(self) -> Optional[float]:
        values = [v for v in (self.monthly_ron_min, self.monthly_ron_max) if v]
        if not values:
            return None
        return sum(values) / len(values)


def _parse_number(token: str) -> Optional[float]:
    """Parse a localized number: '1.500' -> 1500, '1,500.50' -> 1500.5."""
    token = token.strip().replace(" ", "").replace("\u00a0", "")
    if not token:
        return None

    has_dot, has_comma = "." in token, "," in token
    if has_dot and has_comma:
        # The right-most separator is the decimal one.
        if token.rfind(",") > token.rfind("."):
            token = token.replace(".", "").replace(",", ".")
        else:
            token = token.replace(",", "")
    elif has_comma:
        parts = token.split(",")
        # "1,5" -> decimal; "1,500" / "10,000" -> thousands
        token = (
            token.replace(",", ".")
            if len(parts) == 2 and len(parts[1]) <= 2 and len(parts[0]) <= 3
            else token.replace(",", "")
        )
    elif has_dot:
        parts = token.split(".")
        if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3):
            token = token.replace(".", "")  # 1.500 / 1.500.000 -> thousands

    try:
        return float(token)
    except ValueError:
        return None


def _detect_currency(text: str) -> Optional[str]:
    for symbol in ("€", "£", "$"):
        if symbol in text:
            return _CURRENCY_ALIASES[symbol]
    for alias, code in _CURRENCY_ALIASES.items():
        if alias.isalpha() and re.search(rf"(?<![a-z]){re.escape(alias)}(?![a-z])", text):
            return code
    return None


def _detect_period(text: str) -> Optional[str]:
    for pattern, period in _PERIOD_PATTERNS:
        if re.search(pattern, text):
            return period
    return None


def _infer_period(amount: float, currency: Optional[str]) -> str:
    """Guess the period from magnitude when the text does not say."""
    if currency == "ron":
        if amount <= 400:
            return "hour"
        if amount >= 60_000:
            return "year"
        return "month"
    if amount <= 200:
        return "hour"
    if amount >= 15_000:
        return "year"
    return "month"


def parse_salary(
    raw_text: object,
    fallback_min: Optional[float] = None,
    fallback_max: Optional[float] = None,
    currency_hint: Optional[str] = None,
) -> SalaryInfo:
    """Extract a salary range from free text (or structured fallbacks)."""
    raw = str(raw_text or "").strip()
    text = normalize_text(raw)

    currency = _detect_currency(text) or currency_hint
    period = _detect_period(text)

    # Remove spans that are numbers but never salaries ("40 hours per week").
    search_text = _NOISE_RE.sub(" ", text)

    amounts = []
    # Handle "45k - 60k" style shorthand first.
    for match in _K_SUFFIX_RE.finditer(search_text):
        value = _parse_number(match.group(1))
        if value is not None:
            amounts.append(value * 1000)
    if not amounts:
        # A year-like number is only ambiguous when nothing marks it as money.
        # "2000 RON per month" is a salary; a bare "2024" is not.
        has_money_context = currency is not None or period is not None
        for match in _NUMBER_RE.finditer(search_text):
            value = _parse_number(match.group(0))
            if value is None or value < 5:
                continue
            if (
                not has_money_context
                and 1990 <= value <= 2100
                and value == int(value)
            ):
                continue
            amounts.append(value)

    if not amounts:
        if fallback_min is None and fallback_max is None:
            return SalaryInfo(raw=raw, currency=currency, period=period)
        amounts = [a for a in (fallback_min, fallback_max) if a is not None]

    amounts = sorted(set(amounts))[:4]
    if not amounts:
        return SalaryInfo(raw=raw, currency=currency, period=period)

    min_amount = amounts[0]
    max_amount = amounts[-1] if len(amounts) > 1 else None

    if currency is None:
        currency = "ron" if not raw else (currency_hint or "ron")
    if period is None:
        period = _infer_period(min_amount, currency)

    monthly_min = to_monthly_ron(min_amount, currency, period)
    monthly_max = to_monthly_ron(max_amount, currency, period) if max_amount else None

    return SalaryInfo(
        raw=raw,
        currency=currency,
        period=period,
        min_amount=min_amount,
        max_amount=max_amount,
        monthly_ron_min=monthly_min,
        monthly_ron_max=monthly_max,
    )


def to_monthly_ron(
    amount: Optional[float], currency: Optional[str], period: Optional[str]
) -> Optional[float]:
    if amount is None:
        return None
    rate = FX_TO_RON.get((currency or "ron").lower(), 1.0)
    multiplier = _PERIOD_MULTIPLIERS.get((period or "month").lower(), 1.0)
    return round(amount * rate * multiplier, 2)


def format_salary(info: SalaryInfo) -> str:
    """Human-readable summary used in the UI."""
    if info.raw and not info.has_value:
        return info.raw
    if not info.has_value:
        return "Not specified"

    low, high = info.monthly_ron_min, info.monthly_ron_max
    if low and high and abs(high - low) > 1:
        body = f"≈ {low:,.0f} – {high:,.0f} RON/month"
    else:
        body = f"≈ {(low or high):,.0f} RON/month"

    if info.currency and info.currency != "ron":
        return f"{info.raw} ({body})"
    if info.raw:
        return f"{info.raw} ({body})" if info.period != "month" else info.raw
    return body


def parse_range(raw_text: object) -> Tuple[Optional[float], Optional[float]]:
    """Convenience helper returning the monthly RON range as a tuple."""
    info = parse_salary(raw_text)
    return info.monthly_ron_min, info.monthly_ron_max
