"""Consulting-style finding enrichment for ComplianceAI.

This module is intentionally deterministic. It adds metadata used by the final
JSON/PDF report, but it does not change rule-engine scores or statuses.
"""

from __future__ import annotations


def default_mapping() -> dict:
    return {
        "framework": "Internal Control Framework",
        "control_area": "Governance / Documentation",
        "reference": "Internal policy and audit control expectations",
        "legal_or_regulatory_relevance": "Supports auditability, accountability, and operational risk governance.",
    }


def get_regulatory_mapping(control_id: str, source: str | None = None) -> dict:
    """Returns deterministic mapping metadata for DPDP and TPMR controls."""

    control_id = str(control_id or "").lower().strip()
    source = str(source or "").upper().strip()

    dpdp_map = {
        "consent_management": {
            "framework": "DPDP / Privacy Governance",
            "control_area": "Consent and lawful processing",
            "reference": "Consent, notice, and purpose limitation expectations",
            "legal_or_regulatory_relevance": "Helps validate whether personal-data processing has clear user-facing controls.",
        },
        "data_principal_rights": {
            "framework": "DPDP / Privacy Governance",
            "control_area": "Data principal rights",
            "reference": "Access, correction, erasure, and grievance handling expectations",
            "legal_or_regulatory_relevance": "Supports privacy-rights operational readiness and defensible user handling.",
        },
        "security_safeguards": {
            "framework": "DPDP / Security Safeguards",
            "control_area": "Security safeguards",
            "reference": "Reasonable security safeguards and breach prevention expectations",
            "legal_or_regulatory_relevance": "Supports privacy/security governance for protected data.",
        },
        "breach_notification": {
            "framework": "DPDP / Incident Governance",
            "control_area": "Breach and incident notification",
            "reference": "Breach reporting and escalation expectations",
            "legal_or_regulatory_relevance": "Supports timely escalation and accountability for personal-data incidents.",
        },
        "third_party_processing": {
            "framework": "DPDP / Processor Governance",
            "control_area": "Third-party processing",
            "reference": "Processor oversight and contractual processing expectations",
            "legal_or_regulatory_relevance": "Supports accountability where third parties process or access personal data.",
        },
    }

    tpmr_map = {
        "vendor_due_diligence": {
            "framework": "TPMR / Vendor Risk Management",
            "control_area": "Vendor due diligence",
            "reference": "Pre-onboarding due diligence and third-party screening",
            "legal_or_regulatory_relevance": "Supports defensible vendor onboarding and risk-based third-party selection.",
        },
        "vendor_risk_rating": {
            "framework": "TPMR / Vendor Risk Management",
            "control_area": "Vendor tiering and risk classification",
            "reference": "Risk-based classification of vendors by criticality, access, service type, and impact",
            "legal_or_regulatory_relevance": "Supports proportional oversight and governance routing for high-risk vendors.",
        },
        "contractual_safeguards": {
            "framework": "TPMR / Contract Governance",
            "control_area": "Contractual safeguards",
            "reference": "Security, confidentiality, audit, compliance, evidence, and termination clauses",
            "legal_or_regulatory_relevance": "Supports enforceable vendor obligations and audit rights.",
        },
        "data_processing_agreement": {
            "framework": "TPMR / Privacy Contracting",
            "control_area": "Data Processing Agreement / Privacy Addendum",
            "reference": "Processor obligations, processing purpose, privacy addendum, and data-handling terms",
            "legal_or_regulatory_relevance": "Supports privacy accountability where vendors process or access personal data.",
        },
        "right_to_audit": {
            "framework": "TPMR / Vendor Assurance",
            "control_area": "Right to audit",
            "reference": "Audit, inspection, assurance reports, records review, and control validation rights",
            "legal_or_regulatory_relevance": "Supports independent verification of third-party controls.",
        },
        "vendor_breach_notification": {
            "framework": "TPMR / Incident Governance",
            "control_area": "Vendor breach / security incident notification",
            "reference": "Vendor incident reporting, escalation, investigation support, and notification obligations",
            "legal_or_regulatory_relevance": "Supports timely incident response and contractual accountability.",
        },
        "incident_response_sla": {
            "framework": "TPMR / Incident Governance",
            "control_area": "Incident response SLA / notification timeline",
            "reference": "Measurable breach or security incident notification window, such as 24/48/72 hours",
            "legal_or_regulatory_relevance": "Supports operational readiness and timely escalation of third-party incidents.",
        },
        "sub_processor_controls": {
            "framework": "TPMR / Fourth-Party Risk",
            "control_area": "Sub-processor / subcontractor / fourth-party controls",
            "reference": "Approval, notification, monitoring, and flow-down obligations for downstream providers",
            "legal_or_regulatory_relevance": "Supports control over vendor dependency chains and onward transfer risk.",
        },
        "security_assessment": {
            "framework": "TPMR / Security Assurance",
            "control_area": "Vendor security assessment",
            "reference": "Security assessment, questionnaire, certification, independent assurance, or control validation",
            "legal_or_regulatory_relevance": "Supports evidence-based vendor security oversight.",
        },
        "penetration_testing_requirement": {
            "framework": "TPMR / Security Assurance",
            "control_area": "Penetration testing / technical security testing",
            "reference": "Explicit penetration testing, vulnerability testing, remediation evidence, or independent technical testing",
            "legal_or_regulatory_relevance": "Supports validation of vendor technical controls beyond policy statements.",
        },
        "vendor_access_control": {
            "framework": "TPMR / Access Governance",
            "control_area": "Vendor access control",
            "reference": "Least privilege, MFA, approval, recertification, privileged monitoring, and access revocation",
            "legal_or_regulatory_relevance": "Supports prevention of unauthorized third-party access to systems and data.",
        },
        "periodic_vendor_review": {
            "framework": "TPMR / Ongoing Monitoring",
            "control_area": "Periodic vendor review",
            "reference": "Annual/periodic reassessment, monitoring, recertification, and renewal review",
            "legal_or_regulatory_relevance": "Supports continuous oversight after onboarding.",
        },
        "vendor_offboarding": {
            "framework": "TPMR / Exit Governance",
            "control_area": "Vendor offboarding",
            "reference": "Termination, transition, return of assets, access revocation, and exit responsibilities",
            "legal_or_regulatory_relevance": "Supports orderly vendor exit and reduction of residual access/data risk.",
        },
        "data_deletion_after_termination": {
            "framework": "TPMR / Data Lifecycle",
            "control_area": "Data return / deletion after termination",
            "reference": "Return, deletion, destruction, purge certification, or disposal evidence after contract termination",
            "legal_or_regulatory_relevance": "Supports data minimization and lifecycle accountability after vendor exit.",
        },
        "data_classification_framework": {
            "framework": "TPMR / Data Governance",
            "control_area": "Data classification framework",
            "reference": "Formal classification taxonomy and handling requirements by data category",
            "legal_or_regulatory_relevance": "Supports appropriate vendor handling based on sensitivity of information.",
        },
        "children_data_privacy_overlay": {
            "framework": "TPMR / Privacy Overlay",
            "control_area": "Children/minors data overlay",
            "reference": "Controls for vendors processing children/minors data and stricter privacy handling",
            "legal_or_regulatory_relevance": "Flags higher sensitivity where minors' data may be involved.",
        },
    }

    if source == "DPDP" and control_id in dpdp_map:
        return dpdp_map[control_id]

    if source == "TPMR" and control_id in tpmr_map:
        return tpmr_map[control_id]

    return tpmr_map.get(control_id) or dpdp_map.get(control_id) or default_mapping()


