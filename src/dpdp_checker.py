import re


NEGATIVE_PHRASES = [
    "no evidence",
    "no clear evidence",
    "not implemented",
    "not defined",
    "not mentioned",
    "not available",
    "not documented",
    "does not mention",
    "does not define",
    "does not include",
    "does not provide",
    "does not currently",
    "does not guarantee",
    "cannot guarantee",
    "not guaranteed",
    "lacks",
    "lack of",
    "missing",
    "failed",
    "fails to",
    "failure to",
    "non-compliant",
    "non compliant",
    "inadequate",
    "insufficient",
    "unclear",
    "absent",
    "no formal",
    "no documented",
    "not required",
    "not enforced"
]

DPDP_CONTROL_REQUIREMENTS = {
    "notice_and_transparency": "The document should clearly mention privacy notice, what personal data is collected, why it is processed, and how the data principal is informed.",
    "consent_management": "The document should explain how consent is collected, recorded, and used for processing personal data.",
    "withdrawal_of_consent": "The document should explain how a data principal can withdraw consent and how withdrawal requests are handled.",
    "data_principal_rights": "The document should mention data principal rights such as access, correction, erasure, grievance redressal, and request handling.",
    "correction_and_erasure": "The document should explain how personal data can be corrected, updated, erased, or deleted.",
    "grievance_redressal": "The document should define a grievance or complaint handling mechanism, including contact or escalation process.",
    "data_retention": "The document should define how long personal data or records are retained and when they are deleted, purged, archived, or returned.",
    "security_safeguards": "The document should mention technical or organizational safeguards such as encryption, access control, authentication, monitoring, or security controls.",
    "breach_notification": "The document should define breach or security incident reporting, notification timelines, escalation, and responsible parties.",
    "children_data": "The document should mention special handling of children's or minors' personal data and parental consent where applicable.",
    "third_party_processing": "The document should define third-party, vendor, processor, or service provider obligations for handling personal data."
}

DPDP_CANDIDATE_KEYWORDS = {
    "notice_and_transparency": [
        "privacy notice", "personal data", "data collected", "purpose", "processing", "notice"
    ],
    "consent_management": [
        "consent", "permission", "authorization", "agree", "opt-in", "personal data"
    ],
    "withdrawal_of_consent": [
        "withdraw", "withdrawal", "revoke", "opt out", "opt-out", "consent"
    ],
    "data_principal_rights": [
        "rights", "access", "correction", "erasure", "grievance", "data principal", "data subject"
    ],
    "correction_and_erasure": [
        "correction", "erasure", "delete", "deletion", "rectification", "update personal data"
    ],
    "grievance_redressal": [
        "grievance", "complaint", "redressal", "escalation", "support contact", "officer"
    ],
    "data_retention": [
        "retention", "retain", "storage period", "delete", "deletion", "purge", "archive", "records"
    ],
    "security_safeguards": [
        "security", "safeguard", "encryption", "access control", "authentication", "authorization", "monitoring"
    ],
    "breach_notification": [
        "breach", "incident", "notify", "notification", "report", "unauthorized access", "data loss"
    ],
    "children_data": [
        "children", "child", "minor", "parental consent", "guardian"
    ],
    "third_party_processing": [
        "third party", "third-party", "vendor", "service provider", "processor", "contractor", "data processing agreement"
    ]
}


