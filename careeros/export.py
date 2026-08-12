"""CSV / Markdown export helpers."""

from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Dict, Iterable, List

from .text import canonical_url, clean_html_text, safe_company_name, truncate
from .tracker import Application

__all__ = ["jobs_to_csv", "applications_to_csv", "jobs_to_markdown"]


def jobs_to_csv(jobs: List[Dict], applied_urls: Iterable[str] = ()) -> str:
    applied = {canonical_url(u) for u in applied_urls}
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Overall %", "Match %", "Eligibility %", "Hiring reality %",
        "Confidence", "Title", "Company", "Location",
        "Source", "Posted (days ago)", "Salary (published)",
        "Salary (≈RON/month)", "Romanian requirement", "Warnings",
        "Applied", "Link",
    ])
    for index, job in enumerate(jobs, start=1):
        match = job.get("_match")
        salary = getattr(match, "salary", None)
        monthly = ""
        if salary is not None and salary.has_value:
            low, high = salary.monthly_ron_min, salary.monthly_ron_max
            monthly = f"{low:,.0f}" + (f" - {high:,.0f}" if high and high != low else "")
        url = job.get("redirect_url", "")
        writer.writerow([
            index,
            getattr(match, "score", 0),
            getattr(match, "match_score", getattr(match, "score", 0)),
            getattr(match, "eligibility_score", ""),
            getattr(match, "hiring_score", ""),
            getattr(match, "confidence", ""),
            job.get("title", ""),
            safe_company_name(job.get("company")),
            (job.get("location") or {}).get("display_name", ""),
            job.get("source", ""),
            job.get("age_days", ""),
            job.get("salary_text", ""),
            monthly,
            getattr(match, "romanian", ""),
            "; ".join(getattr(match, "warnings", [])),
            "Yes" if canonical_url(url) in applied else "No",
            url,
        ])
    return output.getvalue()


def applications_to_csv(applications: List[Application]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Title", "Company", "Location", "Status", "Match %",
        "Applied at", "Last update", "Notes", "Source", "URL",
    ])
    for app in applications:
        writer.writerow([
            app.title, app.company, app.location, app.status, app.match_score,
            app.applied_at, app.updated_at, app.notes, app.source, app.url,
        ])
    return output.getvalue()


def jobs_to_markdown(jobs: List[Dict], limit: int = 25) -> str:
    lines = [
        "# CareerOS AI — shortlist",
        f"_Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}_",
        "",
    ]
    for index, job in enumerate(jobs[:limit], start=1):
        match = job.get("_match")
        score = getattr(match, "score", 0)
        match_s = getattr(match, "match_score", score)
        elig_s = getattr(match, "eligibility_score", "")
        hire_s = getattr(match, "hiring_score", "")
        lines.append(f"## {index}. {job.get('title', 'Untitled')} — {score}% overall")
        lines.append("")
        lines.append(f"- **Scores:** match {match_s}% · eligibility {elig_s}% · hiring reality {hire_s}%")
        lines.append(f"- **Company:** {safe_company_name(job.get('company'))}")
        lines.append(f"- **Location:** {(job.get('location') or {}).get('display_name', 'n/a')}")
        lines.append(f"- **Source:** {job.get('source', 'n/a')}")
        if job.get("salary_text"):
            lines.append(f"- **Salary:** {job['salary_text']}")
        if job.get("redirect_url"):
            lines.append(f"- **Link:** {job['redirect_url']}")
        reasons = getattr(match, "reasons", [])
        if reasons:
            lines.append(f"- **Why it matches:** {'; '.join(reasons[:4])}")
        warnings = getattr(match, "warnings", [])
        if warnings:
            lines.append(f"- **Check first:** {'; '.join(warnings[:3])}")
        description = clean_html_text(job.get("description", ""))
        if description:
            lines.append("")
            lines.append(f"> {truncate(description, 350)}")
        lines.append("")
    return "\n".join(lines)
