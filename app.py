from __future__ import annotations

from flask import Flask, jsonify, request, render_template

from controller import AutomationController


def create_app() -> Flask:
    app = Flask(__name__)
    controller = AutomationController()

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify({"status": "success", "data": {"service": "AutomateX"}}), 200

    @app.post("/organize")
    def organize():
        payload = request.get_json(silent=True) or {}
        try:
            result = controller.organize(source_folder=payload.get("source_folder"))
            if result.get("status") == "error":
                return jsonify({"status": "error", "message": result.get("message")}), 400
            return jsonify({"status": "success", "data": result}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.post("/send-email")
    def send_email():
        payload = request.get_json(silent=True) or {}
        try:
            result = controller.send_email(
                subject=payload.get("subject", ""),
                body=payload.get("body", ""),
                recipient=payload.get("recipient"),
                dry_run=payload.get("dry_run", False),
            )
            if result.get("status") == "error":
                return jsonify({"status": "error", "message": result.get("message")}), 400
            return jsonify({"status": "success", "data": result}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.post("/generate-report")
    def generate_report():
        try:
            result = controller.generate_report()
            if result.get("status") == "error":
                return jsonify({"status": "error", "message": result.get("message")}), 400
            return jsonify({"status": "success", "data": result}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify({"status": "error", "message": str(e)}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
