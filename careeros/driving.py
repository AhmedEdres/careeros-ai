"""Category B driving fallback and hybrid field-role intelligence."""
from __future__ import annotations
from typing import Dict
from .text import contains_any, normalize_text

DRIVER_TITLE_PATTERNS = ("sofer", "șofer", "driver", "courier", "curier", "livrator", "delivery driver", "distributie", "distribuție", "van driver", "route driver", "transport driver", "driver categoria b", "sofer cat b", "sofer categoria b", "permis categoria b")
HYBRID_PATTERNS = ("field agent", "agent teren", "merchandiser", "field service", "field coordinator", "logistics assistant", "logistics coordinator", "transport coordinator", "dispecer transport", "fleet coordinator", "distribution coordinator", "delivery coordinator")
CATEGORY_B_PATTERNS = ("category b", "categoria b", "cat b", "permis b", "permis categoria b", "driving licence b", "driving license b", "driver license b")
PURE_DRIVER_PATTERNS = ("sofer", "șofer", "driver", "courier", "curier", "livrator", "delivery driver", "van driver", "route driver", "transport driver")


def _text(job: Dict):
    title = normalize_text(str(job.get("title", "") or ""))
    body = normalize_text(str(job.get("description", "") or ""))
    return title, f"{title} {body}"


def is_driver_role(job: Dict) -> bool:
    title, _ = _text(job)
    return contains_any(title, DRIVER_TITLE_PATTERNS)


def is_hybrid_role(job: Dict) -> bool:
    title, full = _text(job)
    return contains_any(title, HYBRID_PATTERNS) or contains_any(full, HYBRID_PATTERNS)


def is_pure_driver(job: Dict) -> bool:
    title, _ = _text(job)
    return contains_any(title, PURE_DRIVER_PATTERNS) and not is_hybrid_role(job)


def requires_category_b(job: Dict) -> bool:
    title, full = _text(job)
    return contains_any(full, CATEGORY_B_PATTERNS) or contains_any(title, DRIVER_TITLE_PATTERNS)


def driver_path(job: Dict) -> str:
    if is_hybrid_role(job) and not is_pure_driver(job):
        return "hybrid"
    if is_driver_role(job):
        return "driver_fallback"
    return "none"


def should_keep_despite_negative_title(job: Dict, profile, track: str = "") -> bool:
    return bool(getattr(profile, "has_category_b_license", True)) and driver_path(job) in {"driver_fallback", "hybrid"}


def enrich_match_result(job: Dict, result, profile, track: str = ""):
    path = driver_path(job)
    if path == "none":
        return result
    if not getattr(profile, "has_category_b_license", True):
        result.warnings.append("Category B is not enabled in the profile")
        result.score = min(result.score, 45)
        return result
    b_required = requires_category_b(job)
    location = normalize_text(str((job.get("location") or {}).get("display_name", "") or ""))
    local = any(x in location for x in ("timisoara", "timișoara", "timis", "romania"))
    bonus = 6 if b_required else 3
    if path == "hybrid":
        result.reasons.append("🚗 Category B + field/logistics work — useful bridge into operations")
        result.apply_signals.append("Category B is directly useful for this role")
        result.track = "🚗 Hybrid / Field fallback"
        result.score = min(78, result.score + bonus + 1)
    else:
        result.reasons.append("🚗 Category B — eligible temporary income-bridge option")
        result.apply_signals.append("Category B makes this a practical fallback role")
        result.apply_risks.append("Temporary/income-bridge role — not the primary career target")
        result.track = "🚗 Driver Category B fallback"
        result.score = min(68, max(result.score + bonus, 52 if local else 45))
    result.adjustments.append(("Category B driving path", bonus))
    return result


def configure_search_presets(presets: Dict[str, list]) -> None:
    """Inject one driver query into the first six queries actually searched."""
    for key in ("🔥 Full Career Scan (recommended)", "🏭 Logistics & Production"):
        if key not in presets:
            continue
        existing = [q for q in presets[key] if q not in {"sofer categoria B", "driver category B", "livrator distributie"}]
        # Preserve the most important professional queries, then add the
        # fallback query inside MAX_QUERIES so it is not silently truncated.
        if len(existing) >= 6:
            existing = existing[:5]
        existing.append("sofer categoria B")
        presets[key] = existing
