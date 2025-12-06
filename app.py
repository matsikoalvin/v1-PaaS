from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from flask_cors import CORS
from firebase_admin import credentials, initialize_app, db
import firebase_admin
import os
import logging
import hashlib
import secrets
import uuid
import time

# --------------------------------------------
# App Setup
# --------------------------------------------
app = Flask(__name__, static_folder='templates', static_url_path='')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------
# Firebase Initialization
# ---------------------------------------------
try:
    if not firebase_admin._apps:
        cred_path = os.getenv('FIREBASE_CONFIG_PATH', 'firebase-key.json')
        database_url = os.getenv(
            'FIREBASE_DATABASE_URL',
            "https://highmarkgh-default-rtdb.firebaseio.com"
        )

        cred = credentials.Certificate(cred_path)
        initialize_app(cred, {"databaseURL": database_url})
        logger.info("Firebase initialized successfully.")
except Exception as e:
    logger.error(f"Firebase initialization failed: {e}")


# ---------------------------------------------
# Helpers
# ---------------------------------------------
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256', password.encode(), salt.encode(), 100000
    )
    return f"{salt}${pwd_hash.hex()}"


def verify_password(stored: str, provided: str) -> bool:
    try:
        salt, pwd_hash = stored.split("$")
        check = hashlib.pbkdf2_hmac(
            'sha256', provided.encode(), salt.encode(), 100000
        ).hex()
        return check == pwd_hash
    except Exception:
        return False


def get_all_users():
    """Retrieve all users at once (Realtime DB has no query-by-field)."""
    return db.reference("users").get() or {}


# ---------------------------------------------
# ROUTES — AUTH
# ---------------------------------------------
@app.route("/signup", methods=["POST"])
def signup():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()
        username = data.get("username", "").strip()

        # Input validation
        if not email or not password or not username:
            return jsonify({"error": "Email, password, and username are required"}), 400
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400

        # Check duplicates
        users = get_all_users()
        for u in users.values():
            if u["email"] == email:
                return jsonify({"error": "Email already registered"}), 409
            if u["username"] == username:
                return jsonify({"error": "Username already taken"}), 409

        uid = str(uuid.uuid4())
        hashed = hash_password(password)

        new_user = {
            "uid": uid,
            "email": email,
            "username": username,
            "password": hashed,
            "role": "user",
            "created_at": int(time.time() * 1000)
        }

        db.reference(f"users/{uid}").set(new_user)

        logger.info(f"New user created: {email}")
        return jsonify({
            "message": "Sign up successful",
            "uid": uid,
            "email": email,
            "username": username
        }), 201

    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({"error": "Sign up failed"}), 500


@app.route("/login", methods=["POST"])
def login():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        users = get_all_users()

        user = None
        uid = None
        for user_id, info in users.items():
            if info["email"] == email:
                user = info
                uid = user_id
                break

        if not user or not verify_password(user["password"], password):
            return jsonify({"error": "Invalid email or password"}), 401

        token = secrets.token_urlsafe(32)

        return jsonify({
            "message": "Login successful",
            "uid": uid,
            "username": user["username"],
            "email": user["email"],
            "role": user.get("role", "user"),
            "token": token
        }), 200

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Authentication failed"}), 500


# ---------------------------------------------
# User retrieval / update
# ---------------------------------------------
@app.route("/user/<uid>", methods=["GET"])
def get_user(uid):
    try:
        user = db.reference(f"users/{uid}").get()
        if not user:
            return jsonify({"error": "User not found"}), 404

        user.pop("password", None)  # Never return password
        return jsonify(user), 200

    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({"error": "Failed to retrieve user"}), 500


@app.route("/user/<uid>", methods=["PUT"])
def update_user(uid):
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()
        user_ref = db.reference(f"users/{uid}")
        user_data = user_ref.get()

        if not user_data:
            return jsonify({"error": "User not found"}), 404

        allowed = ["username", "email", "role"]
        updates = {k: v for k, v in data.items() if k in allowed}

        if not updates:
            return jsonify({"error": "No valid fields to update"}), 400

        user_ref.update(updates)

        return jsonify({"message": "User updated", "uid": uid, **updates}), 200

    except Exception as e:
        logger.error(f"Update error: {e}")
        return jsonify({"error": "Failed to update user"}), 500

@app.route("/test-db")
def test_db():
    try:
        ref = db.reference("test_connection")
        ref.set({"status": "connected"})
        return jsonify({"message": "Firebase connection OK"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------
# Logout
# ---------------------------------------------
@app.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Logged out successfully"}), 200


# ---------------------------------------------
# Error Handlers
# ---------------------------------------------
@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal(_):
    return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------
# Static Pages & Routing
# ---------------------------------------------
@app.route("/")
def index():
    """Root route - redirect to sign-in page"""
    return redirect(url_for('serve_signin'))


@app.route("/pages/sign-in.html")
def serve_signin():
    """Serve sign-in page"""
    return send_from_directory(os.path.join(app.static_folder, 'pages'), 'sign-in.html')


@app.route("/pages/sign-up.html")
def serve_signup():
    """Serve sign-up page"""
    return send_from_directory(os.path.join(app.static_folder, 'pages'), 'sign-up.html')


@app.route("/pages/dashboard.html")
def serve_dashboard():
    """Serve dashboard page (protected by JS on frontend)"""
    return send_from_directory(os.path.join(app.static_folder, 'pages'), 'dashboard.html')


@app.route("/pages/<path:filename>")
def serve_pages(filename):
    """Serve any other pages"""
    return send_from_directory(os.path.join(app.static_folder, 'pages'), filename)


@app.route("/assets/<path:filename>")
def serve_assets(filename):
    """Serve assets (CSS, JS, images, etc)"""
    return send_from_directory(os.path.join(app.static_folder, 'assets'), filename)
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
