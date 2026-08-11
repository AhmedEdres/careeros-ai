import pytest

from careeros.salary import format_salary, parse_salary, to_monthly_ron


class TestParseSalary:
    def test_romanian_monthly_range(self):
        info = parse_salary("3.500 - 5.000 RON / luna")
        assert info.currency == "ron"
        assert info.period == "month"
        assert info.monthly_ron_min == pytest.approx(3500, rel=0.01)
        assert info.monthly_ron_max == pytest.approx(5000, rel=0.01)

    def test_euro_annual_converted_to_monthly_ron(self):
        info = parse_salary("€45,000 per year")
        assert info.currency == "eur"
        assert info.period == "year"
        # 45000 EUR/yr ≈ 3750 EUR/mo ≈ 18.6k RON/mo
        assert 15_000 < info.monthly_ron_min < 22_000

    def test_k_suffix(self):
        info = parse_salary("45k - 60k EUR annually")
        assert info.min_amount == 45_000
        assert info.max_amount == 60_000

    def test_hourly_rate(self):
        info = parse_salary("$25 per hour")
        assert info.period == "hour"
        assert info.monthly_ron_min > 10_000

    def test_ignores_years_and_noise(self):
        info = parse_salary("Posted 2024, 40 hours per week")
        assert info.monthly_ron_min is None or info.monthly_ron_min > 0

    def test_empty_returns_no_value(self):
        assert not parse_salary("").has_value
        assert not parse_salary(None).has_value

    def test_structured_fallback(self):
        info = parse_salary("", fallback_min=4000, fallback_max=6000, currency_hint="ron")
        assert info.has_value
        assert info.monthly_ron_min == pytest.approx(4000, rel=0.01)

    def test_thousand_separators(self):
        assert parse_salary("1,500 USD per month").min_amount == 1500
        assert parse_salary("1.500 RON pe luna").min_amount == 1500

    def test_period_inference_without_keyword(self):
        # A bare large number in RON should read as monthly, not hourly.
        assert parse_salary("6000 RON").period == "month"
        assert parse_salary("120000 RON").period == "year"


class TestConversion:
    def test_to_monthly_ron(self):
        assert to_monthly_ron(1000, "ron", "month") == 1000
        assert to_monthly_ron(1000, "eur", "month") > 4000
        assert to_monthly_ron(12000, "ron", "year") == 1000
        assert to_monthly_ron(None, "ron", "month") is None


class TestFormat:
    def test_formats_monthly_ron(self):
        assert "RON/month" in format_salary(parse_salary("€3000 per month"))

    def test_no_value_falls_back(self):
        assert format_salary(parse_salary("")) == "Not specified"
        assert format_salary(parse_salary("competitive package")) == "competitive package"
