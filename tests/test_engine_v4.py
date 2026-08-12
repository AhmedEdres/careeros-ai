"""Matching engine v4 — three scores, track-aware weights, graded Romanian."""

import pytest

from careeros.matching import (
    BLEND_WEIGHTS,
    WEAK_MATCH_OTHER_CAP,
    WEAK_MATCH_THRESHOLD,
    blend_scores,
    calculate_match,
    hard_filter_job,
)
from careeros.profile import Profile, SKILL_GROUPS
from careeros.search import CAREER_PRESETS, FilterOptions, score_and_filter
from careeros.tracks import (
    ALL_TRACKS,
    TRACK_ARABIC,
    TRACK_FINANCE,
    TRACK_FULL,
    TRACK_LOGISTICS,
    TRACK_SUPPORT,
    romanian_pressure,
    track_weights,
)


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
        "redirect_url": kw.pop("redirect_url", "https://example.com/job/1"),
        "source": "Test",
    }
    job.update(kw)
    return job


@pytest.fixture
def profile():
    return Profile()


# ---------------------------------------------------------------------------
# Blend
# ---------------------------------------------------------------------------
class TestBlend:
    def test_weights_sum_to_one(self):
        assert abs(sum(BLEND_WEIGHTS.values()) - 1.0) < 1e-9

    def test_weights_are_40_35_25(self):
        assert BLEND_WEIGHTS["match"] == 0.40
        assert BLEND_WEIGHTS["eligibility"] == 0.35
        assert BLEND_WEIGHTS["hiring"] == 0.25

    def test_uncapped_when_match_is_strong(self):
        # 80*0.4 + 80*0.35 + 80*0.25 = 80
        assert blend_scores(80, 80, 80) == 80

    def test_weak_match_is_capped_at_32_not_52(self):
        # 9*0.4 + 85*0.35 + 75*0.25 = 3.6 + 29.75 + 18.75 = 52 uncapped
        assert blend_scores(9, 85, 75) == 32

    def test_cap_only_applies_below_threshold(self):
        assert WEAK_MATCH_THRESHOLD == 50
        at_threshold = blend_scores(50, 100, 100)
        below = blend_scores(49, 100, 100)
        assert at_threshold == 80  # 20 + 35 + 25, cap does not apply at 50
        assert below < at_threshold

# ---------------------------------------------------------------------------
# Three scores on MatchResult
# ---------------------------------------------------------------------------
class TestThreeScores:
    def test_result_exposes_three_scores(self, profile):
        match = calculate_match(make_job(description="customer support excel"), profile)
        assert hasattr(match, "match_score")
        assert hasattr(match, "eligibility_score")
        assert hasattr(match, "hiring_score")
        assert 0 <= match.match_score <= 100
        assert 0 <= match.eligibility_score <= 100
        assert 0 <= match.hiring_score <= 100
        assert 0 <= match.score <= 100

    def test_overall_equals_blend(self, profile):
        match = calculate_match(
            make_job(
                title="Arabic Customer Support Specialist",
                description="Arabic required. English required. Romanian is a plus. SAP Excel.",
            ),
            profile,
        )
        assert match.score == blend_scores(
            match.match_score, match.eligibility_score, match.hiring_score
        )

# ---------------------------------------------------------------------------
# Track tables
# ---------------------------------------------------------------------------
class TestTrackTables:
    def test_seven_tracks(self):
        assert len(ALL_TRACKS) == 7

    def test_logistics_track_exists(self):
        assert TRACK_LOGISTICS in ALL_TRACKS
        assert TRACK_LOGISTICS in CAREER_PRESETS
        assert CAREER_PRESETS[TRACK_LOGISTICS]

    def test_every_table_sums_to_100(self):
        for track in ALL_TRACKS:
            assert sum(track_weights(track).values()) == 100, track

    def test_arabic_is_30_on_arabic_track(self):
        assert track_weights(TRACK_ARABIC)["arabic"] == 30

    def test_arabic_is_8_on_logistics_track(self):
        assert track_weights(TRACK_LOGISTICS)["arabic"] == 8

    def test_education_is_0_on_support_track(self):
        assert track_weights(TRACK_SUPPORT)["education"] == 0

    def test_education_is_12_on_finance_track(self):
        assert track_weights(TRACK_FINANCE)["education"] == 12

    def test_arabic_required_scores_higher_on_arabic_track(self, profile):
        job = make_job(
            title="Arabic Customer Support Specialist",
            description="Arabic required. English required. Customer support.",
        )
        arabic = calculate_match(job, profile, TRACK_ARABIC)
        logistics = calculate_match(job, profile, TRACK_LOGISTICS)
        assert arabic.dimensions["arabic"] > logistics.dimensions["arabic"]

    def test_legal_role_education_zero_on_support_track(self, profile):
        job = make_job(title="Legal Compliance Officer", description="Contract review and legal advice.")
        support = calculate_match(job, profile, TRACK_SUPPORT)
        finance = calculate_match(job, profile, TRACK_FINANCE)
        assert support.dimensions["education"] == 0
        assert finance.dimensions["education"] == 12


