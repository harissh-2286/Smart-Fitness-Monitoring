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

def test_trigger_and_query_alert(auth_client):
    payload = {
        "alert_type": "TACHYCARDIA_SPIKE",
        "message": "Heart rate reached 175 BPM unexpectedly.",
        "severity": "high",
        "is_test": True
    }
    res = auth_client.post("/api/alerts", json=payload)
    assert res.status_code in [200, 201]

    # Query alerts
    alerts_res = auth_client.get("/api/alerts")
    assert alerts_res.status_code == 200
    data = alerts_res.get_json()
    assert "alerts" in data
    assert len(data["alerts"]) > 0

def test_emergency_contact_crud(auth_client):
    # 1. Add contact
    contact_data = {
        "name": "Officer Marcus Vance",
        "relationship": "Guardian",
        "phone": "+1 (555) 789-0123",
        "email": "officer.vance@emergency.local",
        "is_primary": False
    }
    add_res = auth_client.post("/api/emergency-contacts", json=contact_data)
    assert add_res.status_code == 201
    contact = add_res.get_json()
    contact_id = contact["contact_id"]

    # 2. Get contacts
    get_res = auth_client.get("/api/emergency-contacts")
    assert get_res.status_code == 200
    contacts = get_res.get_json()["contacts"]
    assert any(c["contact_id"] == contact_id for c in contacts)

    # 3. Test emergency notification simulation
    test_dispatch_res = auth_client.post("/api/emergency-contacts/test")
    assert test_dispatch_res.status_code == 200

    # 4. Delete contact
    del_res = auth_client.delete(f"/api/emergency-contacts/{contact_id}")
    assert del_res.status_code == 200
