import json
import re
from src.ollama_client import call_ollama, check_ollama_server, DEFAULT_MODEL


ALLOWED_SEMANTIC_STATUSES = [
    "Evidence Supports Control",
    "Possible Evidence Found",
    "No Relevant Evidence Found",
    "Contradiction Found",
    "Needs Manual Review"
]

ALLOWED_CONFIDENCE = [
    "High",
    "Medium",
    "Low"
]


def build_semantic_validation_prompt(finding: dict) -> str:
    """
    Builds a very small one-finding prompt for local Ollama.
    Keep this compact so sequential reviews can cover every top finding.
    """

    control = finding.get("control", "Unknown control")
    expected_requirement = finding.get("expected_requirement", "Not provided")
    rule_status = finding.get("status") or finding.get("rule_status", "Unknown")

    evidence_text = format_evidence_for_prompt(finding.get("evidence", []), max_items=1, max_chars=350)
    candidate_text = format_evidence_for_prompt(finding.get("candidate_evidence", []), max_items=1, max_chars=350)

    prompt = f"""
You are reviewing ONE audit finding.
Return ONLY valid JSON.

Rules:
- Do not decide final compliance or score.
- Do not invent evidence.
- Use only evidence/candidate evidence below.
- Ignore table of contents, headings, and index text.
- If evidence is relevant but incomplete, use Possible Evidence Found.

Control: {control}
Expected: {expected_requirement}
Rule Status: {rule_status}

Evidence:
{evidence_text}

Candidate Evidence:
{candidate_text}

Allowed semantic_status:
Evidence Supports Control | Possible Evidence Found | No Relevant Evidence Found | Contradiction Found | Needs Manual Review

Allowed semantic_confidence:
High | Medium | Low

JSON format:
{{
  "semantic_status": "Possible Evidence Found",
  "semantic_confidence": "Medium",
  "semantic_reason": "Short evidence-based reason."
}}
"""

    return prompt.strip()

def format_evidence_for_prompt(evidence_items, max_items: int = 1, max_chars: int = 450) -> str:
    """
    Converts evidence into very compact text for local Ollama.
    Sequential mode stays enabled, so the compromise is prompt size, not review count.
    """

    if not evidence_items:
        return "No evidence provided."

    formatted = []

    for item in evidence_items[:max_items]:
        if isinstance(item, dict):
            page = item.get("page", "Unknown")
            snippet = str(item.get("snippet", ""))
            match_type = item.get("match_type", "")

            if len(snippet) > max_chars:
                snippet = snippet[:max_chars].rsplit(" ", 1)[0] + "..."

            prefix = f"Page {page}"
            if match_type:
                prefix += f" ({match_type})"

            formatted.append(f"{prefix}: {snippet}")

        else:
            text = str(item)
            formatted.append(text[:max_chars])

    return "\n".join(formatted)

def extract_json_from_response(response: str) -> dict:
    """
    Safely extracts JSON from LLM response.
    Handles cases where model adds extra text accidentally.
    """

    if not response:
        raise ValueError("Empty LLM response.")

    try:
        return json.loads(response)

    except json.JSONDecodeError:
        json_match = re.search(r"\{.*\}", response, re.DOTALL)

        if not json_match:
            raise ValueError("No valid JSON object found in LLM response.")

        return json.loads(json_match.group())


def normalize_llm_output(parsed: dict, finding: dict | None = None) -> dict:
    """
    Ensures LLM output always follows expected safe format.
    Also prevents every clear result from staying Low confidence.
    """

    semantic_status = parsed.get("semantic_status", "Needs Manual Review")
    semantic_confidence = parsed.get("semantic_confidence", "Low")
    semantic_reason = parsed.get(
        "semantic_reason",
        "LLM review completed, but no reason was provided."
    )

    if semantic_status not in ALLOWED_SEMANTIC_STATUSES:
        semantic_status = "Needs Manual Review"

    if semantic_confidence not in ALLOWED_CONFIDENCE:
        semantic_confidence = "Low"

    if finding:
        evidence = finding.get("evidence", [])
        candidate_evidence = finding.get("candidate_evidence", [])
        rule_status = str(finding.get("status", "")).lower()

        if semantic_status == "Evidence Supports Control" and evidence:
            semantic_confidence = "High"

        elif semantic_status == "Possible Evidence Found" and candidate_evidence:
            semantic_confidence = "Medium"

        elif (
            semantic_status == "No Relevant Evidence Found"
            and rule_status == "missing"
            and not evidence
            and not candidate_evidence
        ):
            semantic_confidence = "Medium"

        elif semantic_status == "Contradiction Found":
            semantic_confidence = "High" if evidence or candidate_evidence else "Medium"

        elif semantic_status == "Needs Manual Review":
            semantic_confidence = "Low"

    return {
        "semantic_status": semantic_status,
        "semantic_confidence": semantic_confidence,
        "semantic_reason": semantic_reason
    }



