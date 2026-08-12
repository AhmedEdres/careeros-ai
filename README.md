# 🎯 CareerOS AI

AI-powered job search, matching and application assistant for the Romanian &
EU market. Searches several job boards at once, ranks every posting against
your profile with an explainable score, and tracks your applications.

![tests](https://img.shields.io/badge/tests-115%20passing-brightgreen)

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

## How the matching works

Every job is scored out of 100 from **positive evidence only**: a missing
detail scores zero instead of granting free points, so a half-empty listing can
never outrank a genuinely good match.

| Dimension | Max | What earns points |
|---|---|---|
| 📍 Location | 20 | Your city > Romania > EU-eligible remote |
| 💼 Skills | 25 | Operations, finance/compliance, logistics, tools (bonus when in the title) |
| 🗣️ Arabic | 15 | Required > preferred > a plus > mentioned |
| 🇬🇧 English | 10 | Required > preferred > mentioned |
| 🧑‍💼 Experience | 10 | Seniority in the title vs. years requested |
| 💰 Salary | 10 | Parsed from free text, converted to RON/month |
| 🎓 Education | 5 | Law/legal background or degree requirements |
| 🌐 Relevance | 5 | BPO, shared services, MENA exposure |

**Adjustments:** Romanian-friendly wording `+5`; Romanian likely required up to
`-12` (scaled to how far it is above your level); posted in the last 3 days
`+3`; older than 45 days `-3`.

**Rejected before scoring:** advanced Romanian (C1/C2/native), remote roles
restricted to another region, and clearly different career tracks.

Each score comes with a **confidence level** — a 120-character snippet is
labelled *low confidence* rather than being treated as a complete description.

---

## Features

- **6 job sources in parallel** — Jooble, Remotive, Arbeitnow, Jobicy, Adzuna, Careerjet
- **Smart deduplication** — the same posting from two boards is merged, and per-country reposts of one campaign (e.g. `(GR)` / `(UK)` / `(PT)`) collapse into a single card that keeps the most eligible location
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
├── matching.py       # scoring engine v3 (explainable, confidence-aware)
├── search.py         # query expansion, parallel fetch, dedup, filtering
├── tracker.py        # application store with safe persistence
├── ai.py             # Anthropic client (no SDK dependency)
├── export.py         # CSV / Markdown exports
└── sources/
    ├── base.py       # HTTP session, retries, canonical job record
    └── providers.py  # one adapter per job board
app.py                # Streamlit UI only
tests/                # 115 tests
```

Business logic is pure Python with no Streamlit imports, so it is fully
unit-testable and reusable outside the UI.

---

## Development

```bash
pip install -r requirements-dev.txt
pytest                       # 115 tests
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
