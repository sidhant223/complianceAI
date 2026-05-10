import re


CRITICALITY_SIGNALS = {
    "personal_data": [
        "personal data",
        "personal information",
        "personally identifiable information",
        "pii",
        "customer data",
        "employee data",
        "user data",
        "data principal",
        "data subject"
    ],

    "children_data": [
        "children",
        "child",
        "minor",
        "parental consent",
        "verifiable parental consent"
    ],

    "third_party_processing": [
        "third party",
        "third-party",
        "vendor",
        "service provider",
        "processor",
        "data processor",
        "outsourcing",
        "sub-processor",
        "subprocessor",
        "partner",
        "business partner",
        "external party",
        "data processing agreement",
        "dpa"
    ],

    "breach_notification": [
        "breach",
        "data breach",
        "personal data breach",
        "incident notification",
        "notify affected users",
        "notify users",
        "data protection board",
        "security incident",
        "incident response"
    ],

    "consent_management": [
        "consent",
        "withdraw consent",
        "consent manager",
        "permission",
        "opt-in",
        "opt out",
        "lawful consent"
    ],

    "data_retention": [
        "retention",
        "retain",
        "delete",
        "deletion",
        "erasure",
        "storage period",
        "purge",
        "archive",
        "archival",
        "data lifecycle",
        "lifecycle",
        "maintenance",
        "years of inactivity",
        "months of inactivity",
        "retention period"
    ],

    "security_controls": [
        "encryption",
        "access control",
        "authentication",
        "authorization",
        "logging",
        "monitoring",
        "security safeguards",
        "aes-256",
        "aes 256",
        "hsm",
        "hardware security module",
        "pci-dss",
        "pci dss",
        "at rest",
        "in transit",
        "multi-factor authentication",
        "mfa",
        "role-based access",
        "rbac",
        "firewall",
        "tokenization",
        "hashing",
        "key management"
    ],

    "regulatory_obligation": [
        "dpdp",
        "data protection",
        "compliance",
        "regulatory",
        "lawful purpose",
        "data fiduciary",
        "data principal",
        "gdpr",
        "article",
        "privacy law",
        "legal obligation",
        "statutory obligation"
    ],

    "sensitive_data": [
        "financial data",
        "health data",
        "identity data",
        "aadhaar",
        "payment data",
        "bank account",
        "password",
        "biometric",
        "cardholder data",
        "medical data",
        "government id",
        "passport",
        "pan number"
    ],

    "vendor_access": [
        "vendor access",
        "third party access",
        "third-party access",
        "external access",
        "contractor access",
        "service provider access",
        "partner access",
        "sub-processor",
        "subprocessor",
        "dpa",
        "data processing agreement",
        "contractor",
        "security assessment",
        "vendor assessment",
        "supplier assessment",
        "due diligence",
        "audit rights"
    ]
}


HEADER_CONTEXT_MAP = {
    "data_retention": [
        "data lifecycle",
        "retention",
        "storage",
        "deletion",
        "purge",
        "archive",
        "records management"
    ],

    "security_controls": [
        "security",
        "technical safeguards",
        "encryption",
        "access control",
        "information security",
        "cybersecurity"
    ],

    "vendor_access": [
        "third party",
        "third-party",
        "vendor",
        "processor",
        "supplier",
        "partner",
        "contractor",
        "outsourcing"
    ],

    "regulatory_obligation": [
        "compliance",
        "regulatory",
        "dpdp",
        "gdpr",
        "legal",
        "privacy law"
    ]
}


REGEX_PATTERNS = {
    "data_retention": [
        r"\b\d+\s*(day|days|week|weeks|month|months|year|years)\b.{0,80}\b(retention|retain|storage|store|purge|delete|deletion|archive|inactivity)\b",
        r"\b(retention|retain|storage|store|purge|delete|deletion|archive|inactivity)\b.{0,80}\b\d+\s*(day|days|week|weeks|month|months|year|years)\b"
    ],

    "security_controls": [
        r"\bAES[-\s]?256\b",
        r"\bHSM\b",
        r"\bPCI[-\s]?DSS\b",
        r"\bencryption\s+(at rest|in transit)\b",
        r"\b(at rest|in transit)\b",
        r"\bMFA\b",
        r"\bRBAC\b"
    ],

    "vendor_access": [
        r"\bDPA\b",
        r"\bdata processing agreement\b",
        r"\bsecurity assessment\b",
        r"\bvendor assessment\b",
        r"\bdue diligence\b",
        r"\baudit rights\b"
    ]
}


REGULATORY_CONTEXT_TERMS = [
    "gdpr",
    "article",
    "dpdp",
    "data protection",
    "regulatory",
    "privacy law"
]


def detect_criticality_signals(pages: list[dict]) -> dict:
    """
    Detects criticality signals from extracted PDF text.

    Improvements:
    1. Expanded keyword lexicon.
    2. Header-aware scanning.
    3. Numerical pattern matching.
    4. Regulatory context booster.
    """

    results = initialize_results()

    for page in pages:
        page_number = page["page"]
        text = page["text"]
        lower_text = text.lower()

        run_keyword_detection(results, page_number, text, lower_text)
        run_regex_detection(results, page_number, text)
        run_header_aware_detection(results, page_number, text)
        run_regulatory_context_booster(results, page_number, text, lower_text)

    return results


