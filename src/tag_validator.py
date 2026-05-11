TAG_RANK = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4
}

AUDIT_DOMAIN_MAP = {
    "tpmr": "TPMR",
    "vendor_risk": "TPMR",
    "third_party_risk": "TPMR",
    "third_party_vendor_risk": "TPMR",
    "dpdp": "DPDP",
    "privacy": "DPDP",
    "data_protection": "DPDP",
    "general": "GENERAL",
    "general_audit": "GENERAL",
    "auto": "AUTO",
}

TAG_ALIASES = {
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
    "red": "Critical",
}


def normalize_input_token(value: str) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def normalize_tag(tag: str) -> str | None:
    """Returns a normalized criticality tag, or None when not a severity tag."""
    return TAG_ALIASES.get(normalize_input_token(tag))


def normalize_audit_domain(tag: str) -> str | None:
    """Returns a normalized audit domain/category, or None when not a domain."""
    return AUDIT_DOMAIN_MAP.get(normalize_input_token(tag))


def validate_given_tag(given_tag: str, recommended_tag: str, confidence: float) -> dict:
    """
    Compares a user/company provided criticality tag against the system recommended tag.

    Important:
    - TPMR / DPDP / Vendor Risk are audit domains, not severity tiers.
    - Audit domains are accepted and are not penalized as invalid criticality tags.
    """

    audit_domain = normalize_audit_domain(given_tag)

    if audit_domain:
        return {
            "given_tag": given_tag,
            "normalized_tag": audit_domain,
            "input_type": "audit_domain",
            "audit_domain": audit_domain,
            "recommended_tag": recommended_tag,
            "validation_result": "Accepted - Audit Domain",
            "confidence": confidence,
            "reason": (
                f"'{given_tag}' was recognized as an audit domain/category, not a criticality tier. "
                f"The system separately inferred document criticality as '{recommended_tag}'."
            )
        }

    normalized_given_tag = normalize_tag(given_tag)

    if normalized_given_tag not in TAG_RANK:
        return {
            "given_tag": given_tag,
            "normalized_tag": "Needs Human Review",
            "input_type": "unknown",
            "recommended_tag": recommended_tag,
            "validation_result": "Needs Human Review",
            "confidence": confidence,
            "reason": "Given input must be an audit domain such as TPMR/DPDP or a criticality tier: Low, Medium, High, Critical."
        }

    if confidence < 0.65:
        return {
            "given_tag": normalized_given_tag,
            "normalized_tag": normalized_given_tag,
            "input_type": "criticality_tag",
            "recommended_tag": recommended_tag,
            "validation_result": "Needs Human Review",
            "confidence": confidence,
            "reason": "The system confidence is low, so a human auditor should review the classification."
        }

    given_rank = TAG_RANK[normalized_given_tag]
    recommended_rank = TAG_RANK[recommended_tag]

    if given_rank == recommended_rank:
        validation_result = "Correctly Classified"
        reason = (
            f"The given tag '{normalized_given_tag}' matches the system recommended tag "
            f"'{recommended_tag}' based on detected policy risk signals."
        )

    elif given_rank > recommended_rank:
        validation_result = "Over-classified"
        reason = (
            f"The policy was tagged as '{normalized_given_tag}', but the detected risk signals "
            f"support a lower tag of '{recommended_tag}'. This may cause unnecessary review effort."
        )

    else:
        validation_result = "Under-classified"
        reason = (
            f"The policy was tagged as '{normalized_given_tag}', but the detected risk signals "
            f"support a higher tag of '{recommended_tag}'. This may create governance or compliance risk."
        )

    return {
        "given_tag": normalized_given_tag,
        "normalized_tag": normalized_given_tag,
        "input_type": "criticality_tag",
        "recommended_tag": recommended_tag,
        "validation_result": validation_result,
        "confidence": confidence,
        "reason": reason
    }
