# Smart Automation Bot

## Day 1 and Day 2 Scope

This project starts with terminal-based automation before adding Flask and the web dashboard. Day 2 improves the project structure with a central controller, cleaner config handling, and persistent runtime state.

### Available commands

```bash
python controller.py organize
python controller.py send-email --subject "Test" --body "Hello" --recipient "someone@example.com" --dry-run
python controller.py generate-report
python controller.py run-all --subject "Daily Report" --body "Automation completed." --recipient "someone@example.com" --dry-run
```

### Current modules

- `modules/file_organizer.py`: sorts files into category folders
- `modules/email_bot.py`: sends or dry-runs email delivery
- `modules/report_generator.py`: creates text reports in `reports/`
- `modules/logger.py`: writes activity logs to `logs/Activity.log`
- `modules/config_manager.py`: loads settings and prepares runtime paths
- `controller.py`: central orchestration layer for terminal workflows
