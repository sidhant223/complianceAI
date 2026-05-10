def enhance_findings_for_consulting(findings: list[dict]) -> list[dict]:
    """
    Adds senior-manager style metadata to each finding:
    - regulatory mapping
    - remediation guidance
    - entity boundary review

    This is intentionally simple and rule-based.
    """

    enhanced_findings = []

    for finding in findings:
        finding_copy = finding.copy()

        finding_copy["regulatory_mapping"] = get_regulatory_mapping(finding_copy)
        finding_copy["remediation"] = get_remediation(finding_copy)
        finding_copy["entity_boundary_review"] = get_entity_boundary_review(finding_copy)

        if finding_copy["entity_boundary_review"]["source_mismatch"]:
            finding_copy["source_attribution_review_required"] = True
            finding_copy["original_source"] = finding_copy.get("source")
            finding_copy["source"] = finding_copy["entity_boundary_review"]["expected_source"]
            finding_copy["final_status"] = "Needs Manual Review"
            finding_copy["rerouting_note"] = (
                f"Finding source was re-routed from {finding_copy.get('original_source')} "
                f"to {finding_copy.get('source')} based on entity-boundary review."
    )

        enhanced_findings.append(finding_copy)

    return enhanced_findings


def get_regulatory_mapping(finding: dict) -> dict:
    control_id = str(finding.get("control_id", "")).lower()
    source = str(finding.get("source", "")).upper()

    dpdp_map = {
        "notice": {
            "legal_reference": "DPDP Act, 2023 - Section 5",
            "requirement_summary": "Notice should explain personal data processing purpose, rights, and complaint mechanism.",
            "penalty_exposure": "General DPDP non-compliance exposure; exact penalty depends on Board assessment."
        },
        "consent": {
            "legal_reference": "DPDP Act, 2023 - Section 6",
            "requirement_summary": "Consent must be free, specific, informed, unconditional, and unambiguous.",
            "penalty_exposure": "General DPDP non-compliance exposure."
        },
        "withdrawal_of_consent": {
            "legal_reference": "DPDP Act, 2023 - Section 6",
            "requirement_summary": "Data Principal should be able to withdraw consent.",
            "penalty_exposure": "General DPDP non-compliance exposure."
        },
        "security_safeguards": {
            "legal_reference": "DPDP Act, 2023 - Section 8(5)",
            "requirement_summary": "Data Fiduciary must protect personal data using reasonable security safeguards.",
            "penalty_exposure": "Higher exposure; failure of reasonable security safeguards may attract penalty up to ₹250 crore."
        },
        "breach_notification": {
            "legal_reference": "DPDP Act, 2023 - Section 8(6)",
            "requirement_summary": "Data Fiduciary must notify the Board and affected Data Principals after personal data breach.",
            "penalty_exposure": "Higher exposure; breach notification failure may attract penalty up to ₹200 crore."
        },
        "data_principal_rights": {
            "legal_reference": "DPDP Act, 2023 - Sections 11-14",
            "requirement_summary": "Covers access, correction, erasure, grievance redressal, and nomination rights.",
            "penalty_exposure": "General DPDP non-compliance exposure."
        },
        "data_retention": {
            "legal_reference": "DPDP Act, 2023 - Section 8(7)",
            "requirement_summary": "Personal data should be erased when purpose is complete or consent is withdrawn unless retention is required by law.",
            "penalty_exposure": "General DPDP non-compliance exposure."
        }
    }

    tpmr_map = {
        "vendor_due_diligence": {
            "legal_reference": "Third-Party Risk Management Control",
            "requirement_summary": "Vendors should be assessed before onboarding or contract award.",
            "penalty_exposure": "Contractual, operational, and governance exposure."
        },
        "vendor_breach_notification": {
            "legal_reference": "Third-Party Incident Notification Control",
            "requirement_summary": "Vendors should be required to notify the organization of incidents or breaches.",
            "penalty_exposure": "May increase DPDP exposure if vendor processes personal data."
        },
        "data_processing_agreement": {
            "legal_reference": "DPDP Act, 2023 - Section 8(2) + Vendor Contract Governance",
            "requirement_summary": "Data Processor should process personal data only under valid contract.",
            "penalty_exposure": "Privacy and vendor governance exposure."
        },
        "right_to_audit": {
            "legal_reference": "Third-Party Audit Rights Control",
            "requirement_summary": "Contracts should allow audit, inspection, or assurance review of vendor controls.",
            "penalty_exposure": "Assurance and evidence gap."
        },
        "security_assessment": {
            "legal_reference": "Vendor Security Assessment Control",
            "requirement_summary": "Vendors should undergo security review or control validation.",
            "penalty_exposure": "Operational and security risk."
        }
    }

    if source == "DPDP":
        return dpdp_map.get(control_id, default_mapping())

    if source == "TPMR":
        return tpmr_map.get(control_id, default_mapping())

    return default_mapping()


def default_mapping() -> dict:
    return {
        "legal_reference": "Internal Control Framework",
        "requirement_summary": "No specific regulatory mapping configured for this control.",
        "penalty_exposure": "Requires manual audit/legal review."
    }