DPDP_CONTROLS = {
    "notice_and_transparency": {
        "title": "Notice and Transparency",
        "description": "Checks whether the policy explains what personal data is collected and why it is processed.",
        "keywords": [
            "privacy notice",
            "personal data collected",
            "purpose of processing",
            "lawful purpose",
            "processing purpose",
            "data collection",
            "how we collect",
            "how we use personal data",
            "notice to data principal",
            "notice to data subject"
        ],
        "required_context_terms": [
            "personal data",
            "privacy",
            "data principal",
            "data subject",
            "processing",
            "collected",
            "lawful purpose",
            "consent",
            "data fiduciary"
        ],
        "excluded_context_terms": [
            "table of contents",
            "general information",
            "notice to bidders",
            "bid information",
            "proposal information",
            "request for proposal",
            "rfp information",
            "project information",
            "contract information",
            "general conditions",
            "instructions to bidders"
        ]
    },

    "consent_management": {
        "title": "Consent Management",
        "description": "Checks whether the policy mentions consent collection and user permission.",
        "keywords": [
            "consent",
            "obtain consent",
            "user consent",
            "permission",
            "opt-in",
            "agree",
            "authorization"
        ],
        "required_context_terms": [
            "personal data",
            "privacy",
            "data principal",
            "data subject",
            "processing",
            "collected",
            "consent",
            "permission",
            "lawful purpose"
        ],
        "excluded_context_terms": [
            "construction permission",
            "site permission",
            "project permission",
            "permit",
            "building permit"
        ]
    },

    "withdrawal_of_consent": {
        "title": "Withdrawal of Consent",
        "description": "Checks whether users can withdraw consent.",
        "keywords": [
            "withdraw consent",
            "withdrawal of consent",
            "revoke consent",
            "opt out",
            "opt-out",
            "withdraw permission"
        ],
        "required_context_terms": [
            "personal data",
            "privacy",
            "consent",
            "data principal",
            "data subject",
            "processing"
        ]
    },

    "data_principal_rights": {
        "title": "Data Principal Rights",
        "description": "Checks whether rights of users/data principals are mentioned.",
        "keywords": [
            "data principal",
            "user rights",
            "right to access",
            "right to correction",
            "right to erasure",
            "right to grievance",
            "rights of data principal",
            "access personal data",
            "correct personal data"
        ],
        "required_context_terms": [
            "personal data",
            "data principal",
            "data subject",
            "privacy",
            "access",
            "correction",
            "erasure",
            "grievance"
        ]
    },

    "correction_and_erasure": {
        "title": "Correction and Erasure",
        "description": "Checks whether correction, deletion, or erasure of personal data is mentioned.",
        "keywords": [
            "correction",
            "correct personal data",
            "erasure",
            "erase personal data",
            "delete personal data",
            "deletion of personal data",
            "update personal data",
            "rectification"
        ],
        "required_context_terms": [
            "personal data",
            "data principal",
            "data subject",
            "privacy",
            "correction",
            "erasure",
            "deletion",
            "rectification"
        ]
    },

    "grievance_redressal": {
        "title": "Grievance Redressal",
        "description": "Checks whether complaint or grievance handling is mentioned.",
        "keywords": [
            "grievance",
            "complaint",
            "redressal",
            "grievance officer",
            "contact officer",
            "support contact",
            "escalation",
            "complaints mechanism"
        ],
        "excluded_context_terms": [
            "construction defect",
            "workmanship defect",
            "site defect",
            "quality defect"
        ]
    },

    "data_retention": {
        "title": "Data Retention",
        "description": "Checks whether retention period or deletion timeline is defined.",
        "keywords": [
            "retention",
            "retain",
            "retention period",
            "storage period",
            "delete",
            "deletion",
            "purge",
            "archive",
            "data lifecycle",
            "years of inactivity",
            "months of inactivity"
        ],
        "required_context_terms": [
            "data",
            "personal data",
            "records",
            "retention",
            "storage",
            "delete",
            "deletion",
            "purge",
            "archive",
            "lifecycle"
        ],
        "regex": [
            r"\b\d+\s*(day|days|week|weeks|month|months|year|years)\b.{0,80}\b(retention|retain|storage|store|purge|delete|deletion|archive|inactivity)\b",
            r"\b(retention|retain|storage|store|purge|delete|deletion|archive|inactivity)\b.{0,80}\b\d+\s*(day|days|week|weeks|month|months|year|years)\b"
        ]
    },

    "security_safeguards": {
        "title": "Security Safeguards",
        "description": "Checks whether technical or organizational security controls are mentioned.",
        "keywords": [
            "security safeguards",
            "reasonable security",
            "encryption",
            "access control",
            "authentication",
            "authorization",
            "logging",
            "monitoring",
            "aes-256",
            "aes 256",
            "hsm",
            "mfa",
            "rbac",
            "at rest",
            "in transit",
            "firewall",
            "tokenization"
        ],
        "required_context_terms": [
            "security",
            "data",
            "personal data",
            "confidential information",
            "encryption",
            "access control",
            "authentication",
            "authorization",
            "system",
            "network",
            "database",
            "application",
            "monitoring"
        ],
        "excluded_context_terms": [
            "physical security only",
            "site security",
            "construction site",
            "building access",
            "project area"
        ],
        "regex": [
            r"\bAES[-\s]?256\b",
            r"\bHSM\b",
            r"\bMFA\b",
            r"\bRBAC\b",
            r"\bencryption\s+(at rest|in transit)\b",
            r"\b(at rest|in transit)\b"
        ]
    },

    "breach_notification": {
        "title": "Breach Notification",
        "description": "Checks whether the policy mentions personal data breach or security incident notification.",
        "keywords": [
            "data breach",
            "personal data breach",
            "security incident",
            "incident notification",
            "breach notification",
            "privacy incident",
            "cyber incident",
            "unauthorized access",
            "data loss",
            "notify affected users",
            "notify users",
            "regulatory notification",
            "data protection board"
        ],
        "required_context_terms": [
            "breach",
            "data breach",
            "personal data",
            "security incident",
            "cyber incident",
            "privacy incident",
            "unauthorized access",
            "data loss",
            "confidential information",
            "affected users",
            "data protection board"
        ],
        "excluded_context_terms": [
            "defect",
            "defects",
            "services",
            "workmanship",
            "construction",
            "repair",
            "deliverable",
            "quality",
            "nonconforming work",
            "project area",
            "contractor shall notify",
            "notify the contractor",
            "notify contractor",
            "notice of defect"
        ]
    },

    "children_data": {
        "title": "Children's Data",
        "description": "Checks whether processing of children's data or parental consent is mentioned.",
        "keywords": [
            "children",
            "child",
            "minor",
            "minors",
            "parental consent",
            "verifiable parental consent",
            "children's personal data",
            "data from any minor",
            "do not intentionally collect data from any minor"
        ],
        "required_context_terms": [
            "children",
            "child",
            "minor",
            "minors",
            "personal data",
            "data",
            "parental consent",
            "privacy"
        ]
    },

    "third_party_processing": {
        "title": "Third Party Processing",
        "description": "Checks whether vendors, processors, or third-party sharing are mentioned.",
        "keywords": [
            "third party",
            "third-party",
            "vendor",
            "service provider",
            "data processor",
            "processor",
            "sub-processor",
            "subprocessor",
            "partner",
            "contractor",
            "data processing agreement",
            "dpa"
        ],
        "required_context_terms": [
            "third party",
            "third-party",
            "vendor",
            "service provider",
            "processor",
            "data processor",
            "personal data",
            "data",
            "processing",
            "sharing",
            "dpa"
        ],
        "excluded_context_terms": [
            "general contractor",
            "construction contractor",
            "project contractor",
            "contractor access to project area"
        ]
    }
}


