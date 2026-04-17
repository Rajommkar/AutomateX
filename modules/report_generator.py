from __future__ import annotations

from datetime import datetime
from pathlib import Path


def _read_recent_logs(log_file: str | Path, limit: int = 10) -> list[str]:
    log_path = Path(log_file)
    if not log_path.exists():
        return ["No activity log found yet."]

    lines = log_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return ["Activity log is currently empty."]

    return lines[-limit:]


def generate_report(
    reports_folder: str | Path,
    log_file: str | Path,
    organization_result: dict | None = None,
    email_result: dict | None = None,
    logger=None,
) -> dict:
    reports_path = Path(reports_folder)
    reports_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_path = reports_path / f"automation_report_{timestamp}.txt"

    report_lines = [
        "Smart Automation Bot Report",
        f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "Task Summary",
        "-----------",
    ]

    if organization_result:
        report_lines.extend(
            [
                f"Files moved: {organization_result.get('total_files_moved', 0)}",
                "Organization breakdown:",
            ]
        )
        for category, count in organization_result.get("summary", {}).items():
            report_lines.append(f"- {category}: {count}")
    else:
        report_lines.append("Files moved: No organization run attached.")

    report_lines.append("")

    if email_result:
        report_lines.extend(
            [
                f"Email status: {email_result.get('status', 'unknown')}",
                f"Email recipient: {email_result.get('recipient', 'not provided')}",
                f"Email subject: {email_result.get('subject', 'not provided')}",
            ]
        )
    else:
        report_lines.append("Email status: No email run attached.")

    report_lines.extend(["", "Recent Activity Logs", "--------------------"])
    report_lines.extend(_read_recent_logs(log_file))

    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    if logger:
        logger.info("Generated report at %s", report_path)

    return {
        "report_path": str(report_path),
        "status": "generated",
    }
