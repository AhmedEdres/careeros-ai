"""Role-family and transferability guardrails for CareerOS."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
import re
from .text import clean_html_text, contains_any, normalize_text

@dataclass(frozen=True)
class RoleAssessment:
    family: str
    confidence: str
    sales_score: int = 0
    operations_score: int = 0
    finance_score: int = 0
    support_score: int = 0
    legal_score: int = 0
    hr_score: int = 0
    marketing_score: int = 0
    it_score: int = 0
    transferability: str = "adjacent"
    reasons: Tuple[str, ...] = ()

SALES_STRONG = ("quota", "commission", "sales target", "revenue target", "prospecting", "cold calling", "cold call", "outbound sales", "lead generation", "pipeline management", "closing deals", "close deals", "hunter role", "new business", "business development", "sales development")
SALES_SUPPORT = ("upsell", "cross sell", "cross-sell", "upselling", "cross-selling", "sales pipeline", "salesforce", "crm sales", "book of business", "revenue growth", "commercial target", "sales targets", "account executive")
OPS_SIGNALS = ("order management", "order processing", "case management", "back office", "account administration", "account operations", "client operations", "customer operations", "service delivery", "customer support", "customer service", "client service", "client support", "customer care", "billing", "invoicing", "invoice processing", "claims processing", "data entry", "shared services", "workflow", "process improvement", "operational reporting", "administrative support", "account servicing")
FINANCE_SIGNALS = ("tax", "taxation", "compliance", "aml", "kyc", "audit", "accounting", "accounts payable", "accounts receivable", "general ledger", "reconciliation", "financial reporting", "regulatory reporting", "due diligence", "sanctions", "credit control", "collections", "debt recovery", "treasury")
SUPPORT_SIGNALS = ("customer support", "customer service", "customer care", "client support", "help desk", "service desk", "contact center", "call centre", "bpo", "technical support", "case management", "ticketing")
LEGAL_SIGNALS = ("legal assistant", "legal counsel", "paralegal", "jurist", "legal operations", "contract administration", "contract administrator", "legal compliance")
HR_SIGNALS = ("recruitment", "recruiter", "talent acquisition", "human resources", "hr business partner", "people partner", "employee relations", "payroll hr")
MARKETING_SIGNALS = ("digital marketing", "performance marketing", "brand management", "campaign", "content marketing", "seo", "sem", "social media marketing", "marketing strategy")

# These are deliberately high-signal IT/engineering indicators. Generic words
# such as "system", "platform", "data", "technology" or "project" are NOT
# enough on their own, because they occur in ordinary operations/compliance ads.
IT_STRONG = (
    "cloud engineer", "cloud platform engineer", "azure engineer", "aws engineer",
    "devops engineer", "site reliability engineer", "sre engineer", "software engineer",
    "backend engineer", "frontend engineer", "full stack engineer", "data engineer",
    "machine learning engineer", "network engineer", "security engineer",
    "cyber security", "cybersecurity", "cloud architect", "solutions architect",
    "technical architect", "platform engineer", "systems engineer", "it engineer",
    "database administrator", "database engineer", "software developer", "developer",
    "programmer", "infrastructure engineer", "terraform", "kubernetes", "docker",
    "azure", "aws", "gcp", "python developer", "java developer", "c# developer",
)
IT_TITLE = (
    "it governance", "it coordinator", "it locations", "it infrastructure", "it service", "it operations", "information security", "infosec", "quality coordinator emea - tires",
    "cloud engineer", "cloud platform", "devops", "site reliability", "software engineer",
    "software developer", "data engineer", "network engineer", "security engineer",
    "cyber security", "cybersecurity", "platform engineer", "systems engineer",
    "it engineer", "database administrator", "database engineer", "developer",
    "programmer", "infrastructure engineer", "azure cloud", "aws cloud",
)

_IT_GOVERNANCE_TITLE_RE = re.compile(r"\bit\b.+\b(governance|infrastructure|service|operations|coordinator|asset|locations?)\b", re.IGNORECASE)

def _job_parts(job: Dict) -> Tuple[str, str]:
    title = normalize_text(str(job.get("title", "") or ""))
    desc = normalize_text(clean_html_text(job.get("description", "")))
    return title, desc

def _hits(text: str, signals: Tuple[str, ...]) -> List[str]:
    return [s for s in signals if s in text]

def assess_role(job: Dict) -> RoleAssessment:
    title, desc = _job_parts(job)
    body = f"{title} {desc}"
    sales_strong = _hits(body, SALES_STRONG)
    sales_support = _hits(body, SALES_SUPPORT)
    ops = _hits(body, OPS_SIGNALS)
    finance = _hits(body, FINANCE_SIGNALS)
    support = _hits(body, SUPPORT_SIGNALS)
    legal = _hits(body, LEGAL_SIGNALS)
    hr = _hits(body, HR_SIGNALS)
    marketing = _hits(body, MARKETING_SIGNALS)
    it_strong = _hits(body, IT_STRONG)
    it_title = contains_any(title, IT_TITLE) or bool(_IT_GOVERNANCE_TITLE_RE.search(title))
    sales = len(sales_strong) * 4 + len(sales_support) * 2
    operations = len(ops) * 3
    finance_score = len(finance) * 3
    support_score = len(support) * 3
    legal_score = len(legal) * 4
    hr_score = len(hr) * 4
    marketing_score = len(marketing) * 4
    it_score = len(it_strong) * 5 + (12 if it_title else 0)

    # Critical ordering: classify specialist IT roles before generic operations
    # signals. This prevents "support", "operations", "project" and "reporting"
    # words in an engineering description from inflating the candidate match.
    if it_title:
        return RoleAssessment("it_engineering", "high", sales_score=sales, operations_score=operations, finance_score=finance_score, support_score=support_score, legal_score=legal_score, hr_score=hr_score, marketing_score=marketing_score, it_score=it_score, transferability="low", reasons=(f"IT/engineering signals: {', '.join(it_strong[:5])}",))

    title_sales = contains_any(title, ["sales manager", "sales director", "head of sales", "account executive", "business development", "sdr", "bdr", "sales representative", "sales executive", "revenue manager", "revenue director", "chief revenue officer", "cro manager"])
    title_account = contains_any(title, ["account manager", "client manager", "customer success manager"])
    title_accounting = contains_any(title, ["accountant", "accounting specialist", "bookkeeper", "accounts payable", "accounts receivable", "general ledger"])
    if title_sales or sales_strong or sales >= max(6, operations + 2):
        return RoleAssessment("sales_revenue", "high", sales_score=sales, operations_score=operations, finance_score=finance_score, support_score=support_score, legal_score=legal_score, hr_score=hr_score, marketing_score=marketing_score, it_score=it_score, transferability="low", reasons=(f"sales signals: {', '.join((sales_strong + sales_support)[:4])}",))
    if title_account:
        if operations >= 6 or support_score >= 6:
            return RoleAssessment("client_operations", "high", sales_score=sales, operations_score=operations, support_score=support_score, finance_score=finance_score, it_score=it_score, transferability="transferable", reasons=("account/client title supported by operations or service evidence",))
        return RoleAssessment("ambiguous_account", "medium", sales_score=sales, operations_score=operations, support_score=support_score, finance_score=finance_score, it_score=it_score, transferability="adjacent", reasons=("account/client title lacks enough operational evidence to rule out sales",))
    if title_accounting:
        return RoleAssessment("accounting", "high", sales_score=sales, operations_score=operations, finance_score=finance_score, it_score=it_score, transferability="adjacent", reasons=("accounting function detected; profile evidence is stronger in tax/compliance than accounting",))
    scores = {"finance_compliance": finance_score, "operations": operations, "customer_support": support_score, "legal": legal_score, "hr": hr_score, "marketing": marketing_score}
    family, best = max(scores.items(), key=lambda item: item[1])
    if best == 0:
        return RoleAssessment("general", "low", it_score=it_score, transferability="unknown")
    transfer = "transferable" if family in {"finance_compliance", "operations", "customer_support", "legal"} else "low"
    return RoleAssessment(family, "medium", sales_score=sales, operations_score=operations, finance_score=finance_score, support_score=support_score, legal_score=legal_score, hr_score=hr_score, marketing_score=marketing_score, it_score=it_score, transferability=transfer, reasons=(f"{family.replace('_', ' ')} signals: {best}",))

def _candidate_directness(profile, role: RoleAssessment) -> str:
    skills = {normalize_text(s) for s in (profile.skills or [])}
    highlights = normalize_text(" ".join(profile.highlights or []))
    if role.family == "finance_compliance" and any(x in highlights for x in ("tax authority", "tax", "compliance", "aml", "kyc")):
        return "direct"
    if role.family == "operations" and any(x in highlights for x in ("operations", "production operator", "client", "account")):
        return "direct"
    if role.family == "customer_support" and any(x in skills for x in ("customer support", "customer service", "client management")):
        return "transferable"
    if role.family == "client_operations" and any(x in skills for x in ("client management", "operations", "customer service")):
        return "transferable"
    if role.family == "accounting":
        return "adjacent"
    return role.transferability

def apply_role_intelligence(job: Dict, profile, result, blend_scores) -> object:
    role = assess_role(job)
    directness = _candidate_directness(profile, role)
    if role.family == "it_engineering":
        result.reject_reason = "Specialist IT/engineering role detected — core technical requirements are not supported by the documented profile"
        result.warnings.insert(0, "🔴 Specialist IT/engineering function — outside the supported career profile")
        result.hiring_risks.insert(0, "🚫 Core engineering/cloud/software requirements are not evidenced in the profile")
        result.score = min(result.score, 15)
        result.match_score = min(result.match_score, 15)
        result.eligibility_score = min(result.eligibility_score, 35)
        result.hiring_score = min(result.hiring_score, 25)
        result.verdict_label, result.verdict = "🔴 SKIP", "skip"
        result.adjustments.append(("Specialist IT/engineering hard mismatch", -50))
        return result
    if role.family == "sales_revenue":
        result.reject_reason = "Sales/revenue function detected — outside the selected career families"
        result.warnings.insert(0, "🔴 Sales/revenue function — not a target career family")
        result.hiring_risks.insert(0, "🚫 Commercial targets/prospecting/closing indicate a sales role")
        result.score = min(result.score, 35)
        result.match_score = min(result.match_score, 35)
        result.hiring_score = min(result.hiring_score, 35)
        result.verdict_label, result.verdict = "🔴 SKIP", "skip"
        return result
    if role.family in {"hr", "marketing"}:
        result.reject_reason = f"{role.family.replace('_', ' ').title()} function detected"
        result.warnings.insert(0, "🔴 Different career family — not a target function")
        result.score = min(result.score, 35)
        result.verdict_label, result.verdict = "🔴 SKIP", "skip"
        return result
    if role.family == "ambiguous_account":
        penalty = 10
        result.match_score = max(0, result.match_score - penalty)
        result.hiring_score = max(0, result.hiring_score - 8)
        result.score = blend_scores(result.match_score, result.eligibility_score, result.hiring_score)
        result.warnings.insert(0, "🟠 Account/client role is ambiguous — verify it is operations/support, not sales")
        result.hiring_risks.insert(0, "⚠️ No clear operational evidence in the description")
        result.adjustments.append(("Ambiguous account-management function", -penalty))
        return result
    if role.family == "accounting" and directness == "adjacent":
        penalty = 8
        result.match_score = max(0, result.match_score - penalty)
        result.hiring_score = max(0, result.hiring_score - 6)
        result.score = blend_scores(result.match_score, result.eligibility_score, result.hiring_score)
        result.warnings.insert(0, "🟠 Accounting is adjacent to your documented tax/compliance experience")
        result.hiring_risks.insert(0, "⚠️ Job asks for accounting-specific experience; tax/compliance is not the same function")
        result.adjustments.append(("Accounting directness gap", -penalty))
    if directness == "transferable":
        result.reasons.append("🔄 Career function is transferable from your documented skills")
    elif directness == "direct":
        result.reasons.append("🎯 Career function is directly supported by your documented experience")
    return result

def wrap_matching(original_hard_filter, original_calculate_match, blend_scores):
    def hard_filter(job, profile, track=""):
        keep, reason = original_hard_filter(job, profile, track)
        if not keep:
            return keep, reason
        role = assess_role(job)
        if role.family in {"sales_revenue", "hr", "marketing", "it_engineering"}:
            label = role.family.replace("_", " ").title()
            return False, f"🔴 Different career track ({label})"
        return True, ""
    def calculate_match(job, profile, track=""):
        result = original_calculate_match(job, profile, track)
        return apply_role_intelligence(job, profile, result, blend_scores)
    return hard_filter, calculate_match
