import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)
from reportlab.lib.enums import TA_LEFT


REPORT_DIR = "reports"

os.makedirs(REPORT_DIR, exist_ok=True)


def generate_final_audit_pdf_report(
    filename: str,
    given_tag: str,
    audit_result: dict
) -> str:
    """
    Generates final combined audit PDF report.

    Includes:
    - Criticality validation
    - DPDP compliance
    - TPMR/vendor risk
    - Overall risk
    - Top findings
    - Optional LLM semantic review display

    Important:
    Rule-based engine remains the source of truth.
    LLM review is advisory and only shown for semantic missed-evidence review.
    """

    llm_used = is_llm_review_used(audit_result)

    safe_filename = filename.replace(".pdf", "").replace(" ", "_")

    if llm_used:
        report_filename = f"{safe_filename}_final_audit_report_llm.pdf"
    else:
        report_filename = f"{safe_filename}_final_audit_report.pdf"

    report_path = os.path.join(REPORT_DIR, report_filename)

    doc = SimpleDocTemplate(
        report_path,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    normal_style = ParagraphStyle(
        name="NormalWrapped",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        alignment=TA_LEFT,
        wordWrap="CJK"
    )

    header_style = ParagraphStyle(
        name="HeaderWrapped",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        alignment=TA_LEFT,
        wordWrap="CJK",
        fontName="Helvetica-Bold"
    )

    story = []

    criticality = audit_result["criticality"]
    tag_validation = audit_result["tag_validation"]
    dpdp = audit_result["dpdp"]
    tpmr = audit_result["tpmr"]
    overall_risk = audit_result["overall_risk"]
    top_findings = audit_result["top_findings"]
    document_context = audit_result.get("document_context", {})

    # Title
    story.append(Paragraph("Final Policy Compliance & Vendor Risk Audit Report", styles["Title"]))
    story.append(Spacer(1, 16))

    # 1. Document Information
    story.append(Paragraph("1. Document Information", styles["Heading2"]))
    story.append(Paragraph(f"<b>Uploaded File:</b> {escape_text(filename)}", styles["Normal"]))
    story.append(Paragraph(f"<b>Given Tag:</b> {escape_text(given_tag)}", styles["Normal"]))
    story.append(
        Paragraph(
            f"<b>Report Generated At:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"]
        )
    )

    if llm_used:
        story.append(
            Paragraph(
                "<b>LLM Semantic Review:</b> Sequential fault-tolerant review applied to generated top findings",
                styles["Normal"]
            )
        )
    else:
        story.append(
            Paragraph(
                "<b>LLM Semantic Review:</b> Not attached in this report",
                styles["Normal"]
            )
        )

    story.append(Spacer(1, 14))

    # 2. Executive Summary
    story.append(Paragraph("2. Executive Summary", styles["Heading2"]))
    executive_summary = build_executive_summary(audit_result)
    story.append(Paragraph(escape_text(executive_summary), styles["Normal"]))

    if llm_used:
        story.append(Spacer(1, 8))
        story.append(
            Paragraph(
                escape_text(
                    "Sequential fault-tolerant LLM review was applied to generated top findings. "
                    "Rule-based scoring, risks, statuses, and extracted evidence remain the source of truth. "
                    "The LLM does not create controls, invent evidence, silently change scores, or replace auditor judgment."
                ),
                styles["Normal"]
            )
        )

    story.append(Spacer(1, 14))

    # 2A. Document Intelligence
    story.append(Paragraph("2A. Document Intelligence", styles["Heading2"]))

    mismatch_flags = document_context.get("retrieval_mismatch_flags", [])
    sections_used = document_context.get("sections_used_for_scoring", [])

    intelligence_table_data = [
        [cell("Field", header_style), cell("Value", header_style)],
        [cell("Document Type", normal_style), cell(document_context.get("document_type", "unknown"), normal_style)],
        [cell("Audit Format", normal_style), cell(document_context.get("audit_format", "unknown"), normal_style)],
        [cell("Classifier Confidence", normal_style), cell(str(document_context.get("classifier_confidence", "N/A")), normal_style)],
        [cell("Audit Report Mode", normal_style), cell("Active" if document_context.get("audit_report_mode") else "Inactive", normal_style)],
        [cell("Negative Detection", normal_style), cell("Active" if document_context.get("negative_detection_active") else "Inactive", normal_style)],
        [cell("Attribution Filter", normal_style), cell("Active" if document_context.get("attribution_filter_active") else "Inactive", normal_style)],
        [cell("Retrieval Mismatch Flags", normal_style), cell(str(len(mismatch_flags)) if mismatch_flags else "None", normal_style)],
        [cell("Sections Scored Against", normal_style), cell(", ".join(sections_used[:6]) if sections_used else "N/A", normal_style)],
    ]

    intelligence_table = Table(
        intelligence_table_data,
        colWidths=[160, 320],
        repeatRows=1
    )
    intelligence_table.setStyle(get_table_style())
    story.append(intelligence_table)

    story.append(Spacer(1, 14))

    # 3. Overall Risk
    story.append(Paragraph("3. Overall Risk Rating", styles["Heading2"]))
    story.append(Paragraph(f"<b>Overall Risk:</b> {escape_text(overall_risk.get('overall_risk', 'N/A'))}", styles["Normal"]))
    story.append(Paragraph(f"<b>Risk Score:</b> {overall_risk.get('risk_score', 'N/A')}", styles["Normal"]))
    story.append(Paragraph(f"<b>Reason:</b> {escape_text(overall_risk.get('reason', ''))}", styles["Normal"]))
    story.append(Spacer(1, 14))
    # Scoring methodology detail removed to keep the final PDF compact.
    story.append(Spacer(1, 8))


    # 4. Criticality Validation
    story.append(Paragraph("4. Criticality Tag Validation", styles["Heading2"]))

    validation_table_data = [
        [cell("Field", header_style), cell("Value", header_style)],
        [cell("Given Tag", normal_style), cell(tag_validation.get("given_tag", given_tag), normal_style)],
        [cell("Recommended Tag", normal_style), cell(tag_validation.get("recommended_tag", ""), normal_style)],
        [cell("Validation Result", normal_style), cell(tag_validation.get("validation_result", ""), normal_style)],
        [cell("Confidence", normal_style), cell(str(tag_validation.get("confidence", "")), normal_style)],
        [cell("Criticality Score", normal_style), cell(str(criticality.get("score", "")), normal_style)],
        [cell("Reason", normal_style), cell(tag_validation.get("reason", ""), normal_style)],
    ]

    validation_table = Table(
        validation_table_data,
        colWidths=[130, 350],
        repeatRows=1
    )
    validation_table.setStyle(get_table_style())
    story.append(validation_table)
    story.append(Spacer(1, 16))

    document_context = audit_result.get("document_context", {})
    framework_applicability = document_context.get("framework_applicability", {})
    dpdp_applicable = document_context.get("dpdp_applicable", True)
    tpmr_applicable = document_context.get("tpmr_applicable", True)

    # 5. DPDP Summary
    story.append(Paragraph("5. DPDP Compliance Summary", styles["Heading2"]))

    if not dpdp_applicable:
        dpdp_scope_review_required = document_context.get("dpdp_scope_review_required", False)
        applicability_label = (
            "Not Scored / Manual Scope Review Recommended"
            if dpdp_scope_review_required
            else "Not Applicable / Out of Scope"
        )
        story.append(
            Paragraph(
                f"<b>Applicability:</b> {escape_text(applicability_label)}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Reason:</b> {escape_text(dpdp.get('applicability_reason') or framework_applicability.get('frameworks', {}).get('dpdp', {}).get('reason') or framework_applicability.get('applicability_reason', 'DPDP controls were excluded based on document context.'))}",
                styles["Normal"]
            )
        )

        note_text = (
            "DPDP controls were excluded from automated risk scoring, but a human should confirm whether student/staff/personnel or confidential-information processing brings privacy obligations into scope."
            if dpdp_scope_review_required
            else "DPDP controls were not included in effective risk scoring or top audit findings for this document."
        )
        story.append(Paragraph(escape_text(note_text), styles["Normal"]))

    else:
        dpdp_table_data = [
            [cell("Metric", header_style), cell("Value", header_style)],
            [cell("Overall Status", normal_style), cell(dpdp.get("dpdp_overall_status", ""), normal_style)],
            [cell("Risk Level", normal_style), cell(dpdp.get("dpdp_risk_level", ""), normal_style)],
            [cell("Total Controls", normal_style), cell(str(dpdp.get("total_controls", 0)), normal_style)],
            [cell("Present Controls", normal_style), cell(str(dpdp.get("compliant_count", 0)), normal_style)],
            [cell("Partial Controls", normal_style), cell(str(dpdp.get("partial_count", 0)), normal_style)],
            [cell("Missing Controls", normal_style), cell(str(dpdp.get("missing_count", 0)), normal_style)],
            [cell("Failed Controls", normal_style), cell(str(dpdp.get("failed_count", 0)), normal_style)],
        ]

        dpdp_table = Table(
            dpdp_table_data,
            colWidths=[160, 320],
            repeatRows=1
        )

        dpdp_table.setStyle(get_table_style())
        story.append(dpdp_table)

    story.append(Spacer(1, 16))   

    # 6. TPMR Summary
    story.append(Paragraph("6. TPMR / Vendor Risk Summary", styles["Heading2"]))

    tpmr_table_data = [
        [cell("Metric", header_style), cell("Value", header_style)],
        [cell("Overall Status", normal_style), cell(tpmr.get("tpmr_overall_status", ""), normal_style)],
        [cell("Risk Level", normal_style), cell(tpmr.get("tpmr_risk_level", ""), normal_style)],
        [cell("Total Controls", normal_style), cell(str(tpmr.get("total_controls", 0)), normal_style)],
        [cell("Present Controls", normal_style), cell(str(tpmr.get("present_count", 0)), normal_style)],
        [cell("Partial Controls", normal_style), cell(str(tpmr.get("partial_count", 0)), normal_style)],
        [cell("Missing Controls", normal_style), cell(str(tpmr.get("missing_count", 0)), normal_style)],
        [cell("Failed Controls", normal_style), cell(str(tpmr.get("failed_count", 0)), normal_style)],
        [cell("Privacy Overlay Findings", normal_style), cell(str(tpmr.get("privacy_overlay_count", 0)), normal_style)],
    ]

    tpmr_table = Table(
        tpmr_table_data,
        colWidths=[160, 320],
        repeatRows=1
    )
    tpmr_table.setStyle(get_table_style())
    story.append(tpmr_table)

    story.append(PageBreak())

    # 7. Top Findings
    story.append(Paragraph("7. Top Audit Findings", styles["Heading2"]))

    if top_findings:
        findings_table_data = [
            [
                cell("Source", header_style),
                cell("Control", header_style),
                cell("Rule Status", header_style),
                cell("Final Status", header_style),
                cell("Risk", header_style),
                cell("Priority", header_style),
                cell("Severity", header_style),
                cell("Semantic Review", header_style),
                cell("Recommendation", header_style),
            ]
        ]

        for finding in top_findings:
            llm_review = get_finding_llm_review(finding)
            final_status = finding.get("final_status", finding.get("status", ""))
            llm_status = get_llm_status(llm_review)

            findings_table_data.append([
                cell(finding.get("source", ""), normal_style),
                cell(finding.get("control", ""), normal_style),
                cell(finding.get("status", ""), normal_style),
                cell(final_status, normal_style),
                cell(finding.get("risk", ""), normal_style),
                cell(finding.get("priority", "P2"), normal_style),
                cell(finding.get("severity", finding.get("risk", "")), normal_style),
                cell(llm_status, normal_style),
                cell(finding.get("recommendation", ""), normal_style),
            ])

        findings_table = Table(
            findings_table_data,
            colWidths=[34, 72, 48, 58, 34, 38, 45, 58, 93],
            repeatRows=1
        )
        findings_table.setStyle(get_table_style())
        story.append(findings_table)
    else:
        story.append(
            Paragraph(
                "No high-risk or failed findings were identified in the top findings list.",
                styles["Normal"]
            )
        )

    story.append(Spacer(1, 16))

    # 8. Evidence Snapshot
    story.append(Paragraph("8. Evidence Snapshot for Top Findings", styles["Heading2"]))

    if top_findings:
        for index, finding in enumerate(top_findings[:5], start=1):
            llm_review = get_finding_llm_review(finding)
            final_status = finding.get("final_status", finding.get("status", ""))

            story.append(
                Paragraph(
                    f"{index}. {escape_text(finding.get('source', ''))} - {escape_text(finding.get('control', ''))}",
                    styles["Heading3"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Rule-Based Status:</b> {escape_text(finding.get('status', ''))}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Final Status:</b> {escape_text(final_status)}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Risk:</b> {escape_text(finding.get('risk', ''))}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Priority:</b> {escape_text(str(finding.get('priority', 'P2')))}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Severity:</b> {escape_text(str(finding.get('severity', finding.get('risk', ''))))}",
                    styles["Normal"]
                )
            )

            if finding.get("priority_reason"):
                story.append(
                    Paragraph(
                        f"<b>Priority Reason:</b> {escape_text(str(finding.get('priority_reason')))}",
                        styles["Normal"]
                    )
                )

            retrieval_mismatch = bool(finding.get("retrieval_mismatch", False) or finding.get("llm_review", {}).get("retrieval_mismatch", False))
            mismatch_action = finding.get("mismatch_action") or finding.get("llm_review", {}).get("mismatch_action", "N/A")
            negative_signal = finding.get("negative_signal", "None")
            negative_signal_source = finding.get("negative_signal_source", "N/A")

            story.append(Paragraph(f"<b>Retrieval Mismatch:</b> {'Yes' if retrieval_mismatch else 'No'}", styles["Normal"]))
            story.append(Paragraph(f"<b>Mismatch Action:</b> {escape_text(str(mismatch_action))}", styles["Normal"]))
            story.append(Paragraph(f"<b>Negative Signal:</b> {escape_text(str(negative_signal))}", styles["Normal"]))
            story.append(Paragraph(f"<b>Signal Source:</b> {escape_text(str(negative_signal_source))}", styles["Normal"]))

            entity_review = finding.get("entity_boundary_review", {})

            if entity_review:
                boundary_scores = entity_review.get("boundary_scores", {})

                story.append(
                    Paragraph(
                        f"<b>Entity Attribution:</b> {escape_text(entity_review.get('entity_boundary', 'N/A'))}",
                        styles["Normal"]
                    )
                )

                story.append(
                    Paragraph(
                        f"<b>Boundary Scores:</b> Vendor={escape_text(str(boundary_scores.get('vendor_score', 'N/A')))}, "
                        f"Internal={escape_text(str(boundary_scores.get('internal_score', 'N/A')))}",
                        styles["Normal"]
                    )
                )

                if finding.get("rerouting_note"):
                    story.append(
                        Paragraph(
                            f"<b>Rerouting Note:</b> {escape_text(finding.get('rerouting_note'))}",
                            styles["Normal"]
                        )
                    )

            if llm_review:
                story.append(Spacer(1, 5))
                story.append(Paragraph("<b>LLM Semantic Review</b>", styles["Normal"]))

                story.append(
                    Paragraph(
                        f"<b>Review Available:</b> {escape_text(str(llm_review.get('llm_review_available', 'N/A')))}",
                        styles["Normal"]
                    )
                )

                story.append(
                    Paragraph(
                        f"<b>Semantic Status:</b> {escape_text(str(llm_review.get('semantic_status', 'N/A')))}",
                        styles["Normal"]
                    )
                )

                story.append(
                    Paragraph(
                        f"<b>Confidence:</b> {escape_text(str(llm_review.get('semantic_confidence', 'N/A')))}",
                        styles["Normal"]
                    )
                )

                story.append(
                    Paragraph(
                        f"<b>Reason:</b> {escape_text(str(llm_review.get('semantic_reason', '')))}",
                        styles["Normal"]
                    )
                )

                if finding.get("llm_review_selection_reason"):
                    story.append(
                        Paragraph(
                            f"<b>Review Selection Reason:</b> {escape_text(str(finding.get('llm_review_selection_reason')))}",
                            styles["Normal"]
                        )
                    )

            story.append(Spacer(1, 8))

            evidence_items = finding.get("evidence", [])

            if evidence_items:
                evidence_table_data = [
                    [
                        cell("Page", header_style),
                        cell("Keyword", header_style),
                        cell("Sentiment", header_style),
                        cell("Snippet", header_style),
                    ]
                ]

                for evidence in evidence_items:
                    evidence_table_data.append([
                        cell(str(evidence.get("page", "N/A")), normal_style),
                        cell(str(evidence.get("keyword", "")), normal_style),
                        cell(str(evidence.get("sentiment", "")), normal_style),
                        cell(str(evidence.get("snippet", "")), normal_style),
                    ])

                evidence_table = Table(
                    evidence_table_data,
                    colWidths=[35, 100, 65, 280],
                    repeatRows=1
                )
                evidence_table.setStyle(get_table_style())
                story.append(evidence_table)

            else:
                candidate_items = finding.get("candidate_evidence", [])

                if candidate_items:
                    story.append(
                        Paragraph(
                            "<b>Evidence Gap:</b> No direct supporting clause was accepted for this control. "
                            "Closest candidate evidence is shown below for human review.",
                            styles["Normal"]
                        )
                    )

                    candidate_table_data = [
                        [
                            cell("Page", header_style),
                            cell("Candidate Snippet", header_style),
                        ]
                    ]

                    for candidate in candidate_items[:2]:
                        candidate_table_data.append([
                            cell(str(candidate.get("page", "N/A")), normal_style),
                            cell(str(candidate.get("snippet", "")), normal_style),
                        ])

                    candidate_table = Table(
                        candidate_table_data,
                        colWidths=[45, 435],
                        repeatRows=1
                    )

                    candidate_table.setStyle(get_table_style())
                    story.append(candidate_table)

                else:
                    status = str(finding.get("status", "")).lower()

                    if status == "missing":
                        evidence_gap_message = (
                            "<b>Evidence Gap:</b> No direct supporting clause was found for this control. "
                            "This is expected for a Missing finding and indicates a documentation/control gap, "
                            "not an extraction failure."
                        )
                    else:
                        evidence_gap_message = (
                            "<b>Evidence Gap:</b> No direct evidence snippet was available for this finding. "
                            "The rule-based status remains unchanged and should be reviewed with the source document if required."
                        )

                    story.append(
                        Paragraph(
                            evidence_gap_message,
                            styles["Normal"]
                        )
                    )

            story.append(Spacer(1, 14))

    else:
        story.append(
            Paragraph(
                "No evidence snapshot available because no top findings were identified.",
                styles["Normal"]
            )
        )

    # 9. LLM Semantic Review Summary
    story.append(Paragraph("9. LLM Semantic Review Summary", styles["Heading2"]))

    if llm_used:
        reviewed_count = count_llm_reviewed_findings(top_findings)

        llm_summary = audit_result.get("llm_semantic_review_summary", {})

        review_mode = llm_summary.get("review_mode", "Sequential Fault-Tolerant LLM Review")
        attempted_findings = llm_summary.get("attempted_findings", reviewed_count)
        eligible_findings = llm_summary.get("eligible_findings", reviewed_count)
        total_findings = llm_summary.get("total_findings", len(top_findings))
        safety_cap_enabled = llm_summary.get("safety_cap_enabled", False)
        max_reviews = llm_summary.get("max_reviews")

        note = llm_summary.get(
            "note",
            "Sequential fault-tolerant LLM review was applied to generated top findings. "
            "If local LLM review failed for a finding, a conservative fallback review was attached. "
            "Rule-based scoring, risks, statuses, and extracted evidence remain the source of truth."
        )

        report_warning = llm_summary.get("report_warning")
        semantic_validation_status = llm_summary.get("semantic_validation_status", "N/A")

        story.append(Paragraph(f"<b>LLM Reviewed Findings:</b> {reviewed_count}", styles["Normal"]))
        story.append(Paragraph(f"<b>Successful LLM Responses:</b> {llm_summary.get('successful_reviews', llm_summary.get('successful_llm_reviews', reviewed_count))}", styles["Normal"]))
        story.append(Paragraph(f"<b>Fallback Reviews:</b> {llm_summary.get('fallback_reviews', 0)}", styles["Normal"]))
        story.append(Paragraph(f"<b>LLM Review Mode:</b> {escape_text(str(review_mode))}", styles["Normal"]))
        story.append(Paragraph(f"<b>LLM Preflight:</b> {escape_text(str(llm_summary.get('llm_preflight_available', 'N/A')))}", styles["Normal"]))
        story.append(Paragraph(f"<b>LLM Preflight Message:</b> {escape_text(str(llm_summary.get('llm_preflight_message', 'N/A')))}", styles["Normal"]))
        story.append(Paragraph(f"<b>Eligible Findings:</b> {eligible_findings}", styles["Normal"]))
        story.append(Paragraph(f"<b>Attempted Reviews:</b> {attempted_findings}", styles["Normal"]))
        story.append(Paragraph(f"<b>Total Top Findings:</b> {total_findings}", styles["Normal"]))
        story.append(Paragraph(f"<b>Safety Cap Enabled:</b> {escape_text(str(safety_cap_enabled))}", styles["Normal"]))
        story.append(Paragraph(f"<b>Max Reviews:</b> {escape_text(str(max_reviews))}", styles["Normal"]))
        story.append(Paragraph("<b>LLM Purpose:</b> Semantic missed-evidence and ambiguity review", styles["Normal"]))
        story.append(Paragraph("<b>Decision Principle:</b> Rule engine decides. LLM reviews one finding at a time. Human handles ambiguity.", styles["Normal"]))
        story.append(Paragraph(f"<b>Semantic Validation Status:</b> {escape_text(str(semantic_validation_status))}", styles["Normal"]))
        story.append(Paragraph(f"<b>Note:</b> {escape_text(note)}", styles["Normal"]))

        if report_warning:
            story.append(
                Paragraph(
                    f"<b>Warning:</b> {escape_text(report_warning)}",
                    styles["Normal"]
                )
            )

        story.append(Spacer(1, 10))

        llm_table_data = [
            [
                cell("Control", header_style),
                cell("Rule Status", header_style),
                cell("LLM Status", header_style),
                cell("Confidence", header_style),
                cell("Final Status", header_style),
                cell("LLM Reason", header_style),
                cell("Selection Reason", header_style),
            ]
        ]

        for finding in top_findings:
            llm_review = get_finding_llm_review(finding)

            if not llm_review:
                continue

            llm_table_data.append([
                cell(finding.get("control", ""), normal_style),
                cell(finding.get("status", ""), normal_style),
                cell(llm_review.get("semantic_status", "N/A"), normal_style),
                cell(llm_review.get("semantic_confidence", "N/A"), normal_style),
                cell(finding.get("final_status", finding.get("status", "")), normal_style),
                cell(llm_review.get("semantic_reason", ""), normal_style),
                cell(finding.get("llm_review_selection_reason", ""), normal_style),
            ])

        if len(llm_table_data) > 1:
            llm_table = Table(
                llm_table_data,
                colWidths=[75, 50, 58, 52, 55, 120, 70],
                repeatRows=1
            )
            llm_table.setStyle(get_table_style())
            story.append(llm_table)
        else:
            story.append(
                Paragraph(
                    "No individual LLM semantic review objects were attached to top findings.",
                    styles["Normal"]
                )
            )
    else:
        story.append(
            Paragraph(
                "No LLM semantic review objects were attached to this audit result. "
                "This report appears to be generated from the rule-based audit flow only.",
                styles["Normal"]
            )
        )

    story.append(Spacer(1, 14))

    # 10. Human Review Notes
    story.append(Paragraph("10. Human Review Notes", styles["Heading2"]))
    story.append(
        Paragraph(
            "This report is automatically generated using evidence-backed policy analysis. "
            "The rule-based engine provides scores, risk signals, statuses, and extracted evidence. "
            "Any LLM semantic review is advisory only and should be validated by a human auditor before final compliance conclusions.",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 12))

    # 11. AI/LLM Integration Note
    story.append(Paragraph("11. AI/LLM Integration Note", styles["Heading2"]))

    if llm_used:
        story.append(
            Paragraph(
                "This report includes sequential fault-tolerant LLM review for generated top findings. "
                "The LLM was not used to assign risk scores, create controls, invent evidence, or replace auditor judgment. "
                "It was used only to check whether ambiguous or missed evidence may exist in relation to existing rule-based findings. "
                "Where the LLM identifies possible but insufficient evidence, the finding is marked for manual review.",
                styles["Normal"]
            )
        )
    else:
        story.append(
            Paragraph(
                "This report was generated using deterministic rule-based checks for audit defensibility. "
                "No LLM semantic review data was attached to this report. "
                "The recommended architecture remains: rule engine decides, LLM reviews selected ambiguity, and human auditor validates final conclusions.",
                styles["Normal"]
            )
        )

    doc.build(story)

    return report_filename


def build_executive_summary(audit_result: dict) -> str:
    criticality = audit_result["criticality"]
    tag_validation = audit_result["tag_validation"]
    dpdp = audit_result["dpdp"]
    tpmr = audit_result["tpmr"]
    overall_risk = audit_result["overall_risk"]

    summary = (
        f"The document was reviewed for criticality, DPDP applicability, and TPMR/vendor risk controls. "
        f"Recommended tag: {criticality.get('recommended_tag')} | "
        f"Tag validation: {tag_validation.get('validation_result')} | "
        f"DPDP: {dpdp.get('dpdp_risk_level')} | "
        f"TPMR: {tpmr.get('tpmr_risk_level')} | "
        f"Overall risk: {overall_risk.get('overall_risk')}."
    )

    if is_llm_review_used(audit_result):
        summary += " Sequential LLM review was applied to all generated top findings."

    return summary


def get_finding_llm_review(finding: dict) -> dict:
    """
    Supports both LLM review field names.

    Current project uses:
    - llm_review

    Older PDF generator code expected:
    - llm_semantic_review
    """

    return (
        finding.get("llm_review")
        or finding.get("llm_semantic_review")
        or {}
    )


def is_llm_review_used(audit_result: dict) -> bool:
    """
    Detects whether LLM semantic review data is attached.
    Supports both llm_review and llm_semantic_review.
    """

    if audit_result.get("note"):
        note = str(audit_result.get("note", "")).lower()
        if "llm" in note:
            return True

    if audit_result.get("llm_semantic_review_summary"):
        return True

    top_findings = audit_result.get("top_findings", [])

    for finding in top_findings:
        if get_finding_llm_review(finding):
            return True

        if finding.get("final_status") and finding.get("final_status") != finding.get("status"):
            return True

    return False


def count_llm_reviewed_findings(top_findings: list) -> int:
    """
    Counts attempted LLM reviews, not only successful model responses.
    This keeps the PDF aligned with sequential mode: if 6 top findings exist,
    6 review objects should be attached, even if some fall back to manual review.
    """

    count = 0

    for finding in top_findings:
        llm_review = get_finding_llm_review(finding)

        if not llm_review:
            continue

        semantic_status = llm_review.get("semantic_status")

        if semantic_status in ["Not Reviewed", "Rule Based Only"]:
            continue

        count += 1

    return count


def get_llm_status(llm_review: dict) -> str:
    if not llm_review:
        return "Rule Based Only"

    if llm_review.get("semantic_status") == "Not Reviewed":
        return "Rule Based Only"

    if llm_review.get("fallback_used") is True:
        return "Fallback Review Applied"

    if llm_review.get("llm_review_available") is False:
        return "Fallback Review Applied"

    return str(llm_review.get("semantic_status", "Reviewed"))


def cell(text, style):
    return Paragraph(escape_text(str(text)), style)


def escape_text(text: str) -> str:
    if text is None:
        return ""

    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def get_table_style():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])