CONTROL_KEYWORD_STOPWORDS = {
    "control", "management", "risk", "vendor", "policy", "the", "a", "of", "and", "for", "in", "to", "with"
}


def extract_control_keywords(control_name: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z]{4,}", str(control_name or "").lower())
    return [token for token in tokens if token not in CONTROL_KEYWORD_STOPWORDS]


def apply_retrieval_mismatch_guard(
    finding: dict,
    llm_result: dict,
    document_context: dict | None = None
) -> dict:
    """
    Overrides clearly inconsistent no-evidence LLM verdicts.
    Example: title/headers mention the control topic, but LLM says no relevant evidence.
    """

    if not document_context:
        return llm_result

    semantic_status = llm_result.get("semantic_status")
    if semantic_status not in {"No Relevant Evidence Found", "Missing"}:
        return llm_result

    control_name = str(finding.get("control") or finding.get("control_title") or "")
    keywords = extract_control_keywords(control_name)

    if not keywords:
        return llm_result

    title_context = " ".join([
        str(document_context.get("document_title", "")),
        str(document_context.get("document_first_500_tokens", "")),
    ]).lower()

    section_context = " ".join(
        str(header) for header in document_context.get("weighted_section_headers", [])
    ).lower()

    title_hits = sum(1 for keyword in keywords if keyword in title_context)
    section_hits = sum(1 for keyword in keywords if keyword in section_context)

    if title_hits >= 2 or section_hits >= 2:
        flags = document_context.setdefault("retrieval_mismatch_flags", [])
        if control_name and control_name not in flags:
            flags.append(control_name)

        llm_result = dict(llm_result)
        llm_result["semantic_status"] = "Needs Manual Review"
        llm_result["semantic_confidence"] = "Low"
        llm_result["semantic_reason"] = (
            "Retrieval mismatch guard triggered: document title or weighted section headers contain the control topic, "
            "but the LLM returned no relevant evidence. Human review is required."
        )
        llm_result["retrieval_mismatch"] = True
        llm_result["mismatch_action"] = "Overridden to Needs Manual Review"
        return llm_result

    return llm_result

def build_fallback_review(finding: dict, reason: str | None = None) -> dict:
    """
    Honest fallback review used when local Ollama is unavailable or times out.
    It does not pretend that semantic review was completed.
    """

    candidate_evidence = finding.get("candidate_evidence", [])

    if candidate_evidence:
        semantic_confidence = "Medium"
        semantic_reason = (
            "Fallback Review Applied: local LLM did not complete this review. "
            "Candidate evidence exists, so the rule-based finding was retained and marked for manual validation."
        )
    else:
        semantic_confidence = "Low"
        semantic_reason = (
            "Fallback Review Applied: local LLM did not complete this review. "
            "Rule-based finding was retained and should be manually validated if relied upon externally."
        )

    return {
        "llm_review_available": False,
        "fallback_used": True,
        "semantic_status": "Needs Manual Review",
        "semantic_confidence": semantic_confidence,
        "semantic_reason": semantic_reason,
        "llm_raw_response": None,
        "retrieval_mismatch": False,
        "mismatch_action": "Fallback Review Applied",
        "internal_failure_reason": str(reason or "Local LLM was unavailable or timed out."),
    }

def call_ollama_with_timeout(prompt: str, timeout_seconds: int = 35) -> str:
    """
    Calls Ollama with a hard per-finding timeout.

    The timeout is passed directly into requests through src.ollama_client.call_ollama,
    so a slow model cannot silently stall the full audit.
    """

    return call_ollama(
        prompt=prompt,
        timeout=timeout_seconds,
        num_predict=120,
    )


