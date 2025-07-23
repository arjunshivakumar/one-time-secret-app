import pytest
import os 
os.environ["TESTING"] = "1"            
import re
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db
from app.main import create_app


# --- Create in-memory SQLite DB for test isolation ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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
app = create_app()
Base.metadata.create_all(bind=engine)
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_create_secret_basic():
    response = client.post("/secret", json={
        "secret": "my-test-secret",
        "expire_after_minutes": 10
    })
    assert response.status_code == 200
    data = response.json()

    assert "url" in data

    # Optional: Extract UUID from the URL
    match = re.search(r'/secret/([a-f0-9-]+)$', data["url"])
    assert match is not None
    secret_id = match.group(1)
    assert len(secret_id) > 0

# def test_create_secret_with_password_and_expiry():
#     response = client.post("/secret", json={
#         "secret": "secure",
#         "password": "hunter2",
#         "expire_after_minutes": 1
#     })
#     assert response.status_code == 200
#     assert "id" in response.json()

def test_read_secret_once_only():
    # Create a secret
    res = client.post("/secret", json={
        "secret": "my-test-secret",
        "expire_after_minutes": 10
    })
    secret_id = res.json()["url"].split("/")[-1]
    print(secret_id)
    # Read once – should succeed
    read_res = client.get(f"/secret/{secret_id}")
    print(read_res.json())
    assert read_res.status_code == 200
    assert read_res.json()["secret"] == "my-test-secret"

    # Read again – should fail
    read_res_again = client.get(f"/secret/{secret_id}")
    assert read_res_again.status_code in [404, 410]

def test_expired_secret_returns_410():
    # Create a secret that expired 0 minutes ago
    res = client.post("/secret", json={"secret": "expired", "expire_after_minutes": 0})
    secret_id = res.json()["url"].split("/")[-1]   

    expired_res = client.get(f"/secret/{secret_id}")
    assert expired_res.status_code == 410

def test_secret_not_found():
    res = client.get("/secret/fake-uuid")
    assert res.status_code == 404

# def test_incorrect_password():
#     res = client.post("/secret", json={"secret": "top", "password": "1234"})
#     secret_id = res.json()["id"]

#     # Read with wrong password
#     res = client.get(f"/secret/{secret_id}?password=wrong")
#     assert res.status_code == 401

