import os
import sys
import logging
from pathlib import Path
from flask import Flask, render_template, jsonify
from flask_cors import CORS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Config
from backend.routes.auth_routes import auth_bp
from backend.routes.health_routes import health_bp
from backend.routes.analytics_routes import analytics_bp
from backend.routes.alert_routes import alert_bp
from backend.routes.emergency_routes import emergency_bp
from backend.routes.admin_routes import admin_bp
from backend.authentication.auth_manager import auth_manager
from firebase.database_service import get_db_service

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
)
logger = logging.getLogger("SmartFitness.App")

def create_app():
    app = Flask(
        __name__,
        template_folder=str(Config.TEMPLATES_DIR),
        static_folder=str(Config.STATIC_DIR)
    )
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    # Enable CORS for API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(alert_bp)
    app.register_blueprint(emergency_bp)
    app.register_blueprint(admin_bp)

    # Landing page route
    @app.route("/", methods=["GET"])
    def landing_page():
        current_user = auth_manager.get_current_user_from_request()
        return render_template("index.html", user=current_user)

    # API Documentation route
    @app.route("/api/docs", methods=["GET"])
    def api_docs():
        return jsonify({
            "project": "A Mobile Computing Framework for Smart Fitness Monitoring and Healthcare",
            "version": "1.0.0",
            "endpoints": [
                {"method": "POST", "path": "/api/register", "desc": "Register a new user account"},
                {"method": "POST", "path": "/api/login", "desc": "Authenticate and obtain JWT token"},
                {"method": "GET",  "path": "/api/profile", "desc": "Fetch current user profile and goals"},
                {"method": "PUT",  "path": "/api/profile", "desc": "Update user metrics and fitness targets"},
                {"method": "POST", "path": "/api/health-data", "desc": "Ingest biometric health reading"},
                {"method": "GET",  "path": "/api/health-data", "desc": "Query historical health records"},
                {"method": "GET",  "path": "/api/dashboard", "desc": "Aggregated daily & weekly summary"},
                {"method": "GET",  "path": "/api/analytics", "desc": "BMI and Machine Learning analytics"},
                {"method": "POST", "path": "/api/predict", "desc": "Inference on activity and anomaly detection"},
                {"method": "GET",  "path": "/api/predictions", "desc": "Recent ML inference history"},
                {"method": "POST", "path": "/api/alerts", "desc": "Trigger health alert"},
                {"method": "GET",  "path": "/api/alerts", "desc": "Fetch user health alerts"},
                {"method": "PUT",  "path": "/api/alerts/<id>/resolve", "desc": "Resolve active alert"},
                {"method": "GET",  "path": "/api/emergency-contacts", "desc": "List emergency contacts"},
                {"method": "POST", "path": "/api/emergency-contacts", "desc": "Add emergency contact"},
                {"method": "DELETE", "path": "/api/emergency-contacts/<id>", "desc": "Delete emergency contact"},
                {"method": "POST", "path": "/api/emergency-contacts/test", "desc": "Trigger test emergency dispatch"}
            ]
        })

    # Error Handlers
    @app.errorhandler(404)
    def not_found_handler(e):
        if app.request_class and app.test_client:
            pass
        from flask import request
        if request.path.startswith("/api/"):
            return jsonify({"error": "Resource not found"}), 404
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error_handler(e):
        from flask import request
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal server error"}), 500
        return render_template("500.html"), 500

    # Ensure demo accounts exist for testing
    seed_demo_accounts()

    return app

def seed_demo_accounts():
    """
    Creates default admin and demo user accounts if not present,
    guaranteeing seamless presentation during college project evaluations.
    """
    try:
        db = get_db_service()
        # 1. Admin account
        admin_email = "admin@smartfitness.local"
        if not db.get_user_by_email(admin_email):
            admin_data = {
                "name": "System Administrator",
                "email": admin_email,
                "password_hash": auth_manager.hash_password("Admin@123456"),
                "age": 32,
                "height": 178.0,
                "weight": 75.0,
                "gender": "male",
                "role": "admin",
                "step_goal": 10000,
                "calorie_goal": 2200,
                "sleep_goal": 8.0
            }
            db.create_user(admin_data)
            logger.info("Created default Admin account: admin@smartfitness.local (Admin@123456)")

        # 2. Demo User account
        demo_email = "demo@smartfitness.local"
        demo_user = db.get_user_by_email(demo_email)
        if not demo_user:
            demo_data = {
                "name": "Alex Morgan",
                "email": demo_email,
                "password_hash": auth_manager.hash_password("Demo@123456"),
                "age": 24,
                "height": 175.0,
                "weight": 68.5,
                "gender": "female",
                "role": "user",
                "step_goal": 10000,
                "calorie_goal": 1800,
                "sleep_goal": 8.0
            }
            created_demo = db.create_user(demo_data)
            demo_user_id = created_demo["user_id"]
            
            # Seed emergency contact for demo user
            db.add_emergency_contact({
                "user_id": demo_user_id,
                "name": "Dr. Sarah Jenkins",
                "relationship": "Physician",
                "phone": "+1 (555) 345-6789",
                "email": "dr.jenkins@healthcare-clinic.local",
                "is_primary": True
            })
            db.add_emergency_contact({
                "user_id": demo_user_id,
                "name": "Robert Morgan",
                "relationship": "Parent",
                "phone": "+1 (555) 987-6543",
                "email": "robert.morgan@example.com",
                "is_primary": False
            })

            # Seed health history
            from backend.services.health_service import get_health_service
            get_health_service().seed_user_history(demo_user_id)
            logger.info("Created default Demo user: demo@smartfitness.local (Demo@123456)")
    except Exception as e:
        logger.warning(f"Demo seeding warning: {e}")

if __name__ == "__main__":
    app = create_app()
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