def get_remediation(finding: dict) -> dict:
    control_id = str(finding.get("control_id", "")).lower()
    risk = str(finding.get("risk", "Medium"))
    status = str(finding.get("final_status") or finding.get("status", ""))

    remediation_map = {
        "security_safeguards": {
            "owner": "IT Security / CISO Office",
            "complexity": "High",
            "effort": "2-6 weeks",
            "steps": [
                "Define minimum security safeguards for personal data.",
                "Implement encryption at rest and in transit where applicable.",
                "Mandate MFA for sensitive access.",
                "Document logging, monitoring, and incident response controls."
            ]
        },
        "breach_notification": {
            "owner": "Legal / Compliance / Security Operations",
            "complexity": "Medium",
            "effort": "1-3 weeks",
            "steps": [
                "Define breach identification criteria.",
                "Create breach escalation workflow.",
                "Define Board and Data Principal notification responsibilities.",
                "Maintain breach register and notification evidence."
            ]
        },
        "withdrawal_of_consent": {
            "owner": "Legal / Privacy Office / Product Team",
            "complexity": "Medium",
            "effort": "2-4 weeks",
            "steps": [
                "Define consent withdrawal process.",
                "Create request intake and validation workflow.",
                "Stop processing where consent is withdrawn.",
                "Maintain consent withdrawal logs."
            ]
        },
        "data_principal_rights": {
            "owner": "Privacy Office / Legal / Support Team",
            "complexity": "Medium",
            "effort": "2-4 weeks",
            "steps": [
                "Create request workflow for access, correction, erasure, grievance, and nomination.",
                "Define verification process.",
                "Assign request owner and response timeline.",
                "Maintain rights request register."
            ]
        },
        "vendor_breach_notification": {
            "owner": "Procurement / Legal / Vendor Risk",
            "complexity": "Medium",
            "effort": "2-4 weeks",
            "steps": [
                "Add vendor breach notification clause.",
                "Define vendor notification timeline.",
                "Create vendor incident escalation contact.",
                "Track third-party incident notifications."
            ]
        },
        "vendor_due_diligence": {
            "owner": "Procurement / Vendor Risk Management",
            "complexity": "Medium",
            "effort": "2-4 weeks",
            "steps": [
                "Create vendor due diligence checklist.",
                "Classify vendors by criticality and data access.",
                "Collect compliance evidence before onboarding.",
                "Document approval and exception handling."
            ]
        }
    }

    selected = remediation_map.get(control_id, {
        "owner": "Compliance / Control Owner",
        "complexity": "Medium",
        "effort": "1-4 weeks",
        "steps": [
            "Assign a control owner.",
            "Update the relevant policy, process, or contract clause.",
            "Collect implementation evidence.",
            "Perform manual audit review."
        ]
    })

    priority = "High" if risk == "High" or status == "Failed" else "Medium"

    return {
        "priority": priority,
        "action_owner": selected["owner"],
        "remediation_complexity": selected["complexity"],
        "estimated_effort": selected["effort"],
        "remediation_steps": selected["steps"]
    }


def get_entity_boundary_review(finding: dict) -> dict:
    source = str(finding.get("source", "")).upper()
    control_id = str(finding.get("control_id", "")).lower()
    control = str(finding.get("control", "")).lower()

    evidence_items = finding.get("evidence", []) + finding.get("candidate_evidence", [])

    combined_text = " ".join(
        item.get("snippet", "") if isinstance(item, dict) else str(item)
        for item in evidence_items
    ).lower()

    vendor_terms = [
        "vendor",
        "third party",
        "third-party",
        "contractor",
        "supplier",
        "subcontractor",
        "service provider",
        "processor"
    ]

    internal_terms = [
        "we",
        "our",
        "company",
        "organization",
        "data fiduciary",
        "data protection board",
        "data principal",
        "board",
        "regulator"
    ]

    # Split into rough sentences so one random vendor word later
    # does not hijack the whole finding.
    sentences = split_into_sentences(combined_text)

    vendor_score = 0
    internal_score = 0

    for sentence in sentences:
        sentence_has_vendor = any(term in sentence for term in vendor_terms)
        sentence_has_internal = any(term in sentence for term in internal_terms)

        # Control-specific logic
        if "vendor" in control_id or "vendor" in control:
            if sentence_has_vendor:
                vendor_score += 2
            if sentence_has_internal and not sentence_has_vendor:
                internal_score += 2
        else:
            if sentence_has_internal:
                internal_score += 2
            if sentence_has_vendor:
                vendor_score += 1

    # Strong DPDP/internal indicators
    if "data protection board" in combined_text or "data fiduciary" in combined_text:
        internal_score += 3

    # Strong vendor indicators
    if "vendor shall" in combined_text or "contractor shall notify" in combined_text:
        vendor_score += 3

    if vendor_score > internal_score:
        expected_source = "TPMR"
        boundary = "Third-Party / Vendor"
    elif internal_score > vendor_score:
        expected_source = "DPDP"
        boundary = "Internal Governance / DPDP"
    else:
        expected_source = "Manual Review"
        boundary = "Unclear"

    source_mismatch = (
        expected_source in ["DPDP", "TPMR"]
        and source
        and source != expected_source
    )

    return {
        "entity_boundary": boundary,
        "current_source": source,
        "expected_source": expected_source,
        "source_mismatch": source_mismatch,
        "boundary_scores": {
            "vendor_score": vendor_score,
            "internal_score": internal_score
        },
        "boundary_note": (
            "Potential source attribution mismatch. Finding was re-routed and should be manually reviewed."
            if source_mismatch
            else "Source attribution appears acceptable or requires no change."
        )
    }


def split_into_sentences(text: str) -> list[str]:
    separators = [".", ";", "\n"]

    sentences = [text]

    for separator in separators:
        new_sentences = []

        for sentence in sentences:
            new_sentences.extend(sentence.split(separator))

        sentences = new_sentences

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]