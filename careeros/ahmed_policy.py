from __future__ import annotations
import re
from typing import Optional
from .text import normalize_text, contains_phrase

FOREIGN_MARKETS = {
    "olanda":"Netherlands","tara de jos":"Netherlands","netherlands":"Netherlands",
    "germania":"Germany","germany":"Germany","deutschland":"Germany",
    "ungaria":"Hungary","hungary":"Hungary","italia":"Italy","italy":"Italy",
    "franta":"France","franța":"France","france":"France","belgia":"Belgium","belgium":"Belgium",
    "spania":"Spain","spain":"Spain","cehia":"Czechia","czechia":"Czechia",
    "polonia":"Poland","poland":"Poland","austria":"Austria","grecia":"Greece","greece":"Greece",
    "suedia":"Sweden","sweden":"Sweden","danemarca":"Denmark","denmark":"Denmark",
    "irlanda":"Ireland","ireland":"Ireland","portugalia":"Portugal","portugal":"Portugal",
    "anglia":"UK","marea britanie":"UK","regatul unit":"UK","united kingdom":"UK",
}
ROMANIA_TOKENS = ("romania", "românia", "timisoara", "timișoara", "bucuresti", "bucharest", "cluj", "iasi", "brasov", "arad", "sibiu", "oradea")

def _named(text: str):
    n = normalize_text(text)
    found=[]
    for token, market in sorted(FOREIGN_MARKETS.items(), key=lambda x: len(x[0]), reverse=True):
        if contains_phrase(n, token) and market not in found:
            found.append(market)
    return found

def foreign_labour_market(location_text: str, title: str = "", description: str = "") -> Optional[str]:
    title_n = normalize_text(title)
    loc_n = normalize_text(location_text)
    desc_n = normalize_text(description)[:400]
    title_markets = _named(title_n)
    if title_markets and not any(contains_phrase(title_n, token) for token in ROMANIA_TOKENS):
        return title_markets[0]
    loc_markets = _named(loc_n)
    if loc_markets:
        return loc_markets[0]
    desc_markets = _named(desc_n)
    if desc_markets and not any(contains_phrase(desc_n, token) for token in ROMANIA_TOKENS):
        return desc_markets[0]
    return None

_HEAVY_TITLE = re.compile(r"\b(?:c\s*[＋+&/]\s*e|c\s*/\s*e|ce\b|categoria\s+c(?:e|\+e)?|category\s+c(?:e|\+e)?|cat\.?\s*c(?:e|\+e)?|categoria\s+d|category\s+d|cat\.?\s*d|d\s*[＋+&/]\s*e|permis\s+(?:c|ce|c\+e|d|de)\b|sofer\s+camion|șofer\s+camion|truck\s+driver|tir(?:\s+driver)?|sofer\s+autobuz|șofer\s+autobuz|bus\s+driver|coach\s+driver|camion|autobuz|autocar)\b", re.I)
_HEAVY_LICENCE = re.compile(r"(?:permis|licence|license|categoria|category|cat\.?)\s*(?:c\s*[＋+&/]\s*e|ce|c\b|d\b|d\s*[＋+&/]\s*e)", re.I)

def is_heavy_driver_role(job) -> bool:
    title = normalize_text(str(job.get("title", "") or ""))
    desc = normalize_text(str(job.get("description", "") or ""))[:800]
    if _HEAVY_TITLE.search(title):
        return True
    if _HEAVY_LICENCE.search(f"{title} {desc}"):
        text=f"{title} {desc}"
        if re.search(r"(?:categoria|category|cat\.?|permis)\s*b\b", text, re.I) and not re.search(r"(?:categoria|category|cat\.?)\s*(?:c|d)\b|c\s*[＋+&/]\s*e|permis\s*(?:c|d)\b", text, re.I):
            return False
        return True
    return False

IT_HARD_RE = re.compile(r"\bit\b.+\b(?:governance|infrastructure|service|operations|coordinator|asset|locations?)\b", re.I)
IT_PHRASES=("it governance","it coordinator","it locations","it infrastructure","it service","it operations","information security","infosec","cyber security","cybersecurity","quality coordinator emea - tires")

def is_it_hard_title(title: str) -> bool:
    t=normalize_text(title)
    return any(contains_phrase(t,p) for p in IT_PHRASES) or bool(IT_HARD_RE.search(t))

def b_compatible(job) -> bool:
    title=normalize_text(str(job.get("title","") or "")); body=normalize_text(str(job.get("description","") or ""))
    text=f"{title} {body}"
    if is_heavy_driver_role(job): return False
    if re.search(r"\b(?:categoria|category|cat\.?)\s*b\b|\bpermis\s+b\b", text, re.I): return True
    courier=re.search(r"\b(?:courier|curier|livrator|delivery driver|van driver|route driver)\b", title, re.I)
    return bool(courier and not re.search(r"\b(?:c\s*[＋+&/]\s*e|categoria\s+c|category\s+c|cat\.?\s*c|categoria\s+d|category\s+d|cat\.?\s*d|camion|autobuz|tir)\b", text, re.I))

def manager_without_evidence(job, profile) -> bool:
    title=normalize_text(str(job.get("title","") or ""))
    if not re.search(r"\b(?:manager|head|director|supervisor)\b", title): return False
    evidence=normalize_text(" ".join(str(x or "") for x in (getattr(profile,"skills",[]) or []) + (getattr(profile,"highlights",[]) or [])))
    return not any(x in evidence for x in ("managed a team","managed team","team of","direct reports","people management","staff management","supervised staff","supervised a team","led a team","team leadership","managed employees","managed staff"))

def calibrate_result(result, job=None, profile=None, original=None):
    if getattr(result,"verdict","") == "skip" or getattr(result,"reject_reason",""):
        result.score=min(int(getattr(result,"score",0) or 0),34)
        result.verdict_label="🔴 SKIP"; result.verdict="skip"
        return result
    if job is not None and profile is not None and manager_without_evidence(job,profile):
        result.reasons=[r for r in result.reasons if not r.startswith("🧑‍💼 Leadership role — fits")]
        result.match_score=max(0,result.match_score-9)
        if not any("Management scope" in r for r in result.warnings):
            result.warnings.append("⚠️ Management scope is not demonstrated in the documented profile")
    if original is not None:
        result=original(result, job=job, profile=profile)
    hiring=int(getattr(result,"hiring_score",0) or 0)
    if hiring < 50: result.score=min(result.score,49)
    elif hiring < 60: result.score=min(result.score,59)
    elif hiring < 70: result.score=min(result.score,69)
    if any("Management-scope realism" in label or "Specialist-transfer realism" in label for label,_ in getattr(result,"adjustments",[])):
        result.score=min(result.score,69)
    if is_heavy_driver_role(job or {}):
        return result
    if result.score>=80: result.verdict_label,result.verdict="🟢 APPLY","apply"
    elif result.score>=70: result.verdict_label,result.verdict="🟢 STRONG","strong"
    elif result.score>=60: result.verdict_label,result.verdict="🟡 MAYBE","maybe"
    elif result.score>=50: result.verdict_label,result.verdict="🟠 LOW","low"
    else: result.verdict_label,result.verdict="🔴 SKIP","skip"
    return result
