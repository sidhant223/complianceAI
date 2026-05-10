TAG_RANK = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4
}


def validate_given_tag(given_tag: str, recommended_tag: str, confidence: float) -> dict:
    """
    Compares the user/company provided tag against the system recommended tag.
    """

    normalized_given_tag = normalize_tag(given_tag)

    if normalized_given_tag not in TAG_RANK:
        return {
            "given_tag": given_tag,
            "recommended_tag": recommended_tag,
            "validation_result": "Invalid Tag",
            "confidence": confidence,
            "reason": "Given tag must be one of: Low, Medium, High, Critical."
        }

    if confidence < 0.65:
        return {
            "given_tag": normalized_given_tag,
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
        "recommended_tag": recommended_tag,
        "validation_result": validation_result,
        "confidence": confidence,
        "reason": reason
    }


def normalize_tag(tag: str) -> str:
    return tag.strip().lower().capitalize()