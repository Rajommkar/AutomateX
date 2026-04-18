# AutomateX: Smart Automation Bot

## Overview
AutomateX is a professional-grade Python automation system for repetitive daily tasks. It combines clean coding structures with robust backend practices, delivering a highly scalable background processor linked to a Flask API and dashboard.

## Architecture
Flask → Controller → Modules → Logs

Our modular design demonstrates advanced system separation:
- **Flask (Web Layer):** Purely handles incoming HTTP requests and standardizes responses.
- **Controller Layer:** Acts as the strict middleware, keeping complex integrations out of the web layer.
- **Modules (Engine):** Isolated scripts for organizing files, sending emails, generating reports, and scheduling.
- **Configuration (config/settings.json):** We NEVER hardcode values. Paths, categories, and email credentials are all loaded dynamically to enhance scalability.
- **Storage/Logs:** All activities and failures are safely caught through global exception handling and logged to local text records.

## Features
- File automation system
- Email automation
- Logging system
- REST API

## Example API Response
Our backend implements strict, predictable formatting to ensure it is 100% frontend-ready.

```json
{
  "status": "success",
  "data": {
    "total_files_moved": 15,
    "summary": {
      "Images": 12,
      "Documents": 3
    }
  }
}
```

Error responses utilize the same wrapper:
```json
{
  "status": "error",
  "message": "[Errno 13] Permission denied:"
}
```

## Setup & Running the API
Install Flask and standard packages. You can run the automation either purely from the terminal or serve the web dashboard.

**Start the Flask Server:**
```bash
python app.py
```
*Navigate to `http://127.0.0.1:5000` to interact with the premium UI.*

## Email Setup (Environment Variables)
```bash
AUTOMATEX_SENDER_EMAIL=your_email@example.com
AUTOMATEX_SENDER_PASSWORD=your_app_password
AUTOMATEX_SMTP_SERVER=smtp.gmail.com
```
