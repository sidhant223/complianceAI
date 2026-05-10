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


def generate_dpdp_pdf_report(filename: str, dpdp_result: dict) -> str:
    """
    Generates a downloadable PDF report for DPDP compliance analysis.
    Includes:
    - wrapped text inside tables
    - failed controls count
    - evidence sentiment
    - negative evidence visibility
    """

    safe_filename = filename.replace(".pdf", "").replace(" ", "_")
    report_filename = f"{safe_filename}_dpdp_compliance_report.pdf"
    report_path = os.path.join(REPORT_DIR, report_filename)

    doc = SimpleDocTemplate(
        report_path,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
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

    story.append(Paragraph("DPDP Compliance Analysis Report", styles["Title"]))
    story.append(Spacer(1, 16))

    # 1. Document Information
    story.append(Paragraph("1. Document Information", styles["Heading2"]))
    story.append(Paragraph(f"<b>Uploaded File:</b> {escape_text(filename)}", styles["Normal"]))
    story.append(
        Paragraph(
            f"<b>Report Generated At:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"]
        )
    )
    story.append(Spacer(1, 14))

    # 2. DPDP Summary
    story.append(Paragraph("2. DPDP Summary", styles["Heading2"]))
    story.append(Paragraph(f"<b>Overall Status:</b> {escape_text(dpdp_result['dpdp_overall_status'])}", styles["Normal"]))
    story.append(Paragraph(f"<b>Risk Level:</b> {escape_text(dpdp_result['dpdp_risk_level'])}", styles["Normal"]))
    story.append(Paragraph(f"<b>Total Controls Checked:</b> {dpdp_result['total_controls']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Present Controls:</b> {dpdp_result['compliant_count']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Partially Compliant Controls:</b> {dpdp_result['partial_count']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Missing Controls:</b> {dpdp_result['missing_count']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Failed Controls:</b> {dpdp_result.get('failed_count', 0)}", styles["Normal"]))
    story.append(Spacer(1, 16))

    # 3. Control Summary Matrix
    story.append(Paragraph("3. Control Summary Matrix", styles["Heading2"]))

    summary_table_data = [
        [
            cell("Control", header_style),
            cell("Status", header_style),
            cell("Risk", header_style),
            cell("Evidence Count", header_style),
            cell("Negative Evidence", header_style)
        ]
    ]

    for finding in dpdp_result["findings"]:
        summary_table_data.append([
            cell(finding.get("control_title", ""), normal_style),
            cell(finding.get("status", ""), normal_style),
            cell(finding.get("risk", ""), normal_style),
            cell(str(finding.get("evidence_count", 0)), normal_style),
            cell(str(finding.get("negative_evidence_count", 0)), normal_style)
        ])

    summary_table = Table(
        summary_table_data,
        colWidths=[170, 80, 60, 80, 90],
        repeatRows=1
    )
    summary_table.setStyle(get_table_style())
    story.append(summary_table)

    story.append(PageBreak())

    # 4. Detailed Findings
    story.append(Paragraph("4. Detailed DPDP Findings", styles["Heading2"]))
    story.append(Spacer(1, 10))

    for finding in dpdp_result["findings"]:
        story.append(Paragraph(escape_text(finding.get("control_title", "")), styles["Heading3"]))

        story.append(Paragraph(f"<b>Status:</b> {escape_text(finding.get('status', ''))}", styles["Normal"]))
        story.append(Paragraph(f"<b>Risk:</b> {escape_text(finding.get('risk', ''))}", styles["Normal"]))
        story.append(Paragraph(f"<b>Description:</b> {escape_text(finding.get('description', ''))}", styles["Normal"]))
        story.append(Paragraph(f"<b>Recommendation:</b> {escape_text(finding.get('recommendation', ''))}", styles["Normal"]))

        story.append(
            Paragraph(
                f"<b>Positive Evidence Count:</b> {finding.get('positive_evidence_count', 0)}",
                styles["Normal"]
            )
        )
        story.append(
            Paragraph(
                f"<b>Negative Evidence Count:</b> {finding.get('negative_evidence_count', 0)}",
                styles["Normal"]
            )
        )
        story.append(
            Paragraph(
                f"<b>Neutral Evidence Count:</b> {finding.get('neutral_evidence_count', 0)}",
                styles["Normal"]
            )
        )

        matched_keywords = finding.get("matched_keywords", [])

        if matched_keywords:
            keywords_text = ", ".join(str(keyword) for keyword in matched_keywords[:15])
        else:
            keywords_text = "None"

        story.append(Paragraph(f"<b>Matched Keywords:</b> {escape_text(keywords_text)}", styles["Normal"]))
        story.append(Spacer(1, 8))

        evidence_items = finding.get("evidence", [])

        if evidence_items:
            evidence_table_data = [
                [
                    cell("Page", header_style),
                    cell("Keyword / Pattern", header_style),
                    cell("Match Type", header_style),
                    cell("Sentiment", header_style),
                    cell("Evidence Snippet", header_style)
                ]
            ]

            for evidence in evidence_items[:8]:
                sentiment = evidence.get("sentiment", "positive")

                evidence_table_data.append([
                    cell(str(evidence.get("page", "N/A")), normal_style),
                    cell(str(evidence.get("keyword", "")), normal_style),
                    cell(str(evidence.get("match_type", "")), normal_style),
                    cell(str(sentiment), normal_style),
                    cell(str(evidence.get("snippet", "")), normal_style)
                ])

            evidence_table = Table(
                evidence_table_data,
                colWidths=[35, 90, 65, 65, 225],
                repeatRows=1
            )
            evidence_table.setStyle(get_table_style())
            story.append(evidence_table)

        else:
            story.append(Paragraph("No direct evidence found for this control.", styles["Normal"]))

        story.append(Spacer(1, 18))

    # 5. False Positive Note
    story.append(Paragraph("5. False Positive Handling Note", styles["Heading2"]))
    story.append(
        Paragraph(
            "This report includes sentiment-aware evidence detection. This means the system does not treat "
            "every matched keyword as proof of compliance. For example, a sentence such as "
            "'no evidence of encryption at rest' is treated as negative evidence, not as a valid security safeguard.",
            styles["Normal"]
        )
    )
    story.append(Spacer(1, 12))

    # 6. Auditor Notes
    story.append(Paragraph("6. Auditor Notes", styles["Heading2"]))
    story.append(
        Paragraph(
            "This DPDP compliance report was generated automatically using rule-based policy analysis. "
            "It identifies whether DPDP-style controls appear to be present, partially present, missing, or failed. "
            "A human compliance reviewer should validate the final interpretation before making legal or audit decisions.",
            styles["Normal"]
        )
    )

    doc.build(story)

    return report_filename


def cell(text, style):
    """
    Converts table cell text into wrapped Paragraph.
    Prevents text from overflowing outside table cells.
    """

    return Paragraph(escape_text(str(text)), style)


def escape_text(text: str) -> str:
    """
    Escapes special characters that can break ReportLab Paragraph rendering.
    """

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