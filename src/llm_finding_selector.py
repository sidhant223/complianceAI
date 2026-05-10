def select_findings_for_llm(findings: list, max_findings: int = 5) -> list:
    """
    Selects only weak/high-risk findings for LLM semantic review.

    The LLM should NOT review every finding because:
    1. Local Ollama can be slow.
    2. Reviewing all findings increases latency.
    3. The rule engine is still the source of truth.
    """

    if not findings:
        return []

    selected = []

    for finding in findings:
        status = str(
            finding.get("status")
            or finding.get("rule_status")
            or ""
        ).lower()

        risk = str(finding.get("risk", "")).lower()

        evidence = finding.get("evidence", [])
        candidate_evidence = finding.get("candidate_evidence", [])

        is_missing_or_partial = status in ["missing", "partial", "needs manual review"]
        is_high_risk = risk == "high"
        has_weak_evidence = not evidence
        has_candidate_evidence = bool(candidate_evidence)

        if (
            is_missing_or_partial
            or is_high_risk
            or has_weak_evidence
            or has_candidate_evidence
        ):
            selected.append(finding)

    # Prioritize high-risk missing/partial findings first
    def priority_score(finding: dict) -> int:
        score = 0

        status = str(
            finding.get("status")
            or finding.get("rule_status")
            or ""
        ).lower()

        risk = str(finding.get("risk", "")).lower()

        if risk == "high":
            score += 3

        if status == "missing":
            score += 3

        if status == "partial":
            score += 2

        if finding.get("candidate_evidence"):
            score += 1

        return score

    selected = sorted(selected, key=priority_score, reverse=True)

    return selected[:max_findings]