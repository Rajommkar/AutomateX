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


def _pick_result(
    task_name: str,
    explicit_result: dict | None,
    state_snapshot: dict | None,
) -> dict | None:
    if explicit_result:
        return explicit_result

    if not state_snapshot:
        return None

    return state_snapshot.get("last_results", {}).get(task_name)


def generate_report(
    reports_folder: str | Path,
    log_file: str | Path,
    app_settings: dict | None = None,
    state_snapshot: dict | None = None,
    organization_result: dict | None = None,
    email_result: dict | None = None,
    logger=None,
) -> dict:
    try:
        reports_path = Path(reports_folder)
        reports_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_path = reports_path / f"automation_report_{timestamp}.txt"
        report_settings = app_settings or {}
        organization_result = _pick_result(
            "organize",
            organization_result,
            state_snapshot,
        )
        email_result = _pick_result(
            "send_email",
            email_result,
            state_snapshot,
        )
        recent_logs = _read_recent_logs(
            log_file,
            limit=int(report_settings.get("report_log_lines", 10)),
        )

        report_lines = [
            report_settings.get("project_name", "Smart Automation Bot Report"),
            f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "Task Summary",
            "-----------",
        ]

        if organization_result:
            report_lines.extend(
                [
                    f"Files moved: {organization_result.get('total_files_moved', 0)}",
                    f"Files skipped: {len(organization_result.get('skipped_files', []))}",
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
                    f"Email delivery mode: {email_result.get('delivery_mode', 'unknown')}",
                    f"Email recipient: {email_result.get('recipient', 'not provided')}",
                    f"Email subject: {email_result.get('subject', 'not provided')}",
                    f"Email message: {email_result.get('message', 'not provided')}",
                ]
            )
        else:
            report_lines.append("Email status: No email run attached.")

        if state_snapshot:
            report_lines.extend(["", "Recent Task History", "-------------------"])
            for item in state_snapshot.get("history", [])[-5:]:
                report_lines.append(
                    f"- {item['timestamp']} | {item['task']} | {item['status']}"
                )

        report_lines.extend(["", "Recent Activity Logs", "--------------------"])
        report_lines.extend(recent_logs)

        report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

        if logger:
            logger.info("Generated report at %s", report_path)

        return {
            "report_path": str(report_path),
            "status": "completed",
        }
    except Exception as e:
        if logger:
            logger.error(f"Global exception in report_generator: {e}")
        return {"status": "error", "message": str(e)}
