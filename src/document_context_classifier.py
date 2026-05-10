def classify_document_context(pages: list[dict]) -> dict:
    """
    Classifies the uploaded document before risk interpretation.

    Goal:
    Avoid applying heavy DPDP/privacy penalties to documents that do not
    meaningfully involve personal data processing.
    """

    full_text = " ".join(
        page.get("text", "") for page in pages
    ).lower()

    engineering_keywords = [
        "engineering services",
        "parks and recreation",
        "construction",
        "civil",
        "mechanical",
        "electrical",
        "plumbing",
        "structural engineering",
        "landscape architecture",
        "as-built",
        "construction plans"
    ]

    rfp_keywords = [
        "request for proposal",
        "rfp",
        "proposal",
        "offeror",
        "selection criteria",
        "professional services agreement",
        "contractor",
        "contract"
    ]

    personal_data_keywords = [
        "personal data",
        "personal information",
        "data principal",
        "data subject",
        "privacy notice",
        "consent for processing",
        "withdraw consent",
        "right to access personal data",
        "right to correction of personal data",
        "right to erasure",
        "grievance officer",
        "data fiduciary",
        "data processor",
        "processing of personal data"
    ]

    sensitive_business_keywords = [
        "software",
        "application",
        "platform",
        "user data",
        "customer data",
        "employee data",
        "hr data",
        "marketing data",
        "payment data",
        "financial data",
        "health data",
        "identity data",
        "authentication",
        "database",
        "cloud",
        "api"
    ]

    security_keywords = [
        "information security",
        "cybersecurity",
        "access control",
        "encryption",
        "security incident",
        "data breach",
        "penetration testing",
        "vulnerability",
        "security assessment"
    ]

    simulation_keywords = [
        "for testing purposes only",
        "stress test",
        "intentional compliance gaps",
        "intentionally incomplete",
        "sample policy",
        "mock policy",
        "audit simulation",
        "test document"
    ]

    engineering_hits = [kw for kw in engineering_keywords if kw in full_text]
    rfp_hits = [kw for kw in rfp_keywords if kw in full_text]
    personal_data_hits = [kw for kw in personal_data_keywords if kw in full_text]
    sensitive_business_hits = [kw for kw in sensitive_business_keywords if kw in full_text]
    security_hits = [kw for kw in security_keywords if kw in full_text]
    simulation_hits = [kw for kw in simulation_keywords if kw in full_text]
    is_audit_simulation = bool(simulation_hits)

    if engineering_hits and rfp_hits:
        document_type = "Engineering / Construction RFP"
    elif rfp_hits:
        document_type = "RFP / Vendor Contract"
    elif personal_data_hits:
        document_type = "Privacy / Data Protection Document"
    elif sensitive_business_hits:
        document_type = "Technology / Data Processing Document"
    else:
        document_type = "General Business Document"

    personal_data_relevance = calculate_relevance(len(personal_data_hits))
    sensitive_data_relevance = calculate_relevance(len(sensitive_business_hits))
    security_relevance = calculate_relevance(len(security_hits))
    vendor_relevance = calculate_relevance(len(rfp_hits))

    dpdp_applicable = (
        personal_data_relevance in ["Medium", "High"]
        or sensitive_data_relevance in ["Medium", "High"]
    )

    tpmr_applicable = vendor_relevance in ["Medium", "High"]

    if document_type == "Engineering / Construction RFP" and personal_data_relevance == "Low":
        dpdp_applicable = False

    return {
        "document_type": document_type,
        "personal_data_relevance": personal_data_relevance,
        "sensitive_data_relevance": sensitive_data_relevance,
        "security_relevance": security_relevance,
        "vendor_relevance": vendor_relevance,
        "dpdp_applicable": dpdp_applicable,
        "tpmr_applicable": tpmr_applicable,
        "context_keywords": {
            "engineering": engineering_hits[:10],
            "rfp": rfp_hits[:10],
            "personal_data": personal_data_hits[:10],
            "sensitive_business": sensitive_business_hits[:10],
            "security": security_hits[:10]
        },

        "context_keywords": {
            "engineering": engineering_hits[:10],
            "rfp": rfp_hits[:10],
            "personal_data": personal_data_hits[:10],
            "sensitive_business": sensitive_business_hits[:10],
            "security": security_hits[:10],
            "simulation": simulation_hits[:10]
        },

        "context_reason": (
            f"Document classified as '{document_type}'. "
            f"DPDP applicability is {dpdp_applicable} because personal/sensitive data relevance is "
            f"{personal_data_relevance}/{sensitive_data_relevance}. "
            f"TPMR applicability is {tpmr_applicable} because vendor relevance is {vendor_relevance}."
        )
    }


def calculate_relevance(hit_count: int) -> str:
    if hit_count >= 4:
        return "High"
    if hit_count >= 2:
        return "Medium"
    return "Low"