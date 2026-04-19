from __future__ import annotations

import os
from flask import Flask, jsonify, request, render_template, session

from controller import AutomationController
from database.db import init_db
from database.models import create_user, get_user
from modules.auth import require_auth, verify_password


def create_app() -> Flask:
    app = Flask(__name__)
    # Ensures sessions are cryptographically signed correctly
    app.secret_key = os.environ.get("SECRET_KEY", "automatex-pro-dev-secret")
    
    controller = AutomationController()

    # Initialize the local database automatically
    init_db()

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify({"status": "success", "data": {"service": "AutomateX"}}), 200
        
    @app.post("/auth/signup")
    def signup():
        payload = request.get_json(silent=True) or {}
        email = payload.get("email")
        password = payload.get("password")
        if not email or not password:
            return jsonify({"status": "error", "message": "Email and password are required"}), 400
            
        try:
            # Models automatically hashes the password
            user_id = create_user(email, password)
            return jsonify({"status": "success", "message": "Account created!", "data": {"user_id": user_id, "email": email}}), 201
        except Exception as e:
            return jsonify({"status": "error", "message": f"Signup failed (did you use an existing email?): {str(e)}"}), 400

    @app.post("/auth/login")
    def login():
        payload = request.get_json(silent=True) or {}
        email = payload.get("email")
        password = payload.get("password")
        
        user = get_user(email)
        if not user or not verify_password(password, user["password"]):
            return jsonify({"status": "error", "message": "Invalid email or password"}), 401
            
        # Bind the user to the encrypted session cookie dynamically
        session["user_id"] = user["id"]
        # Make the cookie persistent across browser restarts if desired
        session.permanent = True  
        return jsonify({"status": "success", "message": "Logged in successfully", "data": {"user_id": user["id"], "email": user["email"]}}), 200

    @app.post("/auth/logout")
    def logout():
        session.pop("user_id", None)
        return jsonify({"status": "success", "message": "Logged out successfully"}), 200

    @app.post("/organize")
    @require_auth
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
    @require_auth
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
    @require_auth
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
