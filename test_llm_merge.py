from src.llm_semantic_validator import add_llm_semantic_reviews
import json

audit_result = {
    "top_findings": [
        {
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
    ]
}

result = add_llm_semantic_reviews(audit_result, max_reviews=1)

print(json.dumps(result, indent=2))