def analyze_dpdp_compliance(pages: list[dict]) -> dict:
    findings = []

    for control_id, control in DPDP_CONTROLS.items():
        finding = analyze_single_control(
            control_id=control_id,
            control=control,
            pages=pages
        )
        findings.append(finding)

    summary = build_dpdp_summary(findings)

    return {
        "dpdp_overall_status": summary["overall_status"],
        "dpdp_risk_level": summary["risk_level"],
        "total_controls": len(findings),
        "compliant_count": summary["compliant_count"],
        "partial_count": summary["partial_count"],
        "missing_count": summary["missing_count"],
        "failed_count": summary["failed_count"],
        "findings": findings
    }


def analyze_single_control(control_id: str, control: dict, pages: list[dict]) -> dict:
    evidence = []
    matched_keywords = []

    keywords = control.get("keywords", [])
    regex_patterns = control.get("regex", [])

    for page in pages:
        page_number = page["page"]
        text = page["text"]
        lower_text = text.lower()

        for keyword in keywords:
            if keyword.lower() in lower_text:
                snippet = get_evidence_snippet(text, keyword)

                if not passes_context_gate(snippet, control):
                    continue

                if keyword not in matched_keywords:
                    matched_keywords.append(keyword)

                sentiment = detect_evidence_sentiment(snippet)

                evidence.append({
                    "page": page_number,
                    "keyword": keyword,
                    "match_type": "keyword",
                    "sentiment": sentiment,
                    "snippet": snippet
                })

        for pattern in regex_patterns:
            matches = re.finditer(pattern, text, flags=re.IGNORECASE)

            for match in matches:
                matched_text = match.group(0)
                snippet = expand_regex_snippet(text, match)

                if not passes_context_gate(snippet, control):
                    continue

                if matched_text not in matched_keywords:
                    matched_keywords.append(matched_text)

                sentiment = detect_evidence_sentiment(snippet)

                evidence.append({
                    "page": page_number,
                    "keyword": matched_text,
                    "match_type": "regex",
                    "sentiment": sentiment,
                    "snippet": snippet
                })

    evidence = deduplicate_evidence(evidence)

    status = determine_control_status(evidence)
    risk = determine_control_risk(control_id, status)
    recommendation = generate_recommendation(control["title"], status)

    positive_evidence_count = count_evidence_by_sentiment(evidence, "positive")
    negative_evidence_count = count_evidence_by_sentiment(evidence, "negative")
    neutral_evidence_count = count_evidence_by_sentiment(evidence, "neutral")

    candidate_evidence = get_candidate_evidence_for_control(
    pages=pages,
    control_id=control_id
)


    return {
    "control_id": control_id,
    "control_title": control["title"],
    "control": control["title"],
    "description": control["description"],
    "expected_requirement": DPDP_CONTROL_REQUIREMENTS.get(
        control_id,
        "The document should clearly address this DPDP control requirement."
    ),
    "status": status,
    "risk": risk,
    "matched_keywords": matched_keywords,
    "evidence_count": len(evidence),
    "positive_evidence_count": positive_evidence_count,
    "negative_evidence_count": negative_evidence_count,
    "neutral_evidence_count": neutral_evidence_count,
    "evidence": evidence[:10],
    "candidate_evidence": candidate_evidence,
    "recommendation": recommendation,
    "final_status": status
}


