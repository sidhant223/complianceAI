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
    "does not currently guarantee",
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


TPMR_CONTROL_REQUIREMENTS = {
    "vendor_due_diligence": "The document should require vendor assessment, screening, or due diligence before onboarding or contract award.",
    "vendor_risk_rating": "The document should classify vendors based on risk level, criticality, service type, or data access.",
    "data_processing_agreement": "The document should require a formal data processing agreement or privacy addendum defining processing purpose, obligations, safeguards, and data handling responsibilities.",
    "contractual_safeguards": "The document should include contractual security, privacy, confidentiality, compliance, and evidence obligations for vendors.",
    "right_to_audit": "The document should allow audit, inspection, assessment, record review, or independent assurance of vendor controls.",
    "vendor_breach_notification": "The document should require vendors to report security incidents, data breaches, or privacy incidents within defined timelines.",
    "sub_processor_controls": "The document should require approval, monitoring, or control of sub-processors, subcontractors, downstream vendors, or fourth parties.",
    "security_assessment": "The document should require security assessment, security review, certification, questionnaire, penetration testing, or control validation of vendors.",
    "vendor_access_control": "The document should define how vendor access to systems, data, or client environments is authorized, reviewed, limited, and revoked.",
    "periodic_vendor_review": "The document should require ongoing or periodic vendor monitoring, reassessment, recertification, or review after onboarding.",
    "vendor_offboarding": "The document should define vendor offboarding, contract termination handling, access revocation, asset return, and transition obligations.",
    "data_deletion_after_termination": "The document should require secure return, deletion, destruction, or purging of data after contract termination or vendor offboarding.",
    "children_data_privacy_overlay": "The document should mention whether vendors process or access children's or minors' data, and whether parental consent or stricter privacy controls apply."
}


TPMR_CANDIDATE_KEYWORDS = {
    "vendor_due_diligence": [
        "due diligence", "assessment", "evaluate", "vendor", "supplier", "qualification", "screening", "onboarding"
    ],
    "vendor_risk_rating": [
        "risk rating", "risk classification", "risk level", "critical vendor", "risk score", "tier", "classification"
    ],
    "data_processing_agreement": [
        "data processing", "dpa", "processor", "personal data", "privacy addendum", "agreement", "contract"
    ],
    "contractual_safeguards": [
        "contract", "safeguard", "confidentiality", "security clause", "privacy clause", "obligation", "sla", "agreement"
    ],
    "right_to_audit": [
        "audit", "inspect", "inspection", "review", "verify", "records", "attestation", "soc 2", "iso 27001"
    ],
    "vendor_breach_notification": [
        "breach", "incident", "notify", "notification", "report", "data loss", "unauthorized access", "72 hours"
    ],
    "sub_processor_controls": [
        "sub-processor", "subprocessor", "subcontractor", "subcontract", "fourth party", "downstream vendor", "onward transfer"
    ],
    "security_assessment": [
        "security assessment", "security review", "risk assessment", "questionnaire", "penetration test", "vulnerability", "certification"
    ],
    "vendor_access_control": [
        "vendor access", "third-party access", "access control", "least privilege", "rbac", "mfa", "access review", "revoke access"
    ],
    "periodic_vendor_review": [
        "periodic review", "annual review", "ongoing monitoring", "continuous monitoring", "reassessment", "recertification"
    ],
    "vendor_offboarding": [
        "offboarding", "termination", "contract termination", "exit", "access revocation", "return of assets", "transition"
    ],
    "data_deletion_after_termination": [
        "termination",
        "upon termination",
        "on termination",
        "after termination",
        "contract termination",
        "exit",
        "exit management",
        "offboarding",
        "return data",
        "return records",
        "return information",
        "destroy data",
        "destroy records",
        "delete data",
        "deletion of data",
        "secure deletion",
        "purge data",
        "data handling on termination",
        "data retention after termination",
        "return or destroy",
        "returned or destroyed",
        "confidential information",
        "customer information",
        "records"
    ],
    "children_data_privacy_overlay": [
        "children", "child", "minor", "minors", "parental consent", "guardian"
    ]
}


