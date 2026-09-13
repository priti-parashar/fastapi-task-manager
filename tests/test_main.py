from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, this is my API"}

def test_register_and_login():
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "testpass123"

    # Register a new user
    response = client.post(
        "/register",
        params={"username": username, "password": password}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}

    # Log in with the same credentials
    response = client.post(
        "/login",
        data={"username": username, "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"