# ---------------------------------------------------------------------------
# Romanian pressure
# ---------------------------------------------------------------------------
class TestRomanianPressure:
    def test_bucharest_finance_is_1_35(self):
        assert romanian_pressure(TRACK_FINANCE, "Bucharest, Romania", "not_remote") == 1.35

    def test_remote_arabic_desk_is_0_5(self):
        assert romanian_pressure(TRACK_ARABIC, "Remote — Europe", "remote_eu") == 0.5

    def test_plus_costs_nothing(self, profile):
        plus = calculate_match(
            make_job(description="English required. Romanian is a plus. Customer support."),
            profile,
        )
        none = calculate_match(
            make_job(description="English required. Customer support."),
            profile,
        )
        # Eligibility must not drop just because Romanian is mentioned as a plus.
        assert plus.eligibility_score >= none.eligibility_score

    def test_unspecified_romanian_required_is_not_a_hard_reject(self, profile):
        job = make_job(description="Romanian and English required. Customer support.")
        keep, _ = hard_filter_job(job, profile)
        assert keep
        match = calculate_match(job, profile)
        assert match.romanian == "risky"
        assert match.eligibility_score < calculate_match(
            make_job(description="English required. Customer support. Romanian is a plus."),
            profile,
        ).eligibility_score

    def test_fluent_romanian_still_hard_rejects(self, profile):
        keep, reason = hard_filter_job(
            make_job(description="Fluent Romanian required, C1 level."), profile
        )
        assert not keep and "Romanian" in reason

    def test_pressure_scales_risky_penalty(self, profile):
        job = make_job(
            location="Bucharest, Romania",
            description="Romanian required. Finance and compliance. Accounting.",
        )
        finance = calculate_match(job, profile, TRACK_FINANCE)
        arabic = calculate_match(
            make_job(
                location="Remote — Europe",
                description="Romanian required. Arabic customer support.",
            ),
            profile,
            TRACK_ARABIC,
        )
        assert finance.romanian_pressure > arabic.romanian_pressure


# ---------------------------------------------------------------------------
# Logistics & Production
# ---------------------------------------------------------------------------
class TestLogisticsTrack:
    def test_production_skill_group_exists(self):
        assert "production" in SKILL_GROUPS

    def test_cnc_operator_rejected_on_finance(self, profile):
        keep, _ = hard_filter_job(make_job(title="CNC Operator"), profile, TRACK_FINANCE)
        assert not keep

    def test_cnc_operator_kept_on_logistics(self, profile):
        keep, _ = hard_filter_job(make_job(title="CNC Operator"), profile, TRACK_LOGISTICS)
        assert keep

    def test_production_operator_scores_on_logistics_track(self, profile):
        job = make_job(
            title="Production Operator",
            location="Timisoara, Romania",
            description="Machine operator on the production line. Quality control. Shifts.",
        )
        logi = calculate_match(job, profile, TRACK_LOGISTICS)
        finance = calculate_match(job, profile, TRACK_FINANCE)
        assert logi.match_score > finance.match_score

    def test_warehouse_role_aligns_with_logistics_hiring(self, profile):
        job = make_job(
            title="Warehouse Coordinator",
            description="Inventory, shipping, forklift, warehouse operations.",
        )
        match = calculate_match(job, profile, TRACK_LOGISTICS)
        assert match.hiring_score >= 40
        assert any("track" in r.lower() or "Title" in r for r in match.hiring_reasons)

