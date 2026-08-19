"""Targeted regression tests for docs/AHMED_SEARCH_REPAIR_PLAN.md (v5).

One test (or small group) per acceptance-test line in the plan. These lock in
the dedicated Ahmed office track, the expanded taxonomy/query coverage, and
confirm the pre-existing Romanian/German/phrase-aware guardrails still hold.
"""

from careeros import DEFAULT_PROFILE, calculate_match, hard_filter_job
from careeros.search import CAREER_PRESETS, SearchRequest
from careeros.sources.providers import _keyword_filter
from careeros.tracks import (
    ALL_TRACKS,
    TRACK_AHMED_OFFICE,
    TRACK_LOGISTICS,
    track_weights,
)


def job(title, location="Timisoara", description="", salary=""):
    return {
        "title": title,
        "description": description,
        "location": {"display_name": location},
        "company": {"display_name": "X"},
        "salary_text": salary,
        "category": {"label": ""},
    }


# ---------------------------------------------------------------------------
# 1-4: new taxonomy phrases can enter the search pipeline via the dedicated
# Ahmed office track (Full Career Scan already has its own locked-in test —
# tests/test_ahmed_recall_4_3_6.py — so the new coverage lives on the new
# track instead of growing that list further).
# ---------------------------------------------------------------------------
class TestSearchPipelineCoverage:
    def test_ahmed_office_track_exists_with_query_budget_in_range(self):
        assert TRACK_AHMED_OFFICE in ALL_TRACKS
        assert TRACK_AHMED_OFFICE in CAREER_PRESETS
        queries = CAREER_PRESETS[TRACK_AHMED_OFFICE]
        assert 12 <= len(queries) <= 18
        # Every entry is a meaningful phrase, not a single bag-of-words token.
        for query in queries:
            assert query.strip() == query
            assert query == query.lower()

    def test_tax_compliance_enters_the_pipeline(self):
        queries = SearchRequest(preset=TRACK_AHMED_OFFICE, keywords="").resolved_queries()
        assert "tax compliance" in queries

    def test_kyc_and_aml_analyst_enter_the_pipeline(self):
        queries = SearchRequest(preset=TRACK_AHMED_OFFICE, keywords="").resolved_queries()
        assert "kyc analyst" in queries
        assert "aml analyst" in queries
        # Also reachable through custom-keyword expansion.
        assert "kyc analyst" in SearchRequest(keywords="kyc").resolved_queries()
        assert "aml analyst" in SearchRequest(keywords="aml").resolved_queries()

    def test_legal_specialist_and_contract_administrator_enter_the_pipeline(self):
        queries = SearchRequest(preset=TRACK_AHMED_OFFICE, keywords="").resolved_queries()
        assert "legal specialist" in queries
        assert "contract administrator" in queries
        assert "contract administrator" in SearchRequest(keywords="legal").resolved_queries()

    def test_arabic_customer_support_remains_discoverable(self):
        # Was already true via Full Career Scan / ahmed_recall; must still be
        # true there AND on the new dedicated office track.
        assert "arabic customer support" in CAREER_PRESETS["🔥 Full Career Scan (recommended)"]
        assert "arabic customer support" in CAREER_PRESETS[TRACK_AHMED_OFFICE]


# ---------------------------------------------------------------------------
# 5: phrase-aware client-side filtering — "back office" must not degrade into
# a loose "office" match.
# ---------------------------------------------------------------------------
class TestPhraseAwareFiltering:
    def test_office_cleaner_not_admitted_for_back_office_query(self):
        assert _keyword_filter(
            "Office Cleaner - full time position, evenings",
            "back office",
            phrases=["back office"],
        ) is False

    def test_back_office_specialist_is_admitted(self):
        assert _keyword_filter(
            "Back Office Specialist - finance team",
            "back office",
            phrases=["back office"],
        ) is True


