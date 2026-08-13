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
from careeros.text import normalize_text


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

    def test_rejects_engineering_leadership_and_product_titles(self, profile):
        # Regression: "Head of Engineering" was rewarded as leadership because
        # the ad mentioned Operations/Production. Engineering leadership and
        # product titles are not Ahmed's track and must be rejected.
        for title in [
            "Head of Engineering", "Engineering Manager", "Engineering Director",
            "CTO", "Chief Technology Officer", "VP of Engineering",
            "Product Manager", "Product Owner", "Head of Product",
            "Director of Engineering", "Software Architect",
        ]:
            keep, reason = hard_filter_job(make_job(title=title), profile)
            assert not keep, f"{title!r} should be rejected, got keep={keep}"
            assert "career track" in reason, f"{title!r} reason={reason!r}"

    def test_keeps_relevant_job(self, profile):
        keep, _ = hard_filter_job(make_job(description="Customer support, English required."), profile)
        assert keep

    def test_rejects_fluent_english_and_french_title(self, profile):
        keep, reason = hard_filter_job(make_job(
            title="(fluent English & French) Customer Support Consultant, hospitality",
            location="Remote — Anywhere",
            description="Customer support in hospitality.",
        ), profile)
        assert not keep
        assert "French" in reason

    def test_rejects_us_sales_dialer(self, profile):
        keep, reason = hard_filter_job(make_job(
            title="Dialer (US Sales Team)",
            location="Remote — Anywhere",
        ), profile)
        assert not keep

    def test_rejects_english_c1(self, profile):
        keep, reason = hard_filter_job(
            make_job(description="Customer support. English C1 required."),
            profile,
        )
        assert not keep
        assert "B2" in reason or "English" in reason

    def test_keeps_english_required_without_level(self, profile):
        keep, _ = hard_filter_job(
            make_job(description="Customer support. English required."),
            profile,
        )
        assert keep

    def test_rejects_dutch_in_title(self, profile):
        keep, reason = hard_filter_job(
            make_job(title="Service Desk Agent with Dutch", description="Dutch required."),
            profile,
        )
        assert not keep
        assert "Dutch" in reason

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

    def test_fluent_english_ampersand_french_is_required(self):
        text = normalize_text("(fluent English & French) Customer Support Consultant, hospitality")
        assert classify_language_mention(text, "french") == "required"


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

    def test_europe_wide_is_remote_eu(self):
        assert classify_remote_geography("Remote — Europe", "") == "remote_eu"
        assert classify_remote_geography("Remote — EU", "") == "remote_eu"

    def test_romania_remote_is_remote_country(self):
        assert classify_remote_geography("Remote — Romania", "") == "remote_country"

    def test_restricted(self):
        assert classify_remote_geography("Remote", "Must be based in the US") == "restricted"

    def test_single_foreign_country_is_unclear(self):
        # "Remote — Greece" is the Greek labour market, not EU-wide eligibility.
        # "eu" must also not match inside "Deutschland".
        assert classify_remote_geography("Remote — Greece", "") == "remote_unclear"
        assert classify_remote_geography("Remote — Deutschland", "") == "remote_unclear"
        assert classify_remote_geography("Remote — Neuchatel", "") == "remote_unclear"
        assert classify_remote_geography("Remote — UK", "") == "remote_unclear"
        assert classify_remote_geography("Remote — England", "") == "remote_unclear"
        assert classify_remote_geography("Remote — Poland", "") == "remote_unclear"

    def test_description_generic_words_do_not_override_location_country(self):
        # Regression: "global" / "work from anywhere" in the ad body must not
        # turn a "Remote — Greece" listing into EU-wide eligibility. The country
        # named in the location wins over generic wording in the description.
        assert classify_remote_geography(
            "Remote — Greece",
            "Join our global team. Work from anywhere in the world.",
        ) == "remote_unclear"
        assert classify_remote_geography(
            "Remote — Greece",
            "We are hiring worldwide, fully remote, work from anywhere.",
        ) == "remote_unclear"
        assert classify_remote_geography(
            "Remote — UK",
            "Join our global team. Work from anywhere.",
        ) == "remote_unclear"

    def test_anywhere_location_without_country_is_still_eu_wide(self):
        # "Remote — Anywhere" genuinely means worldwide eligibility.
        assert classify_remote_geography(
            "Remote — Anywhere",
            "Join our global team.",
        ) == "remote_eu"

    def test_country_beside_europe_is_not_eu_wide(self):
        # Regression: "Remote — Europe, Netherlands" was treated as EU-wide
        # because the word "Europe" won. A country named next to the open
        # region is that country's labour market, so it must NOT be remote_eu.
        assert classify_remote_geography("Remote — Europe, Netherlands", "") == "remote_unclear"
        assert classify_remote_geography("Remote — Europe, UK", "") == "remote_unclear"
        assert classify_remote_geography("Remote — Europe, Germany hub", "") == "remote_unclear"
        assert classify_remote_geography("Remote — Europe, United Kingdom", "") == "remote_unclear"

    def test_europe_alone_still_remote_eu(self):
        # "Remote — Europe" with no country stays acceptable EU-wide eligibility.
        assert classify_remote_geography("Remote — Europe", "") == "remote_eu"
        assert classify_remote_geography("Remote — EMEA", "") == "remote_eu"


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
        assert match.dimensions["location"] == 15
        assert match.dimensions["arabic"] == 20

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
        from careeros.matching import HIGH_PRIORITY_THRESHOLD, MEDIUM_PRIORITY_THRESHOLD

        assert "APPLY" in priority_band(HIGH_PRIORITY_THRESHOLD)[0]
        assert "APPLY" in priority_band(100)[0]
        assert "MAYBE" in priority_band(MEDIUM_PRIORITY_THRESHOLD)[0]
        assert "STRONG" in priority_band(HIGH_PRIORITY_THRESHOLD - 1)[0]
        assert "LOW" in priority_band(MEDIUM_PRIORITY_THRESHOLD - 1)[0]
        assert "SKIP" in priority_band(0)[0]

    def test_profile_changes_affect_score(self):
        job = make_job(location="Remote — Germany", description="operations role")
        rigid = calculate_match(job, Profile(open_to_relocation=False))
        assert rigid.score >= 0  # remote europe still fine
        onsite = make_job(location="Berlin, Germany", description="operations role")
        a = calculate_match(onsite, Profile(open_to_relocation=False))
        b = calculate_match(onsite, Profile(open_to_relocation=True))
        assert b.eligibility_score > a.eligibility_score


