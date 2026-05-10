from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import os
import shutil
import re

from src.pdf_extractor import extract_text_from_pdf
from src.criticality_detector import detect_criticality_signals
from src.criticality_scorer import calculate_criticality_score
from src.tag_validator import validate_given_tag
from src.pdf_report_generator import (
    generate_detection_pdf_report,
    generate_tag_validation_pdf_report
)
from src.dpdp_checker import analyze_dpdp_compliance
from src.dpdp_pdf_report_generator import generate_dpdp_pdf_report
from src.document_context_classifier import classify_document_context
from src.tpmr_checker import analyze_tpmr_compliance
from src.tpmr_pdf_report_generator import generate_tpmr_pdf_report
from src.final_audit_pdf_generator import generate_final_audit_pdf_report
from src.llm_semantic_validator import add_llm_semantic_reviews
from src.evidence_context_filter import filter_candidate_evidence_for_findings
from src.finding_enhancer import enhance_findings_for_consulting


app = FastAPI(
    title="Local AI Policy Compliance Backend",
    description="Backend for criticality validation, DPDP compliance, and TPMR audit automation",
    version="1.0.0"
)

UPLOAD_DIR = "data/uploads"
REPORT_DIR = "reports"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "Policy Compliance Backend is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "backend": "running",
        "service": "criticality-dpdp-tpmr-audit-engine"
    }


def save_uploaded_pdf(file: UploadFile) -> str:
    """
    Saves uploaded PDF and returns file path.
    Reusable helper function for all endpoints.
    """

    if not file.filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path


def normalize_given_tag_simple(given_tag: str) -> dict:
    """
    Normalizes auditor-entered tag values into standard risk tags.
    Example:
    moderate / fair / yellow -> Medium
    catastrophic / severe / red -> Critical
    """

    tag_map = {
        "low": "Low",
        "minor": "Low",
        "green": "Low",
        "basic": "Low",

        "medium": "Medium",
        "moderate": "Medium",
        "fair": "Medium",
        "yellow": "Medium",
        "mid": "Medium",

        "high": "High",
        "major": "High",
        "serious": "High",
        "orange": "High",

        "critical": "Critical",
        "catastrophic": "Critical",
        "severe": "Critical",
        "red": "Critical"
    }

    raw_tag = str(given_tag or "").strip()
    normalized_tag = tag_map.get(raw_tag.lower())

    return {
        "raw_tag": raw_tag,
        "normalized_tag": normalized_tag or "Needs Human Review",
        "normalization_status": "Normalized" if normalized_tag else "Invalid",
        "normalization_note": (
            f"Input tag '{raw_tag}' was normalized to '{normalized_tag}'."
            if normalized_tag
            else "Input tag could not be normalized to Low, Medium, High, or Critical."
        )
    }


def analyze_policy_file(file_path: str) -> dict:
    """
    Common backend analysis function.
    Used by both JSON endpoint and PDF endpoint.
    """

    pages = extract_text_from_pdf(file_path)

    signals = detect_criticality_signals(pages)

    found_signals = [
        signal_name
        for signal_name, details in signals.items()
        if details["found"]
    ]

    score_result = calculate_criticality_score(signals)

    return {
        "pages": pages,
        "signals": signals,
        "found_signals": found_signals,
        "score_result": score_result
    }

def build_full_text_from_pages(pages: list[dict]) -> str:
    """
    Combines extracted PDF pages into one lowercase text block.
    Used for generic framework applicability checks.
    """

    if not pages:
        return ""

    return "\n".join(
        str(page.get("text", ""))
        for page in pages
        if isinstance(page, dict)
    ).lower()


def count_keyword_hits(text: str, keywords: list[str]) -> int:
    """
    Counts how many framework/domain indicators appear in the document.
    """

    if not text:
        return 0

    return sum(
        1
        for keyword in keywords
        if keyword.lower() in text
    )


DOCUMENT_TYPE_PATTERNS = {
    "audit_report": [
        r"\binternal audit report\b",
        r"\baudit report\b",
        r"\baudit objective\b",
        r"\baudit scope\b",
        r"\baudit methodology\b",
        r"\baudit results\b",
        r"\baudit opinion\b",
        r"\bissue\s+\d+\b",
        r"\brecommendation\s+\d+\b",
        r"\bmanagement action plan\b",
        r"\bmanagement response\b",
        r"\bsome improvement needed\b",
        r"\bmajor improvement needed\b",
    ],
    "policy": [
        r"\bpolicy\b",
        r"\bprocedure\b",
        r"\bstandard\b",
        r"\bguideline\b",
        r"\bpurpose\b",
        r"\bscope\b",
        r"\bshall\b",
        r"\bmust\b",
        r"\bresponsible for\b",
    ],
    "framework": [
        r"\bframework\b",
        r"\bprinciples\b",
        r"\bguidance\b",
        r"\brisk management principles\b",
        r"\bgovernance framework\b",
        r"\bsupervisory\b",
        r"\bcommittee\b",
    ],
    "procedure": [
        r"\bprocedure\b",
        r"\bprocess steps\b",
        r"\bstep\s+\d+\b",
        r"\bworkflow\b",
        r"\boperating procedure\b",
        r"\bsop\b",
        r"\bhow to\b",
    ],
}

