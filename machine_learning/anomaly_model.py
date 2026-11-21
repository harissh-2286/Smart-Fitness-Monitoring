import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

class AnomalyDetector:
    """
    Isolation Forest Health Anomaly Detector.
    Identifies physiological irregularities such as resting tachycardia,
    sudden bradycardia, or irregular activity-heart rate mismatch.
    """
    def __init__(self, contamination=0.04, n_estimators=100, random_state=42):
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_state,
            bootstrap=False
        )

    def fit(self, X):
        self.model.fit(X)
        return self

    def predict(self, X):
        """
        Returns 1 for normal, -1 for anomaly.
        """
        return self.model.predict(X)

    def decision_function(self, X):
        return self.model.decision_function(X)

    def score_single(self, feature_vector):
        """
        Evaluates a single reading.
        Returns:
            is_anomaly: bool
            anomaly_score: float (-1.0 to 1.0, lower means more abnormal)
            risk_indicator: 'Normal', 'Low Risk', 'Moderate Risk', 'High Risk'
            reasoning: explanation of anomaly
        """
        arr = np.array(feature_vector).reshape(1, -1)
        pred = self.model.predict(arr)[0]
        score = float(self.model.decision_function(arr)[0])
        
        # Risk assessment based on score
        # decision_function: < 0 is anomaly in scikit-learn
        is_anomaly = bool(pred == -1)
        
        if score > 0.12:
            risk = "Normal"
        elif score >= 0.0:
            risk = "Low Risk"
        elif score >= -0.08:
            risk = "Moderate Risk"
        else:
            risk = "High Risk"

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(score, 4),
            "risk_indicator": risk
        }

    def save(self, file_path):
        joblib.dump(self.model, file_path)

    @classmethod
    def load(cls, file_path):
        instance = cls()
        instance.model = joblib.load(file_path)
        return instance
