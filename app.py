from __future__ import annotations

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from controller import AutomationController


def create_app() -> Flask:
    app = Flask(__name__)
    controller = AutomationController()

    @app.get("/")
    def index():
        return jsonify(
            {
                "project": controller.settings["app"].get(
                    "project_name",
                    "AutomateX",
                ),
                "message": "Day 3 backend is running.",
                "available_routes": [
                    "GET /health",
                    "POST /organize",
                    "POST /send-email",
                    "POST /generate-report",
                ],
            }
        )

    @app.get("/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "service": "backend",
            }
        )

    @app.post("/organize")
    def organize():
        payload = request.get_json(silent=True) or {}
        source_folder = payload.get("source_folder")
        result = controller.organize(source_folder=source_folder)
        return jsonify(result), 200

    @app.post("/send-email")
    def send_email():
        payload = request.get_json(silent=True) or {}
        subject = payload.get("subject")
        body = payload.get("body")

        if not subject or not body:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Both 'subject' and 'body' are required.",
                    }
                ),
                400,
            )

        result = controller.send_email(
            subject=subject,
            body=body,
            recipient=payload.get("recipient"),
            dry_run=payload.get("dry_run"),
        )
        return jsonify(result), 200

    @app.post("/generate-report")
    def generate_report():
        result = controller.generate_report()
        return jsonify(result), 200

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        if error.code == 404:
            controller.logger.warning("[api] route not found | %s", request.path)
        else:
            controller.logger.warning("[api] http error %s | %s", error.code, error)

        return (
            jsonify(
                {
                    "status": "error",
                    "message": error.description,
                    "code": error.code,
                }
            ),
            error.code,
        )

    @app.errorhandler(Exception)
    def handle_error(error: Exception):
        controller.logger.error("[api] failed | %s", error)
        return jsonify({"status": "error", "message": str(error)}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
