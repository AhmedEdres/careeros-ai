import pytest

from careeros.matching import (
    calculate_match,
    classify_language_mention,
    classify_remote_geography,
    classify_romanian_requirement,
    hard_filter_job,
    priority_band,
)
from careeros.profile import Profile


def make_job(title="Operations Coordinator", description="", location="Timisoara, Romania", **kw):
    job = {
        "title": title,
        "description": description,
        "location": {"display_name": location},
        "company": {"display_name": "ACME"},
        "category": {"label": ""},
        "salary_text": kw.pop("salary_text", ""),
        "salary_min": kw.pop("salary_min", None),
        "salary_max": kw.pop("salary_max", None),
        "redirect_url": "https://example.com/job/1",
        "source": "Test",
    }
    job.update(kw)
    return job


@pytest.fixture
def profile():
    return Profile()


class TestHardFilter:
    def test_rejects_advanced_romanian(self, profile):
        job = make_job(description="Fluent Romanian required, C1 level.")
        keep, reason = hard_filter_job(job, profile)
        assert not keep and "Romanian" in reason

    def test_rejects_us_only_remote(self, profile):
        job = make_job(location="Remote — US only")
        keep, reason = hard_filter_job(job, profile)
        assert not keep

    def test_rejects_wrong_career_track(self, profile):
        keep, reason = hard_filter_job(make_job(title="Senior Java Developer"), profile)
        assert not keep and "career track" in reason

    def test_keeps_relevant_job(self, profile):
        keep, _ = hard_filter_job(make_job(description="Customer support, English required."), profile)
        assert keep

    def test_developer_word_in_description_does_not_reject(self, profile):
        job = make_job(title="Back Office Specialist",
                       description="You will support our java developer teams with invoicing.")
        keep, _ = hard_filter_job(job, profile)
        assert keep

    def test_fluent_romanian_allowed_for_fluent_candidate(self):
        fluent = Profile(romanian_level="C1")
        job = make_job(description="Fluent Romanian required.")
        keep, _ = hard_filter_job(job, fluent)
        assert keep


class TestLanguageClassification:
    def test_required(self):
        assert classify_language_mention("fluent arabic is required", "arabic") == "required"

    def test_plus(self):
        assert classify_language_mention("arabic is a plus", "arabic") == "plus"

    def test_none(self):
        assert classify_language_mention("we need english", "arabic") == "none"

    def test_mentioned(self):
        assert classify_language_mention("our arabic team is growing", "arabic") == "mentioned"


class TestRomanianClassification:
    def test_reject_level(self):
        assert classify_romanian_requirement("native romanian speaker needed") == "reject"

    def test_friendly(self):
        assert classify_romanian_requirement("romanian is a plus") == "friendly"

    def test_none_when_absent(self):
        assert classify_romanian_requirement("english only workplace") == "friendly"
        assert classify_romanian_requirement("we build widgets") == "none"


class TestRemoteGeography:
    def test_not_remote(self):
        assert classify_remote_geography("Timisoara, Romania", "office based") == "not_remote"

    def test_excellent_for_europe(self):
        assert classify_remote_geography("Remote — Europe", "") == "excellent"

    def test_restricted(self):
        assert classify_remote_geography("Remote", "Must be based in the US") == "restricted"

    def test_deutschland_is_not_eu_substring_bug(self):
        # "eu" must not match inside "Deutschland"; it is still EU by country name.
        assert classify_remote_geography("Remote — Deutschland", "") == "excellent"
        assert classify_remote_geography("Remote — Neuchatel", "") in ("good", "excellent")