AUDIT_FORMAT_PATTERNS = {
    "iia": {
        "score_threshold": 4,
        "patterns": [
            r"\binternal audit report\b",
            r"\binternal audit service\b",
            r"\binstitute of internal auditors\b",
            r"\bIIA\b",
            r"\baudit objective\b",
            r"\baudit scope\b",
            r"\baudit methodology\b",
            r"\baudit results\b",
            r"\bmanagement action plan\b",
            r"\brecommendation\s+\d+\b",
            r"\bissue\s+\d+\b",
            r"\bsome improvement needed\b",
            r"\bmajor improvement needed\b",
        ],
    },
    "consulting_management_letter": {
        "score_threshold": 4,
        "patterns": [
            r"\bmanagement letter\b",
            r"\badvisory report\b",
            r"\bconsulting report\b",
            r"\bobservations and recommendations\b",
            r"\bcurrent state assessment\b",
            r"\bfuture state\b",
            r"\bgap assessment\b",
            r"\bcontrol gap\b",
            r"\broot cause\b",
            r"\bmanagement response\b",
            r"\bmanagement action\b",
            r"\brisk rating\b",
            r"\bimpact assessment\b",
            r"\blikelihood\b",
            r"\bremediation plan\b",
            r"\btarget date\b",
            r"\baction owner\b",
            r"\bhigh priority\b",
            r"\bmedium priority\b",
            r"\blow priority\b",
            r"\bkey observation\b",
            r"\brecommendation\b",
        ],
    },
    "iso": {
        "score_threshold": 4,
        "patterns": [
            r"\bISO\b",
            r"\bISO\s*27001\b",
            r"\bISO\s*9001\b",
            r"\bclause\s+\d+",
            r"\bnonconformity\b",
            r"\bminor nonconformity\b",
            r"\bmajor nonconformity\b",
            r"\bcorrective action\b",
            r"\bsurveillance audit\b",
            r"\bcertification audit\b",
            r"\baudit criteria\b",
            r"\baudit evidence\b",
        ],
    },
    "soc": {
        "score_threshold": 4,
        "patterns": [
            r"\bSOC\s*2\b",
            r"\bSOC\s*1\b",
            r"\bType\s*I\b",
            r"\bType\s*II\b",
            r"\btrust services criteria\b",
            r"\bTSC\b",
            r"\bcontrol objective\b",
            r"\bcontrol activity\b",
            r"\boperating effectiveness\b",
            r"\bdesign effectiveness\b",
            r"\bcomplementary user entity controls\b",
            r"\bCUEC\b",
        ],
    },
}


def score_regex_patterns(text: str, patterns: list[str]) -> int:
    return sum(1 for pattern in patterns if re.search(pattern, text or "", flags=re.IGNORECASE))


def detect_audit_format(text: str) -> dict:
    scores = {}

    for audit_format, config in AUDIT_FORMAT_PATTERNS.items():
        scores[audit_format] = score_regex_patterns(text, config["patterns"])

    top_format = max(scores, key=scores.get) if scores else "unknown"
    top_score = scores.get(top_format, 0)
    sorted_scores = sorted(scores.values(), reverse=True)
    second_score = sorted_scores[1] if len(sorted_scores) > 1 else 0
    confidence = round(top_score / (top_score + second_score + 0.001), 2) if top_score else 0.0

    if top_score < AUDIT_FORMAT_PATTERNS[top_format]["score_threshold"]:
        return {
            "audit_format": "unknown",
            "audit_format_confidence": confidence,
            "audit_format_scores": scores,
        }

    return {
        "audit_format": top_format,
        "audit_format_confidence": confidence,
        "audit_format_scores": scores,
    }



def confirm_audit_report_from_title_or_first_page(title_guess: str, first_page_text: str) -> dict:
    """
    Second signal for audit-report activation. Audit mode activates only when
    the classifier winner is audit_report AND the title/first page confirms it.
    """

    combined = f"{title_guess or ''}\n{first_page_text or ''}".lower()
    confirmation_patterns = [
        r"\binternal audit report\b",
        r"\baudit report\b",
        r"\bthematic audit\b",
        r"\baudit objective\b",
        r"\baudit results\b",
        r"\bmanagement action plan\b",
        r"\brecommendation\s+\d+\b",
        r"\bissue\s+\d+\b",
        r"\baudit opinion\b",
    ]
    matched = [pattern for pattern in confirmation_patterns if re.search(pattern, combined, flags=re.IGNORECASE)]
    return {
        "audit_title_confirmation": len(matched) > 0,
        "audit_title_confirmation_matches": matched[:5],
    }


def classify_document_type(pages: list[dict]) -> dict:
    """
    Universal document type classifier.

    Audit-report mode uses two-signal activation:
    1. classifier winner must be audit_report
    2. title / first page must independently confirm audit-report language
    """

    text = build_full_text_from_pages(pages)

    classifier_scores = {
        document_type: score_regex_patterns(text, patterns)
        for document_type, patterns in DOCUMENT_TYPE_PATTERNS.items()
    }

    top_type = max(classifier_scores, key=classifier_scores.get) if classifier_scores else "unknown"
    top_score = classifier_scores.get(top_type, 0)
    sorted_scores = sorted(classifier_scores.values(), reverse=True)
    second_score = sorted_scores[1] if len(sorted_scores) > 1 else 0
    classifier_confidence = round(top_score / (top_score + second_score + 0.001), 2) if top_score else 0.0

    document_type = top_type if top_score >= 3 else "unknown"

    first_page_text = str(pages[0].get("text", "")) if pages else ""
    title_guess = clean_context_title(first_page_text)
    title_confirmation = confirm_audit_report_from_title_or_first_page(
        title_guess=title_guess,
        first_page_text=first_page_text,
    )

    audit_report_mode = (
        document_type == "audit_report"
        and title_confirmation["audit_title_confirmation"] is True
    )

    audit_format_result = detect_audit_format(text)
    first_500_tokens = " ".join(text.split()[:500])

    return {
        "document_type": document_type,
        "audit_report_mode": audit_report_mode,
        "classifier_confidence": classifier_confidence,
        "classifier_scores": classifier_scores,
        "classifier_winner": top_type,
        "classifier_top_score": top_score,
        "classifier_second_score": second_score,
        "audit_title_confirmation": title_confirmation["audit_title_confirmation"],
        "audit_title_confirmation_matches": title_confirmation["audit_title_confirmation_matches"],
        "audit_format": audit_format_result["audit_format"],
        "audit_format_confidence": audit_format_result["audit_format_confidence"],
        "audit_format_scores": audit_format_result["audit_format_scores"],
        "document_title": title_guess,
        "document_first_500_tokens": first_500_tokens,
        "weighted_section_headers": [],
        "section_tag_map": {},
        "sections_used_for_scoring": [],
        "negative_detection_active": audit_report_mode,
        "attribution_filter_active": audit_report_mode,
        "retrieval_mismatch_flags": [],
        "llm_preflight_available": None,
        "llm_preflight_message": "Not checked yet.",
    }

