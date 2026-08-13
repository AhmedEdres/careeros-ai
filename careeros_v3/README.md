# CareerOS AI v3 — Safe Integration Build

This is a parallel, non-destructive implementation of the agreed methodology.
It does **not** overwrite the existing CareerOS files.

## Pipeline

`Source adapters → normalization → URL/fuzzy deduplication → hard eligibility → career-family inference → dimensional score → career-fit guardrail → ranking`

## Source architecture

The engine is source-independent. Jooble and Remotive adapters are included. Future eJobs / BestJobs / LinkedIn adapters can implement the same `SourceAdapter.search()` contract without changing ranking logic.

The architecture follows the useful separation observed in `romania_it_job_scraper`: source-specific collection, a shared job blueprint, description enrichment, and reusable scraping infrastructure. The code here intentionally does not copy that repository's source code.

## Safety properties

- Existing project remains untouched.
- Missing information does not cause automatic rejection.
- Explicit incompatible languages, advanced Romanian, country-locked remote roles, and explicit experience minimums above the profile are rejected before scoring.
- Technical/engineering titles are prevented from receiving a high score merely from generic words such as English, operations, or support.
- Duplicate listings are merged and source count is retained as a trust signal.
- Salary is evidence, not a requirement: missing salary lowers evidence but does not reject a job.
- Freshness and multi-source confirmation affect ranking only.

## Run

```bash
pip install streamlit requests
streamlit run app_careeros_v3.py
```

Optional secrets/environment:

- `JOOBLE_API_KEY`

Remotive does not require a key.

## Regression test

```bash
PYTHONPATH=. pytest -q test_careeros_v3_engine.py
```

The included tests cover wrong-family technical roles, country-locked remote jobs, blocking languages, deduplication, and a strong Arabic/operations role.