def check_ollama_preflight(timeout_seconds: int = 8) -> dict:
    """
    Lightweight preflight check.

    This checks /api/tags through ollama_client.check_ollama_server.
    It does NOT require a generation test, because slow local generation can
    incorrectly disable the LLM layer even when Ollama is actually running.
    """

    result = check_ollama_server(
        model=DEFAULT_MODEL,
        timeout=timeout_seconds,
    )

    if result.get("available"):
        return {
            "available": True,
            "server_alive": result.get("server_alive", True),
            "model_available": result.get("model_available", True),
            "model": result.get("model", DEFAULT_MODEL),
            "message": result.get(
                "message",
                "Ollama server check passed. Sequential LLM review will be attempted."
            ),
        }

    return {
        "available": False,
        "server_alive": result.get("server_alive", False),
        "model_available": result.get("model_available", False),
        "model": result.get("model", DEFAULT_MODEL),
        "message": result.get(
            "message",
            "Local LLM was unavailable during the server preflight check. "
            "LLM calls were skipped and rule-based findings were retained for manual validation."
        ),
    }

def validate_finding_with_llm(
    finding: dict,
    document_context: dict | None = None,
    retry_count: int = 1
) -> dict:
    """
    Fault-tolerant local Ollama review for one finding.

    It attempts the LLM call, retries once, and then returns a conservative
    fallback review instead of leaving the finding without review data.
    """

    prompt = build_semantic_validation_prompt(finding)
    last_error = None

    for attempt in range(retry_count + 1):
        try:
            response = call_ollama_with_timeout(prompt, timeout_seconds=35)
            parsed = extract_json_from_response(response)
            normalized = normalize_llm_output(parsed, finding=finding)

            llm_result = {
                "llm_review_available": True,
                "fallback_used": False,
                "semantic_status": normalized["semantic_status"],
                "semantic_confidence": normalized["semantic_confidence"],
                "semantic_reason": normalized["semantic_reason"],
                "llm_raw_response": None,
                "retrieval_mismatch": False,
                "mismatch_action": "N/A"
            }

            return apply_retrieval_mismatch_guard(
                finding=finding,
                llm_result=llm_result,
                document_context=document_context
            )

        except Exception as error:
            last_error = error
            continue

    return build_fallback_review(finding, reason=str(last_error))

def get_llm_review_selection_reason(finding: dict) -> str:
    """
    Explains why a finding was selected for LLM review.
    This makes the report defensible for senior review.
    """

    reasons = []

    status = str(finding.get("status", "")).lower()
    risk = str(finding.get("risk", "")).lower()
    evidence = finding.get("evidence", [])
    candidate_evidence = finding.get("candidate_evidence", [])

    if status in ["failed", "missing", "partial", "needs manual review"]:
        reasons.append(f"rule status is {finding.get('status', 'Unknown')}")

    if risk == "high":
        reasons.append("risk level is High")

    if not evidence:
        reasons.append("no direct evidence was found")

    if candidate_evidence:
        reasons.append("candidate evidence requires semantic validation")

    if not reasons:
        return "Finding did not meet LLM review criteria."

    return "; ".join(reasons)