def initialize_results() -> dict:
    results = {}

    for signal_name in CRITICALITY_SIGNALS:
        results[signal_name] = {
            "found": False,
            "matched_keywords": [],
            "evidence": []
        }

    return results


def run_keyword_detection(results: dict, page_number: int, text: str, lower_text: str):
    for signal_name, keywords in CRITICALITY_SIGNALS.items():
        for keyword in keywords:
            if keyword.lower() in lower_text:
                add_match(
                    results=results,
                    signal_name=signal_name,
                    page_number=page_number,
                    keyword=keyword,
                    snippet=get_evidence_snippet(text, keyword),
                    match_type="keyword"
                )


def run_regex_detection(results: dict, page_number: int, text: str):
    for signal_name, patterns in REGEX_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text, flags=re.IGNORECASE)

            for match in matches:
                matched_text = match.group(0)

                add_match(
                    results=results,
                    signal_name=signal_name,
                    page_number=page_number,
                    keyword=matched_text,
                    snippet=clean_snippet(matched_text),
                    match_type="regex"
                )


def run_header_aware_detection(results: dict, page_number: int, text: str):
    """
    Detects section headers and boosts nearby paragraphs.

    Example:
    Section 5: Data Lifecycle
    Personal data will be deleted after 7 years of inactivity.

    Even if the paragraph does not say 'retention', the header gives context.
    """

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for index, line in enumerate(lines):
        lower_line = line.lower()

        if not looks_like_header(line):
            continue

        for signal_name, header_terms in HEADER_CONTEXT_MAP.items():
            if any(term in lower_line for term in header_terms):
                nearby_text = " ".join(lines[index:index + 4])

                add_match(
                    results=results,
                    signal_name=signal_name,
                    page_number=page_number,
                    keyword=line,
                    snippet=clean_snippet(nearby_text),
                    match_type="header_context"
                )


def run_regulatory_context_booster(results: dict, page_number: int, text: str, lower_text: str):
    """
    If regulatory context is present, run deeper security scan.
    This catches cases where policies mention GDPR/Article/DPDP along with technical controls.
    """

    has_regulatory_context = any(term in lower_text for term in REGULATORY_CONTEXT_TERMS)

    if not has_regulatory_context:
        return

    add_match(
        results=results,
        signal_name="regulatory_obligation",
        page_number=page_number,
        keyword="regulatory context",
        snippet=get_best_regulatory_snippet(text),
        match_type="context_booster"
    )

    security_booster_terms = [
        "aes-256",
        "aes 256",
        "hsm",
        "encryption",
        "at rest",
        "in transit",
        "pci-dss",
        "pci dss",
        "access control",
        "mfa",
        "rbac"
    ]

    for term in security_booster_terms:
        if term in lower_text:
            add_match(
                results=results,
                signal_name="security_controls",
                page_number=page_number,
                keyword=term,
                snippet=get_evidence_snippet(text, term),
                match_type="regulatory_security_booster"
            )


def looks_like_header(line: str) -> bool:
    """
    Basic header detection.
    Looks for section-like short lines.
    """

    lower_line = line.lower()

    if len(line) > 120:
        return False

    header_patterns = [
        r"^section\s+\d+",
        r"^\d+(\.\d+)*\s+",
        r"^[A-Z][A-Za-z\s\-:]{3,80}$"
    ]

    if any(re.search(pattern, line) for pattern in header_patterns):
        return True

    header_words = [
        "policy",
        "scope",
        "data lifecycle",
        "retention",
        "security",
        "vendor",
        "third party",
        "compliance",
        "deletion",
        "access control"
    ]

    return any(word in lower_line for word in header_words)


def add_match(
    results: dict,
    signal_name: str,
    page_number: int,
    keyword: str,
    snippet: str,
    match_type: str
):
    results[signal_name]["found"] = True

    if keyword not in results[signal_name]["matched_keywords"]:
        results[signal_name]["matched_keywords"].append(keyword)

    evidence_item = {
        "page": page_number,
        "keyword": keyword,
        "match_type": match_type,
        "snippet": snippet
    }

    if evidence_item not in results[signal_name]["evidence"]:
        results[signal_name]["evidence"].append(evidence_item)


def get_evidence_snippet(text: str, keyword: str, window: int = 120) -> str:
    lower_text = text.lower()
    lower_keyword = keyword.lower()

    index = lower_text.find(lower_keyword)

    if index == -1:
        return ""

    start = max(index - window, 0)
    end = min(index + len(keyword) + window, len(text))

    return clean_snippet(text[start:end])


def get_best_regulatory_snippet(text: str) -> str:
    for term in REGULATORY_CONTEXT_TERMS:
        snippet = get_evidence_snippet(text, term)
        if snippet:
            return snippet

    return clean_snippet(text[:250])


def clean_snippet(snippet: str) -> str:
    return " ".join(snippet.replace("\n", " ").split())