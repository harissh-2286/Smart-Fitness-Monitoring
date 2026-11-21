import pytest
from backend.app import create_app

@pytest.fixture
def auth_client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        login_res = client.post("/api/login", json={
            "email": "demo@smartfitness.local",
            "password": "Demo@123456"
        })
        token = login_res.get_json()["token"]
        client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        yield client

def test_bmi_and_activity_analytics(auth_client):
    res = auth_client.get("/api/analytics")
    assert res.status_code == 200
    data = res.get_json()
    assert "bmi" in data
    assert "activity_score" in data
    assert 0 <= data["activity_score"] <= 100
    assert "disclaimer" in data["bmi"]

def test_ml_activity_classification_resting(auth_client):
    payload = {
        "heart_rate": 65,
        "step_cadence": 0,
        "accel_magnitude": 9.81,
        "speed_kmh": 0.0
    }
    res = auth_client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["prediction"]["activity"] == "Resting"
    assert data["prediction"]["confidence"] > 0.8

def test_ml_activity_classification_running(auth_client):
    payload = {
        "heart_rate": 160,
        "step_cadence": 165,
        "accel_magnitude": 20.0,
        "speed_kmh": 11.0
    }
    res = auth_client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["prediction"]["activity"] == "Running"

def test_ml_anomaly_detection_spiking(auth_client):
    # Severe resting tachycardia spike (HR=180 while cadence is 0)
    payload = {
        "heart_rate": 182,
        "step_cadence": 0,
        "accel_magnitude": 9.8,
        "speed_kmh": 0.0
    }
    res = auth_client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["prediction"]["is_anomaly"] is True
    assert data["prediction"]["risk_indicator"] in ["Moderate Risk", "High Risk"]
