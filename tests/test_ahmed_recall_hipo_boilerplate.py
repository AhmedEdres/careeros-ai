"""Regression tests for the Hipo description-boilerplate cleanup.

Found via manual real-data audit: some Hipo scrapes capture the whole page
(site navigation + a rotating "Company News" sidebar widget, ~2500 chars)
before the actual job content, which reliably starts at "Employer:" with
the job title repeated immediately before it. That boilerplate is strong
enough on its own to make role_intelligence misclassify the posting - an
incidental "recruiter" mention in the "CV Clinic: Think Like a Recruiter"
news blurb tipped several Compliance/Operations roles into the "HR" family
and hard-rejected them entirely, including two previously-validated top
matches (Privacy Compliance Officer 96%, Compliance Officer EMEA 90%).
"""

from careeros import DEFAULT_PROFILE, calculate_match, hard_filter_job
from careeros.ahmed_recall import _clean_description, _normalise_hipo_job
from careeros.tracks import TRACK_AHMED_OFFICE

# Verbatim excerpt of the real contaminated description (Hipo, "Privacy
# Compliance Officer (m/f/d)" @ AUMOVIO Romania) that surfaced this bug:
# the leading site-navigation/"Company News" boilerplate (containing the
# "recruiter" mention) is kept exactly as scraped, followed by a genuine
# excerpt of the real job content starting at Hipo's "Employer:" marker.
REAL_CONTAMINATED_DESCRIPTION = (
    "Hipo.ro Hipo.ro Locuri de munca Home MyHipo Adauga CV Hipo.ro pentru Angajatori Contact "
    "Cauta Job Angajatori activi pe Hipo.ro Joburi pe domenii Joburi in orase Jobs cloud Cariera "
    "Stiri cariera Articole cariera Ghidul angajatorilor Interviuri Job Dictionary Hipo Company "
    "News Proiecte Remote Jobs Job Salariu Afisat Job Junior Job Specialist Top Angajatori "
    "Proiecte Hipo Job Manager Podcast CV Designer Angajatori de TOP Timisoara, Bucuresti Home "
    "MyHipo Adauga CV Noutati eveniment Angajatori de TOP Angajatori de TOP Timisoara Cauta job "
    "in Timisoara Angajatori Timisoara TechTalks Timisoara Workshopuri Cariera Timisoara Locatie "
    "Angajatori de TOP Timisoara Angajatori de TOP Bucuresti Cauta job in Bucuresti Angajatori "
    "Bucuresti TechTalks Bucuresti Workshopuri Cariera Bucuresti Locatie Angajatori de TOP "
    "Bucuresti Targ de cariera la nivel national, Angajatori de TOP Virtual! Home MyHipo Adauga "
    "CV Noutati despre Angajatori de TOP Virtual Angajatori de TOP Virtual Targ Virtual Cauta Job "
    "Companii participante Home MyHipo Adauga CV Eveniment Agenda Inscriere Speakeri Editii "
    "trecute Proces de selectie Contact Contact Targul Virtual Hipo.ro pentru Absolventi Home "
    "MyHipo Adauga CV Noutati despre Targul Virtual Hipo.ro pentru Absolventi Contact Targul "
    "Virtual Hipo.ro Absolventi Companii participante Cauta job Targ Virtual Programe Recrutare "
    "Ghid Angajare DevTalks Cluj, Bucuresti Home MyHipo Adauga CV Noutati despre DevTalks "
    "DevTalks Cluj-Napoca Agenda Speakers Exhibitors Registration DevTalks Bucuresti Agenda "
    "Speakers Exhibitors Registration Salarii JumpStart --> Intra in cont CANDIDAT Intra in cont "
    "CANDIDAT Ai uitat parola? Login cu Facebook Login cu LinkedIn Login cu Google Cum "
    "functioneaza login cu retelele sociale? Cont nou CANDIDAT Intra in cont ANGAJATOR Intra in "
    "cont ANGAJATOR Ai uitat parola? Hipo.ro pentru Angajatori MyHipo Adauga CV Cauta Job Cariera "
    "Cariera Stiri cariera Articole cariera Ghidul Angajatorilor Interviuri Job Dictionary Hipo "
    "Company News Podcast Hipo Projects news Company News CV Clinic: Think like a Recruiter "
    "Company News PPC Romania - Becoming a PowerTech company is, above all, a people "
    "transformation Company News Incepe-ti cariera in locul potrivit | Roluri deschise Projects "
    "news Tu la ce companie aplici vara aceasta Remote Jobs Job Salariu Afisat Job Junior Job "
    "Specialist Top Angajatori Proiecte Hipo Job Manager Toate Podcast CV Designer Angajatori "
    "activi pe Hipo.ro Joburi pe domenii Joburi in orase Joburi in judete Joburi Titlu Job Jobs "
    "Cloud "
    "Privacy Compliance Officer (m/f/d) Employer: AUMOVIO Romania Domain: Engineering Job type:: "
    "full-time Job level: 1 - 5 ani experienta Location: Timisoara Updated at: 20-08-2026 Remote "
    "work: On-site Apply to this job Apply with LinkedIn Apply with Facebook Company Description "
    "Since its spin-off in September 2025 AUMOVIO continues the business of the former Continental "
    "group sector Automotive as an independent company. Job Description As a member of the "
    "central AUMOVIO Privacy & AI Compliance team, the Privacy Compliance Officer supports the "
    "Privacy Compliance Management System of AUMOVIO globally. Support the Head of Privacy and AI "
    "Compliance with the design and implementation of the Privacy Management System including "
    "rules, policies, trainings, communication, monitoring and controls. Providing trainings on "
    "Privacy and AI Compliance matters. Qualifications: Academic Degree in Law (preferred) or "
    "Business Administration. At least 5 years of proven professional experience in the area of "
    "privacy. Fluent English language skills (spoken and written) required."
)


