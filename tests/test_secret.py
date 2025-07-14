import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db
from app.main import app


# --- Create in-memory SQLite DB for test isolation ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

# --- Override DB dependency ---
def override_get_db():
    print("Overriden")
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Setup ---
Base.metadata.create_all(bind=engine)
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_create_secret_basic():
    response = client.post("/secret", json={"secret": "my-test-secret"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data

# def test_create_secret_with_password_and_expiry():
#     response = client.post("/secret", json={
#         "secret": "secure",
#         "password": "hunter2",
#         "expire_after_minutes": 1
#     })
#     assert response.status_code == 200
#     assert "id" in response.json()

def test_read_secret_once_only():
    # First, create a secret
    res = client.post("/secret", json={"secret": "read-once"})
    secret_id = res.json()["id"]

    # Read once – should succeed
    read_res = client.get(f"/secret/{secret_id}")
    assert read_res.status_code == 200
    assert read_res.json()["secret"] == "read-once"

    # Read again – should 404 or 410
    second_read = client.get(f"/secret/{secret_id}")
    assert second_read.status_code in [404, 410]

def test_expired_secret_returns_410():
    # Create a secret that expired 0 minutes ago
    res = client.post("/secret", json={"secret": "expired", "expire_after_minutes": 0})
    secret_id = res.json()["id"]

    expired_res = client.get(f"/secret/{secret_id}")
    assert expired_res.status_code == 410

def test_secret_not_found():
    res = client.get("/secret/fake-uuid")
    assert res.status_code == 404

def test_wrong_uuid_format():
    res = client.get("/secret/invalid_uuid")
    assert res.status_code == 422  # Unprocessable Entity

def test_incorrect_password():
    res = client.post("/secret", json={"secret": "top", "password": "1234"})
    secret_id = res.json()["id"]

    # Read with wrong password
    res = client.get(f"/secret/{secret_id}?password=wrong")
    assert res.status_code == 401