def clean_context_title(text: str) -> str:
    lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
    return " | ".join(lines[:4])[:500]


def determine_framework_applicability(
    pages: list[dict],
    document_context: dict | None = None
) -> dict:
    """
    Generic framework applicability engine.

    Purpose:
    Avoid category errors by checking whether a framework is actually in scope
    before scoring/reporting missing controls.

    This is NOT hardcoded to one document type.
    It uses domain signal groups:
    - privacy / data protection
    - third-party / vendor risk
    - security governance
    - financial / prudential
    - HR / employee
    - engineering / procurement
    - legal / contract
    """

    text = build_full_text_from_pages(pages)

    domain_keywords = {
        "privacy_data_protection": [
            "personal data",
            "personally identifiable information",
            "pii",
            "data principal",
            "data subject",
            "consent",
            "withdrawal of consent",
            "privacy notice",
            "data fiduciary",
            "data processor",
            "grievance officer",
            "right to correction",
            "right to erasure",
            "children's data",
            "data protection",
            "dpdp",
            "privacy policy",
            "processing of personal data"
        ],

        "third_party_vendor": [
            "third party",
            "third-party",
            "vendor",
            "supplier",
            "service provider",
            "outsourcing",
            "sub-processor",
            "subprocessor",
            "due diligence",
            "vendor risk",
            "third party risk",
            "right to audit",
            "data processing agreement",
            "contractual safeguards",
            "sla",
            "service level agreement"
        ],

        "security_governance": [
            "information security",
            "cybersecurity",
            "access control",
            "encryption",
            "mfa",
            "multi-factor authentication",
            "incident response",
            "vulnerability",
            "security assessment",
            "security controls",
            "iso 27001",
            "soc 2",
            "nist",
            "security monitoring",
            "audit logs"
        ],

        "financial_prudential": [
            "capital adequacy",
            "liquidity",
            "leverage ratio",
            "credit risk",
            "market risk",
            "operational risk",
            "risk weighted assets",
            "rwa",
            "banking supervision",
            "supervisory review",
            "prudential",
            "stress testing",
            "capital buffer",
            "tier 1 capital",
            "regulatory capital"
        ],

        "hr_employee_policy": [
            "employee",
            "employment",
            "leave policy",
            "payroll",
            "performance review",
            "workplace conduct",
            "disciplinary",
            "attendance",
            "recruitment",
            "termination policy"
        ],

        "engineering_procurement": [
            "request for proposal",
            "rfp",
            "tender",
            "bidder",
            "scope of work",
            "construction",
            "engineering",
            "technical specification",
            "bill of quantities",
            "boq",
            "project site",
            "contractor"
        ],

        "legal_contract": [
            "agreement",
            "contract",
            "liability",
            "indemnity",
            "termination",
            "governing law",
            "confidentiality",
            "warranty",
            "representations",
            "obligations",
            "dispute resolution"
        ]
    }

    domain_scores = {
        domain: count_keyword_hits(text, keywords)
        for domain, keywords in domain_keywords.items()
    }

    detected_domains = [
        domain
        for domain, score in domain_scores.items()
        if score >= 2
    ]

    primary_domain = (
        max(domain_scores, key=domain_scores.get)
        if domain_scores
        else "unknown"
    )

    if domain_scores.get(primary_domain, 0) < 2:
        primary_domain = "unknown"

    context_dpdp = True
    context_tpmr = True

    if document_context:
        context_dpdp = document_context.get("dpdp_applicable", True)
        context_tpmr = document_context.get("tpmr_applicable", True)

    privacy_score = domain_scores.get("privacy_data_protection", 0)
    vendor_score = domain_scores.get("third_party_vendor", 0)
    security_score = domain_scores.get("security_governance", 0)

    # Generic applicability rules
    dpdp_applicable = (
        context_dpdp
        and privacy_score >= 2
    )

    tpmr_applicable = (
        context_tpmr
        and vendor_score >= 2
    )

    security_applicable = security_score >= 2

    return {
        "primary_domain": primary_domain,
        "detected_domains": detected_domains,
        "domain_scores": domain_scores,

        "frameworks": {
            "dpdp": {
                "applicable": dpdp_applicable,
                "confidence": calculate_applicability_confidence(privacy_score),
                "reason": (
                    "Privacy/data-protection indicators were detected."
                    if dpdp_applicable
                    else "Insufficient privacy/personal-data indicators were found. DPDP controls are treated as out of scope."
                )
            },
            "tpmr": {
                "applicable": tpmr_applicable,
                "confidence": calculate_applicability_confidence(vendor_score),
                "reason": (
                    "Third-party/vendor risk indicators were detected."
                    if tpmr_applicable
                    else "Insufficient vendor/outsourcing indicators were found. TPMR controls are treated as out of scope."
                )
            },
            "security": {
                "applicable": security_applicable,
                "confidence": calculate_applicability_confidence(security_score),
                "reason": (
                    "Security governance indicators were detected."
                    if security_applicable
                    else "Insufficient security-control indicators were found."
                )
            }
        },

        "applicability_reason": (
            "Framework applicability was determined using generic domain signal groups, "
            "not by hardcoding a specific document name or standard."
        )
    }


def calculate_applicability_confidence(score: int) -> str:
    """
    Converts keyword/domain hit count into a simple confidence label.
    """

    if score >= 5:
        return "High"

    if score >= 2:
        return "Medium"

    if score == 1:
        return "Low"

    return "Very Low"


def mark_dpdp_not_applicable(dpdp_result: dict, reason: str) -> dict:
    """
    Converts DPDP result into an out-of-scope result.
    Prevents privacy-control gaps from being reported on non-privacy documents.
    """

    return {
        **dpdp_result,
        "dpdp_overall_status": "Not Applicable",
        "dpdp_risk_level": "Not Applicable",
        "missing_count": 0,
        "failed_count": 0,
        "partial_count": 0,
        "compliant_count": 0,
        "applicability_status": "Out of Scope",
        "applicability_reason": reason,
        "findings": []
    }


