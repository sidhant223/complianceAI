from src.llm_finding_selector import select_findings_for_llm
from src.llm_semantic_validator import validate_finding_with_llm
from src.final_status_merger import merge_rule_and_llm_status


def enhance_audit_with_llm(final_audit: dict, max_findings: int = 5) -> dict:
    """
    Adds Level 2 LLM semantic review to existing final audit JSON.

    This function does not replace Level 1.
    It only enhances selected findings.
    """

    if not final_audit:
        return final_audit

    findings = final_audit.get("top_findings", [])

    if not findings:
        final_audit["llm_level_2_enabled"] = False
        final_audit["llm_usage_note"] = "No findings available for LLM review."
        return final_audit

    selected_findings = select_findings_for_llm(
        findings=findings,
        max_findings=max_findings
    )

    enhanced_findings = []

    for finding in findings:
        should_review = finding in selected_findings

        if should_review:
            llm_review = validate_finding_with_llm(finding)
            merged_finding = merge_rule_and_llm_status(finding, llm_review)
            enhanced_findings.append(merged_finding)

        else:
            unchanged_finding = finding.copy()
            rule_status = unchanged_finding.get("status") or unchanged_finding.get("rule_status", "Unknown")

            unchanged_finding["rule_status"] = rule_status
            unchanged_finding["final_status"] = rule_status
            unchanged_finding["llm_review"] = {
                "llm_review_available": False,
                "semantic_status": "Not Reviewed",
                "semantic_confidence": "Low",
                "semantic_reason": "Finding was not selected for LLM review.",
                "manual_review_required": False
            }

            enhanced_findings.append(unchanged_finding)

    final_audit["top_findings"] = enhanced_findings
    final_audit["llm_level_2_enabled"] = True
    final_audit["llm_reviewed_findings_count"] = len(selected_findings)
    final_audit["llm_usage_note"] = (
        "LLM reviewed only selected weak/high-risk findings. "
        "Rule engine remains the source of truth for scoring and evidence."
    )

    return final_audit