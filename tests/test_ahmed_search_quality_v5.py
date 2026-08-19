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
    DEFAULT_TRACK,
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


# ---------------------------------------------------------------------------
# Follow-up fix from real-data ranking validation: two IT-technical titles
# were surfacing as false positives specifically on the office track (higher
# skills ceiling pushed them past the "skip" threshold). Fixed with a precise
# title exclusion (Service Desk Engineer) and an evidence-gated exclusion
# (Security Specialist/Officer) rather than a blanket block, since generic
# "security specialist" postings can be legitimately relevant to Ahmed.
# ---------------------------------------------------------------------------
class TestOfficeTrackFalsePositiveFixes:
    def test_real_service_desk_engineer_posting_is_rejected(self):
        # Real posting text (Remotive) that surfaced this false positive:
        # scored 61/"low" and was visible on the office track before the fix.
        posting = job(
            "Tier III Service Desk Engineer",
            "Remote",
            "Unio Digital is an Arizona-based managed service provider (MSP) delivering "
            "Managed IT Services, Low Voltage Cabling, Access Control, Video Surveillance, "
            "and Intrusion Services. We are looking for an experienced Tier 3 Service Desk "
            "Technician with exceptional problem-solving skills, resolving complex technical "
            "issues, providing above and beyond support and excellent customer service.",
        )
        keep, reason = hard_filter_job(posting, DEFAULT_PROFILE, TRACK_AHMED_OFFICE)
        assert keep is False
        assert "it" in reason.lower() or "technical" in reason.lower()

    def test_service_desk_engineer_boilerplate_customer_service_mention_does_not_rescue_it(self):
        # Regression guard for the specific failure mode found during
        # validation: real IT/helpdesk ads routinely mention "customer
        # service" as a soft skill, so that phrase must not be usable to
        # rescue a Service Desk *Engineer* title from exclusion.
        posting = job(
            "Service Desk Engineer",
            "Timisoara",
            "Excellent customer service and communication skills required. Troubleshoot "
            "technical issues, manage the ticketing system, escalate to network engineering.",
        )
        keep, reason = hard_filter_job(posting, DEFAULT_PROFILE, TRACK_AHMED_OFFICE)
        assert keep is False

    def test_ordinary_service_desk_titles_without_engineer_are_unaffected(self):
        for title in ("Service Desk Agent", "Service Desk Coordinator", "Help Desk Representative"):
            posting = job(title, "Timisoara", "Customer service and administrative support for internal staff.")
            keep, reason = hard_filter_job(posting, DEFAULT_PROFILE, TRACK_AHMED_OFFICE)
            assert keep is True, f"{title!r} should not be affected by the Service Desk Engineer exclusion: {reason}"

    def test_real_security_specialist_posting_is_rejected(self):
        # Real posting text (Jobicy) that surfaced this false positive:
        # scored 61/"low" and was visible on the office track before the fix.
        posting = job(
            "Security Specialist - EMEA (location flexible)",
            "Remote",
            "About ClickHouse: recognized on the 2025 Forbes Cloud 100 list, ClickHouse is "
            "one of the most innovative and fast-growing private cloud companies, real-time "
            "analytics, cybersecurity, AWS and Kubernetes infrastructure.",
        )
        keep, reason = hard_filter_job(posting, DEFAULT_PROFILE, TRACK_AHMED_OFFICE)
        assert keep is False
        assert "it" in reason.lower() or "technical" in reason.lower()

    def test_security_specialist_is_not_globally_blocked(self):
        # Requirement: security/compliance roles can be relevant to Ahmed, so
        # a generic Security Specialist/Officer title with no IT/cloud
        # evidence must remain visible.
        posting = job(
            "Security Compliance Officer",
            "Timisoara",
            "Ensure regulatory security compliance, internal audits, and physical access "
            "control policies. English B2 required.",
        )
        keep, reason = hard_filter_job(posting, DEFAULT_PROFILE, TRACK_AHMED_OFFICE)
        assert keep is True, reason

    def test_security_specialist_with_cloud_evidence_is_rejected(self):
        posting = job(
            "Security Specialist",
            "Timisoara",
            "Own our cloud security posture across AWS and Kubernetes, cybersecurity "
            "incident response, devops collaboration.",
        )
        keep, reason = hard_filter_job(posting, DEFAULT_PROFILE, TRACK_AHMED_OFFICE)
        assert keep is False

    def test_fix_is_track_independent_not_scoped_only_to_office(self):
        # The hard-filter gate is track-independent by design (only the score
        # threshold differs by track), so the same two titles must also be
        # rejected on Full Career Scan / other non-IT tracks.
        from careeros.tracks import TRACK_FINANCE

        posting = job(
            "Tier III Service Desk Engineer",
            "Remote",
            "Managed service provider delivering Managed IT Services. Tier 3 technical "
            "support, troubleshooting, ticketing system, network engineering escalation.",
        )
        for track in (DEFAULT_TRACK, TRACK_FINANCE):
            keep, _ = hard_filter_job(posting, DEFAULT_PROFILE, track)
            assert keep is False

    def test_logistics_track_unaffected(self):
        # Requirement 8: Logistics & Production behavior must not change.
        posting = job(
            "Production Operator",
            "Timisoara",
            "Operate production line machinery, injection molding, quality control checks "
            "on the assembly line.",
            "4500 RON",
        )
        keep, reason = hard_filter_job(posting, DEFAULT_PROFILE, TRACK_LOGISTICS)
        assert keep is True, reason
        result = calculate_match(posting, DEFAULT_PROFILE, track=TRACK_LOGISTICS)
        assert result.dimensions["skills"] >= 25

    def test_previously_validated_office_ranking_improvements_still_hold(self):
        # Requirement 9: keep the existing Ahmed Office ranking improvements
        # found during validation (real posting text, abbreviated).
        # Full real posting text (PORR AG, via Hipo) that surfaced this
        # improvement during validation — kept verbatim so the skill-keyword
        # hits (e.g. "Excel" in the PC-skills line) reproduce exactly.
        contract_manager = job(
            "Contract Manager Senior",
            "Timisoara",
            "Responsabilitățile tale Analizarea prevederilor contractului și identificarea "
            "livrabilelor cu respectarea termenelor contractuale, pentru identificarea "
            "riscurilor din perspectivă tehnică și juridică pe care le pot implica drepturile "
            "și obligațiile părților Gestionarea contractelor principale și oferirea "
            "suportului în administrarea contractelor de subcontractare/ furnizare/prestări "
            "servicii atât în faza de întocmire a ofertelor, cât și în faza executării "
            "contractului Informarea Managementului de Proiect cu privire la stadiul "
            "proiectului prin raportare la termenele contractuale, monitorizarea lucrărilor "
            "din perspectiva obligațiilor contractuale și a îndeplinirii punctelor de "
            "referință, inclusiv cu privire la potențiale modificări/revendicări/ riscuri de "
            "penalități și încălcări ale contractului Gestionarea, analizarea și menținerea "
            "la zi a corespondenței contractuale, oferirea de consultanță echipei de proiect "
            "în ceea ce privește obligațiile contractuale și riscurile identificate, precum și "
            "furnizarea de metode de soluționare a eventualelor probleme identificate "
            "Redactarea corespondenței către beneficiari, consultanți, subantreprenori, "
            "prestatori și/sau furnizori, conform prevederilor contractului Colaborarea cu "
            "Plannerii și Managementul de Proiect pentru analizarea întârzierilor înregistrate "
            "în finalizarea proiectelor și identificarea unor măsuri de remediere din punct de "
            "vedere contractual, pentru pregătirea strategiei contractuale Evaluarea "
            "riscurilor contractuale, pregătirea și redactarea notificărilor de revendicare, "
            "precum și a fundamentării revendicărilor, inclusiv în ceea ce privește "
            "prelungirea duratei de execuție și cuantificarea costurilor suplimentare Oferirea "
            "de asistență contractuală echipelor de proiect pentru rezolvarea situațiilor "
            "apărute în relațiile lor cu managementul autorităților contractante/ "
            "beneficiarilor/ partenerilor comerciali Elaborarea propunerilor de modificare "
            "aferente lucrărilor suplimentare sau optimizărilor aduse proiectului Oferirea "
            "unei viziuni contractuale ușor de înțeles asupra aspectelor privind angajamentele "
            "companiei față de beneficiari, parteneri și principalii subantreprenori și "
            "furnizori Competențele tale Studii superioare finalizate (domeniu – "
            "Construcții/Drept) Minimum 10 ani experiență într-o poziție similară în domeniul "
            "construcțiilor Cunoștințe și experiență în cadrul proiectelor desfășurate cu "
            "respectarea legislației relevante în domeniul achizițiilor publice sau proiecte "
            "în cadrul cărora au fost folosite formele contractuale de tip HG1 și contracte "
            "comerciale între privați Abilități excelente de comunicare scrisă și orală "
            "Abilități de planificare, organizare, prezentare Cunoștințe de limba engleză - "
            "nivel mediu Cunoștințe bune operare PC (Excel, Word, PowerPoint) Beneficiile tale "
            "Abonament privat de servicii medicale Oferte personalizate - 7card; Bookster; "
            "Parteneriate bancare PORR Academy - academie internă pentru cursuri de pregătire "
            "Programe pentru dezvoltarea personală și profesională Te așteptăm în echipa "
            "noastră pentru a construi împreună!",
        )
        assert calculate_match(contract_manager, DEFAULT_PROFILE, track=TRACK_AHMED_OFFICE).score >= 55

        compliance_officer = job(
            "Compliance Officer EMEA (m/f/d)",
            "Timisoara",
            "Compliance, regulatory, English required. Romanian is a plus.",
        )
        full_score = calculate_match(compliance_officer, DEFAULT_PROFILE, track=DEFAULT_TRACK).score
        office_score = calculate_match(compliance_officer, DEFAULT_PROFILE, track=TRACK_AHMED_OFFICE).score
        assert office_score >= full_score


