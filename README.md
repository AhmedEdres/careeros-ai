# 🎯 CareerOS AI

AI-powered job search, matching and application assistant for the Romanian &
EU market. Searches several job boards at once, ranks every posting against
your profile with an explainable score, and tracks your applications.

![tests](https://img.shields.io/badge/tests-241%20passing-brightgreen)

---

## Quick start

```bash
git clone https://github.com/AhmedEdres/careeros-ai
cd careeros-ai

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # add your keys
streamlit run app.py
```

The app runs with **zero API keys** — Remotive, Arbeitnow and Jobicy are free
and enabled by default. Adding a Jooble key unlocks the main Romanian source.

### API keys

| Secret | Needed for | Where to get it |
|---|---|---|
| `JOOBLE_API_KEY` | 🇷🇴 Jooble — the main Romanian source | [jooble.org/api/about](https://jooble.org/api/about) (free) |
| `CLAUDE_API_KEY` | AI analysis, cover letters, CV tailoring | [console.anthropic.com](https://console.anthropic.com) |
| `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` | Adzuna, structured salary data | [developer.adzuna.com](https://developer.adzuna.com) (free) |
| `CAREERJET_AFFID` | Careerjet | [careerjet.com/partners](https://www.careerjet.com/partners/) (free) |

> ⚠️ Never commit `.streamlit/secrets.toml` — it is git-ignored. On Streamlit
> Community Cloud, paste the keys into **App settings → Secrets** instead.

---

## How the matching works (engine v4)

Every job gets **three scores**, blended **40 / 35 / 25** into the ranking.
The question is no longer "what matches my CV?" but "what gives this candidate
the highest realistic probability of being hired in Romania / the EU?".

| Score | Weight | What it answers |
|---|---|---|
| **Match** | 40% | Does the job suit your skills? The 100-point weight table changes with the career track. |
| **Eligibility** | 35% | Can you legally and practically take it — location, work authorisation, languages, Romanian? |
| **Hiring reality** | 25% | Would a recruiter actually shortlist you? |

A weak match cannot be propped up by the absence of legal barriers: when Match
is below 50 the other two scores are capped, so a 9% match cannot sneak up to
52% overall.

**Career tracks change the weights**, not just the search queries. Arabic is
worth 30 points on the Arabic-speaking track and 8 on Logistics; education is
worth 0 on Customer Support and 12 on Finance. A Bucharest finance role is
1.35× more Romanian-dependent than a remote Arabic desk (0.5×).

**Romanian is graded**, not binary. "Romanian is a plus" costs nothing; an
unspecified "Romanian and English required" is a risk, not an automatic reject.
Advanced C1/C2/fluent/native is still a hard filter.

**Remote geography is graded.** `Remote — Romania` is eligible; `Remote — Europe/EU`
is eligible; `Remote — Greece` (or any single foreign country) is *that*
country's labour market, not EU-wide — it no longer ranks as a free remote win.

**Rejected before scoring:** advanced Romanian, remote roles restricted to
another region, and titles on a clearly different career track (a CNC operator
is kept on *Logistics & Production*).

---

## Features

- **6 job sources in parallel** — Jooble, Remotive, Arbeitnow, Jobicy, Adzuna, Careerjet
- **Smart deduplication** — the same posting from two boards is merged, keeping the richer description and both source names. Per-country campaign reposts (`(GR)` / `(UK)` / `(PT)`) collapse into one card, keeping the location he is most likely eligible for
- **Three scores on every card** — Match, Eligibility, Hiring reality, blended 40/35/25
- **Hiring reality tab** — why a recruiter would (or would not) shortlist you
- **Logistics & Production track** — Timișoara manufacturing / warehouse weighting
- **Instant filters** — match %, location, Romanian requirement, age, salary, already-applied. Re-filtering never re-hits the APIs
- **Salary intelligence** — parses `3.500 - 5.000 RON/luna`, `€45k per year`, `$25/hour` and normalises everything to RON/month
- **Application tracker** — status pipeline (Applied → Screening → Interview → Offer), notes, CSV export
- **AI tools** (optional) — fit analysis, cover letter, CV bullet tailoring, interview prep
- **Exports** — results CSV, applications CSV, Markdown shortlist

---

## Project structure

```
careeros/
├── text.py           # normalisation, whole-word matching, URL canonicalisation
├── salary.py         # free-text salary parsing → RON/month
├── profile.py        # candidate model + keyword taxonomy
├── matching.py       # scoring engine v4 (three scores, track-aware)
├── tracks.py         # career-track weight tables and Romanian pressure
├── search.py         # query expansion, parallel fetch, dedup, filtering
├── tracker.py        # application store with safe persistence
├── ai.py             # Anthropic client (no SDK dependency)
├── export.py         # CSV / Markdown exports
└── sources/
    ├── base.py       # HTTP session, retries, canonical job record
    └── providers.py  # one adapter per job board
app.py                # Streamlit UI only
tests/                # 241 tests
```

Business logic is pure Python with no Streamlit imports, so it is fully
unit-testable and reusable outside the UI.

---

## Development

```bash
pip install -r requirements-dev.txt
pytest                       # 241 tests
pytest tests/test_app_ui.py  # UI regression tests
```

### Adding a job source

1. Write a `fetch_*` function in `careeros/sources/providers.py` returning a
   `SourceResult` built with `make_job(...)`.
2. Register it in the `PROVIDERS` dict.

The sidebar, filters, dedup, scoring and exports pick it up automatically. Set
`client_side_filter=True` if the API has no server-side search, so it is
fetched once per search instead of once per query.

---

## Deployment (Streamlit Community Cloud)

1. Push the repository to GitHub.
2. Create an app pointing at `app.py`.
3. Add your keys under **App settings → Secrets**.

The application store falls back to session-only storage on read-only
filesystems and warns you in the sidebar — export the CSV to keep a permanent
record. To persist across restarts, set `CAREEROS_DATA_FILE` to a writable path.
