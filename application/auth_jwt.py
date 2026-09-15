import base64
import hmac
import hashlib
import json
import time
from functools import wraps
from flask import request, jsonify, redirect, url_for, flash, current_app
from flask_login import current_user, login_user

JWT_SECRET_KEY = "trekking_management_jwt_secret_key_v1"


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def _b64_decode(data_str: str) -> bytes:
    padding = '=' * (4 - (len(data_str) % 4))
    return base64.urlsafe_b64decode(data_str + padding)


def generate_jwt(user, expires_in=86400 * 7):
    """
    Generates a battle-tested HS256 JWT token for the user.
    """
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "iat": now,
        "exp": now + expires_in
    }

    header_b64 = _b64_encode(json.dumps(header).encode('utf-8'))
    payload_b64 = _b64_encode(json.dumps(payload).encode('utf-8'))

    msg = f"{header_b64}.{payload_b64}".encode('utf-8')
    sig_raw = hmac.new(
        JWT_SECRET_KEY.encode('utf-8'),
        msg,
        hashlib.sha256
    ).digest()

    sig_b64 = _b64_encode(sig_raw)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_jwt(token: str):
    """
    Decodes and verifies a JWT token. Returns payload dict if valid, else None.
    """
    if not token or not isinstance(token, str):
        return None

    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None

        header_b64, payload_b64, sig_b64 = parts

        msg = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_sig_raw = hmac.new(
            JWT_SECRET_KEY.encode('utf-8'),
            msg,
            hashlib.sha256
        ).digest()

        expected_sig_b64 = _b64_encode(expected_sig_raw)

        if not hmac.compare_digest(sig_b64, expected_sig_b64):
            return None

        payload_bytes = _b64_decode(payload_b64)
        payload = json.loads(payload_bytes.decode('utf-8'))

        now = time.time()
        if payload.get("exp") and now > payload["exp"]:
            return None

        return payload
    except Exception:
        return None


def get_jwt_from_request():
    """
    Extracts JWT token from Authorization header, jwt_token cookie, or query string.
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()

    cookie_token = request.cookies.get("jwt_token")
    if cookie_token:
        return cookie_token.strip()

    param_token = request.args.get("token")
    if param_token:
        return param_token.strip()

    return None


def jwt_required(roles=None):
    """
    Decorator to enforce JWT token authorization & optional role-based access control.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = get_jwt_from_request()
            payload = decode_jwt(token) if token else None

            if not payload:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({"error": "Unauthorized", "message": "Invalid or expired JWT token."}), 401
                flash("Session expired or invalid. Please log in.", "danger")
                return redirect(url_for("login"))

            if roles:
                allowed_roles = [roles] if isinstance(roles, str) else roles
                if payload.get("role") not in allowed_roles:
                    if request.is_json or request.path.startswith('/api/'):
                        return jsonify({"error": "Forbidden", "message": "Insufficient permissions."}), 403
                    return "Access Denied.", 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