def mark_tpmr_not_applicable(tpmr_result: dict, reason: str) -> dict:
    """
    Converts TPMR result into an out-of-scope result.
    Prevents vendor-risk gaps from being reported on documents with no vendor scope.
    """

    return {
        **tpmr_result,
        "tpmr_overall_status": "Not Applicable",
        "tpmr_risk_level": "Not Applicable",
        "missing_count": 0,
        "failed_count": 0,
        "partial_count": 0,
        "present_count": 0,
        "privacy_overlay_count": 0,
        "applicability_status": "Out of Scope",
        "applicability_reason": reason,
        "findings": []
    }


def run_full_audit(file_path: str, given_tag: str) -> dict:
    """
    Runs the complete audit workflow:
    criticality validation + DPDP compliance + TPMR vendor risk.
    """

    pages = extract_text_from_pdf(file_path)

    document_context = classify_document_context(pages)

    document_type_context = classify_document_type(pages)
    document_context.update(document_type_context)

    framework_applicability = determine_framework_applicability(
        pages=pages,
        document_context=document_context
    )

    document_context["framework_applicability"] = framework_applicability
    document_context["primary_domain"] = framework_applicability["primary_domain"]
    document_context["detected_domains"] = framework_applicability["detected_domains"]
    document_context["domain_scores"] = framework_applicability["domain_scores"]
    document_context["dpdp_applicable"] = framework_applicability["frameworks"]["dpdp"]["applicable"]
    document_context["tpmr_applicable"] = framework_applicability["frameworks"]["tpmr"]["applicable"]

    signals = detect_criticality_signals(pages)

    score_result = calculate_criticality_score(signals)

    tag_normalization = normalize_given_tag_simple(given_tag)

    if tag_normalization["normalization_status"] == "Invalid":
        tag_validation = {
        "given_tag": tag_normalization["raw_tag"],
        "normalized_tag": tag_normalization["normalized_tag"],
        "recommended_tag": score_result["recommended_tag"],
        "validation_result": "Needs Human Review",
        "confidence": score_result["confidence"],
        "reason": (
            "The provided tag could not be normalized to Low, Medium, High, or Critical. "
            "A manual review penalty was applied because incorrect or unclear classification "
            "may cause governance routing risk."
        )
    }
    else:
        tag_validation = validate_given_tag(
        given_tag=tag_normalization["normalized_tag"],
        recommended_tag=score_result["recommended_tag"],
        confidence=score_result["confidence"]
    )

    raw_dpdp_result = analyze_dpdp_compliance(pages)
    raw_tpmr_result = analyze_tpmr_compliance(
        pages=pages,
        document_context=document_context
    )

    if document_context["dpdp_applicable"]:
        dpdp_result = raw_dpdp_result
    else:
        dpdp_result = mark_dpdp_not_applicable(
            raw_dpdp_result,
            framework_applicability["frameworks"]["dpdp"]["reason"]
        )

    if document_context["tpmr_applicable"]:
        tpmr_result = raw_tpmr_result
    else:
        tpmr_result = mark_tpmr_not_applicable(
            raw_tpmr_result,
            framework_applicability["frameworks"]["tpmr"]["reason"]
        )

    overall_risk = calculate_overall_audit_risk(
        criticality_tag=score_result["recommended_tag"],
        dpdp_risk=dpdp_result["dpdp_risk_level"],
        tpmr_risk=tpmr_result["tpmr_risk_level"],
        validation_result=tag_validation["validation_result"],
        dpdp_failed_count=dpdp_result.get("failed_count", 0),
        tpmr_failed_count=tpmr_result.get("failed_count", 0),
        privacy_overlay_count=tpmr_result.get("privacy_overlay_count", 0),
        document_context=document_context,
        dpdp_missing_count=dpdp_result.get("missing_count", 0),
        tpmr_missing_count=tpmr_result.get("missing_count", 0)
    )

    top_findings = extract_top_findings(
        dpdp_findings=dpdp_result["findings"],
        tpmr_findings=tpmr_result["findings"],
        document_context=document_context
    )

    return {
        "document_context": document_context,
        "tag_normalization": tag_normalization,

        "criticality": {
            "score": score_result["criticality_score"],
            "recommended_tag": score_result["recommended_tag"],
            "score_meaning": score_result["score_meaning"],
            "confidence": score_result["confidence"],
            "score_scale": score_result["score_scale"],
            "score_breakdown": score_result["score_breakdown"],
            "signals": signals
        },

        "tag_validation": tag_validation,
        "dpdp": dpdp_result,
        "tpmr": tpmr_result,
        "overall_risk": overall_risk,
        "top_findings": top_findings
    }


