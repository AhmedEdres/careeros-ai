from careeros.matching import hard_filter_job
from careeros.profile import Profile


def job(title):
    return {
        "title": title,
        "description": "Customer support and operations.",
        "location": {"display_name": "Timisoara, Romania"},
        "company": {"display_name": "Example"},
    }


def test_german_language_title_is_filtered():
    keep, reason = hard_filter_job(
        job("Customer Support Specialist cu Limba Germană | Kundenservice"),
        Profile(),
    )
    assert not keep
    assert "Different career track" in reason


def test_normal_customer_support_is_not_filtered():
    keep, reason = hard_filter_job(job("Customer Support Specialist"), Profile())
    assert keep, reason
