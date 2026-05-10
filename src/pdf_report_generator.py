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
    TableStyle
)
from reportlab.lib.enums import TA_LEFT


REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)


def generate_detection_pdf_report(
    filename: str,
    signals: dict,
    score_result: dict
) -> str:
    """
    Generates PDF report for criticality signal detection.
    Used by /generate-criticality-pdf.
    """

    safe_filename = filename.replace(".pdf", "").replace(" ", "_")
    report_filename = f"{safe_filename}_criticality_detection_report.pdf"
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

    story.append(Paragraph("Criticality Detection Report", styles["Title"]))
    story.append(Spacer(1, 16))

    story.append(Paragraph("1. Document Information", styles["Heading2"]))
    story.append(Paragraph(f"<b>Uploaded File:</b> {escape_text(filename)}", styles["Normal"]))
    story.append(
        Paragraph(
            f"<b>Report Generated At:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"]
        )
    )
    story.append(Spacer(1, 14))

    story.append(Paragraph("2. Criticality Score Summary", styles["Heading2"]))

    score_table_data = [
        [cell("Metric", header_style), cell("Value", header_style)],
        [cell("Criticality Score", normal_style), cell(str(score_result.get("criticality_score", "")), normal_style)],
        [cell("Recommended Tag", normal_style), cell(score_result.get("recommended_tag", ""), normal_style)],
        [cell("Confidence", normal_style), cell(str(score_result.get("confidence", "")), normal_style)],
        [cell("Score Meaning", normal_style), cell(score_result.get("score_meaning", ""), normal_style)],
        [cell("Score Scale", normal_style), cell(score_result.get("score_scale", ""), normal_style)],
    ]

    score_table = Table(score_table_data, colWidths=[160, 320], repeatRows=1)
    score_table.setStyle(get_table_style())
    story.append(score_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("3. Detected Criticality Signals", styles["Heading2"]))

    signal_table_data = [
        [
            cell("Signal", header_style),
            cell("Found", header_style),
            cell("Weight", header_style),
            cell("Evidence Count", header_style),
            cell("Evidence Preview", header_style),
        ]
    ]

    for signal_name, details in signals.items():
        evidence_items = details.get("evidence", [])
        evidence_preview = ""

        if evidence_items:
            first_evidence = evidence_items[0]
            evidence_preview = first_evidence.get("snippet", "")

        signal_table_data.append([
            cell(signal_name, normal_style),
            cell(str(details.get("found", False)), normal_style),
            cell(str(details.get("weight", "")), normal_style),
            cell(str(len(evidence_items)), normal_style),
            cell(evidence_preview, normal_style),
        ])

    signal_table = Table(
        signal_table_data,
        colWidths=[100, 55, 50, 75, 200],
        repeatRows=1
    )
    signal_table.setStyle(get_table_style())
    story.append(signal_table)

    story.append(Spacer(1, 16))

    story.append(Paragraph("4. Human Review Note", styles["Heading2"]))
    story.append(
        Paragraph(
            "This report is generated using deterministic criticality signal detection. "
            "The output should be reviewed by a human auditor before final classification decisions.",
            styles["Normal"]
        )
    )

    doc.build(story)

    return report_filename


def generate_tag_validation_pdf_report(
    filename: str,
    validation: dict,
    signals: dict,
    score_result: dict
) -> str:
    """
    Generates PDF report for given criticality tag validation.
    Used by /generate-tag-validation-pdf.
    """

    safe_filename = filename.replace(".pdf", "").replace(" ", "_")
    report_filename = f"{safe_filename}_tag_validation_report.pdf"
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

    story.append(Paragraph("Criticality Tag Validation Report", styles["Title"]))
    story.append(Spacer(1, 16))

    story.append(Paragraph("1. Document Information", styles["Heading2"]))
    story.append(Paragraph(f"<b>Uploaded File:</b> {escape_text(filename)}", styles["Normal"]))
    story.append(
        Paragraph(
            f"<b>Report Generated At:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"]
        )
    )
    story.append(Spacer(1, 14))

    story.append(Paragraph("2. Tag Validation Summary", styles["Heading2"]))

    validation_table_data = [
        [cell("Field", header_style), cell("Value", header_style)],
        [cell("Given Tag", normal_style), cell(validation.get("given_tag", ""), normal_style)],
        [cell("Recommended Tag", normal_style), cell(validation.get("recommended_tag", ""), normal_style)],
        [cell("Validation Result", normal_style), cell(validation.get("validation_result", ""), normal_style)],
        [cell("Confidence", normal_style), cell(str(validation.get("confidence", "")), normal_style)],
        [cell("Reason", normal_style), cell(validation.get("reason", ""), normal_style)],
    ]

    validation_table = Table(
        validation_table_data,
        colWidths=[150, 330],
        repeatRows=1
    )
    validation_table.setStyle(get_table_style())
    story.append(validation_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("3. System Criticality Score", styles["Heading2"]))

    score_table_data = [
        [cell("Metric", header_style), cell("Value", header_style)],
        [cell("Criticality Score", normal_style), cell(str(score_result.get("criticality_score", "")), normal_style)],
        [cell("Recommended Tag", normal_style), cell(score_result.get("recommended_tag", ""), normal_style)],
        [cell("Confidence", normal_style), cell(str(score_result.get("confidence", "")), normal_style)],
        [cell("Score Meaning", normal_style), cell(score_result.get("score_meaning", ""), normal_style)],
        [cell("Score Scale", normal_style), cell(score_result.get("score_scale", ""), normal_style)],
    ]

    score_table = Table(
        score_table_data,
        colWidths=[150, 330],
        repeatRows=1
    )
    score_table.setStyle(get_table_style())
    story.append(score_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("4. Signal Evidence Summary", styles["Heading2"]))

    signal_table_data = [
        [
            cell("Signal", header_style),
            cell("Found", header_style),
            cell("Weight", header_style),
            cell("Evidence Count", header_style),
            cell("Evidence Preview", header_style),
        ]
    ]

    for signal_name, details in signals.items():
        evidence_items = details.get("evidence", [])
        evidence_preview = ""

        if evidence_items:
            evidence_preview = evidence_items[0].get("snippet", "")

        signal_table_data.append([
            cell(signal_name, normal_style),
            cell(str(details.get("found", False)), normal_style),
            cell(str(details.get("weight", "")), normal_style),
            cell(str(len(evidence_items)), normal_style),
            cell(evidence_preview, normal_style),
        ])

    signal_table = Table(
        signal_table_data,
        colWidths=[100, 55, 50, 75, 200],
        repeatRows=1
    )
    signal_table.setStyle(get_table_style())
    story.append(signal_table)

    story.append(Spacer(1, 16))

    story.append(Paragraph("5. Human Review Note", styles["Heading2"]))
    story.append(
        Paragraph(
            "This validation report compares the given criticality tag with the system-recommended tag. "
            "Final classification should be reviewed by a human auditor before use in formal compliance decisions.",
            styles["Normal"]
        )
    )

    doc.build(story)

    return report_filename


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