# ---------------------------------------------------------------------------
# 6-8: Romanian/English/German hard-gate behavior must be unchanged.
# ---------------------------------------------------------------------------
class TestLanguageHardGates:
    def test_romanian_c1_is_rejected(self):
        keep, reason = hard_filter_job(
            job("Compliance Officer", "Timisoara", "Romanian C1 required. English B2."),
            DEFAULT_PROFILE,
        )
        assert keep is False
        assert "romanian" in reason.lower()

    def test_romanian_is_a_plus_is_retained(self):
        keep, reason = hard_filter_job(
            job("Compliance Officer", "Timisoara", "Romanian is a plus. English B2 required."),
            DEFAULT_PROFILE,
        )
        assert keep is True, reason

    def test_german_required_is_rejected(self):
        keep, reason = hard_filter_job(
            job("Customer Support Specialist", "Timisoara", "German required. English B2."),
            DEFAULT_PROFILE,
        )
        assert keep is False
        assert "german" in reason.lower()


# ---------------------------------------------------------------------------
# 9: a realistic Timișoara customer-support target scores well.
# ---------------------------------------------------------------------------
class TestRealisticOfficeTarget:
    def test_timisoara_customer_support_b2_no_romanian_scores_as_realistic(self):
        result = calculate_match(
            job(
                "Customer Support Specialist",
                "Timisoara",
                "Handle client requests via phone and email. English B2 required. SAP and Excel "
                "used daily. Support customers across Europe.",
                "5500 RON",
            ),
            DEFAULT_PROFILE,
            track=TRACK_AHMED_OFFICE,
        )
        assert result.score >= 55
        assert result.verdict in {"strong", "apply", "maybe"}
        assert result.romanian in {"none", "friendly"}


# ---------------------------------------------------------------------------
# 10: production/warehouse/driving stays a real fallback under Logistics &
# Production, but must not dominate the new office track's scoring.
# ---------------------------------------------------------------------------
class TestFallbackTrackSeparation:
    def test_production_operator_discoverable_under_logistics(self):
        posting = job(
            "Production Operator",
            "Timisoara",
            "Operate production line machinery, injection molding, quality control checks "
            "on the assembly line.",
            "4500 RON",
        )
        keep, reason = hard_filter_job(posting, DEFAULT_PROFILE, track=TRACK_LOGISTICS)
        assert keep is True, reason
        result = calculate_match(posting, DEFAULT_PROFILE, track=TRACK_LOGISTICS)
        assert result.dimensions["skills"] >= 20

    def test_production_operator_does_not_dominate_the_office_track(self):
        posting = job(
            "Production Operator",
            "Timisoara",
            "Operate production line machinery, injection molding, quality control checks "
            "on the assembly line.",
            "4500 RON",
        )
        office_job = job(
            "Tax Compliance Specialist",
            "Timisoara",
            "Tax compliance, regulatory reporting, KYC and AML reviews, Excel, SAP, "
            "English B2 required.",
            "6000 RON",
        )
        production_under_office = calculate_match(posting, DEFAULT_PROFILE, track=TRACK_AHMED_OFFICE)
        office_under_office = calculate_match(office_job, DEFAULT_PROFILE, track=TRACK_AHMED_OFFICE)
        production_under_logistics = calculate_match(posting, DEFAULT_PROFILE, track=TRACK_LOGISTICS)

        # Production evidence is heavily suppressed on the office track...
        assert production_under_office.dimensions["skills"] < 10
        # ...while a genuine office role scores its full skills credit there.
        assert office_under_office.dimensions["skills"] >= 25
        # ...and the same production job still gets full credit on its own track.
        assert production_under_logistics.dimensions["skills"] >= 25
        assert office_under_office.score > production_under_office.score

    def test_driving_evidence_suppressed_on_office_track_skill_multiplier(self):
        from careeros.tracks import skill_multiplier

        assert skill_multiplier(TRACK_AHMED_OFFICE, "driving") <= 0.2
        assert skill_multiplier(TRACK_AHMED_OFFICE, "production") <= 0.2


# ---------------------------------------------------------------------------
# 11: the core blend is untouched by this repair.
# ---------------------------------------------------------------------------
class TestCoreBlendUnchanged:
    def test_blend_weights_still_40_35_25(self):
        from careeros.matching import BLEND_WEIGHTS

        assert BLEND_WEIGHTS == {"match": 0.40, "eligibility": 0.35, "hiring": 0.25}

    def test_new_track_weight_table_sums_to_100(self):
        assert sum(track_weights(TRACK_AHMED_OFFICE).values()) == 100