def job(title, description, location="Timisoara", source="Hipo"):
    return {
        "title": title,
        "description": description,
        "location": {"display_name": location},
        "company": {"display_name": "X"},
        "salary_text": "",
        "category": {"label": ""},
        "source": source,
    }


class TestHipoDescriptionBoilerplateCleanup:
    def test_real_contaminated_description_is_cleaned(self):
        posting = job(
            "Privacy Compliance Officer (m/f/d)",
            REAL_CONTAMINATED_DESCRIPTION,
        )
        cleaned = _normalise_hipo_job(posting)
        assert "recruiter" not in cleaned["description"].lower()
        assert "hipo.ro" not in cleaned["description"].lower()
        assert cleaned["description"].startswith("Privacy Compliance Officer (m/f/d) Employer:")
        assert len(cleaned["description"]) < len(REAL_CONTAMINATED_DESCRIPTION)

    def test_real_contaminated_posting_is_no_longer_misclassified_as_hr(self):
        # Before the fix: hard-rejected as "Different career track (Hr)"
        # because of the incidental "recruiter" mention in the boilerplate.
        posting = job(
            "Privacy Compliance Officer (m/f/d)",
            REAL_CONTAMINATED_DESCRIPTION,
        )
        cleaned = _normalise_hipo_job(posting)
        keep, reason = hard_filter_job(cleaned, DEFAULT_PROFILE, TRACK_AHMED_OFFICE)
        assert keep is True, reason
        result = calculate_match(cleaned, DEFAULT_PROFILE, TRACK_AHMED_OFFICE)
        assert result.score >= 70
        assert result.verdict in {"apply", "strong"}

    def test_short_clean_hipo_description_is_untouched(self):
        # No "Employer:" marker -> already clean, must not be modified at all.
        posting = job("ServiceNow Developer", "ServiceNow Developer SCHAEFFLER 20-08-2026 Timisoara")
        cleaned = _normalise_hipo_job(posting)
        assert cleaned["description"] == posting["description"]

    def test_description_without_employer_marker_is_returned_unchanged(self):
        text = "A perfectly normal, short job description with no boilerplate at all."
        assert _clean_description({"title": "X", "description": text}) == text

    def test_empty_description_does_not_error(self):
        assert _clean_description({"title": "X", "description": ""}) == ""
        assert _clean_description({"title": "X"}) == ""

    def test_cleanup_falls_back_gracefully_when_title_does_not_match(self):
        # Title text isn't found verbatim before "Employer:" (e.g. mismatched
        # formatting) - must still strip most of the boilerplate via the
        # look-back fallback, rather than raising or returning everything.
        text = (
            "Some navigation boilerplate padding padding padding padding padding padding "
            "padding padding padding padding padding padding padding padding padding more "
            "than one hundred and twenty characters long before the real content starts. "
            "Employer: Acme Corp. Real job content follows."
        )
        cleaned = _clean_description({"title": "Completely Different Title", "description": text})
        assert "Employer: Acme Corp" in cleaned
        assert len(cleaned) < len(text)
