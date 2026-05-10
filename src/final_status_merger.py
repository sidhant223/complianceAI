def merge_rule_and_llm_status(finding: dict, llm_review: dict) -> dict:
    """
    Conservatively merges rule-based status with LLM semantic review.

    Rule engine remains source of truth.
    LLM can only:
    1. Support existing evidence
    2. Flag possible missed evidence
    3. Escalate to manual review
    """

    rule_status = finding.get("status") or finding.get("rule_status", "Unknown")
    semantic_status = llm_review.get("semantic_status", "Needs Manual Review")
    llm_available = llm_review.get("llm_review_available", False)

    normalized_rule_status = str(rule_status).lower()

    final_status = rule_status
    manual_review_required = False

    if not llm_available:
        final_status = rule_status
        manual_review_required = False

    elif normalized_rule_status == "present":
        if semantic_status == "Evidence Supports Control":
            final_status = "Present"
            manual_review_required = False

        elif semantic_status == "Contradiction Found":
            final_status = "Needs Manual Review"
            manual_review_required = True

        else:
            final_status = "Present"
            manual_review_required = False

    elif normalized_rule_status in ["missing", "partial"]:
        if semantic_status in ["Evidence Supports Control", "Possible Evidence Found"]:
            final_status = "Needs Manual Review"
            manual_review_required = True

        elif semantic_status == "No Relevant Evidence Found":
            final_status = rule_status
            manual_review_required = False

        elif semantic_status == "Contradiction Found":
            final_status = "Needs Manual Review"
            manual_review_required = True

        else:
            final_status = "Needs Manual Review"
            manual_review_required = True

    else:
        final_status = "Needs Manual Review"
        manual_review_required = True

    merged_finding = finding.copy()

    merged_finding["rule_status"] = rule_status
    merged_finding["final_status"] = final_status

    merged_finding["llm_review"] = {
        "llm_review_available": llm_review.get("llm_review_available", False),
        "semantic_status": llm_review.get("semantic_status", "Needs Manual Review"),
        "semantic_confidence": llm_review.get("semantic_confidence", "Low"),
        "semantic_reason": llm_review.get(
            "semantic_reason",
            "No LLM reason available."
        ),
        "manual_review_required": manual_review_required
    }

    return merged_finding