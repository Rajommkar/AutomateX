from __future__ import annotations

from datetime import datetime

from flask import Flask, jsonify, request, render_template
from werkzeug.exceptions import HTTPException

from controller import AutomationController


def format_api_response(success: bool, message: str, data: dict | None = None, error: str | None = None) -> dict:
    """Standardize the API response format for professional presentation."""
    return {
        "success": success,
        "message": message,
        "data": data or {},
        "error": error,
        "timestamp": datetime.now().isoformat(),
    }


def create_app() -> Flask:
    app = Flask(__name__)
    controller = AutomationController()

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify(
            format_api_response(
                success=True,
                message="Service is healthy and running.",
                data={"service": "AutomateX Backend", "status": "ok"}
            )
        ), 200

    @app.post("/organize")
    def organize():
        payload = request.get_json(silent=True) or {}
        source_folder = payload.get("source_folder")
        
        # Controller acts as the strict middle-man. Flask handles ONLY HTTP.
        result = controller.organize(source_folder=source_folder)
        
        files_moved = result.get("total_files_moved", 0)
        warning_msg = " (with warnings)" if result.get("status") == "completed_with_warnings" else ""
        
        return jsonify(
            format_api_response(
                success=True,
                message=f"Successfully organized {files_moved} files{warning_msg}.",
                data=result
            )
        ), 200

    @app.post("/send-email")
    def send_email():
        payload = request.get_json(silent=True) or {}
        subject = payload.get("subject")
        body = payload.get("body")

        if not subject or not body:
            return jsonify(
                format_api_response(
                    success=False,
                    message="Validation failed.",
                    error="Both 'subject' and 'body' are required fields."
                )
            ), 400

        result = controller.send_email(
            subject=subject,
            body=body,
            recipient=payload.get("recipient"),
            dry_run=payload.get("dry_run"),
        )
        
        mode = "Dry run: " if result.get("status") == "dry_run" else ""
        return jsonify(
            format_api_response(
                success=True,
                message=f"{mode}Email successfully processed for {result.get('recipient')}.",
                data=result
            )
        ), 200

    @app.post("/generate-report")
    def generate_report():
        result = controller.generate_report()
        return jsonify(
            format_api_response(
                success=True,
                message="System report generated successfully.",
                data=result
            )
        ), 200

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        if error.code == 404:
            controller.logger.warning("[api] route not found | %s", request.path)
        else:
            controller.logger.warning("[api] http error %s | %s", error.code, error.description)

        return jsonify(
            format_api_response(
                success=False,
                message="HTTP Error occurred.",
                error=error.description,
            )
        ), error.code

    @app.errorhandler(ValueError)
    def handle_validation_error(error: ValueError):
        controller.logger.warning("[api] validation failed | %s", error)
        return jsonify(
            format_api_response(
                success=False,
                message="Invalid input data provided.",
                error=str(error),
            )
        ), 400

    @app.errorhandler(Exception)
    def handle_error(error: Exception):
        controller.logger.error("[api] failed | %s", error)
        return jsonify(
            format_api_response(
                success=False,
                message="An internal server error occurred.",
                error=str(error),
            )
        ), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
