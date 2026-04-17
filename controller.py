from __future__ import annotations

import argparse
import json
from pathlib import Path

from modules.email_bot import send_email
from modules.file_organizer import organize_files
from modules.logger import get_logger
from modules.report_generator import generate_report


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "settings.json"


def load_settings() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as file:
        return json.load(file)


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
        help="Validate email flow without sending a real email",
    )

    subparsers.add_parser("generate-report", help="Generate a text report")
    return parser


def main() -> None:
    settings = load_settings()
    logger = get_logger(BASE_DIR / settings["paths"]["log_file"])
    parser = build_parser()
    args = parser.parse_args()

    organization_result = None
    email_result = None

    if args.command == "organize":
        source_folder = args.source_folder or settings["paths"]["source_folder"]
        organization_result = organize_files(
            BASE_DIR / source_folder,
            settings["organization"]["categories"],
            logger=logger,
        )
        print(json.dumps(organization_result, indent=2))
        return

    if args.command == "send-email":
        email_result = send_email(
            settings["email"],
            args.subject,
            args.body,
            recipient=args.recipient,
            logger=logger,
            dry_run=args.dry_run,
        )
        print(json.dumps(email_result, indent=2))
        return

    if args.command == "generate-report":
        report_result = generate_report(
            BASE_DIR / settings["paths"]["reports_folder"],
            BASE_DIR / settings["paths"]["log_file"],
            organization_result=organization_result,
            email_result=email_result,
            logger=logger,
        )
        print(json.dumps(report_result, indent=2))


if __name__ == "__main__":
    main()