TPMR_CONTROLS = {
    "vendor_due_diligence": {
        "title": "Vendor Due Diligence",
        "description": "Checks whether vendors are reviewed before onboarding.",
        "keywords": [
            "vendor due diligence",
            "due diligence",
            "vendor onboarding",
            "third-party onboarding",
            "supplier onboarding",
            "vendor review",
            "supplier review",
            "pre-onboarding assessment",
            "third-party assessment",
            "vendor screening",
            "supplier screening",
            "vendor evaluation",
            "supplier evaluation"
        ]
    },

    "vendor_risk_rating": {
        "title": "Vendor Risk Rating",
        "description": "Checks whether vendors are classified based on risk level.",
        "keywords": [
            "vendor risk rating",
            "risk rating",
            "risk classification",
            "vendor classification",
            "supplier classification",
            "low risk",
            "medium risk",
            "high risk",
            "critical vendor",
            "risk tier",
            "tiering",
            "vendor tier",
            "supplier tier",
            "risk score"
        ]
    },

    "data_processing_agreement": {
        "title": "Data Processing Agreement",
        "description": "Checks whether DPA or data processing contractual terms are required.",
        "keywords": [
            "data processing agreement",
            "dpa",
            "processing agreement",
            "data processor agreement",
            "processor agreement",
            "data protection agreement",
            "data processing addendum",
            "privacy addendum",
            "processor terms"
        ]
    },

    "contractual_safeguards": {
        "title": "Contractual Safeguards",
        "description": "Checks whether vendor contracts include security, privacy, and compliance clauses.",
        "keywords": [
            "contractual safeguards",
            "contractual controls",
            "contract clauses",
            "security clauses",
            "privacy clauses",
            "data protection clauses",
            "confidentiality clause",
            "confidentiality obligations",
            "service agreement",
            "master service agreement",
            "msa",
            "sla",
            "service level agreement",
            "contractual obligations",
            "legal agreement"
        ]
    },

    "right_to_audit": {
        "title": "Right to Audit",
        "description": "Checks whether the organization has the right to audit, inspect, or assess vendors.",
        "keywords": [
            "right to audit",
            "audit rights",
            "audit clause",
            "vendor audit",
            "third-party audit",
            "supplier audit",
            "audit access",
            "inspection rights",
            "right of inspection",
            "inspection clause",
            "on-site visit",
            "onsite visit",
            "on-site assessment",
            "onsite assessment",
            "independent audit report",
            "soc 2 report",
            "iso 27001 certificate",
            "compliance attestation",
            "vendor attestation",
            "evidence of compliance",
            "review vendor records",
            "access to records",
            "inspection of records",
            "rights of banks to access",
            "rights of banks to access including premises",
            "access including premises",
            "access premises",
            "obtain relevant information",
            "access and obtain relevant information",
            "audit and obtain relevant information",
            "access audit and obtain relevant information",
            "tpsp",
            "tpsps",
            "third party service provider",
            "third party service providers",
            "key nth parties",
            "nth parties"
        ],
        "context_terms": [
            "vendor",
            "third-party",
            "third party",
            "supplier",
            "processor",
            "service provider",
            "contractor",
            "records",
            "inspection",
            "access",
            "independent",
            "soc 2",
            "iso 27001",
            "attestation",
            "right",
            "clause",
            "bank",
            "banks",
            "premises",
            "information",
            "tpsp",
            "tpsps",
            "nth parties",
            "key nth parties"
        ]
    },

    "vendor_breach_notification": {
        "title": "Vendor Breach Notification",
        "description": "Checks whether vendors must notify the organization about breaches or incidents.",
        "keywords": [
            "vendor breach notification",
            "breach notification",
            "security incident",
            "incident notification",
            "notify",
            "notification timeline",
            "data breach",
            "third-party breach",
            "supplier breach",
            "processor breach",
            "72-hour window",
            "72 hour window",
            "within 72 hours",
            "within seventy two hours",
            "incident reporting"
        ],
        "regex": [
            r"\b\d+\s*(hour|hours|day|days)\b.{0,120}\b(notify|notification|breach|incident|report)\b",
            r"\b(notify|notification|breach|incident|report)\b.{0,120}\b\d+\s*(hour|hours|day|days)\b"
        ]
    },

    "sub_processor_controls": {
        "title": "Sub-Processor Controls",
        "description": "Checks whether sub-processors or downstream vendors are controlled.",
        "keywords": [
            "sub-processor",
            "subprocessor",
            "sub processor",
            "downstream vendor",
            "fourth party",
            "fourth-party",
            "subcontractor",
            "subcontracting",
            "sub-processing",
            "processor chain",
            "onward transfer",
            "sub-vendor",
            "sub vendor"
        ]
    },

    "security_assessment": {
        "title": "Security Assessment",
        "description": "Checks whether security assessments are required for vendors.",
        "keywords": [
            "security assessment",
            "vendor security assessment",
            "supplier security assessment",
            "risk assessment",
            "cybersecurity assessment",
            "information security assessment",
            "security questionnaire",
            "iso 27001",
            "soc 2",
            "penetration test",
            "vulnerability assessment",
            "security review",
            "control assessment",
            "security due diligence"
        ]
    },

    "vendor_access_control": {
        "title": "Vendor Access Control",
        "description": "Checks whether vendor access to systems or data is controlled.",
        "keywords": [
            "vendor access",
            "third-party access",
            "external access",
            "contractor access",
            "privileged access",
            "access control",
            "least privilege",
            "role-based access",
            "rbac",
            "mfa",
            "multi-factor authentication",
            "access review",
            "access termination",
            "access revocation",
            "revoke access",
            "identity and access management",
            "iam"
        ]
    },

    "periodic_vendor_review": {
        "title": "Periodic Vendor Review",
        "description": "Checks whether vendors are reviewed periodically after onboarding.",
        "keywords": [
            "periodic review",
            "annual review",
            "quarterly review",
            "monthly review",
            "yearly review",
            "ongoing monitoring",
            "continuous monitoring",
            "vendor monitoring",
            "supplier monitoring",
            "periodic reassessment",
            "renewal review",
            "recertification",
            "vendor recertification"
        ],
        "regex": [
            r"\b(annual|quarterly|monthly|yearly)\b.{0,120}\b(review|assessment|monitoring|reassessment|recertification)\b",
            r"\b(review|assessment|monitoring|reassessment|recertification)\b.{0,120}\b(annual|quarterly|monthly|yearly)\b"
        ]
    },

    "vendor_offboarding": {
        "title": "Vendor Offboarding",
        "description": "Checks whether vendor offboarding is defined after contract termination.",
        "keywords": [
            "vendor offboarding",
            "offboarding",
            "termination",
            "contract termination",
            "exit process",
            "vendor exit",
            "supplier exit",
            "access revocation",
            "revoke access",
            "return of assets",
            "contract end",
            "end of contract",
            "transition assistance"
        ]
    },

    "data_deletion_after_termination": {
        "title": "Data Deletion After Termination",
        "description": "Checks whether vendors must delete, return, or destroy data after contract termination or offboarding.",
        "keywords": [
            "deletion after termination",
            "data deletion after termination",
            "termination data deletion",
            "delete data after termination",
            "return data after termination",
            "destroy data after termination",
            "vendor offboarding data deletion",
            "contract termination data return",
            "data return upon termination",
            "data destruction upon termination",
            "return or destroy data upon termination",
            "delete or return personal data",
            "upon termination",
            "on termination",
            "after termination",
            "data handling on termination",
            "data retention after termination",
            "return data",
            "return records",
            "return information",
            "destroy data",
            "destroy records",
            "delete data",
            "secure deletion",
            "return or destroy",
            "returned or destroyed",
            "customer information",
            "confidential information",
            "exit management"
        ],
        "regex": [
            r"\b(termination|contract termination|offboarding|exit|end of contract|contract end)\b.{0,120}\b(delete|deletion|destroy|destruction|return|purge)\b.{0,80}\b(data|personal data|records)\b",
            r"\b(delete|deletion|destroy|destruction|return|purge)\b.{0,80}\b(data|personal data|records)\b.{0,120}\b(termination|contract termination|offboarding|exit|end of contract|contract end)\b",
            r"\b(data|personal data|records)\b.{0,120}\b(delete|deletion|destroy|destruction|return|purge)\b.{0,120}\b(termination|contract termination|offboarding|exit|end of contract|contract end)\b"
        ]
    },

    # Privacy overlay inside TPMR
    "children_data_privacy_overlay": {
        "title": "Children's Data Privacy Overlay",
        "description": "Flags whether the policy discusses minors or children's data, because this increases vendor/privacy risk even in a TPMR-focused review.",
        "keywords": [
            "children",
            "child",
            "minor",
            "minors",
            "children's data",
            "children's personal data",
            "parental consent",
            "verifiable parental consent",
            "under the age",
            "data from any minor",
            "do not intentionally collect data from any minor"
        ],
        "privacy_overlay": True
    }
}



SECTION_WEIGHT = {
    "strong": 1.0,
    "medium": 0.4,
    "weak": 0.05,
}

STRONG_SECTION_PATTERNS = [
    r"\baudit results\b",
    r"\bissue\s+\d+\b",
    r"\bfinding\s+\d+\b",
    r"\brecommendation\s+\d+\b",
    r"\bmanagement action plan\b",
    r"\bmanagement response\b",
    r"\brequirements?\b",
    r"\bcontrols?\b",
    r"\bprocedure steps?\b",
]

WEAK_SECTION_PATTERNS = [
    r"\btable of contents\b",
    r"\bcontents\b",
    r"\bintroduction\b",
    r"\bbackground\b",
    r"\bacronyms?\b",
    r"\babbreviations?\b",
    r"\bdefinitions?\b",
    r"\bannex\b",
    r"\bappendix\b",
]


SECTION_HEADER_PATTERNS = [
    r"^\s*\d{1,2}\.\s+[A-Z][A-Za-z0-9 /&()\-:,]{2,}$",
    r"^\s*[IVXLCDM]{1,6}\.\s+[A-Z][A-Za-z0-9 /&()\-:,]{2,}$",
    r"^\s*Issue\s+\d+\s*[:\-].+",
    r"^\s*Finding\s+\d+\s*[:\-].+",
    r"^\s*Recommendation\s+\d+\s*[:\-].+",
    r"^\s*Management Action Plan.*",
    r"^\s*Management Response.*",
    r"^\s*Audit Results.*",
    r"^\s*Requirements?.*",
    r"^\s*Controls?.*",
    r"^\s*Procedure Steps?.*",
]

BROKEN_HEADER_ENDINGS = {
    "and", "or", "of", "for", "to", "with", "which", "that", "because", "including", "where"
}

ATTRIBUTION_MARKERS = [
    "according to",
    "as stated by",
    "as defined by",
    "as noted by",
    "the standard states",
    "the guideline requires",
    "as per the framework",
]

STANDARD_BODY_PATTERN = re.compile(
    r"\b(IIA|ISO|BCBS|FSB|IOSCO|OECD)\b.{0,30}\b(states|defines|recommends|requires)\b",
    flags=re.IGNORECASE,
)

FAILED_TIER_PATTERNS = [
    r"\bdid not have\b",
    r"\bdoes not have\b",
    r"\bhas not yet adopted\b",
    r"\bhas not yet established\b",
    r"\bhas not yet implemented\b",
    r"\bno formal process exists\b",
    r"\bnot yet defined\b",
    r"\bnot yet available\b",
    r"\babsent\b",
    r"\blacking\b",
    r"\bnonexistent\b",
    r"\bunsatisfactory\b",
    r"\binadequate\b",
    r"\bineffective\b",
    r"\bmajor improvement needed\b",
    r"\bfailed to comply\b",
    r"\bfailed to meet\b",
    r"\bnon[- ]compliant\b",
    r"\bno guidance (on|for)\b",
]

PARTIAL_TIER_PATTERNS = [
    r"\bin most but not all\b",
    r"\bsome but not all\b",
    r"\blimited\b",
    r"\bincomplete\b",
    r"\binconsistent\b",
    r"\binsufficient\b",
    r"\bnot always\b",
    r"\bnot consistently\b",
    r"\bnot fully\b",
    r"\bnot exhaustive\b",
    r"\bgaps in\b",
    r"\bweaknesses in\b",
    r"\bdeficiencies in\b",
    r"\bsome improvement needed\b",
    r"\bpartially compliant\b",
    r"\bpartially covered\b",
    r"\bpartially implemented\b",
    r"\bneed for improvement\b",
    r"\bcould be strengthened\b",
    r"\bcould be improved\b",
    r"\bnot sufficient\b",
]


def is_audit_report_mode(document_context: dict | None) -> bool:
    return bool(document_context and document_context.get("audit_report_mode") is True)


def get_page_number(page: dict):
    return page.get("page", page.get("page_number", "N/A"))


