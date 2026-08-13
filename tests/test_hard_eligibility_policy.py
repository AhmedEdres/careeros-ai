"""Regression tests for CareerOS hard eligibility policy."""

from careeros import DEFAULT_PROFILE, hard_filter_job
from careeros.matching import required_foreign_languages


def job(title, description="", location="Timișoara"):
    return {
        "title": title,
        "description": description,
        "company": "Test Co",
        "location": {"display_name": location},
    }


def test_required_german_is_blocked_for_ahmed():
    text = "Customer service specialist. German language required. English required."
    assert "german" in required_foreign_languages(text, DEFAULT_PROFILE)
    keep, reason = hard_filter_job(job("Customer Support Specialist cu Limba Germană", text), DEFAULT_PROFILE)
    assert keep is False
    assert "language" in reason.lower()


def test_optional_german_is_not_blocked():
    text = "Customer service specialist. German is a plus. English required."
    assert "german" not in required_foreign_languages(text, DEFAULT_PROFILE)


def test_c_plus_e_is_blocked_for_category_b_only_profile():
    keep, reason = hard_filter_job(
        job("Sofer profesionist C+E - Olanda", "C+E licence required; 3000 EUR net", "Timișoara"),
        DEFAULT_PROFILE,
    )
    assert keep is False
    assert "heavy-vehicle" in reason.lower()


def test_category_b_driver_fallback_remains_allowed():
    keep, reason = hard_filter_job(
        job("Șofer categoria B", "Category B driving licence required; 5000 RON", "Timișoara"),
        DEFAULT_PROFILE,
    )
    assert keep is True
    assert reason == ""