class TestRemoteGreeceLabourMarket:
    """Regression: a "Remote — Greece" job must not rank as an EU/Europe-wide
    role even when the ad body says "global" / "work from anywhere".

    Seen in production: "Customer service manager (GR) / Remote — Greece"
    scored ~75% and ranked #1 as "EU/Europe/worldwide eligible". After the fix
    the location country wins over generic description wording.
    """

    def test_remote_greece_is_not_eu_wide(self, profile):
        job = make_job(
            title="Customer service manager (GR)",
            location="Remote — Greece",
            description=(
                "Join our global team. Work from anywhere. "
                "English required. 5 years of experience. "
                "Customer service operations and client management."
            ),
        )
        match = calculate_match(job, profile)
        assert match.remote in {"remote_unclear", "remote_country", "restricted"}
        assert match.remote != "remote_eu"
        assert not any("EU/Europe/worldwide eligible" in r for r in match.eligibility_reasons)
        assert any("another country" in n for n in match.eligibility_reasons)

    def test_remote_greece_ranks_below_eu_wide_role(self, profile):
        # The same role offered EU-wide should beat one tied to a single country.
        greece = calculate_match(make_job(
            title="Customer service manager",
            location="Remote — Greece",
            description="Customer service operations. English required.",
        ), profile)
        eu_wide = calculate_match(make_job(
            title="Customer service manager",
            location="Remote — Europe",
            description="Customer service operations. English required. Work from anywhere.",
        ), profile)
        assert eu_wide.score > greece.score

    def test_remote_greece_is_hard_filtered(self, profile):
        keep, reason = hard_filter_job(make_job(
            title="Customer service manager (GR)",
            location="Remote — Greece",
            description="Join our global team. Work from anywhere. English required.",
        ), profile)
        assert not keep
        assert "Greece" in reason


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


