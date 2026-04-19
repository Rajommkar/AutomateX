import hashlib
from functools import wraps
from flask import session, jsonify

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against the hashed footprint stored in the database.
    Re-hashes the input to ensure a perfect 1-way mathematical match without decrypting the DB value.
    """
    hashed_input = hashlib.sha256(plain_password.encode()).hexdigest()
    return hashed_input == hashed_password

def require_auth(f):
    """
    Standard route protector decorator.
    Verifies the client possesses a cryptographically signed session cookie mapped to a user_id.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"status": "error", "message": "unauthorized. Please login to continue."}), 401
        return f(*args, **kwargs)
    return decorated
