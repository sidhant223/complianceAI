import json
import re

from src.ollama_client import call_ollama


def generate_llm_audit_explanation(audit_result: dict, filename: str, given_tag: str) -> dict:
    """
    Uses Ollama to generate human-readable audit explanations
    from structured rule-based findings.

    Important:
    - Rule engine remains the source of truth.
    - LLM does not decide risk, status, score, or evidence.
    - LLM only explains weak / important findings.
    - If LLM fails, the system returns a safe fallback summary.
    """

    compact_audit_data = build_compact_audit_data(
        audit_result=audit_result,
        filename=filename,
        given_tag=given_tag
    )

    prompt = build_audit_prompt(compact_audit_data)

    try:
        llm_text = call_ollama(
            prompt,
            json_mode=False,
            num_predict=220,
            timeout=180
        )

        if not llm_text or not str(llm_text).strip():
            raise ValueError("Empty response received from Ollama.")

        return {
            "llm_enabled": True,
            "llm_summary": str(llm_text).strip(),
            "llm_usage_note": (
                "This explanation was generated from structured rule-based findings. "
                "The LLM does not determine compliance status, risk scores, tag validation, or evidence."
            )
        }

    except Exception as e:
        return {
            "llm_enabled": False,
            "llm_summary": build_fallback_audit_summary(compact_audit_data),
            "llm_error": str(e),
            "llm_usage_note": (
                "LLM generation failed. A fallback rule-based explanation was generated instead. "
                "The audit result, risk score, evidence, and status remain rule-based."
            )
        }


def build_compact_audit_data(audit_result: dict, filename: str, given_tag: str) -> dict:
    """
    Keeps only important audit fields before sending to LLM.
    Avoids sending full PDF text or excessive evidence.
    """

    dpdp = audit_result.get("dpdp", {})
    tpmr = audit_result.get("tpmr", {}) 
    criticality = audit_result.get("criticality", {})
    top_findings = audit_result.get("top_findings", [])

    weak_findings = select_weak_findings(top_findings, limit=3)

    return {
        "filename": filename,
        "given_tag": given_tag,

        "overall_risk": audit_result.get("overall_risk", "Not Available"),

        "criticality": {
            "score": criticality.get("score", "Not Available"),
            "recommended_tag": criticality.get("recommended_tag", "Not Available"),
            "confidence": criticality.get("confidence", "Not Available"),
            "score_meaning": criticality.get("score_meaning", "Not Available")
        },

        "tag_validation": audit_result.get("tag_validation", "Not Available"),

        "dpdp_summary": {
            "overall_status": dpdp.get("dpdp_overall_status", "Not Available"),
            "risk_level": dpdp.get("dpdp_risk_level", "Not Available"),
            "total_controls": dpdp.get("total_controls", 0),
            "present_count": dpdp.get("compliant_count", 0),
            "partial_count": dpdp.get("partial_count", 0),
            "missing_count": dpdp.get("missing_count", 0),
            "failed_count": dpdp.get("failed_count", 0)
        },

        "tpmr_summary": {
            "overall_status": tpmr.get("tpmr_overall_status", "Not Available"),
            "risk_level": tpmr.get("tpmr_risk_level", "Not Available"),
            "total_controls": tpmr.get("total_controls", 0),
            "present_count": tpmr.get("present_count", 0),
            "partial_count": tpmr.get("partial_count", 0),
            "missing_count": tpmr.get("missing_count", 0),
            "failed_count": tpmr.get("failed_count", 0),
            "privacy_overlay_count": tpmr.get("privacy_overlay_count", 0)
        },

        "semantic_review_targets": weak_findings
    }


def select_weak_findings(findings: list, limit: int = 3) -> list:
    """
    Selects only findings where LLM can add value:
    - missing controls
    - partial controls
    - failed controls
    - high risk findings
    - vague / low-confidence findings
    """

    if not isinstance(findings, list):
        return []

    selected = []

    for finding in findings:
        if not isinstance(finding, dict):
            continue

        finding_text = json.dumps(finding, default=str).lower()

        is_weak = any(keyword in finding_text for keyword in [
            "missing",
            "partial",
            "failed",
            "high",
            "critical",
            "weak",
            "vague",
            "not found",
            "low confidence",
            "review",
            "needs manual review"
        ])

        if is_weak:
            selected.append(compact_finding(finding))

        if len(selected) >= limit:
            break

    if not selected:
        selected = [
            compact_finding(f)
            for f in findings[:limit]
            if isinstance(f, dict)
        ]

    return selected


def compact_finding(finding: dict) -> dict:
    """
    Removes overly long fields from each finding.
    Keeps the LLM input small and focused.
    """

    compact = {}

    possible_keys = [
        "framework",
        "category",
        "control",
        "requirement",
        "expected_requirement",
        "status",
        "final_status",
        "risk",
        "risk_level",
        "severity",
        "recommendation",
        "reason",
        "confidence",
        "match_type"
    ]

    for key in possible_keys:
        if key in finding:
            compact[key] = trim_text(finding.get(key), max_chars=180)

    llm_review = finding.get("llm_semantic_review")
    if isinstance(llm_review, dict):
        compact["llm_semantic_review"] = {
            "semantic_status": trim_text(
                llm_review.get("semantic_status", "Not Available"),
                max_chars=80
            ),
            "semantic_confidence": trim_text(
                llm_review.get("semantic_confidence", "Not Available"),
                max_chars=80
            ),
            "semantic_reason": trim_text(
                llm_review.get("semantic_reason", "Not Available"),
                max_chars=180
            )
        }

    evidence = finding.get("evidence", [])
    candidate_evidence = finding.get("candidate_evidence", [])

    compact["evidence"] = compact_evidence_list(evidence, limit=1)
    compact["candidate_evidence"] = compact_evidence_list(candidate_evidence, limit=1)

    if not compact:
        for key, value in list(finding.items())[:5]:
            compact[key] = trim_text(value, max_chars=150)

    return compact


