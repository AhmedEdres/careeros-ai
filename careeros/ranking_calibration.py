"""Post-match ranking calibration for Ahmed's target profile.

This layer deliberately separates *career fit* from generic keyword overlap.
It is applied after the existing v4 scoring/role-intelligence layer and before
results are rendered.  The goal is to stop high salary, generic finance words,
or seniority labels from overpowering direct career evidence.
"""
from __future__ import annotations

import re


def _text(job):
    title = str(job.get("title", "") or "").lower()
    desc = str(job.get("description", "") or "").lower()
    return title, desc


def calibrate_ahmed_ranking(result, job, profile):
    """Apply small, explainable ranking corrections for Ahmed.

    The function never creates eligibility. It only changes ranking after the
    existing hard filters and role-family classifier have run.
    """
    title, desc = _text(job)
    experience = int(getattr(profile, "experience_years", 0) or 0)

    # 1) Junior roles should not outrank realistic mid/senior opportunities for
    # a candidate with substantial experience unless there is unusually strong
    # direct evidence.
    junior = bool(re.search(r"\b(junior|jr\.?|entry[- ]level|intern|trainee|graduate)\b", title))
    if junior and experience >= 8:
        penalty = 5
        result.score = max(0, int(result.score) - penalty)
        result.hiring_score = max(0, int(result.hiring_score) - 6)
        result.warnings.append("⚠️ Seniority calibration: junior title is below your 10+ years of experience")
        result.adjustments.append(("Junior seniority calibration", -penalty))

    # 2) Accounting is adjacent to Ahmed's tax/compliance background. Generic
    # finance keywords must not make accounting roles look like direct matches.
    accounting = bool(re.search(
        r"\b(accountant|accounting|accounts payable|accounts receivable|general ledger|bookkeeper|contabil)\b",
        title,
    ))
    tax_compliance = bool(re.search(
        r"\b(tax|taxation|fiscal|compliance|aml|kyc|regulatory|audit|sanctions)\b",
        title + " " + desc,
    ))
    if accounting and tax_compliance:
        penalty = 5
        result.match_score = max(0, int(result.match_score) - penalty)
        result.hiring_score = max(0, int(result.hiring_score) - 4)
        result.score = max(0, int(result.score) - penalty)
        result.warnings.append("🟠 Accounting remains adjacent to your tax/compliance background")
        result.adjustments.append(("Accounting-vs-tax directness calibration", -penalty))

    # 3) A manager/director label alone is not evidence that Ahmed has the
    # required people-management scope. The existing warning remains; this
    # makes the ranking effect meaningful without rejecting the vacancy.
    leadership = bool(re.search(r"\b(manager|director|head|supervisor)\b", title))
    management_evidence = bool(re.search(
        r"\b(managed (a )?team|team of \d+|direct reports|people management|"
        r"staff management|supervised (staff|a team)|led (a )?team|team leadership|"
        r"hiring and performance|performance reviews|workforce management|"
        r"p&l|budget (ownership|management)|managed employees|managed staff)\b",
        desc,
    ))
    if leadership and not management_evidence:
        penalty = 3
        result.hiring_score = max(0, int(result.hiring_score) - 5)
        result.score = max(0, int(result.score) - penalty)
        result.warnings.append("⚠️ Leadership title detected without clear people-management evidence")
        result.adjustments.append(("Unverified management scope", -penalty))

    # 4) Direct target-family evidence gets a modest boost. This is intentionally
    # small: it should break ties, not manufacture a high match.
    direct_signals = (
        "tax specialist", "tax officer", "tax compliance", "compliance officer",
        "compliance specialist", "regulatory compliance", "back office",
        "operations specialist", "operations coordinator", "order management",
        "logistics coordinator", "customer support specialist", "customer service",
    )
    if any(signal in title for signal in direct_signals):
        bonus = 4
        result.match_score = min(100, int(result.match_score) + bonus)
        result.score = min(100, int(result.score) + bonus)
        result.reasons.append("🎯 Ranking calibration: title is directly aligned with a target career family")
        result.adjustments.append(("Direct target-family evidence", bonus))

    # 5) Do not allow a very high salary to disguise weak career fit. The base
    # matcher already weights salary modestly; this final guard only applies to
    # obviously adjacent roles.
    salary = getattr(result, "salary", None)
    high_salary = bool(salary and getattr(salary, "has_value", False) and
                       (getattr(salary, "monthly_ron_max", 0) or 0) >= 9000)
    if high_salary and int(result.match_score) < 55:
        cap = 55
        if int(result.score) > cap:
            result.score = cap
            result.adjustments.append(("High-salary / weak-fit cap", 0))
            result.warnings.append("⚠️ High salary cannot compensate for weak career fit")

    return result
