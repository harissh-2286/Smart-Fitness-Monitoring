import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from machine_learning.preprocessing import generate_synthetic_biometric_dataset, DataPreprocessor, FEATURE_COLUMNS, TARGET_COLUMN
from machine_learning.activity_model import ActivityClassifier
from machine_learning.anomaly_model import AnomalyDetector

def run_training_pipeline():
    print("==================================================================")
    print("SMART FITNESS MONITORING - MACHINE LEARNING PIPELINE TRAINING")
    print("==================================================================")
    
    data_dir = PROJECT_ROOT / "machine_learning" / "dataset"
    models_dir = PROJECT_ROOT / "machine_learning" / "models"
    data_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    dataset_path = data_dir / "fitness_activity_dataset.csv"
    print(f"[1/5] Generating physiologically consistent biometric dataset...")
    df = generate_synthetic_biometric_dataset(num_samples=3000, random_state=42)
    df.to_csv(dataset_path, index=False)
    print(f"      Saved dataset to: {dataset_path} ({len(df)} samples)")
    print("      Class Distribution:\n", df[TARGET_COLUMN].value_counts().to_string())

    print(f"\n[2/5] Data Preprocessing & Missing Value Imputation...")
    preprocessor = DataPreprocessor()
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    X_train = preprocessor.fit_transform(X_train_raw)
    X_test = preprocessor.transform(X_test_raw)

    scaler_path = models_dir / "scaler.joblib"
    preprocessor.save(scaler_path)
    print(f"      Saved preprocessor scaler to: {scaler_path}")

    print(f"\n[3/5] Training Random Forest Activity Classifier...")
    activity_clf = ActivityClassifier(n_estimators=120, max_depth=12, random_state=42)
    activity_clf.fit(X_train, y_train)

    y_pred = activity_clf.predict(X_test)
    classes = list(np.unique(y_test))

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, average="weighted"))
    rec = float(recall_score(y_test, y_pred, average="weighted"))
    f1 = float(f1_score(y_test, y_pred, average="weighted"))
    cm = confusion_matrix(y_test, y_pred, labels=classes).tolist()
    clf_report = classification_report(y_test, y_pred, output_dict=True)

    print(f"      Activity Classifier Evaluation:")
    print(f"      Accuracy  : {acc * 100:.2f}%")
    print(f"      Precision : {prec * 100:.2f}%")
    print(f"      Recall    : {rec * 100:.2f}%")
    print(f"      F1-Score  : {f1 * 100:.2f}%")
    print(f"      Confusion Matrix:\n      {cm}")

    activity_model_path = models_dir / "activity_classifier.joblib"
    activity_clf.save(activity_model_path)
    print(f"      Saved Activity Classifier to: {activity_model_path}")

    print(f"\n[4/5] Training Isolation Forest Anomaly Detector...")
    # Train anomaly detector on normal resting & steady activity baseline
    anomaly_detector = AnomalyDetector(contamination=0.04, n_estimators=120, random_state=42)
    anomaly_detector.fit(X_train)

    anomaly_model_path = models_dir / "anomaly_detector.joblib"
    anomaly_detector.save(anomaly_model_path)
    print(f"      Saved Anomaly Detector to: {anomaly_model_path}")

    # Test an anomaly example: Heart rate 175 bpm while step_cadence is 0 (Resting tachycardia anomaly)
    test_anomaly_raw = pd.DataFrame([{
        "heart_rate": 178,
        "step_cadence": 0,
        "accel_magnitude": 9.8,
        "speed_kmh": 0.0
    }])
    test_anomaly_scaled = preprocessor.transform(test_anomaly_raw)
    anomaly_eval = anomaly_detector.score_single(test_anomaly_scaled)
    print(f"      Anomaly Test Case (HR=178, Cadence=0): is_anomaly={anomaly_eval['is_anomaly']}, risk={anomaly_eval['risk_indicator']}")

    print(f"\n[5/5] Compiling and Persisting Model Evaluation Metrics...")
    metrics_data = {
        "model_name": "Smart Fitness Multi-Task ML Engine",
        "activity_classifier": {
            "algorithm": "Random Forest",
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "classes": classes,
            "confusion_matrix": cm,
            "classification_report": clf_report
        },
        "anomaly_detector": {
            "algorithm": "Isolation Forest",
            "contamination": 0.04,
            "features_evaluated": FEATURE_COLUMNS,
            "sample_anomaly_test": anomaly_eval
        },
        "features": FEATURE_COLUMNS,
        "clinical_disclaimer": "These machine learning models provide experimental fitness and wellness classification for educational capstone demonstration. They are not intended for clinical diagnostic use."
    }

    metrics_path = models_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
    print(f"      Saved Metrics JSON to: {metrics_path}")

    print("\n==================================================================")
    print("SUCCESS: Machine learning training and serialization complete!")
    print("==================================================================")

if __name__ == "__main__":
    run_training_pipeline()
