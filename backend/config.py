import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "smart-fitness-dev-secret-key-fallback")
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
    PORT = int(os.getenv("PORT", 5000))
    HOST = os.getenv("HOST", "127.0.0.1")
    
    # Project paths
    BASE_DIR = BASE_DIR
    FRONTEND_DIR = BASE_DIR / "frontend"
    STATIC_DIR = FRONTEND_DIR / "static"
    TEMPLATES_DIR = FRONTEND_DIR / "templates"
    
    # Firebase settings
    FIREBASE_MODE = os.getenv("FIREBASE_MODE", "emulated") # 'cloud' or 'emulated'
    FIREBASE_SERVICE_ACCOUNT_KEY = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY", "firebase/serviceAccountKey.json")
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "smart-fitness-health-capstone")
    LOCAL_DB_PATH = BASE_DIR / "firebase" / "local_firestore_db.json"
    
    # Machine Learning settings
    ML_ACTIVITY_MODEL_PATH = BASE_DIR / os.getenv("ML_ACTIVITY_MODEL_PATH", "machine_learning/models/activity_classifier.joblib")
    ML_ANOMALY_MODEL_PATH = BASE_DIR / os.getenv("ML_ANOMALY_MODEL_PATH", "machine_learning/models/anomaly_detector.joblib")
    ML_SCALER_PATH = BASE_DIR / os.getenv("ML_SCALER_PATH", "machine_learning/models/scaler.joblib")
    ML_METRICS_PATH = BASE_DIR / os.getenv("ML_METRICS_PATH", "machine_learning/models/metrics.json")
    
    # Notification settings
    SMTP_ENABLED = os.getenv("SMTP_ENABLED", "false").lower() == "true"
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "alerts@smartfitness.local")
    
    TWILIO_ENABLED = os.getenv("TWILIO_ENABLED", "false").lower() == "true"
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Clinical & Threshold defaults
    HR_RESTING_LOW = int(os.getenv("HR_RESTING_LOW_THRESHOLD", 50))
    HR_RESTING_HIGH = int(os.getenv("HR_RESTING_HIGH_THRESHOLD", 100))
    HR_EXERCISE_MAX = int(os.getenv("HR_EXERCISE_MAX_THRESHOLD", 185))
    SLEEP_MIN_HOURS = float(os.getenv("SLEEP_MIN_HOURS", 6.0))
    INACTIVITY_MAX_MINUTES = int(os.getenv("INACTIVITY_MAX_MINUTES", 120))