def calculate_overall_audit_risk(
    criticality_tag: str,
    dpdp_risk: str,
    tpmr_risk: str,
    validation_result: str,
    dpdp_failed_count: int,
    tpmr_failed_count: int,
    privacy_overlay_count: int,
    document_context: dict | None = None,
    dpdp_missing_count: int = 0,
    tpmr_missing_count: int = 0
) -> dict:
    """
    Calculates final overall audit risk from criticality, DPDP, TPMR,
    failed controls, missing controls, privacy overlay, tag validation,
    and document context.

    If DPDP is not applicable based on document context, DPDP missing/failed
    controls are excluded from effective scoring and explanation.
    """

    risk_rank = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Critical": 4
    }

    criticality_score = risk_rank.get(criticality_tag, 1)
    original_dpdp_score = risk_rank.get(dpdp_risk, 1)
    dpdp_score = original_dpdp_score
    tpmr_score = risk_rank.get(tpmr_risk, 1)

    dpdp_applicable = True

    if document_context:
        dpdp_applicable = document_context.get("dpdp_applicable", True)

    dpdp_context_adjustment = 0

    effective_dpdp_missing_count = dpdp_missing_count
    effective_dpdp_failed_count = dpdp_failed_count
    effective_dpdp_risk = dpdp_risk

    if not dpdp_applicable:
        dpdp_context_adjustment = -(dpdp_score - 1)
        dpdp_score = 1

        effective_dpdp_missing_count = 0
        effective_dpdp_failed_count = 0
        effective_dpdp_risk = "Not Applicable"

    under_classification_penalty = 0
    manual_review_penalty = 0
    dpdp_failed_controls_penalty = 0
    tpmr_failed_controls_penalty = 0
    privacy_overlay_penalty = 0

    if validation_result == "Under-classified":
        under_classification_penalty = 1.5

    if validation_result == "Needs Human Review":
        manual_review_penalty = 1.0

    if effective_dpdp_failed_count > 0:
        dpdp_failed_controls_penalty = 1

    if tpmr_failed_count > 0:
        tpmr_failed_controls_penalty = 1

    if privacy_overlay_count > 0:
        privacy_overlay_penalty = 0.5

    total_score = (
        criticality_score
        + dpdp_score
        + tpmr_score
        + under_classification_penalty
        + manual_review_penalty
        + dpdp_failed_controls_penalty
        + tpmr_failed_controls_penalty
        + privacy_overlay_penalty
    )

    if total_score >= 10:
        final_risk = "Critical"
    elif total_score >= 7:
        final_risk = "High"
    elif total_score >= 4:
        final_risk = "Medium"
    else:
        final_risk = "Low"

    if not dpdp_applicable:
        dpdp_reason = (
            "DPDP controls were treated as not applicable based on document context, "
            "so DPDP missing and failed controls were excluded from effective risk scoring."
        )
    else:
        dpdp_reason = (
            f"DPDP risk '{dpdp_risk}' was included with "
            f"DPDP missing controls '{dpdp_missing_count}' and "
            f"DPDP failed controls '{dpdp_failed_count}'."
        )

    return {
        "overall_risk": final_risk,
        "risk_score": total_score,
        "risk_score_breakdown": {
            "criticality_score_component": criticality_score,
            "original_dpdp_risk_component": original_dpdp_score,
            "effective_dpdp_risk_component": dpdp_score,
            "tpmr_risk_component": tpmr_score,
            "dpdp_context_adjustment": dpdp_context_adjustment,
            "under_classification_penalty": under_classification_penalty,
            "manual_review_penalty": manual_review_penalty,
            "dpdp_failed_controls_penalty": dpdp_failed_controls_penalty,
            "tpmr_failed_controls_penalty": tpmr_failed_controls_penalty,
            "privacy_overlay_penalty": privacy_overlay_penalty,
            "total_score": total_score
        },
        "applicability_adjustments": {
            "dpdp_applicable": dpdp_applicable,
            "original_dpdp_risk": dpdp_risk,
            "effective_dpdp_risk": effective_dpdp_risk,
            "original_dpdp_missing_controls": dpdp_missing_count,
            "effective_dpdp_missing_controls": effective_dpdp_missing_count,
            "original_dpdp_failed_controls": dpdp_failed_count,
            "effective_dpdp_failed_controls": effective_dpdp_failed_count
        },
        "reason": (
            f"Overall risk is based on criticality tag '{criticality_tag}', "
            f"TPMR risk '{tpmr_risk}', tag validation result '{validation_result}', "
            f"TPMR missing controls '{tpmr_missing_count}', "
            f"TPMR failed controls '{tpmr_failed_count}', "
            f"and privacy overlay findings '{privacy_overlay_count}'. "
            f"{dpdp_reason}"
        )
    }

def assign_finding_priority(finding: dict) -> dict:
    """
    Adds practical remediation priority so all findings do not look equally urgent.
    """

    control = str(finding.get("control", "")).lower()
    status = str(finding.get("status", "")).lower()
    risk = str(finding.get("risk", "")).lower()
    source = str(finding.get("source", "")).lower()

    p1_controls = [
        "security safeguards",
        "breach notification",
        "vendor breach notification",
        "access control",
        "encryption",
        "incident",
        "mfa",
        "data deletion after termination"
    ]

    p2_controls = [
        "data processing agreement",
        "right to audit",
        "vendor risk rating",
        "vendor due diligence",
        "sub-processor",
        "subprocessor",
        "contractual safeguards",
        "grievance"
    ]

    if status == "failed":
        priority = "P1"
        severity = "Critical"
        fix_order = 1
        priority_reason = "Control failure is explicitly indicated or negative evidence was found."

    elif any(keyword in control for keyword in p1_controls):
        priority = "P1"
        severity = "High"
        fix_order = 1
        priority_reason = "Control relates to security, incident response, deletion, or access risk."

    elif any(keyword in control for keyword in p2_controls):
        priority = "P2"
        severity = "High" if risk == "high" else "Medium"
        fix_order = 2
        priority_reason = "Control relates to governance, contracts, vendor assurance, or auditability."

    elif risk == "high":
        priority = "P2"
        severity = "Medium"
        fix_order = 2
        priority_reason = "Finding is high-risk but does not indicate immediate operational failure."

    else:
        priority = "P3"
        severity = "Medium"
        fix_order = 3
        priority_reason = "Finding is mainly a documentation or process maturity gap."

    finding["priority"] = priority
    finding["severity"] = severity
    finding["fix_order"] = fix_order
    finding["priority_reason"] = priority_reason

    return finding


def filter_findings_by_applicability(
    top_findings: list[dict],
    document_context: dict | None
) -> list[dict]:
    """
    Final safety filter.
    Removes findings from frameworks that are out of scope.
    Prevents zombie DPDP/TPMR findings after enhancement or rerouting.
    """

    if not document_context:
        return top_findings

    dpdp_applicable = document_context.get("dpdp_applicable", True)
    tpmr_applicable = document_context.get("tpmr_applicable", True)

    filtered_findings = []

    for finding in top_findings:
        source = str(finding.get("source", "")).upper()

        if source == "DPDP" and not dpdp_applicable:
            continue

        if source == "TPMR" and not tpmr_applicable:
            continue

        filtered_findings.append(finding)

    return filtered_findings