def is_valid_section_header(line: str) -> bool:
    """
    Strict 80-character / no-fragment / pattern-match rule.
    Prevents broken OCR fragments or long sentences from becoming section headers.
    """

    clean = " ".join(str(line or "").strip().split())

    if not clean or len(clean) > 80:
        return False

    if clean.endswith((",", ";", ":")) and not re.search(r"^(issue|finding|recommendation)\s+\d+", clean, flags=re.IGNORECASE):
        return False

    words = clean.split()
    if words and words[-1].lower() in BROKEN_HEADER_ENDINGS:
        return False

    if len(words) > 14:
        return False

    return any(re.search(pattern, clean, flags=re.IGNORECASE) for pattern in SECTION_HEADER_PATTERNS)


def extract_section_header(text: str) -> str:
    """
    Extracts only clean section headers.
    Does not fall back to random first lines, because that pollutes retrieval weighting.
    """

    lines = [" ".join(line.strip().split()) for line in str(text or "").splitlines() if line.strip()]

    for line in lines[:20]:
        if is_valid_section_header(line):
            return line

    return "N/A"

def substantive_density(text: str) -> float:
    words = re.findall(r"[A-Za-z]{3,}", str(text or ""))
    if not words:
        return 0.0
    substantive = [w for w in words if w.lower() not in {"the", "and", "for", "with", "that", "this", "from", "were", "are", "was", "have", "has"}]
    return len(substantive) / max(len(words), 1)


def tag_section_strength(header_or_text: str) -> str:
    text = str(header_or_text or "").strip()

    if not text or text == "N/A":
        return "medium"

    if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in STRONG_SECTION_PATTERNS):
        return "strong"

    if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in WEAK_SECTION_PATTERNS):
        return "weak"

    return "strong" if substantive_density(text) > 0.60 else "medium"

def record_section_context(document_context: dict | None, page_number, header: str, strength: str) -> None:
    if not document_context:
        return

    document_context.setdefault("weighted_section_headers", [])
    document_context.setdefault("section_tag_map", {})
    document_context.setdefault("sections_used_for_scoring", [])

    clean_header = str(header or "").strip()
    document_context["section_tag_map"][str(page_number)] = strength

    if clean_header and clean_header != "N/A" and is_valid_section_header(clean_header):
        if clean_header not in document_context["weighted_section_headers"]:
            document_context["weighted_section_headers"].append(clean_header)

        if strength == "strong" and clean_header not in document_context["sections_used_for_scoring"]:
            document_context["sections_used_for_scoring"].append(clean_header)

def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", str(text or "")) if part.strip()]


def apply_attribution_filter(text: str) -> str:
    kept = []
    for sentence in split_sentences(text):
        lower_sentence = sentence.lower()
        if any(marker in lower_sentence for marker in ATTRIBUTION_MARKERS):
            continue
        if STANDARD_BODY_PATTERN.search(sentence):
            continue
        if re.search(r"[\"“”‘’].{10,}[\"“”‘’]", sentence):
            continue
        kept.append(sentence)
    return " ".join(kept)


def detect_audit_negative_signal(snippet: str, section_strength: str, document_context: dict | None) -> str | None:
    if not is_audit_report_mode(document_context):
        return None
    if section_strength != "strong":
        return None
    filtered = apply_attribution_filter(snippet)
    if any(re.search(pattern, filtered, flags=re.IGNORECASE) for pattern in FAILED_TIER_PATTERNS):
        return "failed"
    if any(re.search(pattern, filtered, flags=re.IGNORECASE) for pattern in PARTIAL_TIER_PATTERNS):
        return "partial"
    return None


def sentiment_from_negative_signal(snippet: str, section_strength: str, document_context: dict | None) -> str:
    signal = detect_audit_negative_signal(snippet, section_strength, document_context)
    if signal in {"failed", "partial"}:
        return signal
    return detect_evidence_sentiment(snippet)


def evidence_strength_rank(strength: str) -> int:
    return {"weak": 1, "medium": 2, "strong": 3}.get(strength, 0)


def strongest_positive_evidence_strength(evidence: list[dict]) -> str:
    positives = [item.get("section_strength", "medium") for item in evidence if item.get("sentiment") == "positive"]
    if not positives:
        return "weak"
    return max(positives, key=evidence_strength_rank)


def strongest_negative_signal(evidence: list[dict]) -> str | None:
    signals = [item.get("negative_signal") for item in evidence if item.get("negative_signal")]
    if "failed" in signals:
        return "failed"
    if "partial" in signals:
        return "partial"
    return None


def negative_signal_source(evidence: list[dict]) -> str:
    for item in evidence:
        if item.get("negative_signal"):
            return item.get("section_header") or f"Page {item.get('page', 'N/A')}"
    return "N/A"


def resolve_tpmr_status(
    positive_evidence_found: bool,
    positive_evidence_strength: str,
    negative_signal: str | None,
    audit_report_mode: bool,
    default_rule_status: str,
) -> str:
    if not audit_report_mode:
        return default_rule_status
    if positive_evidence_found and positive_evidence_strength == "strong" and negative_signal is None:
        return "Present"
    if positive_evidence_found and negative_signal == "partial":
        return "Partially Compliant"
    if positive_evidence_found and negative_signal == "failed":
        return "Partially Compliant"
    if not positive_evidence_found and negative_signal == "failed":
        return "Failed"
    if not positive_evidence_found and negative_signal == "partial":
        return "Partially Compliant"
    if positive_evidence_found and positive_evidence_strength == "weak":
        return "Partially Compliant"
    if not positive_evidence_found and negative_signal is None:
        return "Missing"
    return default_rule_status


def weighted_candidate_score(section_strength: str, audit_report_mode: bool, similarity_score: float = 1.0) -> float:
    section_weight = SECTION_WEIGHT.get(section_strength, 0.4)
    mode_multiplier = 1.3 if audit_report_mode else 1.0
    return round(similarity_score * section_weight * mode_multiplier, 4)

def analyze_tpmr_compliance(
    pages: list[dict],
    document_context: dict | None = None
) -> dict:
    findings = []

    if document_context is not None:
        document_context["negative_detection_active"] = is_audit_report_mode(document_context)
        document_context["attribution_filter_active"] = is_audit_report_mode(document_context)

    for control_id, control in TPMR_CONTROLS.items():
        finding = analyze_single_tpmr_control(
            control_id=control_id,
            control=control,
            pages=pages,
            document_context=document_context
        )
        findings.append(finding)

    summary = build_tpmr_summary(findings)

    privacy_overlay_findings = [
        finding for finding in findings
        if finding.get("is_privacy_overlay") is True and finding["status"] != "Missing"
    ]

    return {
        "tpmr_overall_status": summary["overall_status"],
        "tpmr_risk_level": summary["risk_level"],
        "total_controls": len(findings),
        "present_count": summary["present_count"],
        "partial_count": summary["partial_count"],
        "missing_count": summary["missing_count"],
        "failed_count": summary["failed_count"],
        "privacy_overlay_count": len(privacy_overlay_findings),
        "findings": findings
    }


