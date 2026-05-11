def is_table_of_contents_or_heading(snippet: str) -> bool:
    """
    Rejects table-of-contents, index, or heading-only candidate snippets.
    Candidate evidence must be substantive enough for audit review.

    This is the shared TOC/heading filter used by both:
    - src.evidence_context_filter
    - src.tpmr_checker via is_table_of_contents_snippet() wrapper
    """

    text = str(snippet or "").lower().strip()

    if not text:
        return True

    toc_terms = [
        "table of contents",
        "contents",
        "page no",
        "page number",
        "list of tables",
        "list of figures",
    ]

    if any(term in text for term in toc_terms):
        return True

    if "....." in text or "……" in text or "…." in text:
        return True

    words = text.split()
    weak_heading_terms = [
        "right to audit",
        "data deletion",
        "termination",
        "audit",
        "access",
        "offboarding",
        "security assessment",
        "incident notification",
        "penetration testing",
        "data classification",
    ]

    if len(words) <= 10 and any(term in text for term in weak_heading_terms):
        return True

    return False


def is_relevant_candidate_evidence(finding: dict, evidence_item: dict) -> bool:
    """
    Filters candidate evidence that matched a keyword but not the real control intent.
    """

    control = str(finding.get("control", "")).lower()
    expected = str(finding.get("expected_requirement", "")).lower()
    snippet = str(evidence_item.get("snippet", "")).lower()

    if is_table_of_contents_or_heading(snippet):
        return False

    privacy_terms = [
        "personal data",
        "personal information",
        "data principal",
        "data subject",
        "data fiduciary",
        "data processor",
        "processing",
        "privacy",
        "consent for processing",
        "withdraw consent",
        "right to access",
        "right to correction",
        "right to erasure",
        "grievance",
    ]

    admin_rfp_terms = [
        "ambiguity",
        "correction",
        "addendum",
        "proposal",
        "offeror",
        "rfp",
        "selection criteria",
        "mistakes may be crossed out",
        "initialed in ink",
        "contract administrator",
        "assignment",
        "subcontract",
        "prior written consent from the city",
    ]

    is_dpdp_control = (
        "dpdp" in str(finding.get("source", "")).lower()
        or "data principal" in control
        or "consent" in control
        or "personal data" in expected
        or "privacy" in expected
    )

    has_privacy_context = any(term in snippet for term in privacy_terms)
    has_admin_rfp_context = any(term in snippet for term in admin_rfp_terms)

    if is_dpdp_control and has_admin_rfp_context and not has_privacy_context:
        return False

    return True


def filter_candidate_evidence_for_findings(findings: list[dict]) -> list[dict]:
    filtered_findings = []

    for finding in findings:
        finding_copy = finding.copy()
        candidate_evidence = finding_copy.get("candidate_evidence", [])

        filtered_candidates = [
            item for item in candidate_evidence
            if is_relevant_candidate_evidence(finding_copy, item)
        ]

        removed_count = len(candidate_evidence) - len(filtered_candidates)

        finding_copy["candidate_evidence"] = filtered_candidates
        finding_copy["discarded_candidate_evidence_count"] = removed_count

        if removed_count > 0:
            finding_copy["evidence_filter_note"] = (
                f"{removed_count} candidate evidence snippet(s) were discarded "
                "because they appeared to match headings, TOC text, or administrative/RFP language "
                "rather than the control intent."
            )

        filtered_findings.append(finding_copy)

    return filtered_findings
