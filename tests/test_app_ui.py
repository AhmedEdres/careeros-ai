"""UI-level regression tests using Streamlit's AppTest harness.

The most important one is ``test_results_survive_rerun``: in the previous
version every widget interaction wiped the results, because the whole result
list was rendered inside ``if search_clicked:``.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

AppTest = pytest.importorskip("streamlit.testing.v1").AppTest

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")

from careeros.sources.base import make_job  # noqa: E402


def sample_jobs():
    return [
        make_job(
            title="Arabic Customer Support Specialist",
            company="Global BPO",
            location="Timisoara, Romania",
            description=(
                "We need a customer support specialist. Arabic is required and English "
                "is required. Romanian is a plus. Experience with SAP and Excel. "
                "Salary 6000 - 7000 RON per month. Shared services centre."
            ),
            url="https://example.com/job/1",
            source="Jooble",
            salary_text="6000 - 7000 RON per month",
        ),
        make_job(
            title="Accounts Payable Officer",
            company="FinCo",
            location="Remote — Europe",
            description="Accounts payable, invoicing and compliance. English required.",
            url="https://example.com/job/2",
            source="Remotive",
        ),
    ]


def run_app_with_results():
    at = AppTest.from_file(APP_PATH, default_timeout=120)
    at.run()
    at.session_state["raw_jobs"] = sample_jobs()
    at.session_state["has_searched"] = True
    at.run()
    # Trigger scoring the way a filter change would.
    at.session_state["f_min_score"] = 0
    at.run()
    return at


def test_app_loads_without_exception():
    at = AppTest.from_file(APP_PATH, default_timeout=120).run()
    assert not at.exception
    assert any("CareerOS" in t.value for t in at.title)


def test_empty_state_prompts_user():
    at = AppTest.from_file(APP_PATH, default_timeout=120).run()
    assert any("Search jobs" in b.label for b in at.button)
    assert at.info, "an onboarding hint should be shown before the first search"


def test_missing_secrets_do_not_crash():
    """The app must render even with no secrets.toml present."""
    at = AppTest.from_file(APP_PATH, default_timeout=120).run()
    assert not at.exception


def test_results_render_from_session_state():
    at = run_app_with_results()
    assert not at.exception
    markdown_blob = " ".join(m.value for m in at.markdown)
    assert "Arabic Customer Support Specialist" in markdown_blob


def test_results_survive_rerun():
    """Regression: clicking any widget used to wipe the result list."""
    at = run_app_with_results()
    before = len(at.session_state["results"])
    assert before > 0

    at.run()  # a plain rerun, as any button click would cause
    assert not at.exception
    assert len(at.session_state["results"]) == before
    markdown_blob = " ".join(m.value for m in at.markdown)
    assert "Arabic Customer Support Specialist" in markdown_blob


def test_filter_change_rescoring_keeps_results():
    at = run_app_with_results()
    at.session_state["f_min_score"] = 95
    at.run()
    # Raw jobs are retained so lowering the threshold restores the list.
    assert at.session_state["raw_jobs"]
    at.session_state["f_min_score"] = 0
    at.run()
    assert len(at.session_state["results"]) == 2


def test_mark_applied_persists_in_store():
    at = run_app_with_results()
    store = at.session_state["store"]
    store.add("https://example.com/job/1", title="Arabic Customer Support Specialist", company="Global BPO")
    at.run()
    assert not at.exception
    assert len(at.session_state["store"]) == 1
    # And it is still there after another rerun.
    at.run()
    assert len(at.session_state["store"]) == 1


def test_profile_edit_rescoring_does_not_crash():
    at = run_app_with_results()
    at.session_state["profile"].target_salary_min = 12000
    at.session_state["f_min_score"] = 0
    at.run()
    assert not at.exception


def test_ranking_is_ordered_by_score():
    at = run_app_with_results()
    scores = [j["_match"].score for j in at.session_state["results"]]
    assert scores == sorted(scores, reverse=True)


def test_stale_session_results_are_rescored_after_engine_change():
    """Regression: an open tab kept showing scores from the previous version.

    The filter signature was built from `id()` and `len()` of the raw jobs, so
    a code change to the scoring engine did not invalidate results already in
    session state — the fix looked like it had never been deployed.
    """
    at = run_app_with_results()
    assert at.session_state["results"]

    # Simulate results scored by an older engine still sitting in the session.
    for job in at.session_state["results"]:
        job["_match"].score = 999
    at.session_state["last_signature"] = ("stale-engine-fingerprint",)
    at.run()

    assert not at.exception
    assert all(j["_match"].score != 999 for j in at.session_state["results"]), \
        "results must be rescored when the engine fingerprint changes"


def test_engine_version_is_exposed():
    at = AppTest.from_file(APP_PATH, default_timeout=120).run()
    captions = " ".join(c.value for c in at.caption)
    assert "engine" in captions, "the engine fingerprint should be visible for diagnosis"
