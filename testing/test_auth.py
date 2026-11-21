import pytest
from backend.app import create_app
from firebase.database_service import get_db_service

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_user_registration(client):
    unique_email = f"test_{int(__import__('time').time())}@example.com"
    payload = {
        "name": "Jane Doe",
        "email": unique_email,
        "password": "Password123!",
        "age": 28,
        "height": 168.0,
        "weight": 62.0,
        "gender": "female"
    }
    response = client.post("/api/register", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "token" in data
    assert data["user"]["email"] == unique_email

def test_duplicate_registration_fails(client):
    payload = {
        "name": "Alex Duplicate",
        "email": "demo@smartfitness.local", # already exists
        "password": "Password123!",
        "age": 25,
        "height": 170.0,
        "weight": 65.0
    }
    response = client.post("/api/register", json=payload)
    assert response.status_code == 409

def test_user_login_success(client):
    response = client.post("/api/login", json={
        "email": "demo@smartfitness.local",
        "password": "Demo@123456"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "token" in data
    assert data["user"]["email"] == "demo@smartfitness.local"

def test_user_login_invalid_password(client):
    response = client.post("/api/login", json={
        "email": "demo@smartfitness.local",
        "password": "WrongPassword999"
    })
    assert response.status_code == 401

def test_unauthorized_access_prevented(client):
    # Attempting to access protected profile API without token
    response = client.get("/api/profile")
    assert response.status_code == 401

def test_forgot_and_reset_password(client):
    # Forgot password request
    forgot_res = client.post("/api/forgot-password", json={
        "email": "demo@smartfitness.local"
    })
    assert forgot_res.status_code == 200

    # Reset password
    reset_res = client.post("/api/reset-password", json={
        "email": "demo@smartfitness.local",
        "new_password": "NewSecretPass@123"
    })
    assert reset_res.status_code == 200

    # Verify login with new password
    login_new = client.post("/api/login", json={
        "email": "demo@smartfitness.local",
        "password": "NewSecretPass@123"
    })
    assert login_new.status_code == 200

    # Revert back to default demo password for consistency
    client.post("/api/reset-password", json={
        "email": "demo@smartfitness.local",
        "new_password": "Demo@123456"
    })
