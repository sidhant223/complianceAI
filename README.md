# ComplianceAI
ComplianceAI is an AI-assisted compliance audit automation platform built with Python and FastAPI. It helps automate the first-pass review of policy, vendor, RFP, and compliance-related PDF documents by extracting text, identifying document context, validating applicable compliance areas, and generating structured audit outputs.

The platform uses a deterministic rule-based engine as the source of truth for scoring, statuses, risks, evidence extraction, and compliance findings. It includes modules for criticality assessment, DPDP applicability checks, and third-party/vendor risk management review.

An optional local Ollama-powered LLM layer performs semantic review on selected weak or high-risk findings and helps generate consulting-style explanations. The LLM does not replace the rule engine or make final compliance decisions; it only supports review quality and report clarity.

The system can generate both structured JSON audit results and professional PDF audit reports, making it useful as a proof-of-concept for compliance automation, vendor risk assessment, and audit documentation workflows.


## Features

- PDF upload and text extraction
- Criticality scoring
- DPDP applicability and compliance checks
- TPMR/vendor risk control checks
- Evidence-backed findings
- Sequential fault-tolerant LLM review using Ollama
- Final audit JSON and PDF generation

## Tech Stack

- Python
- FastAPI
- ReportLab
- PyMuPDF
- Ollama
- Local LLM review layer
