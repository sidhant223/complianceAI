from src.llm_semantic_validator import validate_finding_with_llm

finding = {
    "control": "Vendor risk assessment",
    "expected_requirement": "The document should mention periodic vendor risk assessment or third-party due diligence.",
    "status": "Missing",
    "risk": "High",
    "evidence": [],
    "candidate_evidence": [
        {
            "page": 2,
            "snippet": "The vendor shall comply with security obligations and provide audit support when requested."
        }
    ],
    "recommendation": "Add explicit vendor risk assessment and due diligence requirements."
}

result = validate_finding_with_llm(finding)
print(result)