class TestScoring:
    def test_perfect_local_job_scores_high(self, profile):
        job = make_job(
            title="Customer Support Specialist",
            location="Timisoara, Romania",
            description=(
                "We are looking for a customer support specialist with SAP and Excel skills. "
                "Arabic is required, English required. Romanian is a plus. "
                "5 years of experience. Salary 6000 - 7000 RON per month."
            ),
        )
        match = calculate_match(job, profile)
        assert match.score >= 80
        assert match.dimensions["location"] == 20
        assert match.dimensions["arabic"] == 15

    def test_empty_job_scores_near_zero(self, profile):
        match = calculate_match(make_job(title="Unknown role", location="", description=""), profile)
        assert match.score <= 15

    def test_score_bounded(self, profile):
        job = make_job(
            title="Senior Operations Finance Compliance Logistics SAP Manager",
            description="arabic required english required romanian is a plus " * 30
            + " salary 20000 RON per month, master degree in law, bpo mena shared services",
        )
        match = calculate_match(job, profile)
        assert 0 <= match.score <= 100

    def test_salary_dimension_now_works_for_text_salaries(self, profile):
        job = make_job(salary_text="6.000 RON pe luna")
        match = calculate_match(job, profile)
        assert match.dimensions["salary"] >= 9

    def test_below_target_salary_warns(self, profile):
        job = make_job(salary_text="2000 RON per month")
        match = calculate_match(job, profile)
        assert match.dimensions["salary"] <= 3
        assert any("below target" in w for w in match.warnings)

    def test_confidence_reflects_description_length(self, profile):
        short = calculate_match(make_job(description="short"), profile)
        long = calculate_match(make_job(description="word " * 400), profile)
        assert short.confidence == "low"
        assert long.confidence == "high"

    def test_freshness_boost(self, profile):
        fresh = calculate_match(make_job(age_days=1), profile)
        stale = calculate_match(make_job(age_days=90), profile)
        assert fresh.score > stale.score

    def test_reasons_are_populated(self, profile):
        match = calculate_match(make_job(description="customer support with excel"), profile)
        assert match.reasons

    def test_junior_role_warns(self, profile):
        match = calculate_match(make_job(title="Junior Accounting Intern"), profile)
        assert any("Entry-level" in w for w in match.warnings)

    def test_priority_band(self):
        assert "HIGH" in priority_band(80)[0]
        assert "WORTH" in priority_band(50)[0]
        assert "LOW" in priority_band(10)[0]

    def test_profile_changes_affect_score(self):
        job = make_job(location="Remote — Germany", description="operations role")
        rigid = calculate_match(job, Profile(open_to_relocation=False))
        assert rigid.score >= 0  # remote europe still fine
        onsite = make_job(location="Berlin, Germany", description="operations role")
        a = calculate_match(onsite, Profile(open_to_relocation=False))
        b = calculate_match(onsite, Profile(open_to_relocation=True))
        assert b.score > a.score


class TestForeignLanguageRequirements:
    """Regression: a role requiring French/German must not rank as a top match.

    Seen in production: "(fluent English & French) Customer Support Consultant"
    scored 74% and ranked #1, despite French not being in the profile.
    """

    def test_required_french_is_heavily_penalised(self, profile):
        job = make_job(
            title="(fluent English & French) Customer Support Consultant",
            location="Remote — Anywhere",
            description="Fluent English and French required. Multilingual team.",
        )
        match = calculate_match(job, profile)
        assert "french" in match.blocking_languages
        assert match.score < 45, "a role he cannot get must not be high priority"
        assert any("French" in w for w in match.warnings)

    def test_language_as_a_plus_is_not_penalised(self, profile):
        job = make_job(
            title="Customer Support Agent",
            description="English required. French is a plus. Arabic is a plus.",
        )
        match = calculate_match(job, profile)
        assert match.blocking_languages == []

    def test_penalised_below_equivalent_job_without_the_requirement(self, profile):
        base = "Customer support role. Multilingual team. English required."
        with_french = calculate_match(
            make_job(title="Support Consultant", description=base + " French required."), profile
        )
        without = calculate_match(make_job(title="Support Consultant", description=base), profile)
        assert with_french.score < without.score - 20

    def test_multiple_missing_languages_penalised_more(self, profile):
        one = calculate_match(make_job(description="German required."), profile)
        two = calculate_match(make_job(description="German required. Dutch required."), profile)
        assert two.score <= one.score

    def test_speaking_language_is_not_blocking(self, profile):
        match = calculate_match(make_job(description="Fluent English and Arabic required."), profile)
        assert match.blocking_languages == []


class TestLegalBoilerplate:
    """Regression: "we comply with legal requirements" awarded a Law-degree bonus."""

    def test_boilerplate_does_not_award_education_points(self, profile):
        job = make_job(
            title="Customer Support Agent",
            description="We comply with all legal requirements and data protection laws.",
        )
        assert calculate_match(job, profile).dimensions["education"] == 0

    def test_genuine_legal_role_scores_full(self, profile):
        job = make_job(title="Legal Compliance Officer", description="Contract review and legal advice.")
        assert calculate_match(job, profile).dimensions["education"] == 5

    def test_legal_adjacent_body_still_credited(self, profile):
        job = make_job(title="Compliance Specialist",
                       description="You will work with our legal counsel on contracts and litigation.")
        assert calculate_match(job, profile).dimensions["education"] >= 4
