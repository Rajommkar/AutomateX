from __future__ import annotations

import argparse
import json
from pathlib import Path

from modules.config_manager import load_settings, resolve_paths
from modules.email_bot import send_email
from modules.file_organizer import organize_files
from modules.logger import (
    get_logger,
    log_task_error,
    log_task_start,
    log_task_success,
)
from modules.report_generator import generate_report
from modules.scheduler import NativeScheduler
from database.models import save_log



BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "settings.json"


class AutomationController:
    def __init__(self, base_dir: str | Path = BASE_DIR, config_path: str | Path = CONFIG_PATH):
        self.base_dir = Path(base_dir)
        self.config_path = Path(config_path)
        self.settings = load_settings(self.config_path)
        self.paths = resolve_paths(self.base_dir, self.settings)
        self.logger = get_logger(
            self.paths["log_file"],
            enable_console=bool(self.settings["app"].get("console_logging", False)),
        )

    def organize(self, source_folder: str | None = None) -> dict:
        task_name = "organize"
        log_task_start(self.logger, task_name)
        source_path = Path(source_folder) if source_folder else self.paths["source_folder"]
        if not source_path.is_absolute():
            source_path = self.base_dir / source_path

        result = organize_files(
            source_path,
            self.settings["organization"]["categories"],
            logger=self.logger,
        )
        self._record_task_result(task_name, result)
        log_task_success(
            self.logger,
            task_name,
            f"moved {result['total_files_moved']} files",
        )
        return result

    def send_email(
        self,
        subject: str,
        body: str,
        recipient: str | None = None,
        dry_run: bool | None = None,
    ) -> dict:
        task_name = "send_email"
        log_task_start(self.logger, task_name)
        should_dry_run = (
            self.settings["app"].get("default_email_dry_run", False)
            if dry_run is None
            else dry_run
        )
        result = send_email(
            self.settings["email"],
            subject,
            body,
            recipient=recipient,
            logger=self.logger,
            dry_run=should_dry_run,
        )
        self._record_task_result(task_name, result)
        log_task_success(
            self.logger,
            task_name,
            f"status {result['status']} for {result['recipient']}",
        )
        return result

    def generate_report(self) -> dict:
        task_name = "generate_report"
        log_task_start(self.logger, task_name)
        state_snapshot = self._load_state()
        result = generate_report(
            self.paths["reports_folder"],
            self.paths["log_file"],
            app_settings=self.settings["app"],
            state_snapshot=state_snapshot,
            logger=self.logger,
        )
        self._record_task_result(task_name, result)
        log_task_success(
            self.logger,
            task_name,
            f"saved report to {result['report_path']}",
        )
        return result

    def run_all(
        self,
        source_folder: str | None = None,
        subject: str | None = None,
        body: str | None = None,
        recipient: str | None = None,
        dry_run: bool | None = None,
    ) -> dict:
        workflow_result = {
            "organization": self.organize(source_folder=source_folder),
        }

        if subject and body:
            workflow_result["email"] = self.send_email(
                subject=subject,
                body=body,
                recipient=recipient,
                dry_run=dry_run,
            )

        workflow_result["report"] = self.generate_report()
        return workflow_result

    def start_scheduler(self):
        self.logger.info("Initializing global task scheduler...")
        scheduler = NativeScheduler(logger=self.logger)
        
        scheduler.every_hour(lambda: self.organize())
        scheduler.every_day_at(18, 0, lambda: self.generate_report())
        
        scheduler.start_blocking_loop()

    def _load_state(self) -> dict:
        state_path = self.paths["state_file"]
        if not state_path.exists():
            return {"last_results": {}, "history": []}

        with state_path.open(encoding="utf-8") as file:
            return json.load(file)

    def _record_task_result(self, task_name: str, result: dict) -> None:
        save_log(action=task_name, status=result.get("status", "completed"))
        state = self._load_state()
        timestamp = _current_timestamp()
        history_limit = int(self.settings["app"].get("history_limit", 20))

        state.setdefault("last_results", {})
        state.setdefault("history", [])
        state["last_results"][task_name] = result
        state["history"].append(
            {
                "task": task_name,
                "status": result.get("status", "completed"),
                "timestamp": timestamp,
            }
        )
        state["history"] = state["history"][-history_limit:]

        with self.paths["state_file"].open("w", encoding="utf-8") as file:
            json.dump(state, file, indent=2)


def _current_timestamp() -> str:
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Smart Automation Bot controller")
    subparsers = parser.add_subparsers(dest="command", required=True)

    organize_parser = subparsers.add_parser("organize", help="Organize files by type")
    organize_parser.add_argument(
        "--source-folder",
        help="Optional custom folder to organize",
    )

    email_parser = subparsers.add_parser("send-email", help="Send an email")
    email_parser.add_argument("--subject", required=True, help="Email subject")
    email_parser.add_argument("--body", required=True, help="Email message body")
    email_parser.add_argument("--recipient", help="Optional override recipient email")
    email_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=None,
        help="Validate email flow without sending a real email",
    )

    subparsers.add_parser("generate-report", help="Generate a text report")
    subparsers.add_parser("start-scheduler", help="Run the continuous background task scheduler")
    run_all_parser = subparsers.add_parser(
        "run-all",
        help="Run organization, optional email, and reporting in one workflow",
    )
    run_all_parser.add_argument(
        "--source-folder",
        help="Optional custom folder to organize",
    )
    run_all_parser.add_argument("--subject", help="Optional email subject")
    run_all_parser.add_argument("--body", help="Optional email body")
    run_all_parser.add_argument("--recipient", help="Optional email recipient")
    run_all_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=None,
        help="Validate the email step without sending a real email",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        controller = AutomationController()
        if args.command == "organize":
            result = controller.organize(source_folder=args.source_folder)
        elif args.command == "send-email":
            result = controller.send_email(
                subject=args.subject,
                body=args.body,
                recipient=args.recipient,
                dry_run=args.dry_run,
            )
        elif args.command == "generate-report":
            result = controller.generate_report()
        elif args.command == "start-scheduler":
            controller.start_scheduler()
            result = {"status": "success", "message": "Scheduler terminated."}
        else:
            result = controller.run_all(
                source_folder=args.source_folder,
                subject=args.subject,
                body=args.body,
                recipient=args.recipient,
                dry_run=args.dry_run,
            )
    except ValueError as error:
        if "controller" in locals():
            controller.logger.warning("[%s] validation failed | %s", args.command, error)
        print(json.dumps({"status": "error", "message": str(error)}, indent=2))
        raise SystemExit(1) from error
    except Exception as error:
        if "controller" in locals():
            log_task_error(controller.logger, args.command, error)
        print(json.dumps({"status": "error", "message": str(error)}, indent=2))
        raise SystemExit(1) from error

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