def analyze_single_tpmr_control(
    control_id: str,
    control: dict,
    pages: list[dict],
    document_context: dict | None = None
) -> dict:
    evidence = []
    matched_keywords = []

    keywords = control.get("keywords", [])
    regex_patterns = control.get("regex", [])

    for page in pages:
        page_number = get_page_number(page)
        text = page["text"]
        lower_text = text.lower()
        section_header = extract_section_header(text)
        section_strength = tag_section_strength(section_header or text)
        record_section_context(document_context, page_number, section_header, section_strength)

        for keyword in keywords:
            if keyword.lower() in lower_text:
                snippet = get_evidence_snippet(text, keyword)

                if is_table_of_contents_snippet(snippet):
                    continue

                if not has_required_context(snippet, control):
                    continue

                if keyword not in matched_keywords:
                    matched_keywords.append(keyword)

                sentiment = sentiment_from_negative_signal(snippet, section_strength, document_context)

                evidence.append({
                    "page": page_number,
                    "keyword": keyword,
                    "match_type": "keyword",
                    "sentiment": sentiment,
                    "negative_signal": detect_audit_negative_signal(snippet, section_strength, document_context),
                    "section_strength": section_strength,
                    "section_header": section_header,
                    "candidate_score": weighted_candidate_score(section_strength, is_audit_report_mode(document_context)),
                    "snippet": snippet
                })

        for pattern in regex_patterns:
            matches = re.finditer(pattern, text, flags=re.IGNORECASE)

            for match in matches:
                matched_text = match.group(0)
                snippet = expand_regex_snippet(text, match)

                if is_table_of_contents_snippet(snippet):
                    continue

                if not has_required_context(snippet, control):
                    continue

                if matched_text not in matched_keywords:
                    matched_keywords.append(matched_text)

                sentiment = sentiment_from_negative_signal(snippet, section_strength, document_context)

                evidence.append({
                    "page": page_number,
                    "keyword": matched_text,
                    "match_type": "regex",
                    "sentiment": sentiment,
                    "negative_signal": detect_audit_negative_signal(snippet, section_strength, document_context),
                    "section_strength": section_strength,
                    "section_header": section_header,
                    "candidate_score": weighted_candidate_score(section_strength, is_audit_report_mode(document_context)),
                    "snippet": snippet
                })

    evidence = deduplicate_evidence(evidence)
    evidence.sort(key=lambda item: item.get("candidate_score", 0), reverse=True)

    paragraph_fallback_controls = {
        "right_to_audit",
        "data_deletion_after_termination"
    }

    if control_id in paragraph_fallback_controls and not evidence:
        fallback_evidence = find_paragraph_evidence_for_control(
            pages=pages,
            control_id=control_id,
            control=control,
            max_results=3,
            document_context=document_context
        )
        evidence.extend(fallback_evidence)
        evidence = deduplicate_evidence(evidence)

    default_status = determine_tpmr_control_status(evidence)
    positive_evidence_found = count_evidence_by_sentiment(evidence, "positive") > 0
    positive_evidence_strength = strongest_positive_evidence_strength(evidence)
    negative_signal = strongest_negative_signal(evidence)

    status = resolve_tpmr_status(
        positive_evidence_found=positive_evidence_found,
        positive_evidence_strength=positive_evidence_strength,
        negative_signal=negative_signal,
        audit_report_mode=is_audit_report_mode(document_context),
        default_rule_status=default_status
    )
    risk = determine_tpmr_control_risk(control_id, status, control)
    recommendation = generate_tpmr_recommendation(control["title"], status, control)

    positive_evidence_count = count_evidence_by_sentiment(evidence, "positive")
    negative_evidence_count = count_evidence_by_sentiment(evidence, "negative")
    neutral_evidence_count = count_evidence_by_sentiment(evidence, "neutral")

    candidate_evidence = get_candidate_evidence_for_control(
        pages=pages,
        control_id=control_id,
        document_context=document_context
    )

    return {
        "control_id": control_id,
        "control_title": control["title"],
        "control": control["title"],
        "description": control["description"],
        "expected_requirement": TPMR_CONTROL_REQUIREMENTS.get(
            control_id,
            "The document should clearly address this vendor risk control requirement."
        ),
        "status": status,
        "risk": risk,
        "is_privacy_overlay": control.get("privacy_overlay", False),
        "matched_keywords": matched_keywords,
        "evidence_count": len(evidence),
        "positive_evidence_count": positive_evidence_count,
        "negative_evidence_count": negative_evidence_count,
        "neutral_evidence_count": neutral_evidence_count,
        "evidence": evidence[:10],
        "candidate_evidence": candidate_evidence,
        "negative_signal": negative_signal or "None",
        "negative_signal_source": negative_signal_source(evidence),
        "positive_evidence_strength": positive_evidence_strength,
        "audit_report_mode": is_audit_report_mode(document_context),
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
    context_terms = control.get("context_terms", [])

    if not context_terms:
        return True

    snippet_lower = snippet.lower()

    return any(term.lower() in snippet_lower for term in context_terms)


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


def determine_tpmr_control_status(evidence: list[dict]) -> str:
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


def determine_tpmr_control_risk(control_id: str, status: str, control: dict) -> str:
    if control.get("privacy_overlay", False):
        if status == "Missing":
            return "Low"
        if status == "Failed":
            return "High"
        return "Medium"

    high_importance_controls = {
        "vendor_due_diligence",
        "vendor_risk_rating",
        "data_processing_agreement",
        "contractual_safeguards",
        "right_to_audit",
        "vendor_breach_notification",
        "security_assessment",
        "vendor_access_control",
        "data_deletion_after_termination"
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


def generate_tpmr_recommendation(control_title: str, status: str, control: dict) -> str:
    if control.get("privacy_overlay", False):
        if status == "Missing":
            return (
                f"{control_title} was not detected. No minor-related privacy overlay was triggered from this policy."
            )
        return (
            f"{control_title} was detected. Review whether vendors process or can access minors' data, "
            f"and ensure parental consent, purpose limitation, and stricter vendor controls are considered."
        )

    if status == "Present":
        return (
            f"{control_title} appears to be covered. Review whether ownership, frequency, "
            f"contractual wording, and evidence requirements are clearly defined."
        )

    if status == "Failed":
        return (
            f"{control_title} is referenced, but the evidence suggests the control is missing, failed, "
            f"not guaranteed, or not implemented. Treat this as a high-risk vendor governance finding."
        )

    if status == "Partially Compliant":
        return (
            f"{control_title} is mentioned but may need clearer vendor responsibilities, timelines, "
            f"contractual obligations, evidence requirements, or review frequency."
        )

    return (
        f"{control_title} is not clearly mentioned. Add a dedicated vendor risk control covering this area."
    )


def build_tpmr_summary(findings: list[dict]) -> dict:
    main_findings = [
        finding for finding in findings
        if finding.get("is_privacy_overlay") is not True
    ]

    present_count = sum(1 for finding in main_findings if finding["status"] == "Present")
    partial_count = sum(1 for finding in main_findings if finding["status"] == "Partially Compliant")
    missing_count = sum(1 for finding in main_findings if finding["status"] == "Missing")
    failed_count = sum(1 for finding in main_findings if finding["status"] == "Failed")

    privacy_overlay_risk = any(
        finding.get("is_privacy_overlay") is True and finding["status"] != "Missing"
        for finding in findings
    )

    if failed_count >= 1 or missing_count >= 5:
        overall_status = "Weak / Needs Major Improvement"
        risk_level = "High"
    elif missing_count >= 3 or partial_count >= 4:
        overall_status = "Partially Covered"
        risk_level = "Medium"
    else:
        overall_status = "Mostly Covered"
        risk_level = "Low"

    if privacy_overlay_risk and risk_level == "Low":
        risk_level = "Medium"
        overall_status = "Mostly Covered With Privacy Overlay"

    return {
        "overall_status": overall_status,
        "risk_level": risk_level,
        "present_count": present_count,
        "partial_count": partial_count,
        "missing_count": missing_count,
        "failed_count": failed_count
    }


def count_evidence_by_sentiment(evidence: list[dict], sentiment: str) -> int:
    if sentiment == "negative":
        return sum(1 for item in evidence if item.get("sentiment") in {"negative", "failed", "partial"})
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
    """
    Prevents ugly clipped snippets like 'guara' or 'Cons'.
    Expands boundaries to nearest word/paragraph punctuation.
    """

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


def is_table_of_contents_snippet(snippet: str) -> bool:
    """
    Rejects table-of-contents, index, or heading-only snippets.
    These snippets are not substantive audit evidence.
    """

    text = str(snippet or "").lower().strip()

    if not text:
        return True

    toc_indicators = [
        "table of contents",
        "contents",
        "page no",
        "page number",
        "list of tables",
        "list of figures"
    ]

    if any(indicator in text for indicator in toc_indicators):
        return True

    if "....." in text or "……" in text:
        return True

    words = text.split()
    heading_like_terms = [
        "termination",
        "audit",
        "access",
        "deletion",
        "data handling",
        "right to audit"
    ]

    if len(words) <= 10 and any(term in text for term in heading_like_terms):
        return True

    return False


def split_pages_into_paragraphs(
    pages: list[dict],
    document_context: dict | None = None
) -> list[dict]:
    """
    Splits page text into paragraph-like chunks while preserving page numbers.
    Used as fallback when keyword-window evidence misses substantive clauses.
    """

    chunks = []

    for page in pages:
        page_number = page.get("page", "N/A")
        text = str(page.get("text", ""))

        raw_parts = re.split(r"\n\s*\n|(?=\n?\s*\d{1,3}\.\s+)", text)

        for part in raw_parts:
            clean = clean_snippet(part)

            if len(clean.split()) < 10:
                continue

            if is_table_of_contents_snippet(clean):
                continue

            section_header = extract_section_header(part)
            section_strength = tag_section_strength(section_header or clean)
            record_section_context(document_context, page_number, section_header, section_strength)

            chunks.append({
                "page": page_number,
                "snippet": clean[:900],
                "section_header": section_header,
                "section_strength": section_strength,
                "candidate_score": weighted_candidate_score(section_strength, is_audit_report_mode(document_context))
            })

    return chunks


def find_paragraph_evidence_for_control(
    pages: list[dict],
    control_id: str,
    control: dict,
    max_results: int = 3,
    document_context: dict | None = None
) -> list[dict]:
    """
    Finds paragraph-level evidence for important controls.
    This helps catch clauses where exact keyword-window matching fails.
    """

    keywords = list(control.get("keywords", []))
    keywords.extend(TPMR_CANDIDATE_KEYWORDS.get(control_id, []))

    chunks = split_pages_into_paragraphs(pages, document_context=document_context)
    results = []

    for chunk in chunks:
        snippet = chunk.get("snippet", "")
        lower_snippet = snippet.lower()

        matched_keywords = [
            keyword
            for keyword in keywords
            if str(keyword).lower() in lower_snippet
        ]

        if not matched_keywords:
            continue

        if not has_required_context(snippet, control):
            continue

        sentiment = sentiment_from_negative_signal(snippet, chunk.get("section_strength", "medium"), document_context)

        results.append({
            "page": chunk.get("page", "N/A"),
            "keyword": ", ".join(matched_keywords[:3]),
            "match_type": "paragraph_fallback",
            "sentiment": sentiment,
            "negative_signal": detect_audit_negative_signal(snippet, chunk.get("section_strength", "medium"), document_context),
            "section_strength": chunk.get("section_strength", "medium"),
            "section_header": chunk.get("section_header", "N/A"),
            "candidate_score": chunk.get("candidate_score", 0),
            "snippet": snippet
        })


    results.sort(key=lambda item: item.get("candidate_score", 0), reverse=True)
    return results[:max_results]


def get_candidate_evidence_for_control(
    pages: list[dict],
    control_id: str,
    max_snippets: int = 3,
    document_context: dict | None = None
) -> list:
    """
    Finds related candidate snippets even when exact rule evidence is missing.
    Section-weighted ranking prevents weak intro/TOC snippets from outranking issue/recommendation sections.
    """

    keywords = TPMR_CANDIDATE_KEYWORDS.get(control_id, [])

    if not keywords:
        return []

    candidate_evidence = []

    for page in pages:
        page_number = get_page_number(page)
        text = page.get("text", "")
        section_header = extract_section_header(text)
        section_strength = tag_section_strength(section_header or text)
        record_section_context(document_context, page_number, section_header, section_strength)

        snippets = extract_candidate_snippets(
            text=text,
            keywords=keywords,
            max_snippets=2,
        )

        for snippet in snippets:
            candidate_evidence.append({
                "page": page_number,
                "snippet": snippet,
                "section_header": section_header,
                "section_strength": section_strength,
                "candidate_score": weighted_candidate_score(
                    section_strength,
                    is_audit_report_mode(document_context)
                )
            })

    candidate_evidence.sort(key=lambda item: item.get("candidate_score", 0), reverse=True)
    return candidate_evidence[:max_snippets]

def extract_candidate_snippets(
    text: str,
    keywords: list,
    max_snippets: int = 3,
    window: int = 220
) -> list:
    """
    Extracts small nearby snippets around related keywords.
    This is broader than strict evidence matching and helps semantic review.
    """

    if not text or max_snippets <= 0:
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

        if is_table_of_contents_snippet(snippet):
            continue

        if snippet and snippet not in snippets:
            snippets.append(snippet)

        if len(snippets) >= max_snippets:
            break

    return snippets


def clean_snippet(snippet: str) -> str:
    return " ".join(str(snippet).replace("\n", " ").split())


# ---------------------------------------------------------------------------
# GT-ready TPMR rule-engine enhancements
# ---------------------------------------------------------------------------
# These enhancements intentionally keep the engine deterministic.  The LLM is
# not used to discover controls; this layer improves control discovery,
# evidence strength scoring, section-aware matching, and precise status mapping.

ENHANCED_TPMR_CONTROL_KEYWORDS = {
    "vendor_due_diligence": [
        "risk-based due diligence", "appropriate due diligence", "due care review",
        "prior to entering into contractual agreements", "before onboarding",
        "before contract award", "background investigation", "screening",
        "corporate information", "beneficial owners", "controllers", "watch-lists",
        "sanctions lists", "risk-based profile assessment", "pre-contract review",
        "third-party risk assessment", "third party risk assessment",
    ],
    "vendor_risk_rating": [
        "risk profile", "risk-based profile", "risk categories", "risk category",
        "high, medium, or low", "high medium or low", "classified as high-risk",
        "classified as high risk", "risk determination", "criticality", "critical vendor",
        "risk level is determined", "risk framework to determine the level of risk",
    ],
    "data_processing_agreement": [
        # Keep this intentionally strict. General contract/security clauses do
        # not automatically prove a formal DPA.
        "data processing agreement", "data processing addendum", "dpa",
        "processor agreement", "processor terms", "privacy addendum",
        "processing purpose", "data processing terms", "personal data processing",
        "data processor obligations", "controller processor", "data fiduciary processor",
    ],
    "contractual_safeguards": [
        "contract agreements", "contractual agreements", "contractual provisions",
        "contractual clauses", "contract must include", "contracts must include",
        "agreements must contain", "contracts must stipulate", "contract may be terminated",
        "right to terminate", "specific language appearing in contracts",
        "define their relationship", "terms and conditions", "contractual terms",
        "security responsibilities", "information security responsibilities",
        "confidentiality obligations", "non-disclosure agreement", "nda",
        "service provider accountability", "responsible for the security of confidential data",
        "fiscal penalties", "representations and warranties",
    ],
    "right_to_audit": [
        "third-party auditing agreements", "periodic auditing", "right to aid in the investigation",
        "retain the right to aid", "audit and obtain relevant information", "right to inspect",
        "permission to audit", "clause granting permission", "independent security control reports",
        "independent opinion", "independent security scans", "independent third party to validate",
    ],
    "vendor_breach_notification": [
        "security violations", "security incident", "notify immediately", "must notify",
        "incident likely to impact", "report weaknesses", "cybersecurity incident",
        "reported immediately", "breach", "data breach", "incident response plan",
    ],
    "sub_processor_controls": [
        "subcontractor", "subcontractors", "subcontract", "outsourcing firm",
        "outsourced personnel", "downstream", "nth party", "fourth party",
        "supplier chain", "supply chain elements", "onward transfer",
    ],
    "security_assessment": [
        "security assessment", "security review", "security risk assessment",
        "independent security control reports", "independent security scans",
        "validate the security", "independent third party to validate", "adequacy of the controls",
        "security controls in place", "control validation", "security questionnaire",
        "security due diligence", "vulnerability assessment", "penetration test",
        "assessment to classify", "risk-based profile assessment",
    ],
    "vendor_access_control": [
        "third-party access terms and conditions", "access approval", "third-party access approval",
        "before any third party is given access", "contract defining the terms and conditions of such access",
        "access to confidential information", "access critical information systems", "least privilege",
        "access revocation", "revoke access", "authority to direct third-party contractors",
        "handle confidential data", "access to systems", "access to systems",
    ],
    "periodic_vendor_review": [
        "reviewed and updated annually", "annual review", "annually perform",
        "regular re-evaluation", "periodic due diligence", "business case review",
        "reviews and/or monitoring", "monitoring & review", "monitoring and review",
        "ongoing monitoring", "periodic auditing", "annual receive a report",
        "financial condition of vendors", "annually", "periodically reviewed", "reassessment of risks",
    ],
    "vendor_offboarding": [
        "contract expiration", "contract termination", "termination handling", "transition",
        "worker terminations", "notice of worker terminations", "termination rights",
        "right to terminate", "contract may be terminated", "vendor exit", "service termination",
    ],
    "data_deletion_after_termination": [
        "information handling at contract termination", "immediately thereafter destroy or return",
        "destroy or return all", "return all data", "destroy all data", "data disposed",
        "information disposal", "data was disposed", "archiving and destruction of data",
        "handling of sensitive data", "system access revocation", "destroy or return all organization data",
    ],
}

ENHANCED_TPMR_REGEX = {
    "vendor_due_diligence": [
        r"\b(due diligence|due care|screening|assessment)\b.{0,160}\b(third[- ]party|vendor|supplier|service provider|contractor)\b",
        r"\b(third[- ]party|vendor|supplier|service provider|contractor)\b.{0,160}\b(due diligence|due care|screening|assessment)\b",
        r"\bprior to entering into contractual agreements\b.{0,160}\b(third[- ]party|vendor|provider|supplier)\b",
    ],
    "vendor_risk_rating": [
        r"\b(classif(y|ies|ied)|categor(y|ies|ised|ized)|risk profile|risk category|risk categories)\b.{0,160}\b(high|medium|low|critical)\b",
        r"\b(high|medium|low|critical)\b.{0,160}\b(risk category|risk categories|risk profile|vendor|third[- ]party)\b",
    ],
    "contractual_safeguards": [
        r"\b(contract|agreement|outsourcing contract)\b.{0,180}\b(must|shall|required|include|contain|stipulate|define)\b.{0,180}\b(security|confidential|responsibilit|controls|termination|compliance|information)\b",
        r"\b(security|confidential|responsibilit|controls|termination|compliance|information)\b.{0,180}\b(contract|agreement|outsourcing contract)\b",
    ],
    "right_to_audit": [
        r"\b(audit|auditing|inspect|inspection|independent opinion|independent report|independent security scan)\b.{0,180}\b(third[- ]party|vendor|supplier|outsourcing|provider|controls)\b",
        r"\b(third[- ]party|vendor|supplier|outsourcing|provider)\b.{0,180}\b(audit|auditing|inspect|inspection|independent opinion|independent report|independent security scan)\b",
    ],
    "vendor_breach_notification": [
        r"\b(third[- ]party|vendor|supplier|outsourcing|provider)\b.{0,180}\b(notify|notification|report|incident|breach|violation)\b",
        r"\b(notify|notification|report|incident|breach|violation)\b.{0,180}\b(third[- ]party|vendor|supplier|outsourcing|provider|confidential information)\b",
    ],
    "security_assessment": [
        r"\b(independent|qualified|annual|periodic)\b.{0,180}\b(security|control|assessment|scan|report|validate|validation)\b",
        r"\b(security|control)\b.{0,180}\b(assessment|scan|report|validate|validation|questionnaire|certification)\b",
    ],
    "vendor_access_control": [
        r"\b(third[- ]party|vendor|contractor|consultant|provider)\b.{0,180}\b(access|privilege|approval|authorized|revocation|revoke)\b",
        r"\b(access|privilege|approval|authorized|revocation|revoke)\b.{0,180}\b(third[- ]party|vendor|contractor|consultant|provider|confidential information|systems)\b",
    ],
    "periodic_vendor_review": [
        r"\b(annual|annually|periodic|periodically|ongoing|regular|continuous)\b.{0,180}\b(review|monitor|monitoring|reassessment|re-evaluation|audit|report)\b",
        r"\b(review|monitor|monitoring|reassessment|re-evaluation|audit|report)\b.{0,180}\b(annual|annually|periodic|periodically|ongoing|regular|continuous)\b",
    ],
    "vendor_offboarding": [
        r"\b(termination|contract expiration|contract end|offboarding|transition|exit)\b.{0,180}\b(access|return|destroy|terminate|notice|knowledge transfer|data|assets)\b",
    ],
    "data_deletion_after_termination": [
        r"\b(termination|contract termination|contract expiration|offboarding|exit)\b.{0,200}\b(destroy|return|dispose|disposal|delete|deletion|archive|revocation)\b.{0,120}\b(data|information|records|access)\b",
        r"\b(destroy|return|dispose|disposal|delete|deletion|archive|revocation)\b.{0,160}\b(data|information|records|access)\b.{0,160}\b(termination|contract termination|offboarding|exit)\b",
    ],
}

CONTROL_CORE_TERMS = {
    "data_processing_agreement": [
        "data processing agreement", "data processing addendum", "privacy addendum", "processor agreement",
        "processor terms", "processing purpose", "personal data processing", "data processor obligations",
    ],
    "contractual_safeguards": [
        "contracts must include", "agreements must contain", "contracts must stipulate",
        "specific language appearing in contracts", "contractual provisions", "security responsibilities",
        "responsible for the security of confidential data", "contract may be terminated",
    ],
    "vendor_access_control": [
        "third-party access terms", "before any third party is given access", "third-party access approval",
        "access to confidential information", "access critical information systems", "access revocation",
    ],
    "right_to_audit": [
        "third-party auditing agreements", "periodic auditing", "permission for periodic auditing",
        "independent opinion", "independent security control reports", "independent security scans",
        "right to aid in the investigation", "rights of banks to access", "audit and obtain relevant information",
    ],
    "data_deletion_after_termination": [
        "destroy or return", "destroy or return all", "data was disposed", "information handling at contract termination",
        "archiving and destruction of data", "system access revocation", "return all data", "destroy all data",
    ],
}

STRONG_CONTROL_IDS = {
    "vendor_due_diligence", "vendor_risk_rating", "contractual_safeguards", "right_to_audit",
    "vendor_breach_notification", "security_assessment", "vendor_access_control",
    "periodic_vendor_review", "vendor_offboarding", "data_deletion_after_termination",
}

WEAK_DPA_RELATED_TERMS = [
    "contract", "agreement", "security responsibilities", "confidential data", "information security responsibilities",
]


def apply_tpmr_rule_engine_enhancements() -> None:
    """Mutates TPMR dictionaries with expanded deterministic coverage."""
    for control_id, extra_keywords in ENHANCED_TPMR_CONTROL_KEYWORDS.items():
        if control_id in TPMR_CONTROLS:
            existing = TPMR_CONTROLS[control_id].setdefault("keywords", [])
            for keyword in extra_keywords:
                if keyword not in existing:
                    existing.append(keyword)
        existing_candidate = TPMR_CANDIDATE_KEYWORDS.setdefault(control_id, [])
        for keyword in extra_keywords:
            if keyword not in existing_candidate:
                existing_candidate.append(keyword)

    for control_id, extra_regex in ENHANCED_TPMR_REGEX.items():
        if control_id in TPMR_CONTROLS:
            existing_regex = TPMR_CONTROLS[control_id].setdefault("regex", [])
            for pattern in extra_regex:
                if pattern not in existing_regex:
                    existing_regex.append(pattern)


def contains_any(text: str, terms: list[str]) -> bool:
    lower = str(text or "").lower()
    return any(term.lower() in lower for term in terms)


def modal_strength_score(text: str) -> int:
    lower = str(text or "").lower()
    score = 0
    strong_modals = ["must", "shall", "required", "will", "is required", "are required"]
    strong_contract_terms = ["contract must", "contracts must", "agreement must", "agreements must", "must include", "must contain", "must stipulate"]
    periodic_terms = ["annually", "annual", "periodic", "periodically", "regular", "ongoing"]
    for term in strong_modals:
        if term in lower:
            score += 2
    for term in strong_contract_terms:
        if term in lower:
            score += 3
    for term in periodic_terms:
        if term in lower:
            score += 1
    return score


def classify_evidence_strength(
    snippet: str,
    control_id: str,
    keyword: str | None = None,
    match_type: str | None = None,
    section_strength: str = "medium",
) -> str:
    """Returns strong/medium/weak based on control specificity + section + modal language."""
    text = str(snippet or "").lower()
    score = 0

    if section_strength == "strong":
        score += 2
    elif section_strength == "medium":
        score += 1

    if match_type == "regex":
        score += 2
    elif match_type == "paragraph_fallback":
        score += 1

    score += modal_strength_score(text)

    if contains_any(text, CONTROL_CORE_TERMS.get(control_id, [])):
        score += 4

    # Keep DPA strict: general contract language is only weak related evidence.
    if control_id == "data_processing_agreement" and not contains_any(text, CONTROL_CORE_TERMS["data_processing_agreement"]):
        if contains_any(text, WEAK_DPA_RELATED_TERMS):
            return "weak"
        return "weak"

    if control_id in STRONG_CONTROL_IDS and score >= 4:
        return "strong"
    if score >= 3:
        return "medium"
    return "weak"


def normalize_evidence_quality(evidence: list[dict], control_id: str) -> list[dict]:
    for item in evidence:
        strength = classify_evidence_strength(
            snippet=item.get("snippet", ""),
            control_id=control_id,
            keyword=item.get("keyword"),
            match_type=item.get("match_type"),
            section_strength=item.get("section_strength", "medium"),
        )
        item["evidence_strength"] = strength
        # Boost candidate score by evidence strength.
        boost = {"strong": 1.0, "medium": 0.35, "weak": 0.0}.get(strength, 0)
        item["candidate_score"] = round(float(item.get("candidate_score", 0)) + boost, 4)
    return evidence


def determine_tpmr_control_status(evidence: list[dict]) -> str:
    """
    Enhanced policy-mode resolver.
    - strong evidence can make a control Present even with one good clause
    - weak/candidate-only evidence stays Partial
    - negative evidence remains Failed/Partial
    """
    if len(evidence) == 0:
        return "Missing"

    positive = [item for item in evidence if item.get("sentiment") == "positive"]
    negative = [item for item in evidence if item.get("sentiment") == "negative"]

    if negative and not positive:
        return "Failed"
    if negative and positive:
        return "Partially Compliant"

    strong_count = sum(1 for item in positive if item.get("evidence_strength") == "strong")
    medium_count = sum(1 for item in positive if item.get("evidence_strength") == "medium")
    weak_count = sum(1 for item in positive if item.get("evidence_strength") == "weak")

    if strong_count >= 1 or medium_count >= 2:
        return "Present"
    if medium_count == 1 or weak_count > 0:
        return "Partially Compliant"
    return "Missing"


def strongest_positive_evidence_strength(evidence: list[dict]) -> str:
    strengths = [item.get("evidence_strength") or item.get("section_strength", "weak") for item in evidence if item.get("sentiment") == "positive"]
    if "strong" in strengths:
        return "strong"
    if "medium" in strengths:
        return "medium"
    if "weak" in strengths:
        return "weak"
    return "none"


def add_evidence_item(
    evidence: list[dict],
    page_number,
    keyword: str,
    match_type: str,
    snippet: str,
    control_id: str,
    section_header: str,
    section_strength: str,
    document_context: dict | None,
) -> None:
    if is_table_of_contents_snippet(snippet):
        return
    sentiment = sentiment_from_negative_signal(snippet, section_strength, document_context)
    negative_signal = detect_audit_negative_signal(snippet, section_strength, document_context)
    strength = classify_evidence_strength(snippet, control_id, keyword, match_type, section_strength)
    score = weighted_candidate_score(section_strength, is_audit_report_mode(document_context))
    score += {"strong": 1.0, "medium": 0.35, "weak": 0.0}.get(strength, 0)
    evidence.append({
        "page": page_number,
        "keyword": keyword,
        "match_type": match_type,
        "sentiment": sentiment,
        "negative_signal": negative_signal,
        "section_strength": section_strength,
        "section_header": section_header,
        "evidence_strength": strength,
        "candidate_score": round(score, 4),
        "snippet": snippet,
    })


def find_paragraph_evidence_for_control(
    pages: list[dict],
    control_id: str,
    control: dict,
    max_results: int = 4,
    document_context: dict | None = None,
) -> list[dict]:
    """Enhanced paragraph-level fallback for every TPMR control."""
    keywords = list(control.get("keywords", []))
    keywords.extend(TPMR_CANDIDATE_KEYWORDS.get(control_id, []))
    keywords = list(dict.fromkeys([str(k) for k in keywords if str(k).strip()]))

    chunks = split_pages_into_paragraphs(pages, document_context=document_context)
    results = []

    for chunk in chunks:
        snippet = chunk.get("snippet", "")
        lower_snippet = snippet.lower()
        matched_keywords = [keyword for keyword in keywords if keyword.lower() in lower_snippet]

        # Regex-backed semantic phrases can detect controls even if simple keywords miss.
        for pattern in TPMR_CONTROLS.get(control_id, {}).get("regex", []):
            if re.search(pattern, snippet, flags=re.IGNORECASE):
                matched_keywords.append("regex:control_pattern")
                break

        if not matched_keywords:
            continue

        if not has_required_context(snippet, control):
            continue

        section_strength = chunk.get("section_strength", "medium")
        evidence_strength = classify_evidence_strength(
            snippet=snippet,
            control_id=control_id,
            keyword=matched_keywords[0],
            match_type="paragraph_fallback",
            section_strength=section_strength,
        )
        sentiment = sentiment_from_negative_signal(snippet, section_strength, document_context)
        score = chunk.get("candidate_score", 0) + {"strong": 1.0, "medium": 0.35, "weak": 0.0}.get(evidence_strength, 0)

        results.append({
            "page": chunk.get("page", "N/A"),
            "keyword": ", ".join(matched_keywords[:3]),
            "match_type": "paragraph_fallback",
            "sentiment": sentiment,
            "negative_signal": detect_audit_negative_signal(snippet, section_strength, document_context),
            "section_strength": section_strength,
            "section_header": chunk.get("section_header", "N/A"),
            "evidence_strength": evidence_strength,
            "candidate_score": round(score, 4),
            "snippet": snippet,
        })

    results = deduplicate_evidence(results)
    results.sort(key=lambda item: item.get("candidate_score", 0), reverse=True)
    return results[:max_results]


def analyze_single_tpmr_control(
    control_id: str,
    control: dict,
    pages: list[dict],
    document_context: dict | None = None,
) -> dict:
    evidence: list[dict] = []
    matched_keywords: list[str] = []

    keywords = list(dict.fromkeys(control.get("keywords", [])))
    regex_patterns = list(dict.fromkeys(control.get("regex", [])))

    for page in pages:
        page_number = get_page_number(page)
        text = page.get("text", "")
        lower_text = text.lower()
        section_header = extract_section_header(text)
        section_strength = tag_section_strength(section_header or text)
        record_section_context(document_context, page_number, section_header, section_strength)

        for keyword in keywords:
            if keyword.lower() in lower_text:
                snippet = get_evidence_snippet(text, keyword)
                if not snippet or is_table_of_contents_snippet(snippet):
                    continue
                if not has_required_context(snippet, control):
                    continue
                if keyword not in matched_keywords:
                    matched_keywords.append(keyword)
                add_evidence_item(evidence, page_number, keyword, "keyword", snippet, control_id, section_header, section_strength, document_context)

        for pattern in regex_patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                matched_text = match.group(0)
                snippet = expand_regex_snippet(text, match)
                if not snippet or is_table_of_contents_snippet(snippet):
                    continue
                if not has_required_context(snippet, control):
                    continue
                if matched_text not in matched_keywords:
                    matched_keywords.append(matched_text)
                add_evidence_item(evidence, page_number, matched_text, "regex", snippet, control_id, section_header, section_strength, document_context)

    # Fallback now runs for every control, not just a small hardcoded subset.
    fallback_evidence = find_paragraph_evidence_for_control(
        pages=pages,
        control_id=control_id,
        control=control,
        max_results=4,
        document_context=document_context,
    )
    evidence.extend(fallback_evidence)
    evidence = deduplicate_evidence(normalize_evidence_quality(evidence, control_id))
    evidence = [item for item in evidence if is_control_evidence_acceptable(control_id, item)]
    evidence.sort(key=lambda item: item.get("candidate_score", 0), reverse=True)

    default_status = determine_tpmr_control_status(evidence)
    positive_evidence_found = count_evidence_by_sentiment(evidence, "positive") > 0
    positive_evidence_strength = strongest_positive_evidence_strength(evidence)
    negative_signal = strongest_negative_signal(evidence)

    status = resolve_tpmr_status(
        positive_evidence_found=positive_evidence_found,
        positive_evidence_strength=positive_evidence_strength,
        negative_signal=negative_signal,
        audit_report_mode=is_audit_report_mode(document_context),
        default_rule_status=default_status,
    )

    risk = determine_tpmr_control_risk(control_id, status, control)
    recommendation = generate_tpmr_recommendation(control["title"], status, control)

    positive_evidence_count = count_evidence_by_sentiment(evidence, "positive")
    negative_evidence_count = count_evidence_by_sentiment(evidence, "negative")
    neutral_evidence_count = count_evidence_by_sentiment(evidence, "neutral")

    candidate_evidence = get_candidate_evidence_for_control(
        pages=pages,
        control_id=control_id,
        document_context=document_context,
    )

    related_control_support = infer_related_control_support(control_id, candidate_evidence, evidence)

    return {
        "control_id": control_id,
        "control_title": control["title"],
        "control": control["title"],
        "description": control["description"],
        "expected_requirement": TPMR_CONTROL_REQUIREMENTS.get(control_id, "The document should clearly address this vendor risk control requirement."),
        "status": status,
        "risk": risk,
        "is_privacy_overlay": control.get("privacy_overlay", False),
        "matched_keywords": matched_keywords,
        "evidence_count": len(evidence),
        "positive_evidence_count": positive_evidence_count,
        "negative_evidence_count": negative_evidence_count,
        "neutral_evidence_count": neutral_evidence_count,
        "evidence": evidence[:10],
        "candidate_evidence": candidate_evidence,
        "related_control_support": related_control_support,
        "negative_signal": negative_signal or "None",
        "negative_signal_source": negative_signal_source(evidence),
        "positive_evidence_strength": positive_evidence_strength,
        "audit_report_mode": is_audit_report_mode(document_context),
        "recommendation": recommendation,
        "final_status": status,
    }


def infer_related_control_support(control_id: str, candidate_evidence: list[dict], evidence: list[dict]) -> list[str]:
    """Explains when candidate evidence supports adjacent TPMR controls but not the exact control."""
    combined = " ".join([str(item.get("snippet", "")) for item in (candidate_evidence + evidence)]).lower()
    related = []
    if control_id == "data_processing_agreement":
        if any(term in combined for term in ["contract", "agreement", "security responsibilities", "confidential information", "responsible for the security"]):
            related.append("Contractual Safeguards")
        if any(term in combined for term in ["confidential information", "store, process", "data", "information handling"]):
            related.append("Confidential Information Handling")
    return related


# Final generic TPMR expansion: intentionally organization-agnostic.
# This prevents the engine from being tuned to one sample policy and improves
# matching across policies, frameworks, audit reports, vendor contracts, and procedures.
GENERIC_TPMR_SYNONYM_EXPANSION = {
    "vendor_due_diligence": [
        "third party due diligence", "supplier due diligence", "service provider due diligence",
        "vendor qualification", "supplier qualification", "pre-engagement review",
        "pre-contract due diligence", "pre onboarding review", "third party screening",
        "supplier screening", "counterparty screening", "beneficial ownership review",
        "sanctions screening", "watchlist screening", "background check", "integrity review",
    ],
    "vendor_risk_rating": [
        "vendor tiering", "supplier tiering", "third party tiering", "critical supplier",
        "material outsourcing", "critical outsourcing", "risk segmentation",
        "inherent risk rating", "residual risk rating", "service criticality",
        "data sensitivity classification", "business criticality",
    ],
    "contractual_safeguards": [
        "contractual requirements", "contractual commitments", "contractual protections",
        "information security addendum", "security schedule", "security exhibit",
        "confidentiality agreement", "data protection clauses", "compliance obligations",
        "termination rights", "service levels", "sla requirements", "right to terminate",
        "contractual remedies", "indemnity", "liability", "audit cooperation",
    ],
    "data_processing_agreement": [
        "data protection addendum", "data privacy addendum", "controller to processor",
        "processor obligations", "processing instructions", "processing activities",
        "personal information processing", "personal information handling",
        "personal data handling", "privacy terms", "data processing terms",
    ],
    "right_to_audit": [
        "audit rights", "inspection rights", "right of inspection", "right to inspect",
        "access to records", "review records", "control audit", "third party audit",
        "vendor audit", "supplier audit", "independent assurance report",
        "assurance report", "soc report", "iso certificate", "control attestation",
        "regulator access", "access to premises", "obtain information",
    ],
    "vendor_breach_notification": [
        "incident notification", "incident reporting", "security incident notification",
        "privacy incident notification", "breach reporting", "unauthorized access notification",
        "notify without undue delay", "notify promptly", "report immediately",
        "data loss notification", "cyber incident notification",
    ],
    "sub_processor_controls": [
        "subprocessor", "sub processor", "sub-processing", "sub-processing approval",
        "subcontracting approval", "subcontractor approval", "downstream provider",
        "downstream supplier", "fourth party", "fourth-party", "nth party", "material subcontractor",
        "onward transfer", "sub-vendor", "sub vendor",
    ],
    "security_assessment": [
        "security questionnaire", "security certification", "security attestation",
        "vulnerability assessment", "penetration testing", "pen test",
        "control testing", "control validation", "cyber risk assessment",
        "information security review", "third party security review", "supplier security review",
    ],
    "vendor_access_control": [
        "third party access", "vendor access", "supplier access", "external access",
        "contractor access", "privileged access", "logical access", "system access",
        "access provisioning", "access approval", "access review", "access recertification",
        "access removal", "access revocation", "least privilege", "role based access",
        "mfa", "multi-factor authentication",
    ],
    "periodic_vendor_review": [
        "ongoing due diligence", "ongoing monitoring", "continuous monitoring",
        "periodic reassessment", "vendor reassessment", "supplier reassessment",
        "annual vendor review", "quarterly vendor review", "periodic performance review",
        "service review", "control review", "recertification", "renewal review",
    ],
    "vendor_offboarding": [
        "exit plan", "exit strategy", "exit management", "transition plan",
        "termination assistance", "supplier exit", "vendor exit", "service exit",
        "contract termination handling", "return of assets", "knowledge transfer",
        "access removal on termination", "offboarding process",
    ],
    "data_deletion_after_termination": [
        "return or destroy data", "return or delete data", "secure deletion",
        "secure destruction", "data destruction certificate", "certificate of destruction",
        "data return", "data disposal", "record disposal", "purge data",
        "delete personal data", "destroy personal data", "return confidential information",
        "destroy confidential information", "data retention after termination",
    ],
}

GENERIC_TPMR_REGEX_EXPANSION = {
    "data_processing_agreement": [
        r"\b(data processing|privacy|data protection)\b.{0,160}\b(addendum|agreement|terms|schedule|obligations|instructions)\b",
        r"\b(controller|processor|sub[- ]?processor)\b.{0,160}\b(obligations|instructions|personal data|processing)\b",
    ],
    "sub_processor_controls": [
        r"\b(sub[- ]?processor|subcontractor|fourth[- ]party|nth party|downstream provider|sub[- ]vendor)\b.{0,180}\b(approval|monitor|notify|control|due diligence|consent)\b",
        r"\b(approval|consent|monitor|control|notify)\b.{0,180}\b(sub[- ]?processor|subcontractor|fourth[- ]party|nth party|downstream provider|sub[- ]vendor)\b",
    ],
    "vendor_access_control": [
        r"\b(access|privilege|account|credential|identity)\b.{0,180}\b(approve|review|recertif|revoke|remove|terminate|least privilege|mfa|multi[- ]factor)\b",
    ],
    "data_deletion_after_termination": [
        r"\b(return|delete|destroy|purge|dispose|erase)\b.{0,180}\b(data|records|information|personal data|confidential information)\b.{0,180}\b(termination|expiry|expiration|offboarding|exit)\b",
    ],
}


def apply_generic_tpmr_synonyms() -> None:
    for control_id, terms in GENERIC_TPMR_SYNONYM_EXPANSION.items():
        if control_id in TPMR_CONTROLS:
            target = TPMR_CONTROLS[control_id].setdefault("keywords", [])
            for term in terms:
                if term not in target:
                    target.append(term)
        candidate_target = TPMR_CANDIDATE_KEYWORDS.setdefault(control_id, [])
        for term in terms:
            if term not in candidate_target:
                candidate_target.append(term)
    for control_id, patterns in GENERIC_TPMR_REGEX_EXPANSION.items():
        if control_id in TPMR_CONTROLS:
            regex_target = TPMR_CONTROLS[control_id].setdefault("regex", [])
            for pattern in patterns:
                if pattern not in regex_target:
                    regex_target.append(pattern)


apply_tpmr_rule_engine_enhancements()
apply_generic_tpmr_synonyms()


def is_control_evidence_acceptable(control_id: str, item: dict) -> bool:
    """Filters broad false positives for controls that require precise language."""
    snippet = str(item.get("snippet", "")).lower()

    if control_id == "data_processing_agreement":
        # General contract/security language supports contractual safeguards,
        # but it does not prove a formal DPA/privacy addendum.
        return contains_any(snippet, CONTROL_CORE_TERMS.get("data_processing_agreement", []))

    if control_id == "sub_processor_controls":
        # Outsourcing or supply-chain language alone is too broad. Require
        # explicit downstream/subcontractor/fourth-party style terminology.
        precise_terms = [
            "sub-processor", "subprocessor", "sub processor", "subcontractor",
            "subcontracting", "fourth party", "fourth-party", "downstream",
            "nth party", "nth parties", "onward transfer", "sub-vendor", "sub vendor",
        ]
        return contains_any(snippet, precise_terms)

    return True
