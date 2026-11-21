import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

class ActivityClassifier:
    """
    Random Forest Activity Classifier for Human Physical State
    Recognizes: Walking, Running, Resting.
    """
    def __init__(self, n_estimators=100, max_depth=12, random_state=42):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            class_weight='balanced'
        )
        self.classes_ = None

    def fit(self, X, y):
        self.model.fit(X, y)
        self.classes_ = list(self.model.classes_)
        return self

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)

    def predict_single(self, feature_vector):
        """
        Takes a 1D or 2D array and returns class prediction + confidence breakdown.
        """
        arr = np.array(feature_vector).reshape(1, -1)
        pred = self.model.predict(arr)[0]
        probs = self.model.predict_proba(arr)[0]
        confidence_dict = {cls: round(float(prob), 4) for cls, prob in zip(self.model.classes_, probs)}
        return {
            "activity": pred,
            "confidence": round(float(np.max(probs)), 4),
            "probabilities": confidence_dict
        }

    def save(self, file_path):
        joblib.dump(self.model, file_path)

    @classmethod
    def load(cls, file_path):
        instance = cls()
        instance.model = joblib.load(file_path)
        instance.classes_ = list(instance.model.classes_)
        return instance