def compact_evidence_list(evidence_list, limit: int = 1) -> list:
    """
    Keeps only very short evidence snippets for report writing.
    """

    if not isinstance(evidence_list, list):
        return []

    compact_items = []

    for item in evidence_list[:limit]:
        if isinstance(item, dict):
            compact_items.append({
                "page": item.get("page", "Not Available"),
                "snippet": trim_text(item.get("snippet", ""), max_chars=180)
            })
        else:
            compact_items.append({
                "page": "Not Available",
                "snippet": trim_text(item, max_chars=180)
            })

    return compact_items


def trim_text(value, max_chars: int = 180) -> str:
    """
    Converts values to safe short text.
    """

    if value is None:
        return ""

    text = str(value)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) > max_chars:
        return text[:max_chars] + "..."

    return text


def build_audit_prompt(compact_audit_data: dict) -> str:
    """
    Builds a short strict prompt so local Ollama does not time out.
    """

    audit_json = json.dumps(compact_audit_data, indent=2, ensure_ascii=False)

    return f"""
You are a compliance audit reporting assistant.

Use ONLY the structured audit data below.
Do NOT invent evidence.
Do NOT create new controls.
Do NOT change scores, risks, statuses, tag validation, or findings.
Do NOT claim legal certainty.

Structured audit data:
{audit_json}

Write a concise audit-style management summary in this exact format:

1. Executive Summary
Give 3 short lines on overall risk and audit posture.

2. Key Observations
Summarize DPDP posture, TPMR/vendor risk posture, and criticality tag result.

3. Semantic Review Notes
Mention weak or ambiguous findings that need manual review.

4. Recommended Next Actions
Give 3 practical remediation actions based only on the provided findings.

Maximum length: 220 words.
Do not repeat the JSON.
"""


def build_fallback_audit_summary(compact_audit_data: dict) -> str:
    """
    Safe non-LLM fallback summary.
    This keeps PDF/report generation working even if Ollama fails.
    """

    filename = compact_audit_data.get("filename", "Uploaded file")
    overall_risk = compact_audit_data.get("overall_risk", "Not Available")

    criticality = compact_audit_data.get("criticality", {})
    dpdp = compact_audit_data.get("dpdp_summary", {})
    tpmr = compact_audit_data.get("tpmr_summary", {})
    tag_validation = compact_audit_data.get("tag_validation", "Not Available")

    weak_findings = compact_audit_data.get("semantic_review_targets", [])

    lines = []

    lines.append("1. Executive Summary")
    lines.append(
        f"The audit was completed for {filename}. "
        f"The overall rule-based risk rating is {overall_risk}. "
        "The findings were generated using deterministic checklist validation and evidence matching."
    )

    lines.append("\n2. Key Observations")
    lines.append(
        f"Criticality recommended tag: {criticality.get('recommended_tag', 'Not Available')}. "
        f"Confidence: {criticality.get('confidence', 'Not Available')}. "
        f"Tag validation result: {tag_validation}."
    )
    lines.append(
        f"DPDP status: {dpdp.get('overall_status', 'Not Available')}. "
        f"Risk level: {dpdp.get('risk_level', 'Not Available')}. "
        f"Present: {dpdp.get('present_count', 0)}, "
        f"Partial: {dpdp.get('partial_count', 0)}, "
        f"Missing: {dpdp.get('missing_count', 0)}, "
        f"Failed: {dpdp.get('failed_count', 0)}."
    )
    lines.append(
        f"TPMR status: {tpmr.get('overall_status', 'Not Available')}. "
        f"Risk level: {tpmr.get('risk_level', 'Not Available')}. "
        f"Present: {tpmr.get('present_count', 0)}, "
        f"Partial: {tpmr.get('partial_count', 0)}, "
        f"Missing: {tpmr.get('missing_count', 0)}, "
        f"Failed: {tpmr.get('failed_count', 0)}."
    )

    lines.append("\n3. Semantic Review Notes")
    if weak_findings:
        lines.append(
            "The following findings require attention because they were identified as missing, partial, failed, high-risk, or ambiguous:"
        )

        for index, finding in enumerate(weak_findings, start=1):
            control = (
                finding.get("control")
                or finding.get("requirement")
                or finding.get("expected_requirement")
                or finding.get("category")
                or "Unnamed control"
            )

            status = finding.get("final_status") or finding.get("status", "Not Available")
            risk = (
                finding.get("risk_level")
                or finding.get("risk")
                or finding.get("severity")
                or "Not Available"
            )

            lines.append(
                f"{index}. {control} | Status: {status} | Risk: {risk}"
            )
    else:
        lines.append("No specific semantic review targets were available from the top findings.")

    lines.append("\n4. Recommended Next Actions")
    lines.append(
        "1. Review findings marked Missing, Partial, Failed, or Needs Manual Review."
    )
    lines.append(
        "2. Add clearer contractual clauses, ownership details, timelines, and measurable compliance obligations."
    )
    lines.append(
        "3. Strengthen privacy, vendor-risk, incident response, audit-support, and evidence-retention requirements."
    )

    return "\n".join(lines)