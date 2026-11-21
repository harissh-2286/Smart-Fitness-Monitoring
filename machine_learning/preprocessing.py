import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from pathlib import Path

FEATURE_COLUMNS = ["heart_rate", "step_cadence", "accel_magnitude", "speed_kmh"]
TARGET_COLUMN = "activity_type"

def generate_synthetic_biometric_dataset(num_samples=2500, random_state=42):
    """
    Generates a physiologically sound dataset representing human biometric readings
    across resting, walking, and running states, with realistic sensor noise and edge cases.
    """
    np.random.seed(random_state)
    
    samples_per_class = num_samples // 3
    
    # 1. Resting: HR 55-80 bpm, 0 cadence, ~9.8 m/s² gravity vector, 0 km/h speed
    resting_hr = np.random.normal(loc=68, scale=6, size=samples_per_class)
    resting_cadence = np.maximum(0, np.random.normal(loc=0.5, scale=1.5, size=samples_per_class))
    resting_accel = np.random.normal(loc=9.81, scale=0.35, size=samples_per_class)
    resting_speed = np.maximum(0, np.random.normal(loc=0.1, scale=0.15, size=samples_per_class))
    resting_labels = ["Resting"] * samples_per_class
    
    # 2. Walking: HR 90-125 bpm, 75-115 steps/min, 11-15 m/s² accel, 3.5-5.8 km/h speed
    walking_hr = np.random.normal(loc=105, scale=10, size=samples_per_class)
    walking_cadence = np.random.normal(loc=95, scale=12, size=samples_per_class)
    walking_accel = np.random.normal(loc=12.5, scale=1.2, size=samples_per_class)
    walking_speed = np.random.normal(loc=4.5, scale=0.8, size=samples_per_class)
    walking_labels = ["Walking"] * samples_per_class
    
    # 3. Running: HR 135-178 bpm, 145-185 steps/min, 17-25 m/s² accel, 8.0-14.5 km/h speed
    running_hr = np.random.normal(loc=156, scale=12, size=samples_per_class)
    running_cadence = np.random.normal(loc=162, scale=14, size=samples_per_class)
    running_accel = np.random.normal(loc=19.8, scale=2.5, size=samples_per_class)
    running_speed = np.random.normal(loc=10.5, scale=1.8, size=samples_per_class)
    running_labels = ["Running"] * samples_per_class
    
    df = pd.DataFrame({
        "heart_rate": np.concatenate([resting_hr, walking_hr, running_hr]),
        "step_cadence": np.concatenate([resting_cadence, walking_cadence, running_cadence]),
        "accel_magnitude": np.concatenate([resting_accel, walking_accel, running_accel]),
        "speed_kmh": np.concatenate([resting_speed, walking_speed, running_speed]),
        "activity_type": np.concatenate([resting_labels, walking_labels, running_labels])
    })
    
    # Introduce small realistic missingness (1.5%) to test imputation pipeline
    mask_missing = np.random.rand(len(df)) < 0.015
    df.loc[mask_missing, "speed_kmh"] = np.nan
    
    mask_missing_hr = np.random.rand(len(df)) < 0.01
    df.loc[mask_missing_hr, "heart_rate"] = np.nan
    
    # Shuffle dataset
    df = df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    return df


class DataPreprocessor:
    """
    Handles missing values, outlier bounding, scaling, and feature transformation.
    """
    def __init__(self):
        self.scaler = StandardScaler()
        self.impute_values = {}
        self.is_fitted = False

    def fit_transform(self, X):
        X_df = pd.DataFrame(X, columns=FEATURE_COLUMNS).copy()
        for col in FEATURE_COLUMNS:
            median_val = X_df[col].median()
            self.impute_values[col] = median_val
            X_df[col] = X_df[col].fillna(median_val)
        
        scaled_features = self.scaler.fit_transform(X_df)
        self.is_fitted = True
        return scaled_features

    def transform(self, X):
        X_df = pd.DataFrame(X, columns=FEATURE_COLUMNS).copy()
        for col in FEATURE_COLUMNS:
            val = self.impute_values.get(col, 0.0)
            X_df[col] = X_df[col].fillna(val)
        return self.scaler.transform(X_df)

    def save(self, file_path):
        payload = {
            "scaler": self.scaler,
            "impute_values": self.impute_values,
            "feature_columns": FEATURE_COLUMNS
        }
        joblib.dump(payload, file_path)

    @classmethod
    def load(cls, file_path):
        payload = joblib.load(file_path)
        instance = cls()
        instance.scaler = payload["scaler"]
        instance.impute_values = payload["impute_values"]
        instance.is_fitted = True
        return instance
