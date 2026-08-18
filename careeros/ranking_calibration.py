"""Post-match ranking calibration for Ahmed's target profile.

This layer deliberately separates *career fit* from generic keyword overlap.
It is applied after the existing v4 scoring/role-intelligence layer and before
results are rendered. The goal is to stop high salary, generic finance words,
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

    junior = bool(re.search(r"\b(junior|jr\.?|entry[- ]level|intern|trainee|graduate)\b", title))
    if junior and experience >= 8:
        penalty = 5
        result.score = max(0, int(result.score) - penalty)
        result.hiring_score = max(0, int(result.hiring_score) - 6)
        result.warnings.append("⚠️ Seniority calibration: junior title is below your 10+ years of experience")
        result.adjustments.append(("Junior seniority calibration", -penalty))

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

    # Direct target-family evidence must matter more than generic keyword
    # overlap. Title evidence is stronger than description-only evidence.
    direct_signals = (
        "tax specialist", "tax officer", "tax compliance", "tax advisor",
        "tax consultant", "specialist fiscal", "ofițer fiscal", "ofiter fiscal",
        "compliance officer", "compliance specialist", "regulatory compliance",
        "back office", "operations specialist", "operations coordinator",
        "order management", "logistics coordinator", "customer support specialist",
        "customer service specialist", "customer support", "customer service",
    )
    tax_title_signals = (
        "tax specialist", "tax officer", "tax compliance", "tax advisor",
        "tax consultant", "specialist fiscal", "ofițer fiscal", "ofiter fiscal",
    )
    direct_title = any(signal in title for signal in direct_signals)
    direct_body = any(signal in desc for signal in direct_signals)
    direct_tax_title = any(signal in title for signal in tax_title_signals)

    if direct_tax_title:
        # Tax/fiscal is Ahmed's strongest documented target family. Give it a
        # small additional edge over generic operations/customer-support titles.
        bonus = 10
        result.match_score = min(100, int(result.match_score) + bonus)
        result.score = min(100, int(result.score) + bonus)
        result.reasons.append("🎯 Direct target-family evidence — tax/fiscal title prioritized")
        result.adjustments.append(("Direct target-family evidence: tax/fiscal title priority", bonus))
    elif direct_title:
        bonus = 8
        result.match_score = min(100, int(result.match_score) + bonus)
        result.score = min(100, int(result.score) + bonus)
        result.reasons.append("🎯 Direct title-family evidence — prioritized for your target career")
        result.adjustments.append(("Direct target-family evidence: title priority", bonus))
    elif direct_body:
        bonus = 2
        result.match_score = min(100, int(result.match_score) + bonus)
        result.score = min(100, int(result.score) + bonus)
        result.reasons.append("🎯 Direct target-family evidence in job description")
        result.adjustments.append(("Direct target-family evidence: body", bonus))

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