def extract_top_findings(
    dpdp_findings: list[dict],
    tpmr_findings: list[dict],
    document_context: dict | None = None
) -> list[dict]:
    """
    Extracts high-priority findings from DPDP and TPMR results.

    Important:
    - If DPDP is not applicable based on document context, DPDP findings
      are not pushed into top_findings.
    - Candidate evidence is filtered before final output.
    - Findings are enhanced with regulatory mapping, remediation metadata,
      and entity-boundary review for consulting-style output.
    """

    top_findings = []

    dpdp_applicable = True

    if document_context:
        dpdp_applicable = document_context.get("dpdp_applicable", True)

    if dpdp_applicable:
        for finding in dpdp_findings:
            if finding.get("status") == "Failed" or finding.get("risk") == "High":
                top_findings.append({
                    "source": "DPDP",
                    "control_id": finding.get("control_id"),
                    "control": finding.get("control") or finding.get("control_title"),
                    "control_title": finding.get("control_title"),
                    "description": finding.get("description"),
                    "expected_requirement": finding.get("expected_requirement"),
                    "status": finding.get("status"),
                    "final_status": finding.get("final_status", finding.get("status")),
                    "risk": finding.get("risk"),
                    "recommendation": finding.get("recommendation"),
                    "matched_keywords": finding.get("matched_keywords", []),
                    "negative_evidence_count": finding.get("negative_evidence_count", 0),
                    "evidence_count": finding.get("evidence_count", 0),
                    "evidence": finding.get("evidence", [])[:3],
                    "candidate_evidence": finding.get("candidate_evidence", [])[:3]
                })

    for finding in tpmr_findings:
        if finding.get("status") == "Failed" or finding.get("risk") == "High":
            top_findings.append({
                "source": "TPMR",
                "control_id": finding.get("control_id"),
                "control": finding.get("control") or finding.get("control_title"),
                "control_title": finding.get("control_title"),
                "description": finding.get("description"),
                "expected_requirement": finding.get("expected_requirement"),
                "status": finding.get("status"),
                "final_status": finding.get("final_status", finding.get("status")),
                "risk": finding.get("risk"),
                "recommendation": finding.get("recommendation"),
                "matched_keywords": finding.get("matched_keywords", []),
                "negative_evidence_count": finding.get("negative_evidence_count", 0),
                "evidence_count": finding.get("evidence_count", 0),
                "is_privacy_overlay": finding.get("is_privacy_overlay", False),
                "negative_signal": finding.get("negative_signal", "None"),
                "negative_signal_source": finding.get("negative_signal_source", "N/A"),
                "positive_evidence_strength": finding.get("positive_evidence_strength", "N/A"),
                "audit_report_mode": finding.get("audit_report_mode", False),
                "evidence": finding.get("evidence", [])[:3],
                "candidate_evidence": finding.get("candidate_evidence", [])[:3]
            })

    risk_order = {
        "High": 3,
        "Medium": 2,
        "Low": 1
    }

    top_findings.sort(
        key=lambda item: (
            1 if item.get("status") == "Failed" else 0,
            risk_order.get(item.get("risk"), 0),
            item.get("negative_evidence_count", 0),
            item.get("evidence_count", 0)
        ),
        reverse=True
    )

    top_findings = top_findings[:10]
    top_findings = filter_candidate_evidence_for_findings(top_findings)
    top_findings = enhance_findings_for_consulting(top_findings)
    top_findings = filter_findings_by_applicability(
        top_findings=top_findings,
        document_context=document_context
    )

    top_findings = [
        assign_finding_priority(finding)
        for finding in top_findings
    ]

    top_findings.sort(
        key=lambda item: (
            item.get("fix_order", 99),
            1 if item.get("status") == "Failed" else 0,
            risk_order.get(item.get("risk"), 0),
            item.get("negative_evidence_count", 0),
            item.get("evidence_count", 0)
        ),
        reverse=False
    )

    return top_findings


@app.post("/upload-policy")
def upload_policy(file: UploadFile = File(...)):
    try:
        file_path = save_uploaded_pdf(file)

        return {
            "status": "success",
            "message": "PDF uploaded successfully",
            "filename": file.filename,
            "saved_path": file_path
        }

    except ValueError as error:
        return {
            "status": "failed",
            "message": str(error)
        }


@app.post("/extract-policy-text")
def extract_policy_text(file: UploadFile = File(...)):
    try:
        file_path = save_uploaded_pdf(file)

        pages = extract_text_from_pdf(file_path)

        full_text = "\n".join([page["text"] for page in pages])

        return {
            "status": "success",
            "filename": file.filename,
            "total_pages": len(pages),
            "text_preview": full_text[:1500],
            "pages": pages[:2]
        }

    except ValueError as error:
        return {
            "status": "failed",
            "message": str(error)
        }


@app.post("/detect-criticality-signals")
def detect_signals(file: UploadFile = File(...)):
    try:
        file_path = save_uploaded_pdf(file)

        analysis = analyze_policy_file(file_path)

        return {
            "status": "success",
            "filename": file.filename,
            "found_signal_count": len(analysis["found_signals"]),
            "found_signals": analysis["found_signals"],
            "signals": analysis["signals"]
        }

    except ValueError as error:
        return {
            "status": "failed",
            "message": str(error)
        }


@app.post("/score-criticality-json")
def score_criticality_json(file: UploadFile = File(...)):
    """
    Returns JSON analysis only.
    Use this when you want API-style machine-readable output.
    """

    try:
        file_path = save_uploaded_pdf(file)

        analysis = analyze_policy_file(file_path)

        score_result = analysis["score_result"]

        return {
            "status": "success",
            "output_type": "json",
            "filename": file.filename,

            "criticality_score": score_result["criticality_score"],
            "recommended_tag": score_result["recommended_tag"],
            "score_meaning": score_result["score_meaning"],
            "score_scale": score_result["score_scale"],

            "found_signal_count": len(analysis["found_signals"]),
            "found_signals": analysis["found_signals"],

            "score_breakdown": score_result["score_breakdown"],
            "signals": analysis["signals"]
        }

    except ValueError as error:
        return {
            "status": "failed",
            "message": str(error)
        }


@app.post("/generate-criticality-pdf")
def generate_criticality_pdf(file: UploadFile = File(...)):
    """
    Generates and directly returns a PDF report.
    """

    try:
        file_path = save_uploaded_pdf(file)

        analysis = analyze_policy_file(file_path)

        pdf_report_filename = generate_detection_pdf_report(
            filename=file.filename,
            signals=analysis["signals"],
            score_result=analysis["score_result"]
        )

        pdf_report_path = os.path.join(REPORT_DIR, pdf_report_filename)

        return FileResponse(
            path=pdf_report_path,
            filename=pdf_report_filename,
            media_type="application/pdf"
        )

    except ValueError as error:
        return {
            "status": "failed",
            "message": str(error)
        }