def detect_evidence_sentiment(snippet: str) -> str:
    snippet_lower = snippet.lower()

    for phrase in NEGATIVE_PHRASES:
        if phrase in snippet_lower:
            return "negative"

    return "positive"


def has_required_context(snippet: str, control: dict) -> bool:
    required_terms = control.get("required_context_terms", [])

    if not required_terms:
        return True

    snippet_lower = snippet.lower()

    return any(term.lower() in snippet_lower for term in required_terms)


def has_excluded_context(snippet: str, control: dict) -> bool:
    excluded_terms = control.get("excluded_context_terms", [])

    if not excluded_terms:
        return False

    snippet_lower = snippet.lower()

    return any(term.lower() in snippet_lower for term in excluded_terms)


def passes_context_gate(snippet: str, control: dict) -> bool:
    if has_excluded_context(snippet, control):
        return False

    if not has_required_context(snippet, control):
        return False

    return True


def deduplicate_evidence(evidence: list[dict]) -> list[dict]:
    unique_evidence = []
    seen_snippets = set()

    for item in evidence:
        snippet = item.get("snippet", "")
        normalized_snippet = normalize_snippet_for_dedup(snippet)

        if normalized_snippet in seen_snippets:
            continue

        seen_snippets.add(normalized_snippet)
        unique_evidence.append(item)

    return unique_evidence


def normalize_snippet_for_dedup(snippet: str) -> str:
    return " ".join(
        str(snippet)
        .lower()
        .replace(".", "")
        .replace(",", "")
        .replace(";", "")
        .replace(":", "")
        .replace("-", " ")
        .split()
    )


def determine_control_status(evidence: list[dict]) -> str:
    if len(evidence) == 0:
        return "Missing"

    positive_count = count_evidence_by_sentiment(evidence, "positive")
    negative_count = count_evidence_by_sentiment(evidence, "negative")

    if negative_count > 0 and positive_count == 0:
        return "Failed"

    if negative_count > 0 and positive_count > 0:
        return "Partially Compliant"

    if positive_count == 1:
        return "Partially Compliant"

    return "Present"


def determine_control_risk(control_id: str, status: str) -> str:
    high_importance_controls = {
        "consent_management",
        "withdrawal_of_consent",
        "data_principal_rights",
        "security_safeguards",
        "breach_notification",
        "third_party_processing"
    }

    if status == "Present":
        return "Low"

    if status == "Failed":
        return "High"

    if control_id in high_importance_controls:
        if status == "Missing":
            return "High"
        return "Medium"

    if status == "Missing":
        return "Medium"

    return "Low"


def generate_recommendation(control_title: str, status: str) -> str:
    if status == "Present":
        return f"{control_title} appears to be covered. Review the wording for completeness and operational clarity."

    if status == "Failed":
        return (
            f"{control_title} is referenced, but the evidence suggests the requirement is missing, failed, "
            f"or not implemented. Treat this as a high-risk audit finding and add corrective controls."
        )

    if status == "Partially Compliant":
        return f"{control_title} is mentioned but may need clearer procedures, responsibilities, timelines, or user-facing wording."

    return f"{control_title} is not clearly mentioned. Add a dedicated section covering this requirement with clear process details."