class TestScoreNormalisation:
    """Scores are rescaled against the points a posting could actually award.

    Seen in production: only 1 of 112 matches reached "high priority", because
    Arabic (15) and salary (10) are absent from most ads, capping a perfect
    local job at ~70/100 and flattening the ranking.
    """

    def test_excellent_local_job_reaches_high_priority(self, profile):
        job = make_job(
            title="Back Office Specialist",
            location="Timisoara, Romania",
            description=(
                "Back office operations, invoicing, SAP and Excel. "
                "English required. 5 years experience. University degree."
            ),
        )
        match = calculate_match(job, profile)
        assert match.score >= 80, "a perfect local match must be high priority"
        assert match.normalised is True

    def test_job_mentioning_everything_is_not_normalised(self, profile):
        job = make_job(
            title="Arabic Customer Support Specialist",
            location="Timisoara, Romania",
            description="Arabic required. English required. Salary 6500 RON per month.",
            salary_text="6500 RON per month",
        )
        match = calculate_match(job, profile)
        assert match.normalised is False
        assert match.score >= 75

    def test_weak_job_stays_low_after_normalisation(self, profile):
        job = make_job(title="Assistant", location="Berlin, Germany",
                       description="General assistant work.")
        assert calculate_match(job, profile).score < 45

    def test_ordering_is_preserved(self, profile):
        strong = calculate_match(make_job(
            title="Operations Coordinator", location="Timisoara, Romania",
            description="Operations, SAP, Excel, invoicing. English required."), profile)
        weak = calculate_match(make_job(
            title="Assistant", location="Berlin, Germany", description="Assistant."), profile)
        assert strong.score > weak.score

    def test_penalties_survive_normalisation(self, profile):
        """A French requirement must still sink the score after rescaling."""
        job = make_job(
            title="Operations Coordinator", location="Timisoara, Romania",
            description="Operations and invoicing. English and French required.",
        )
        match = calculate_match(job, profile)
        assert match.score < 80, "a blocking language must prevent high priority"

    def test_score_never_exceeds_100(self, profile):
        job = make_job(
            title="Senior Arabic Operations Compliance Manager",
            location="Timisoara, Romania",
            description=("Arabic required English required romanian is a plus " * 20
                         + "SAP Excel invoicing compliance logistics. Salary 9000 RON per month. "
                           "Master degree in law. BPO shared services MENA."),
            salary_text="9000 RON per month",
            age_days=1,
        )
        assert 0 <= calculate_match(job, profile).score <= 100


class TestReachableWorkLocation:
    """He works from Timișoara. Only Romania / open-region remote is reachable.

    Country-locked remote (Greece, Poland, UK/England) and on-site jobs in
    those countries must not appear. Worldwide / Europe-wide remote must.
    """

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
        keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )
        assert keep is should_keep, f"{title} / {location}: keep={keep} reason={reason!r}"

    def test_relocation_unlocks_onsite_but_not_foreign_remote(self):
        mover = Profile(open_to_relocation=True)
        onsite, _ = hard_filter_job(
            make_job(title="Support", location="Berlin, Germany", description="office"),
            mover,
        )
        remote_gr, reason = hard_filter_job(
            make_job(title="Support", location="Remote — Greece", description="remote"),
            mover,
        )
        assert onsite, "relocation should allow an on-site EU office"
        assert not remote_gr
        assert "Greece" in reason

    def test_generic_worldwide_wording_does_not_save_uk_remote(self, profile):
        keep, reason = hard_filter_job(make_job(
            title="Customer service manager (UK)",
            location="Remote — UK",
            description="Join our global team. Work from anywhere in the world.",
        ), profile)
        assert not keep
        assert "UK" in reason


class TestReportedBadResults:
    """Regression: the three jobs reported as wrong for Ahmed must disappear.

    (1) "Head of Engineering" — not his track (was rewarded as leadership).
    (2) "Consultant, Service Development" — Remote — Europe, Netherlands, but
        a country next to Europe means the Netherlands market, not EU-wide.
    (3) "Data Support Specialist" — Remote — Europe, UK, likewise the UK
        market.
    """

    def test_head_of_engineering_is_rejected(self, profile):
        keep, reason = hard_filter_job(make_job(
            title="Head of Engineering",
            location="Remote — Europe",
            description="Leading operations and production engineering teams.",
        ), profile)
        assert not keep
        assert "career track" in reason

    def test_consultant_service_development_europe_netherlands_rejected(self, profile):
        keep, reason = hard_filter_job(make_job(
            title="Consultant, Service Development",
            location="Remote — Europe, Netherlands",
            description="Service development and operations across the region.",
        ), profile)
        assert not keep
        assert "Netherlands" in reason

    def test_data_support_specialist_europe_uk_rejected(self, profile):
        keep, reason = hard_filter_job(make_job(
            title="Data Support Specialist",
            location="Remote — Europe, UK",
            description="Data support and operations.",
        ), profile)
        assert not keep
        assert "UK" in reason
