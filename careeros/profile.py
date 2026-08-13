"""Candidate profile model and the keyword taxonomy used for scoring."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List

__all__ = [
    "Profile", "DEFAULT_PROFILE", "SKILL_GROUPS", "NEGATIVE_TITLES",
    "LOCATION_SYNONYMS", "ROMANIAN_REJECT", "ROMANIAN_RISKY",
    "ROMANIAN_FRIENDLY", "ENGLISH_ABOVE_B2", "REMOTE_FRIENDLY",
    "REMOTE_RESTRICTED", "SENIORITY_PATTERNS", "CEFR_ORDER",
]

CEFR_ORDER = ["None", "A1", "A2", "B1", "B2", "C1", "C2", "Native"]

@dataclass
class Profile:
    name: str = "Ahmed"
    location: str = "Timisoara"
    country: str = "Romania"
    romanian_level: str = "A1"
    english_level: str = "B2"
    arabic_level: str = "Native"
    education: str = "Master's Degree in Law"
    experience_years: int = 10
    target_salary_min: int = 5000
    target_salary_max: int = 7000
    open_to_remote: bool = True
    open_to_relocation: bool = False
    other_languages: List[str] = field(default_factory=lambda: [
        "french", "german", "dutch", "italian", "spanish", "portuguese",
        "polish", "czech", "hungarian", "greek", "turkish", "russian",
        "swedish", "norwegian", "danish", "finnish", "hebrew", "chinese",
        "japanese", "korean", "bulgarian", "serbian", "croatian", "ukrainian",
    ])
    skills: List[str] = field(default_factory=lambda: [
        "operations", "client management", "financial compliance",
        "customer service", "customer support", "excel", "sap", "erp", "sql",
        "administration", "logistics", "arabic", "english", "tax", "banking",
        "accounting", "collections", "category b driving", "driving license b",
    ])
    preferred_locations: List[str] = field(default_factory=lambda: ["Timisoara", "Romania", "Remote"])
    highlights: List[str] = field(default_factory=lambda: [
        "Managed 250+ corporate accounts at the Egyptian Tax Authority (10 years)",
        "Currently production operator at Techplast RO, Timisoara — seeking career transition",
        "Tools: SAP, Excel/VBA, IBM Cognos, Power BI, SQL",
        "Romanian driving licence — Category B; open to temporary driver/delivery work",
    ])

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Profile":
        known = {f for f in cls().to_dict()}
        return cls(**{k: v for k, v in (data or {}).items() if k in known})

    @property
    def romanian_rank(self) -> int:
        try: return CEFR_ORDER.index(self.romanian_level)
        except ValueError: return 1

    @property
    def english_rank(self) -> int:
        try: return CEFR_ORDER.index(self.english_level)
        except ValueError: return 4

DEFAULT_PROFILE = Profile()

SKILL_GROUPS: Dict[str, Dict] = {
    "operations_support": {"label": "Operations / Customer Support", "weight": 14, "words": [
        "operations", "operational", "coordinator", "administrator", "administration", "back office", "backoffice", "front office",
        "customer support", "customer service", "customer care", "client service", "client support", "client management",
        "account management", "call center", "call centre", "contact center", "contact centre", "help desk", "helpdesk",
        "service desk", "support specialist", "support agent", "support representative", "customer success", "customer experience",
        "bpo", "business process outsourcing", "shared services", "shared service", "order management", "order processing", "data entry",
        "case management", "service delivery", "relatii clienti", "suport clienti",
    ]},
    "finance_compliance": {"label": "Finance / Compliance / Legal", "weight": 18, "words": [
        "finance", "financial", "accounting", "accountant", "contabil", "accounts payable", "accounts receivable", "bookkeeping",
        "general ledger", "reconciliation", "tax", "taxation", "fiscal", "compliance", "regulatory", "invoice", "invoicing", "billing",
        "legal", "juridic", "audit", "auditor", "auditing", "banking", "collections", "debt recovery", "treasury", "credit control",
        "risk", "aml", "anti money laundering", "kyc", "know your customer", "due diligence", "sanctions", "financial analyst",
        "financial controller", "controlling", "o2c", "order to cash", "p2p", "procure to pay", "r2r", "record to report", "payroll",
    ]},
    "logistics": {"label": "Logistics / Supply Chain", "weight": 10, "words": [
        "logistics", "warehouse", "depot", "supply chain", "inventory", "transport", "transportation", "purchasing", "procurement",
        "shipping", "freight", "forwarding", "distribution", "fulfillment", "fulfilment", "customs", "import", "export",
        "logistics coordinator", "warehouse coordinator", "supply chain coordinator", "material planner",
    ]},
    "production": {"label": "Production / Manufacturing", "weight": 10, "words": [
        "production", "manufacturing", "assembly", "assembler", "production operator", "machine operator", "process operator",
        "quality control", "quality assurance", "quality inspector", "injection", "molding", "moulding", "plastics", "extrusion",
        "shift leader", "production planner", "operator productie", "productie", "fabricatie", "linia de productie", "warehouse operator",
        "stivuitor", "cnc operator", "production technician", "process technician",
    ]},
    "driving": {"label": "Driving / Category B", "weight": 14, "words": [
        "driver", "delivery driver", "courier driver", "van driver", "car driver", "category b", "category b licence", "category b license",
        "driving licence b", "driving license b", "driving license", "driver license", "driver's license", "sofer categoria b",
        "șofer categoria b", "sofer b", "șofer b", "șofer", "curier", "livrator", "delivery", "courier", "distributie",
        "distribuție", "livrare",
    ]},
    "tools": {"label": "Tools (SAP / ERP / Excel / SQL)", "weight": 8, "words": [
        "sap", "erp", "excel", "microsoft excel", "sql", "vba", "ibm cognos", "power bi", "oracle", "navision", "dynamics",
        "salesforce", "servicenow", "zendesk", "jira", "sharepoint",
    ]},
    "languages_market": {"label": "Multilingual / MENA market", "weight": 6, "words": [
        "arabic", "multilingual", "bilingual", "middle east", "mena", "gulf", "gcc", "uae", "saudi", "egypt", "levant",
    ]},
}

NEGATIVE_TITLES = [
    "software developer", "software engineer", "senior developer", "senior engineer", "lead developer", "staff engineer",
    "principal engineer", "machine learning engineer", "data scientist", "head of engineering", "engineering manager", "engineering lead",
    "engineering director", "director of engineering", "software engineering manager", "software team lead", "vp of engineering",
    "vp engineering", "vice president of engineering", "head of software", "software architect", "cto", "chief technology officer",
    "chief technical officer", "head of product", "product manager", "product owner", "product management", "chief product officer",
    "vp of product", "vp product", "devops", "sre", "site reliability", "full stack developer", "fullstack developer",
    "frontend developer", "front end developer", "backend developer", "back end developer", "react developer", "java developer",
    "python developer", "php developer", "c developer", "golang developer", "rust developer", "ios developer", "android developer",
    "mobile developer", "qa automation", "test automation engineer", "embedded engineer", "cloud architect", "ux designer", "ui designer",
    "graphic designer", "3d artist", "medical doctor", "nurse", "asistent medical", "dentist", "pharmacist", "truck driver",
    # IMPORTANT: ordinary Category-B driver titles are intentionally NOT here.
    "construction worker", "electrician", "plumber", "mechanic", "welder", "sudor", "lacatus", "operator cnc", "cnc operator",
    "chef", "bucatar", "waiter", "ospatar", "barista", "security guard", "agent de securitate", "cleaner", "femeie de serviciu",
    "chief revenue officer", "cro manager", "cro director", "revenue manager", "revenue director", "revenue operations manager",
    "revenue operations director", "sales director", "sales manager", "head of sales", "vp of sales", "vice president of sales",
    "chief sales officer", "sales executive", "account executive", "sales development representative", "sales representative",
    "business development representative", "business development manager", "business development director", "sdr", "bdr", "marketing manager",
    "marketing director", "head of marketing", "vp of marketing", "chief marketing officer", "digital marketing", "performance marketing",
    "brand manager", "growth manager", "growth director", "content manager", "recruiter", "talent acquisition", "hr manager",
    "hr business partner", "human resources manager", "head of hr", "people partner", "people operations manager",
    "ai compliance officer", "ai compliance specialist", "ai compliance analyst", "ai governance officer", "ai governance specialist",
    "ai governance analyst", "responsible ai", "model governance", "algorithmic governance", "senior regulatory and sustainability compliance specialist",
    "regulatory and sustainability compliance", "sustainability compliance", "sustainability specialist", "sustainability manager", "esg specialist",
    "esg manager", "environmental compliance", "environmental specialist", "environmental manager", "ehs manager", "hse manager",
    "trademark paralegal", "senior trademark paralegal", "trademark specialist", "trademark counsel", "intellectual property paralegal",
    "ip paralegal", "intellectual property specialist", "patent paralegal", "patent specialist", "senior regional it locations coordinator",
    "regional it locations coordinator", "it locations coordinator", "it locations", "it asset coordinator", "it asset manager",
    "it infrastructure coordinator", "it infrastructure manager", "it service manager", "it service management", "it operations manager",
    "technical operations manager", "it regional coordinator", "regional operations manager", "plant operations manager",
    "manufacturing operations manager", "warehouse operations manager", "supply chain operations manager", "production operations manager",
]

LOCATION_SYNONYMS: Dict[str, List[str]] = {
    "Timișoara": ["timisoara", "temesvar", "temeschburg", "timis", "dumbravita", "giroc"],
    "Romania": ["romania", "bucharest", "bucuresti", "cluj", "cluj napoca", "iasi", "brasov", "timisoara", "constanta", "sibiu", "oradea", "arad", "craiova", "ploiesti", "galati", "pitesti", "targu mures"],
    "Remote": ["remote", "work from home", "wfh", "telemunca", "anywhere", "hybrid"],
    "Europe": ["europe", "europa", "european union", "eu", "eea", "emea", "cet", "germany", "deutschland", "france", "spain", "italy", "netherlands", "poland", "polska", "czech", "czechia", "austria", "belgium", "portugal", "ireland", "sweden", "denmark", "finland", "norway", "switzerland", "hungary", "croatia", "greece", "bulgaria", "slovakia", "slovenia", "lithuania", "latvia", "estonia"],
}

ROMANIAN_REJECT = ["romanian c1", "romanian c2", "romana c1", "romana c2", "fluent romanian", "romanian fluent", "fluent in romanian", "native romanian", "romanian native", "limba romana nivel avansat", "romana avansat", "romanian mandatory", "romanian is mandatory", "excellent romanian", "very good romanian"]
ROMANIAN_RISKY = ["romanian b2", "romana b2", "romanian required", "romanian language required", "limba romana", "limba română", "romanian speaking", "good knowledge of romanian", "advanced romanian", "cunoasterea limbii romane"]
ROMANIAN_FRIENDLY = ["romanian a1", "romanian a2", "romana a1", "romana a2", "basic romanian", "romanian optional", "romanian is a plus", "romanian preferred", "romanian beginner"]
ENGLISH_ABOVE_B2 = ["english c1", "english c2", "fluent english", "native english", "native-level english", "english at c1", "english at c2", "proficient english"]
REMOTE_FRIENDLY = ["remote — europe", "remote europe", "remote - europe", "remote — eu", "remote eu", "remote - eu", "remote — romania", "remote romania", "remote - romania", "remote — eea", "remote eea", "remote — emea", "remote emea", "remote — cet", "remote cet", "worldwide", "global", "anywhere"]
REMOTE_RESTRICTED = ["us only", "usa only", "united states only", "us residents", "us-based", "us based", "canada only", "uk only", "uk residents", "india only", "australia only", "must be located in the us", "must be based in the us"]
SENIORITY_PATTERNS = ["senior", "lead", "manager", "director", "head of"]
