CRITICALITY_WEIGHTS = {
    "personal_data": 1.0,
    "children_data": 1.5,
    "third_party_processing": 1.2,
    "breach_notification": 1.2,
    "consent_management": 0.8,
    "data_retention": 0.8,
    "security_controls": 1.0,
    "regulatory_obligation": 1.5,
    "sensitive_data": 1.5,
    "vendor_access": 1.0
}


MAX_SCORE = sum(CRITICALITY_WEIGHTS.values())


SCORE_SCALE = {
    "0-2": "Low: Minimal compliance, security, privacy, or third-party risk impact.",
    "3-5": "Medium: Some privacy, security, vendor, or compliance relevance exists.",
    "6-8": "High: Strong regulatory, privacy, vendor, or security impact exists.",
    "9-10": "Critical: Severe legal, regulatory, sensitive data, breach, or vendor-risk exposure exists."
}


def calculate_criticality_score(signals: dict) -> dict:
    """
    Calculates criticality score on a 0-10 scale.
    Also calculates confidence based on number of detected signals and evidence count.
    """

    raw_score = 0
    score_breakdown = {}

    found_signal_count = 0
    total_evidence_count = 0

    for signal_name, details in signals.items():
        found = details.get("found", False)
        weight = CRITICALITY_WEIGHTS.get(signal_name, 0)
        evidence_count = len(details.get("evidence", []))

        if found:
            raw_score += weight
            contribution = weight
            found_signal_count += 1
            total_evidence_count += evidence_count
        else:
            contribution = 0

        score_breakdown[signal_name] = {
            "found": found,
            "weight": weight,
            "contribution": contribution,
            "evidence_count": evidence_count
        }

    normalized_score = round((raw_score / MAX_SCORE) * 10, 2)

    confidence = calculate_confidence(
        found_signal_count=found_signal_count,
        total_evidence_count=total_evidence_count
    )

    return {
        "criticality_score": normalized_score,
        "recommended_tag": map_score_to_tag(normalized_score),
        "score_meaning": get_score_meaning(normalized_score),
        "score_scale": SCORE_SCALE,
        "confidence": confidence,
        "score_breakdown": score_breakdown
    }


def map_score_to_tag(score: float) -> str:
    if score >= 9:
        return "Critical"
    elif score >= 6:
        return "High"
    elif score >= 3:
        return "Medium"
    return "Low"


def get_score_meaning(score: float) -> str:
    if score >= 9:
        return SCORE_SCALE["9-10"]
    elif score >= 6:
        return SCORE_SCALE["6-8"]
    elif score >= 3:
        return SCORE_SCALE["3-5"]
    return SCORE_SCALE["0-2"]


def calculate_confidence(found_signal_count: int, total_evidence_count: int) -> float:
    """
    Simple confidence scoring:
    - more detected signals = stronger confidence
    - more evidence snippets = stronger confidence
    """

    signal_score = min(found_signal_count / 10, 1.0)
    evidence_score = min(total_evidence_count / 20, 1.0)

    confidence = (signal_score * 0.6) + (evidence_score * 0.4)

    return round(confidence, 2)