# ---------------------------------------------------------------------------
# Hiring reality
# ---------------------------------------------------------------------------
class TestHiringReality:
    def test_arabic_required_boosts_hiring(self, profile):
        with_ar = calculate_match(
            make_job(title="Customer Support Specialist", description="Arabic required. English required."),
            profile,
        )
        without = calculate_match(
            make_job(title="Customer Support Specialist", description="English required."),
            profile,
        )
        assert with_ar.hiring_score > without.hiring_score

    def test_french_required_hurts_hiring_and_eligibility(self, profile):
        job = make_job(
            title="Customer Support Consultant",
            description="Fluent English and French required.",
        )
        match = calculate_match(job, profile)
        assert "french" in match.blocking_languages
        assert match.eligibility_score < 40
        assert match.hiring_score < 50
        assert match.hiring_risks

    def test_junior_title_is_a_hiring_risk(self, profile):
        match = calculate_match(make_job(title="Junior Accounting Intern"), profile)
        assert any("overqualified" in r.lower() or "Junior" in r for r in match.hiring_risks)

    def test_stale_listing_lowers_hiring(self, profile):
        fresh = calculate_match(make_job(description="customer support", age_days=1), profile)
        stale = calculate_match(make_job(description="customer support", age_days=90), profile)
        assert fresh.hiring_score > stale.hiring_score

    def test_eu_finance_role_flags_local_experience_gap(self, profile):
        match = calculate_match(
            make_job(title="Tax Compliance Officer", description="AML KYC tax compliance."),
            profile,
            TRACK_FINANCE,
        )
        assert any("EU-regulated" in r or "local" in r.lower() for r in match.hiring_risks)


# ---------------------------------------------------------------------------
# Eligibility
# ---------------------------------------------------------------------------
class TestEligibility:
    def test_timisoara_beats_berlin(self, profile):
        local = calculate_match(make_job(location="Timisoara, Romania", description="support"), profile)
        away = calculate_match(make_job(location="Berlin, Germany", description="support"), profile)
        assert local.eligibility_score > away.eligibility_score

    def test_blocking_language_crushes_eligibility(self, profile):
        match = calculate_match(
            make_job(description="German required. Customer support."),
            profile,
        )
        assert match.eligibility_score < 40


# ---------------------------------------------------------------------------
# Weak-fit cannot be propped up
# ---------------------------------------------------------------------------
class TestWeakFitCap:
    def test_empty_job_stays_low_overall(self, profile):
        match = calculate_match(make_job(title="Unknown role", location="", description=""), profile)
        assert match.score <= 15
        assert match.match_score < WEAK_MATCH_THRESHOLD

# ---------------------------------------------------------------------------
# score_and_filter respects track
# ---------------------------------------------------------------------------
class TestScoreAndFilterTrack:
    def test_track_changes_ranking(self, profile):
        arabic_job = make_job(
            title="Arabic Customer Support Specialist",
            description="Arabic required. Customer support. English required.",
            redirect_url="https://example.com/a",
        )
        warehouse_job = make_job(
            title="Warehouse Coordinator",
            description="Warehouse coordinator for logistics, inventory, shipping and freight forwarding.",
            redirect_url="https://example.com/b",
        )
        a_on_arabic = calculate_match(arabic_job, profile, TRACK_ARABIC)
        w_on_arabic = calculate_match(warehouse_job, profile, TRACK_ARABIC)
        a_on_logi = calculate_match(arabic_job, profile, TRACK_LOGISTICS)
        w_on_logi = calculate_match(warehouse_job, profile, TRACK_LOGISTICS)
        assert a_on_arabic.match_score > w_on_arabic.match_score
        assert w_on_logi.match_score > a_on_logi.match_score
        kept, _ = score_and_filter(
            [arabic_job, warehouse_job], profile,
            FilterOptions(min_score=0, track=TRACK_ARABIC),
        )
        assert kept[0]["title"].startswith("Arabic")


