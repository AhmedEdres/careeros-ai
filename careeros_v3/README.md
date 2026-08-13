# CareerOS AI v3.1 — Safe Integration / Ranking Fix

This build is a **non-destructive parallel build**. It does not overwrite the existing CareerOS project.

## What was fixed

The previous ranking engine had a structural weakness: a technically unrelated job could accumulate points from location + English + generic support/operations words. It could therefore look like a 60%+ match even when the career family was wrong.

v3.1 changes the order of trust:

`collect → normalize → deduplicate → hard eligibility → career-family evidence → transferable skills → dimensional score → guardrail → rank`

### Main corrections

1. **Career family is now decisive.** Technical/engineering titles are capped at 24 and cannot appear as actionable recommendations.
2. **Unknown information scores zero.** Missing experience or salary no longer receives free points.
3. **Title evidence is stronger than generic description words.** A role title such as `Accountant`, `Compliance Specialist`, or `Operations Coordinator` carries much more weight than a random occurrence of `support` in a description.
4. **Word-boundary matching was added.** For example, `tax` does not match `taxi`.
5. **Profile arguments are respected.** Experience and salary scoring now use the supplied profile instead of silently falling back to the global profile.
6. **Remote country restrictions are checked in both location and description.**
7. **Actionable tiers are exposed:** `strong`, `good`, `possible`, `weak`, `reject-like`.
8. **The UI defaults to actionable matches**, while weak/technical results remain available in the audit view.
9. **Regression coverage increased from 5 to 9 tests.**

## What we learned from the Romanian scraper project

The public `cucubogdan00/romania_it_job_scraper` project has useful architectural ideas: separate source scrapers, a shared parser/data model, strong negative-keyword filtering, work-mode/location parsing, database UPSERT/deduplication, expiry checking, and scheduled scraping. CareerOS should borrow these **architectural principles**, not copy its IT-only filters or source code.

That project is explicitly designed around eJobs, BestJobs and LinkedIn and an IT/technical market, so it is not a complete fit for Ahmed's target roles. Its strongest reusable idea for CareerOS is the **source-adapter + normalization + enrichment pipeline**.

## Current source limitation

This safe build contains Jooble and Remotive adapters. Remotive is remote-focused; it should not be treated as sufficient Romanian-market coverage by itself. Jooble requires `JOOBLE_API_KEY`.

The next source layer should add Romanian-market coverage (eJobs / BestJobs / ANOFM / peViitor or a maintained equivalent) behind the same adapter contract. Do this **after the ranking engine passes the fixture tests**, so we do not mix collection bugs with ranking bugs.

## Run

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app_careeros_v3.py
```

Optional:

```text
JOOBLE_API_KEY=...
```

## Regression test

```bash
PYTHONPATH=. pytest -q
```

Expected result for this build:

```text
9 passed
```

## Important

Do not replace the existing `main` project with this archive yet. First run this build and compare its top 20 jobs with the current application. Only then should the ranking module be promoted into `main`.