def infer_remediation_metadata(finding: dict) -> dict:
    control_id = str(finding.get("control_id", "")).lower()
    risk = str(finding.get("risk", "Medium")).lower()
    status = str(finding.get("status", "")).lower()

    legal_owner_controls = {
        "data_processing_agreement",
        "contractual_safeguards",
        "right_to_audit",
        "sub_processor_controls",
        "vendor_offboarding",
        "data_deletion_after_termination",
    }
    security_owner_controls = {
        "security_assessment",
        "penetration_testing_requirement",
        "vendor_access_control",
        "vendor_breach_notification",
        "incident_response_sla",
        "data_classification_framework",
    }

    if control_id in legal_owner_controls:
        owner = "Legal / Procurement / Vendor Risk"
    elif control_id in security_owner_controls:
        owner = "Information Security / Vendor Risk"
    else:
        owner = "Vendor Risk / Control Owner"

    if risk in {"critical", "high"} or status in {"failed", "missing"}:
        effort = "Medium"
        target = "30-60 days"
    else:
        effort = "Low-Medium"
        target = "60-90 days"

    return {
        "owner": owner,
        "estimated_effort": effort,
        "target_timeline": target,
    }


def infer_entity_boundary(finding: dict) -> dict:
    text_parts = [
        str(finding.get("control", "")),
        str(finding.get("expected_requirement", "")),
        " ".join(str(item.get("snippet", "")) for item in finding.get("evidence", []) if isinstance(item, dict)),
        " ".join(str(item.get("snippet", "")) for item in finding.get("candidate_evidence", []) if isinstance(item, dict)),
    ]
    text = " ".join(text_parts).lower()

    vendor_terms = ["vendor", "third-party", "third party", "supplier", "service provider", "outsourcing", "processor", "subcontractor", "sub-processor", "fourth-party"]
    internal_terms = ["employee", "staff", "department", "internal", "business owner", "management", "faculty"]

    vendor_score = sum(1 for term in vendor_terms if term in text)
    internal_score = sum(1 for term in internal_terms if term in text)

    if vendor_score > internal_score:
        boundary = "Third-Party / Vendor"
    elif internal_score > vendor_score:
        boundary = "Internal / Organization"
    else:
        boundary = "Unclear"

    return {
        "entity_boundary": boundary,
        "boundary_scores": {
            "vendor_score": vendor_score,
            "internal_score": internal_score,
        },
    }


def enhance_findings_for_consulting(findings: list[dict]) -> list[dict]:
    """Adds consulting/reporting metadata without changing rule-engine decisions."""

    enhanced = []

    for finding in findings or []:
        item = dict(finding)
        control_id = item.get("control_id")
        source = item.get("source")

        item["regulatory_mapping"] = get_regulatory_mapping(control_id, source)
        item["remediation"] = infer_remediation_metadata(item)
        item["entity_boundary_review"] = infer_entity_boundary(item)

        if not item.get("recommendation"):
            item["recommendation"] = (
                f"Define and evidence a clear control for {item.get('control', 'this area')} with owner, "
                "frequency, contractual obligation, and review evidence where applicable."
            )

        enhanced.append(item)

    return enhanced
