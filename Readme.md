# AutomateX

## Overview

AutomateX is a Python-based automation system for repetitive daily tasks. It currently organizes files by type, prepares email workflows, generates activity reports, and records system events through a reusable logging module.

## Features

- Organizes files into categories such as Documents, Images, Audio, Archives, and Code
- Generates text reports for completed automation runs
- Supports dynamic email input with subject, message, and recipient
- Supports dry-run email testing before real credential setup
- Reads email credentials from environment variables instead of hardcoding them
- Logs actions, warnings, and errors with timestamps in `logs/activity.log`
- Uses `controller.py` as the central workflow layer connecting modules
- Uses a modular project structure that can scale into Flask and a web dashboard

## Project Structure

- `controller.py`: central control layer for running automation tasks
- `modules/file_organizer.py`: scans folders and moves files into category-based directories
- `modules/email_bot.py`: handles email send or dry-run execution
- `modules/report_generator.py`: creates reports in the `reports/` folder
- `modules/logger.py`: configures timestamped file logging
- `modules/config_manager.py`: loads settings and resolves runtime paths
- `controller.py`: coordinates file organization, email, and reporting as one system
- `config/settings.json`: stores source paths, log paths, and email settings

## Run From Terminal

```bash
python -B controller.py organize
python -B controller.py send-email --subject "Test" --body "Hello" --recipient "someone@example.com" --dry-run
python -B controller.py generate-report
python -B controller.py run-all --subject "Daily Report" --body "Automation completed." --recipient "someone@example.com" --dry-run
```

## Email Setup

Use environment variables for real email delivery:

```bash
AUTOMATEX_SENDER_EMAIL=your_email@example.com
AUTOMATEX_SENDER_PASSWORD=your_app_password
AUTOMATEX_SMTP_SERVER=smtp.gmail.com
AUTOMATEX_SMTP_PORT=587
AUTOMATEX_USE_TLS=true
AUTOMATEX_RECIPIENT_EMAIL=receiver@example.com
```

## Logging

All task activity is written to `logs/activity.log` with timestamps. This makes the project easier to debug, easier to demonstrate, and more aligned with real-world automation tools.
