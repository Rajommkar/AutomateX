# Smart Automation Bot

## Day 1 Scope

This project starts with terminal-based automation before adding Flask and the web dashboard.

### Available commands

```bash
python controller.py organize
python controller.py send-email --subject "Test" --body "Hello" --recipient "someone@example.com" --dry-run
python controller.py generate-report
```

### Current modules

- `modules/file_organizer.py`: sorts files into category folders
- `modules/email_bot.py`: sends or dry-runs email delivery
- `modules/report_generator.py`: creates text reports in `reports/`
- `modules/logger.py`: writes activity logs to `logs/Activity.log`