def build_dpdp_summary(findings: list[dict]) -> dict:
    compliant_count = sum(1 for finding in findings if finding["status"] == "Present")
    partial_count = sum(1 for finding in findings if finding["status"] == "Partially Compliant")
    missing_count = sum(1 for finding in findings if finding["status"] == "Missing")
    failed_count = sum(1 for finding in findings if finding["status"] == "Failed")

    if failed_count >= 1 or missing_count >= 4:
        overall_status = "Weak / Needs Major Improvement"
        risk_level = "High"
    elif missing_count >= 2 or partial_count >= 4:
        overall_status = "Partially Compliant"
        risk_level = "Medium"
    else:
        overall_status = "Mostly Covered"
        risk_level = "Low"

    return {
        "overall_status": overall_status,
        "risk_level": risk_level,
        "compliant_count": compliant_count,
        "partial_count": partial_count,
        "missing_count": missing_count,
        "failed_count": failed_count
    }


def count_evidence_by_sentiment(evidence: list[dict], sentiment: str) -> int:
    return sum(1 for item in evidence if item.get("sentiment") == sentiment)


def get_evidence_snippet(text: str, keyword: str, window: int = 220) -> str:
    lower_text = text.lower()
    lower_keyword = keyword.lower()

    index = lower_text.find(lower_keyword)

    if index == -1:
        return ""

    raw_start = max(index - window, 0)
    raw_end = min(index + len(keyword) + window, len(text))

    return clean_snippet(expand_to_full_words_or_clause(text, raw_start, raw_end))


def expand_regex_snippet(text: str, match: re.Match, window: int = 160) -> str:
    raw_start = max(match.start() - window, 0)
    raw_end = min(match.end() + window, len(text))

    return clean_snippet(expand_to_full_words_or_clause(text, raw_start, raw_end))


def expand_to_full_words_or_clause(text: str, start: int, end: int) -> str:
    while start > 0 and text[start - 1].isalnum():
        start -= 1

    while end < len(text) and text[end].isalnum():
        end += 1

    clause_start_candidates = [
        text.rfind(".", 0, start),
        text.rfind("\n", 0, start),
        text.rfind(";", 0, start)
    ]

    clause_start = max(clause_start_candidates)

    if clause_start != -1 and start - clause_start < 80:
        start = clause_start + 1

    clause_end_candidates = [
        text.find(".", end),
        text.find("\n", end),
        text.find(";", end)
    ]

    valid_clause_ends = [
        candidate for candidate in clause_end_candidates
        if candidate != -1
    ]

    if valid_clause_ends:
        nearest_clause_end = min(valid_clause_ends)
        if nearest_clause_end - end < 120:
            end = nearest_clause_end + 1

    return text[start:end]


def clean_snippet(snippet: str) -> str:
    return " ".join(str(snippet).replace("\n", " ").split())

def get_candidate_evidence_for_control(
    pages: list[dict],
    control_id: str,
    max_snippets: int = 3
) -> list:
    keywords = DPDP_CANDIDATE_KEYWORDS.get(control_id, [])

    if not keywords:
        return []

    candidate_evidence = []

    for page in pages:
        page_number = page.get("page")
        text = page.get("text", "")

        snippets = extract_candidate_snippets(
            text=text,
            keywords=keywords,
            max_snippets=max_snippets - len(candidate_evidence)
        )

        for snippet in snippets:
            candidate_evidence.append({
                "page": page_number,
                "snippet": snippet
            })

        if len(candidate_evidence) >= max_snippets:
            break

    return candidate_evidence


def extract_candidate_snippets(
    text: str,
    keywords: list,
    max_snippets: int = 3,
    window: int = 220
) -> list:
    if not text:
        return []

    snippets = []
    lower_text = text.lower()

    for keyword in keywords:
        keyword_lower = keyword.lower()
        index = lower_text.find(keyword_lower)

        if index == -1:
            continue

        start = max(index - window, 0)
        end = min(index + len(keyword) + window, len(text))

        snippet = clean_snippet(
            expand_to_full_words_or_clause(text, start, end)
        )

        if snippet and snippet not in snippets:
            snippets.append(snippet)

        if len(snippets) >= max_snippets:
            break

    return snippets