import re
import datetime
from datetime import timezone
import jwt
import bcrypt
from functools import wraps
from flask import request, jsonify, session, current_app
from backend.config import Config
from firebase.database_service import get_db_service

class AuthManager:
    """
    Handles user authentication, token issuance, password hashing,
    and role-based access control.
    """
    def __init__(self):
        self.db = get_db_service()

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        if not plain_password or not hashed_password:
            return False
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False

    @staticmethod
    def generate_token(user_id: str, role: str = "user", expires_in_hours: int = 24) -> str:
        payload = {
            "sub": user_id,
            "role": role,
            "iat": datetime.datetime.now(timezone.utc),
            "exp": datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=expires_in_hours)
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def decode_token(token: str):
        try:
            return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def register_user(self, data):
        """
        Validates and registers a new user.
        Fields: name, email, password, age, height, weight, gender.
        """
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        age = data.get("age")
        height = data.get("height")
        weight = data.get("weight")
        gender = data.get("gender", "prefer_not_to_say")
        role = data.get("role", "user")

        # Basic validations
        if not name or len(name) < 2:
            return {"error": "Name must be at least 2 characters long."}, 400

        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email):
            return {"error": "Invalid email address format."}, 400

        if not password or len(password) < 6:
            return {"error": "Password must be at least 6 characters long."}, 400

        try:
            age = int(age) if age else 25
            height = float(height) if height else 175.0 # in cm
            weight = float(weight) if weight else 70.0  # in kg
        except ValueError:
            return {"error": "Age, height, and weight must be valid numeric values."}, 400

        # Check existing user
        existing_user = self.db.get_user_by_email(email)
        if existing_user:
            return {"error": "An account with this email address already exists."}, 409

        password_hash = self.hash_password(password)

        new_user = {
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "age": age,
            "height": height,
            "weight": weight,
            "gender": gender,
            "role": role,
            "step_goal": 10000,
            "calorie_goal": 2000,
            "sleep_goal": 8.0,
            "resting_hr_baseline": 68
        }

        created = self.db.create_user(new_user)
        # Create a safe copy without password
        safe_user = {k: v for k, v in created.items() if k != "password_hash"}
        token = self.generate_token(safe_user["user_id"], safe_user.get("role", "user"))

        return {
            "message": "User registered successfully.",
            "token": token,
            "user": safe_user
        }, 201

    def login_user(self, email, password):
        if not email or not password:
            return {"error": "Email and password are required."}, 400

        user = self.db.get_user_by_email(email)
        if not user or not self.verify_password(password, user.get("password_hash", "")):
            return {"error": "Invalid email or password credentials."}, 401

        safe_user = {k: v for k, v in user.items() if k != "password_hash"}
        token = self.generate_token(safe_user["user_id"], safe_user.get("role", "user"))

        return {
            "message": "Login successful.",
            "token": token,
            "user": safe_user
        }, 200

    def get_current_user_from_request(self):
        """
        Extracts authenticated user from either Bearer token or session.
        """
        auth_header = request.headers.get("Authorization")
        token = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        elif "jwt_token" in session:
            token = session.get("jwt_token")

        if not token:
            return None

        decoded = self.decode_token(token)
        if not decoded:
            return None

        user_id = decoded.get("sub")
        user = self.db.get_user_by_id(user_id)
        if user:
            return {k: v for k, v in user.items() if k != "password_hash"}
        return None


auth_manager = AuthManager()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = auth_manager.get_current_user_from_request()
        if not user:
            # If AJAX / API request
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized. Please authenticate."}), 401
            # If web view
            session["next_url"] = request.url
            from flask import redirect, url_for
            return redirect(url_for("auth_views.login_page"))
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = auth_manager.get_current_user_from_request()
        if not user or user.get("role") != "admin":
            if request.path.startswith("/api/"):
                return jsonify({"error": "Forbidden: Administrator privileges required."}), 403
            from flask import redirect, url_for, flash
            return redirect(url_for("dashboard_views.dashboard_page"))
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function