def add_llm_semantic_reviews(
    audit_result: dict,
    max_reviews: int | None = None,
    document_context: dict | None = None
) -> dict:
    """
    Adds dynamic sequential LLM semantic review.

    Meaning:
    - The PDF is uploaded once.
    - Rule engine generates top_findings once.
    - LLM reviews eligible findings one by one.
    - Each Ollama call receives only one finding.
    - max_reviews=None means review all eligible generated findings.
    - max_reviews=3 means review only first 3 eligible findings as safety cap.
    - Rule engine remains the source of truth.
    """

    if not audit_result:
        return audit_result

    if document_context is None:
        document_context = audit_result.get("document_context", {})

    top_findings = audit_result.get("top_findings", [])

    if not top_findings:
        audit_result["llm_semantic_review_summary"] = {
            "enabled": False,
            "review_mode": "Sequential Fault-Tolerant LLM Review",
            "llm_preflight_available": None,
            "llm_preflight_message": "No top findings were available, so preflight was not required.",
            "reviewed_findings": 0,
            "attempted_findings": 0,
            "eligible_findings": 0,
            "total_findings": 0,
            "max_reviews": max_reviews,
            "safety_cap_enabled": max_reviews is not None,
            "semantic_validation_status": "No Findings Available",
            "note": "No top findings were available for LLM semantic review."
        }
        return audit_result

    llm_preflight = check_ollama_preflight(timeout_seconds=8)

    if document_context is not None:
        document_context["llm_preflight_available"] = llm_preflight["available"]
        document_context["llm_preflight_message"] = llm_preflight["message"]

    if not llm_preflight["available"]:
        enhanced_findings = []

        for index, finding in enumerate(top_findings, start=1):
            finding_copy = finding.copy()
            finding_copy["rule_status"] = finding_copy.get("status", "Unknown")
            finding_copy["semantic_review_mode"] = "Sequential Fault-Tolerant LLM Review"
            finding_copy["llm_review_sequence"] = index
            finding_copy["llm_review_selection_reason"] = get_llm_review_selection_reason(finding_copy)
            finding_copy["llm_review"] = build_fallback_review(
                finding_copy,
                reason=llm_preflight["message"],
            )
            finding_copy["final_status"] = finding_copy.get("final_status", finding_copy.get("status", "Unknown"))
            enhanced_findings.append(finding_copy)

        audit_result["top_findings"] = enhanced_findings
        audit_result["llm_semantic_review_summary"] = {
            "enabled": True,
            "review_mode": "Sequential Fault-Tolerant LLM Review",
            "llm_preflight_available": False,
            "llm_preflight_message": llm_preflight["message"],
            "llm_preflight_model": llm_preflight.get("model"),
            "reviewed_findings": len(top_findings),
            "attempted_findings": len(top_findings),
            "eligible_findings": len(top_findings),
            "total_findings": len(top_findings),
            "successful_reviews": 0,
            "successful_llm_reviews": 0,
            "fallback_reviews": len(top_findings),
            "max_reviews": max_reviews,
            "safety_cap_enabled": max_reviews is not None,
            "skipped_findings": 0,
            "llm_unavailable_count": len(top_findings),
            "semantic_validation_status": "LLM Skipped After Server Preflight Failure",
            "decision_principle": "Rule engine decides. LLM is optional. Human auditor handles ambiguity.",
            "report_warning": llm_preflight["message"],
            "note": "Local LLM server/model preflight failed, so all LLM calls were skipped. Rule-based audit completed successfully and fallback review objects were attached to every top finding.",
        }
        return audit_result

    enhanced_findings = []

    reviewed_count = 0
    attempted_count = 0
    eligible_count = 0
    skipped_count = 0
    llm_unavailable_count = 0
    llm_successful_count = 0
    fallback_count = 0

    for index, finding in enumerate(top_findings, start=1):
        finding_copy = finding.copy()

        # Review every generated top finding sequentially.
        # If there are 6 top findings, the LLM attempts 6 small one-finding calls.
        should_review = True

        finding_copy["rule_status"] = finding_copy.get("status", "Unknown")
        finding_copy["semantic_review_mode"] = "Sequential Fault-Tolerant LLM Review"
        finding_copy["llm_review_sequence"] = index
        finding_copy["llm_review_selection_reason"] = get_llm_review_selection_reason(finding_copy)

        if should_review:
            eligible_count += 1

        safety_cap_reached = (
            max_reviews is not None
            and attempted_count >= max_reviews
        )

        if should_review and not safety_cap_reached:
            attempted_count += 1

            llm_review = validate_finding_with_llm(finding_copy, document_context=document_context)

            llm_available = llm_review.get("llm_review_available", False)

            reviewed_count += 1

            if llm_available:
                llm_successful_count += 1
            else:
                llm_unavailable_count += 1

            if llm_review.get("fallback_used"):
                fallback_count += 1

            finding_copy["llm_review"] = {
                "llm_review_available": llm_available,
                "semantic_status": llm_review.get("semantic_status", "Needs Manual Review"),
                "semantic_confidence": llm_review.get("semantic_confidence", "Low"),
                "semantic_reason": llm_review.get(
                    "semantic_reason",
                    "No LLM reason available."
                ),
                "fallback_used": llm_review.get("fallback_used", False),
                "retrieval_mismatch": llm_review.get("retrieval_mismatch", False),
                "mismatch_action": llm_review.get("mismatch_action", "N/A")
            }

            finding_copy["retrieval_mismatch"] = llm_review.get("retrieval_mismatch", False)
            finding_copy["mismatch_action"] = llm_review.get("mismatch_action", "N/A")

            finding_copy["final_status"] = decide_final_status(
                rule_status=finding_copy.get("status", "Unknown"),
                semantic_status=llm_review.get("semantic_status", "Needs Manual Review"),
                llm_available=llm_available
            )

        elif should_review and safety_cap_reached:
            skipped_count += 1

            finding_copy["final_status"] = finding_copy.get(
                "final_status",
                finding_copy.get("status", "Unknown")
            )

            finding_copy["llm_review"] = {
                "llm_review_available": False,
                "semantic_status": "Not Reviewed",
                "semantic_confidence": "Low",
                "semantic_reason": (
                    "Finding was eligible for LLM review, but the optional safety cap was reached. "
                    "Rule-based status remains unchanged."
                )
            }

        else:
            skipped_count += 1

            finding_copy["final_status"] = finding_copy.get(
                "final_status",
                finding_copy.get("status", "Unknown")
            )

            finding_copy["llm_review"] = {
                "llm_review_available": False,
                "semantic_status": "Rule Based Only",
                "semantic_confidence": "Low",
                "semantic_reason": (
                    "Finding did not require LLM semantic review based on rule status, risk level, "
                    "direct evidence, and candidate evidence."
                )
            }

        enhanced_findings.append(finding_copy)

    audit_result["top_findings"] = enhanced_findings

    if fallback_count > 0:
        semantic_validation_status = "Completed With Fallback Reviews"
    elif llm_unavailable_count > 0:
        semantic_validation_status = "Completed With Manual Review Fallbacks"
    elif eligible_count == 0:
        semantic_validation_status = "No Findings Required LLM Review"
    elif max_reviews is not None and attempted_count < eligible_count:
        semantic_validation_status = "Partially Validated Due To Safety Cap"
    else:
        semantic_validation_status = "Sequentially Validated for Eligible Findings"

    audit_result["llm_semantic_review_summary"] = {
        "enabled": True,
        "review_mode": "Sequential Fault-Tolerant LLM Review",
        "llm_preflight_available": llm_preflight["available"],
        "llm_preflight_message": llm_preflight["message"],
        "llm_preflight_model": llm_preflight.get("model"),
        "reviewed_findings": reviewed_count,
        "successful_reviews": llm_successful_count,
        "successful_llm_reviews": llm_successful_count,
        "fallback_reviews": fallback_count,
        "attempted_findings": attempted_count,
        "eligible_findings": eligible_count,
        "total_findings": len(top_findings),
        "max_reviews": max_reviews,
        "safety_cap_enabled": max_reviews is not None,
        "skipped_findings": skipped_count,
        "llm_unavailable_count": llm_unavailable_count,
        "semantic_validation_status": semantic_validation_status,
        "decision_principle": (
            "Rule engine decides. LLM reviews one finding at a time. "
            "Human auditor handles ambiguity."
        ),
        "report_warning": (
            "One or more findings used a conservative fallback review because the local LLM did not complete within the allowed execution path. "
            "Risk scoring remains rule-based and the report was completed successfully."
            if fallback_count > 0
            else None
        ),
        "note": (
            "Sequential fault-tolerant LLM review was applied to every generated top finding. "
            "Each Ollama call reviewed one finding only. If the local LLM failed, a conservative fallback review was attached. "
            "Rule engine remains the source of truth."
        )
    }

    return audit_result


def decide_final_status(rule_status: str, semantic_status: str, llm_available: bool) -> str:
    """
    Conservative final status merger.
    LLM does not directly override rule-based status.
    """

    if not llm_available:
        return rule_status

    normalized_rule_status = str(rule_status).lower()

    if normalized_rule_status in ["present", "passed", "compliant"]:
        if semantic_status == "Contradiction Found":
            return "Needs Manual Review"
        return rule_status

    if normalized_rule_status in ["failed", "missing", "partial", "partially compliant"]:
        if semantic_status in ["Evidence Supports Control", "Possible Evidence Found"]:
            return "Needs Manual Review"

        if semantic_status == "No Relevant Evidence Found":
            return rule_status

        return "Needs Manual Review"

    return rule_status