@app.get("/download-detection-report/{report_filename}")
def download_detection_report(report_filename: str):
    report_path = os.path.join(REPORT_DIR, report_filename)

    if not os.path.exists(report_path):
        return {
            "status": "failed",
            "message": "Report file not found"
        }

    media_type = "application/pdf" if report_filename.endswith(".pdf") else "text/plain"

    return FileResponse(
        path=report_path,
        filename=report_filename,
        media_type=media_type
    )


@app.post("/generate-tag-validation-pdf")
def generate_tag_validation_pdf(
    given_tag: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Generates a PDF report for criticality tag validation.
    """

    try:
        file_path = save_uploaded_pdf(file)

        analysis = analyze_policy_file(file_path)

        score_result = analysis["score_result"]

        tag_normalization = normalize_given_tag_simple(given_tag)

        validation = validate_given_tag(
            given_tag=tag_normalization["normalized_tag"],
            recommended_tag=score_result["recommended_tag"],
            confidence=score_result["confidence"]
        )

        pdf_report_filename = generate_tag_validation_pdf_report(
            filename=file.filename,
            validation=validation,
            signals=analysis["signals"],
            score_result=score_result
        )

        pdf_report_path = os.path.join(REPORT_DIR, pdf_report_filename)

        return FileResponse(
            path=pdf_report_path,
            filename=pdf_report_filename,
            media_type="application/pdf"
        )

    except ValueError as error:
        return {
            "status": "failed",
            "message": str(error)
        }


@app.post("/analyze-dpdp-json")
def analyze_dpdp_json(file: UploadFile = File(...)):
    """
    Analyzes uploaded policy PDF for DPDP-style compliance controls.
    Returns JSON only.
    """

    try:
        file_path = save_uploaded_pdf(file)

        pages = extract_text_from_pdf(file_path)

        dpdp_result = analyze_dpdp_compliance(pages)

        return {
            "status": "success",
            "output_type": "json",
            "filename": file.filename,
            "dpdp_overall_status": dpdp_result["dpdp_overall_status"],
            "dpdp_risk_level": dpdp_result["dpdp_risk_level"],
            "total_controls": dpdp_result["total_controls"],
            "compliant_count": dpdp_result["compliant_count"],
            "partial_count": dpdp_result["partial_count"],
            "missing_count": dpdp_result["missing_count"],
            "failed_count": dpdp_result["failed_count"],
            "findings": dpdp_result["findings"]
        }

    except ValueError as error:
        return {
            "status": "failed",
            "message": str(error)
        }


@app.post("/generate-dpdp-pdf")
def generate_dpdp_pdf(file: UploadFile = File(...)):
    """
    Generates a downloadable PDF report for DPDP compliance analysis.
    """

    try:
        file_path = save_uploaded_pdf(file)

        pages = extract_text_from_pdf(file_path)

        dpdp_result = analyze_dpdp_compliance(pages)

        pdf_report_filename = generate_dpdp_pdf_report(
            filename=file.filename,
            dpdp_result=dpdp_result
        )

        pdf_report_path = os.path.join(REPORT_DIR, pdf_report_filename)

        return FileResponse(
            path=pdf_report_path,
            filename=pdf_report_filename,
            media_type="application/pdf"
        )

    except ValueError as error:
        return {
            "status": "failed",
            "message": str(error)
        }


@app.post("/analyze-tpmr-json")
def analyze_tpmr_json(file: UploadFile = File(...)):
    """
    Analyzes uploaded policy PDF for TPMR / vendor risk controls.
    Returns JSON only.
    """

    try:
        file_path = save_uploaded_pdf(file)

        pages = extract_text_from_pdf(file_path)

        tpmr_result = analyze_tpmr_compliance(pages)

        return {
            "status": "success",
            "output_type": "json",
            "filename": file.filename,
            "tpmr_overall_status": tpmr_result["tpmr_overall_status"],
            "tpmr_risk_level": tpmr_result["tpmr_risk_level"],
            "total_controls": tpmr_result["total_controls"],
            "present_count": tpmr_result["present_count"],
            "partial_count": tpmr_result["partial_count"],
            "missing_count": tpmr_result["missing_count"],
            "failed_count": tpmr_result["failed_count"],
            "privacy_overlay_count": tpmr_result.get("privacy_overlay_count", 0),
            "findings": tpmr_result["findings"]
        }

    except ValueError as error:
        return {
            "status": "failed",
            "message": str(error)
        }


@app.post("/generate-tpmr-pdf")
def generate_tpmr_pdf(file: UploadFile = File(...)):
    """
    Generates a downloadable PDF report for TPMR / vendor risk analysis.
    """

    try:
        file_path = save_uploaded_pdf(file)

        pages = extract_text_from_pdf(file_path)

        tpmr_result = analyze_tpmr_compliance(pages)

        pdf_report_filename = generate_tpmr_pdf_report(
            filename=file.filename,
            tpmr_result=tpmr_result
        )

        pdf_report_path = os.path.join(REPORT_DIR, pdf_report_filename)

        return FileResponse(
            path=pdf_report_path,
            filename=pdf_report_filename,
            media_type="application/pdf"
        )

    except ValueError as error:
        return {
            "status": "failed",
            "message": str(error)
        }


@app.post("/final-audit-json")
def final_audit_json(
    given_tag: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Runs complete audit workflow and returns one combined JSON report.
    """

    try:
        file_path = save_uploaded_pdf(file)

        audit_result = run_full_audit(
            file_path=file_path,
            given_tag=given_tag
        )

        return {
            "status": "success",
            "output_type": "json",
            "filename": file.filename,
            "given_tag": given_tag,
            "tag_normalization": audit_result.get("tag_normalization"),
            "document_context": audit_result.get("document_context"),

            "overall_risk": audit_result["overall_risk"],

            "criticality_summary": {
                "score": audit_result["criticality"]["score"],
                "recommended_tag": audit_result["criticality"]["recommended_tag"],
                "confidence": audit_result["criticality"]["confidence"],
                "score_meaning": audit_result["criticality"]["score_meaning"]
            },

            "tag_validation": audit_result["tag_validation"],

            "dpdp_summary": {
                "overall_status": audit_result["dpdp"]["dpdp_overall_status"],
                "risk_level": audit_result["dpdp"]["dpdp_risk_level"],
                "total_controls": audit_result["dpdp"]["total_controls"],
                "present_count": audit_result["dpdp"]["compliant_count"],
                "partial_count": audit_result["dpdp"]["partial_count"],
                "missing_count": audit_result["dpdp"]["missing_count"],
                "failed_count": audit_result["dpdp"].get("failed_count", 0)
            },

            "tpmr_summary": {
                "overall_status": audit_result["tpmr"]["tpmr_overall_status"],
                "risk_level": audit_result["tpmr"]["tpmr_risk_level"],
                "total_controls": audit_result["tpmr"]["total_controls"],
                "present_count": audit_result["tpmr"]["present_count"],
                "partial_count": audit_result["tpmr"]["partial_count"],
                "missing_count": audit_result["tpmr"]["missing_count"],
                "failed_count": audit_result["tpmr"]["failed_count"],
                "privacy_overlay_count": audit_result["tpmr"].get("privacy_overlay_count", 0)
            },

            "top_findings": audit_result["top_findings"],

            "dpdp_findings": audit_result["dpdp"]["findings"],
            "tpmr_findings": audit_result["tpmr"]["findings"]
        }

    except ValueError as error:
        return {
            "status": "failed",
            "message": str(error)
        }


@app.post("/final-audit-pdf")
def final_audit_pdf(
    given_tag: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Runs complete audit workflow and returns final combined PDF report.
    """

    try:
        file_path = save_uploaded_pdf(file)

        audit_result = run_full_audit(
            file_path=file_path,
            given_tag=given_tag
        )

        pdf_report_filename = generate_final_audit_pdf_report(
            filename=file.filename,
            given_tag=given_tag,
            audit_result=audit_result
        )

        pdf_report_path = os.path.join(REPORT_DIR, pdf_report_filename)

        return FileResponse(
            path=pdf_report_path,
            filename=pdf_report_filename,
            media_type="application/pdf"
        )

    except ValueError as error:
        return {
            "status": "failed",
            "message": str(error)
        }


@app.post("/final-audit-json-llm")
def final_audit_json_llm(
    given_tag: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Runs complete rule-based audit and adds lightweight Ollama semantic review.

    Important:
    - Rule engine remains the source of truth.
    - LLM only reviews selected weak/high-risk findings for possible missed evidence.
    - Heavy LLM report generation is intentionally disabled here to avoid timeout.
    """

    try:
        file_path = save_uploaded_pdf(file)

        audit_result = run_full_audit(
            file_path=file_path,
            given_tag=given_tag
        )

        audit_result = add_llm_semantic_reviews(
            audit_result=audit_result,
            max_reviews=None,
            document_context=audit_result.get("document_context")
        )

        return {
            "status": "success",
            "output_type": "json_with_llm_semantic_review",
            "filename": file.filename,
            "given_tag": given_tag,
            "tag_normalization": audit_result.get("tag_normalization"),
            "document_context": audit_result.get("document_context"),

            "overall_risk": audit_result["overall_risk"],

            "criticality_summary": {
                "score": audit_result["criticality"]["score"],
                "recommended_tag": audit_result["criticality"]["recommended_tag"],
                "confidence": audit_result["criticality"]["confidence"],
                "score_meaning": audit_result["criticality"]["score_meaning"]
            },

            "tag_validation": audit_result["tag_validation"],

            "dpdp_summary": {
                "overall_status": audit_result["dpdp"]["dpdp_overall_status"],
                "risk_level": audit_result["dpdp"]["dpdp_risk_level"],
                "total_controls": audit_result["dpdp"]["total_controls"],
                "present_count": audit_result["dpdp"]["compliant_count"],
                "partial_count": audit_result["dpdp"]["partial_count"],
                "missing_count": audit_result["dpdp"]["missing_count"],
                "failed_count": audit_result["dpdp"].get("failed_count", 0)
            },

            "tpmr_summary": {
                "overall_status": audit_result["tpmr"]["tpmr_overall_status"],
                "risk_level": audit_result["tpmr"]["tpmr_risk_level"],
                "total_controls": audit_result["tpmr"]["total_controls"],
                "present_count": audit_result["tpmr"]["present_count"],
                "partial_count": audit_result["tpmr"]["partial_count"],
                "missing_count": audit_result["tpmr"]["missing_count"],
                "failed_count": audit_result["tpmr"]["failed_count"],
                "privacy_overlay_count": audit_result["tpmr"].get("privacy_overlay_count", 0)
            },

            "top_findings": audit_result["top_findings"],
            "llm_semantic_review_summary": audit_result.get("llm_semantic_review_summary")
        }

    except ValueError as error:
        return {
            "status": "failed",
            "message": str(error)
        }


@app.post("/final-audit-pdf-llm")
def final_audit_pdf_llm(
    given_tag: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Runs complete audit, adds lightweight LLM semantic review,
    and passes the enhanced audit_result into the existing PDF generator.
    """

    try:
        file_path = save_uploaded_pdf(file)

        audit_result = run_full_audit(
            file_path=file_path,
            given_tag=given_tag
        )

        audit_result = add_llm_semantic_reviews(
            audit_result=audit_result,
            max_reviews=None,
            document_context=audit_result.get("document_context")
        )

        pdf_report_filename = generate_final_audit_pdf_report(
            filename=file.filename,
            given_tag=given_tag,
            audit_result=audit_result
        )

        pdf_report_path = os.path.join(REPORT_DIR, pdf_report_filename)

        return FileResponse(
            path=pdf_report_path,
            filename=pdf_report_filename,
            media_type="application/pdf"
        )

    except ValueError as error:
        return {
            "status": "failed",
            "message": str(error)
        }
