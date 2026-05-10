import os
from datetime import datetime


REPORT_DIR = "reports"

os.makedirs(REPORT_DIR, exist_ok=True)


def generate_detection_report(
    filename: str,
    signals: dict,
    score_result: dict
) -> str:
    """
    Generates a human-readable markdown report that mirrors the JSON response.
    """

    safe_filename = filename.replace(".pdf", "").replace(" ", "_")
    report_filename = f"{safe_filename}_detection_report.md"
    report_path = os.path.join(REPORT_DIR, report_filename)

    found_signals = [
        signal_name
        for signal_name, details in signals.items()
        if details["found"]
    ]

    with open(report_path, "w", encoding="utf-8") as report:
        report.write("# Policy Criticality Detection Report\n\n")

        report.write("## 1. Document Information\n\n")
        report.write(f"- **Uploaded File:** {filename}\n")
        report.write(f"- **Report Generated At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        report.write("## 2. Criticality Score Summary\n\n")
        report.write(f"- **Criticality Score:** {score_result['criticality_score']} / 10\n")
        report.write(f"- **Recommended Tag:** {score_result['recommended_tag']}\n")
        report.write(f"- **Score Meaning:** {score_result['score_meaning']}\n\n")

        report.write("## 3. Score Scale\n\n")
        report.write("| Score Range | Level Meaning |\n")
        report.write("|---|---|\n")

        for score_range, meaning in score_result["score_scale"].items():
            report.write(f"| {score_range} | {meaning} |\n")

        report.write("\n")

        report.write("## 4. Signals Detected\n\n")

        if found_signals:
            for signal in found_signals:
                report.write(f"- {format_signal_name(signal)}\n")
        else:
            report.write("No criticality signals were detected.\n")

        report.write("\n")

        report.write("## 5. Score Breakdown\n\n")
        report.write("| Signal | Found | Weight | Contribution | Evidence Count |\n")
        report.write("|---|---:|---:|---:|---:|\n")

        for signal_name, details in score_result["score_breakdown"].items():
            report.write(
                f"| {format_signal_name(signal_name)} "
                f"| {details['found']} "
                f"| {details['weight']} "
                f"| {details['contribution']} "
                f"| {details['evidence_count']} |\n"
            )

        report.write("\n")

        report.write("## 6. Detailed Evidence\n\n")

        for signal_name, details in signals.items():
            report.write(f"### {format_signal_name(signal_name)}\n\n")
            report.write(f"- **Detected:** {details['found']}\n")

            matched_keywords = details.get("matched_keywords", [])

            if matched_keywords:
                report.write(f"- **Matched Keywords:** {', '.join(matched_keywords)}\n\n")
            else:
                report.write("- **Matched Keywords:** None\n\n")

            evidence_items = details.get("evidence", [])

            if evidence_items:
                report.write("| Page | Keyword / Pattern | Match Type | Evidence Snippet |\n")
                report.write("|---:|---|---|---|\n")

                for evidence in evidence_items[:10]:
                    page = evidence.get("page", "N/A")
                    keyword = escape_markdown_table(evidence.get("keyword", ""))
                    match_type = evidence.get("match_type", "keyword")
                    snippet = escape_markdown_table(evidence.get("snippet", ""))

                    report.write(
                        f"| {page} | {keyword} | {match_type} | {snippet} |\n"
                    )

                report.write("\n")
            else:
                report.write("No evidence found for this signal.\n\n")

        report.write("## 7. Auditor Notes\n\n")
        report.write(
            "This report is generated automatically from detected policy signals. "
            "It should be reviewed by a human auditor before making final compliance or classification decisions.\n"
        )

    return report_filename


def format_signal_name(signal_name: str) -> str:
    return signal_name.replace("_", " ").title()


def escape_markdown_table(text: str) -> str:
    if text is None:
        return ""

    return str(text).replace("|", "\\|").replace("\n", " ").strip()