# ---------------------------------------------------------------------------
# Second follow-up fix from real-data validation (post-merge, salary filter
# off): "Data Architect" scored 82%/APPLY on the office track despite being
# a data-engineering/IT-architecture role Ahmed has no evidence for. The
# "Automotive Finance & Controlling" domain label plus SAP/ERP/SQL tool
# mentions inflated the skills match even though the function itself was
# never on any IT block list.
# ---------------------------------------------------------------------------
class TestDataArchitectFalsePositiveFix:
    def test_real_data_architect_posting_is_rejected(self):
        # Real posting text (Hipo, AUMOVIO Romania) that surfaced this false
        # positive: scored 82%/APPLY on the office track before the fix.
        posting = job(
            "Data Architect (m/f/div) - Automotive Finance & Controlling",
            "Timisoara",
            "Design and maintain data models, ETL pipelines and the enterprise data "
            "warehouse for Finance and Controlling. SAP, SQL, Excel reporting.",
        )
        keep, reason = hard_filter_job(posting, DEFAULT_PROFILE, TRACK_AHMED_OFFICE)
        assert keep is False
        assert "it" in reason.lower() or "technical" in reason.lower()

    def test_fix_is_track_independent(self):
        posting = job(
            "Data Architect (m/f/div) - Automotive Finance & Controlling",
            "Timisoara",
            "Design and maintain data models, ETL pipelines and the enterprise data "
            "warehouse for Finance and Controlling. SAP, SQL, Excel reporting.",
        )
        keep, _ = hard_filter_job(posting, DEFAULT_PROFILE, DEFAULT_TRACK)
        assert keep is False

    def test_unrelated_finance_and_compliance_titles_are_unaffected(self):
        for title, desc in (
            ("Finance Analyst", "SAP, Excel, financial reporting, controlling."),
            ("Compliance Case Manager - Tires", "Compliance, regulatory, English required."),
        ):
            posting = job(title, "Timisoara", desc)
            keep, reason = hard_filter_job(posting, DEFAULT_PROFILE, TRACK_AHMED_OFFICE)
            assert keep is True, f"{title!r} should not be affected by the Data Architect exclusion: {reason}"