# ---------------------------------------------------------------------------
# Strong local job still reaches high priority on the default track
# ---------------------------------------------------------------------------
class TestHighPriorityStillWorks:
    def test_arabic_local_support_is_high_priority(self, profile):
        job = make_job(
            title="Arabic Customer Support Specialist",
            location="Timisoara, Romania",
            description=(
                "We need a customer support specialist with SAP and Excel skills. "
                "Arabic is required, English required. Romanian is a plus. "
                "5 years of experience. Salary 6000 - 7000 RON per month. "
                "Shared services centre."
            ),
            salary_text="6000 - 7000 RON per month",
        )
        match = calculate_match(job, profile)
        assert match.score >= 80
        assert match.match_score >= 70
        assert match.eligibility_score >= 70
        assert match.hiring_score >= 60


# ---------------------------------------------------------------------------
# Per-country campaign collapse
# ---------------------------------------------------------------------------
class TestCampaignDeduplication:
    """One opening reposted per country must not occupy four result slots.

    Seen live: "Customer service manager (GR) / (CY) / (UK) / (PT)" from the
    same employer filled positions 1-4, all with identical scores.
    """

    def _campaign(self, countries):
        from careeros.sources.base import make_job
        return [
            make_job(
                title=f"Customer service manager ({code})",
                company="ParcelHero",
                location=f"Remote — {name}",
                description="Customer service manager. Operations and logistics. English required.",
                url=f"https://jobicy.com/j/pc-{code.lower()}",
                source="Jobicy",
            )
            for code, name in countries
        ]

    def test_country_variants_collapse_into_one(self):
        from careeros.search import deduplicate_jobs

        jobs = self._campaign([("GR", "Greece"), ("CY", "Cyprus"),
                               ("UK", "UK"), ("PT", "Portugal")])
        unique, removed = deduplicate_jobs(jobs)
        assert len(unique) == 1
        assert removed == 3
        assert unique[0]["variant_count"] == 4

    def test_variant_locations_are_recorded(self):
        from careeros.search import deduplicate_jobs

        unique, _ = deduplicate_jobs(self._campaign([("GR", "Greece"), ("PT", "Portugal")]))
        assert len(unique[0]["variant_locations"]) == 2

    def test_most_eligible_variant_is_kept(self):
        from careeros.search import deduplicate_jobs

        jobs = self._campaign([("GR", "Greece"), ("RO", "Romania")])
        unique, _ = deduplicate_jobs(jobs)
        kept = unique[0]["location"]["display_name"]
        assert "Romania" in kept, "the variant he can actually work from must win"

    def test_different_roles_are_not_merged(self):
        from careeros.search import deduplicate_jobs
        from careeros.sources.base import make_job

        jobs = self._campaign([("GR", "Greece")]) + [
            make_job(title="Back Office Specialist", company="Other Co",
                     location="Timisoara, Romania", description="Back office.",
                     url="https://x.com/9", source="Jooble")
        ]
        unique, removed = deduplicate_jobs(jobs)
        assert len(unique) == 2 and removed == 0

    def test_same_title_different_employer_is_not_merged(self):
        from careeros.search import deduplicate_jobs
        from careeros.sources.base import make_job

        jobs = [
            make_job(title="Customer service manager (GR)", company="ParcelHero",
                     location="Remote — Greece", description="A", url="https://x.com/1", source="Jobicy"),
            make_job(title="Customer service manager (GR)", company="Rival Ltd",
                     location="Remote — Greece", description="B", url="https://x.com/2", source="Jobicy"),
        ]
        unique, _ = deduplicate_jobs(jobs)
        assert len(unique) == 2

    def test_greece_only_campaign_is_dropped_from_results(self, profile):
        """After collapse, a campaign with no Romania/worldwide variant is hidden."""
        jobs = self._campaign([("GR", "Greece"), ("UK", "UK"), ("PL", "Poland")])
        kept, stats = score_and_filter(jobs, profile, FilterOptions(min_score=0))
        assert kept == []
        assert stats["rejected_hard"] >= 1

    def test_romania_variant_survives_into_results(self, profile):
        jobs = self._campaign([("GR", "Greece"), ("RO", "Romania")])
        kept, _ = score_and_filter(jobs, profile, FilterOptions(min_score=0))
        assert len(kept) == 1
        assert "Romania" in kept[0]["location"]["display_name"]
