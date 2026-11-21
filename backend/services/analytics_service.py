import os
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from backend.config import Config
from firebase.database_service import get_db_service
from machine_learning.preprocessing import DataPreprocessor, FEATURE_COLUMNS
from machine_learning.activity_model import ActivityClassifier
from machine_learning.anomaly_model import AnomalyDetector

logger = logging.getLogger("SmartFitness.AnalyticsService")

class AnalyticsService:
    def __init__(self):
        self.db = get_db_service()
        self.preprocessor = None
        self.activity_classifier = None
        self.anomaly_detector = None
        self.metrics_info = {}
        self._load_ml_components()

    def _load_ml_components(self):
        try:
            if os.path.exists(Config.ML_SCALER_PATH):
                self.preprocessor = DataPreprocessor.load(Config.ML_SCALER_PATH)
            if os.path.exists(Config.ML_ACTIVITY_MODEL_PATH):
                self.activity_classifier = ActivityClassifier.load(Config.ML_ACTIVITY_MODEL_PATH)
            if os.path.exists(Config.ML_ANOMALY_MODEL_PATH):
                self.anomaly_detector = AnomalyDetector.load(Config.ML_ANOMALY_MODEL_PATH)
            if os.path.exists(Config.ML_METRICS_PATH):
                with open(Config.ML_METRICS_PATH, "r", encoding="utf-8") as f:
                    self.metrics_info = json.load(f)
            logger.info("Machine learning models and preprocessor successfully loaded into AnalyticsService.")
        except Exception as e:
            logger.error(f"Failed to load ML models: {e}")

    def calculate_bmi(self, weight_kg, height_cm):
        """
        BMI = Weight (kg) / (Height (m))^2
        Returns BMI score, category, and disclaimer.
        """
        if not weight_kg or not height_cm or height_cm <= 0:
            return None

        height_m = height_cm / 100.0
        bmi_val = round(weight_kg / (height_m ** 2), 1)

        if bmi_val < 18.5:
            category = "Underweight"
            color = "#3b82f6"
        elif bmi_val < 25.0:
            category = "Normal weight"
            color = "#10b981"
        elif bmi_val < 30.0:
            category = "Overweight"
            color = "#f59e0b"
        else:
            category = "Obesity range"
            color = "#ef4444"

        return {
            "bmi": bmi_val,
            "category": category,
            "color": color,
            "disclaimer": "BMI is a general screening indicator for health and wellness, not a clinical medical diagnosis."
        }

    def predict_activity_and_anomaly(self, heart_rate, step_cadence=0, accel_magnitude=9.8, speed_kmh=0.0):
        """
        Uses trained Random Forest and Isolation Forest models.
        """
        if not self.preprocessor or not self.activity_classifier or not self.anomaly_detector:
            return {
                "activity": "Resting" if heart_rate < 85 else ("Walking" if heart_rate < 130 else "Running"),
                "confidence": 0.85,
                "is_anomaly": False,
                "risk_indicator": "Normal",
                "mode": "Heuristic fallback (ML models unmounted)"
            }

        input_df = pd.DataFrame([{
            "heart_rate": float(heart_rate),
            "step_cadence": float(step_cadence),
            "accel_magnitude": float(accel_magnitude),
            "speed_kmh": float(speed_kmh)
        }])

        scaled_features = self.preprocessor.transform(input_df)
        act_res = self.activity_classifier.predict_single(scaled_features)
        anom_res = self.anomaly_detector.score_single(scaled_features)

        return {
            "activity": act_res["activity"],
            "confidence": act_res["confidence"],
            "probabilities": act_res["probabilities"],
            "is_anomaly": anom_res["is_anomaly"],
            "anomaly_score": anom_res["anomaly_score"],
            "risk_indicator": anom_res["risk_indicator"],
            "features_used": {
                "heart_rate": heart_rate,
                "step_cadence": step_cadence,
                "accel_magnitude": accel_magnitude,
                "speed_kmh": speed_kmh
            }
        }

    def compute_user_analytics(self, user_id):
        user = self.db.get_user_by_id(user_id) or {}
        weight_kg = user.get("weight", 70.0)
        height_cm = user.get("height", 175.0)
        bmi_data = self.calculate_bmi(weight_kg, height_cm)

        records = self.db.get_health_records(user_id, limit=60)
        total_steps = sum(r.get("steps", 0) for r in records if r.get("steps"))
        step_goal = user.get("step_goal", 10000)

        # Activity score (0 to 100)
        # Weighted by step progress, resting heart rate health, and sleep
        step_score = min(50.0, (total_steps / max(1, step_goal * 7)) * 50.0)
        
        # Heart rate consistency score (up to 30 pts)
        hr_values = [r.get("heart_rate") for r in records if r.get("heart_rate")]
        avg_hr = sum(hr_values) / len(hr_values) if hr_values else 72
        hr_score = 30.0 if (60 <= avg_hr <= 80) else (20.0 if (50 <= avg_hr <= 95) else 10.0)

        # Sleep score (up to 20 pts)
        sleep_recs = [r.get("sleep_hours") for r in records if r.get("sleep_hours") is not None]
        avg_sleep = sum(sleep_recs) / len(sleep_recs) if sleep_recs else 7.2
        sleep_score = 20.0 if (7.0 <= avg_sleep <= 9.0) else (14.0 if (6.0 <= avg_sleep <= 10.0) else 8.0)

        activity_score = int(min(100, step_score + hr_score + sleep_score))

        latest_rec = records[0] if records else {"heart_rate": 72, "steps": 0}
        ml_prediction = self.predict_activity_and_anomaly(
            heart_rate=latest_rec.get("heart_rate", 72),
            step_cadence=min(180, int(latest_rec.get("steps", 0) / 60)) if latest_rec.get("steps") else 0
        )

        analytics_entry = {
            "user_id": user_id,
            "BMI": bmi_data["bmi"] if bmi_data else 22.5,
            "bmi_category": bmi_data["category"] if bmi_data else "Normal weight",
            "activity_score": activity_score,
            "risk_indicator": ml_prediction["risk_indicator"],
            "prediction": ml_prediction["activity"],
            "avg_heart_rate": round(avg_hr, 1),
            "avg_sleep_hours": round(avg_sleep, 1),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        self.db.save_analytics(analytics_entry)
        
        return {
            "bmi": bmi_data,
            "activity_score": activity_score,
            "latest_prediction": ml_prediction,
            "ml_metrics": self.metrics_info,
            "averages": {
                "heart_rate": round(avg_hr, 1),
                "sleep_hours": round(avg_sleep, 1),
                "total_steps": total_steps
            }
        }


_analytics_service = None

def get_analytics_service():
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service
