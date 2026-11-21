import pytest
from backend.app import create_app

@pytest.fixture
def auth_client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Log in as demo user
        login_res = client.post("/api/login", json={
            "email": "demo@smartfitness.local",
            "password": "Demo@123456"
        })
        token = login_res.get_json()["token"]
        client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        yield client

def test_record_health_data(auth_client):
    payload = {
        "heart_rate": 84,
        "steps": 1250,
        "activity_type": "Walking",
        "data_source": "sensor"
    }
    res = auth_client.post("/api/health-data", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["record"]["heart_rate"] == 84
    assert data["record"]["steps"] == 1250
    assert data["record"]["distance"] > 0 # verified automatic distance derivation
    assert data["record"]["calories"] > 0 # verified automatic calories derivation

def test_get_health_data_history(auth_client):
    res = auth_client.get("/api/health-data?limit=10")
    assert res.status_code == 200
    data = res.get_json()
    assert "records" in data
    assert isinstance(data["records"], list)

def test_get_dashboard_summary(auth_client):
    res = auth_client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.get_json()
    assert "summary" in data
    assert "steps" in data["summary"]
    assert "heart_rate" in data["summary"]
    assert "move_chart" in data
    assert "hr_zones" in data
    assert "daily_goals_streak" in data
