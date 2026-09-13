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

def _get_auth_headers():
    """Helper: register a user, log in, and return auth headers for requests."""
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "testpass123"

    client.post("/register", params={"username": username, "password": password})
    login_response = client.post(
        "/login",
        data={"username": username, "password": password}
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_and_get_task():
    headers = _get_auth_headers()

    # Create a task
    response = client.post(
        "/tasks",
        params={"title": "Buy groceries", "description": "Milk, eggs, bread"},
        headers=headers
    )
    assert response.status_code == 200
    created_task = response.json()
    assert created_task["title"] == "Buy groceries"
    assert "id" in created_task

    # Fetch tasks and confirm the new one is there
    response = client.get("/tasks", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert any(t["title"] == "Buy groceries" for t in tasks)


def test_update_task():
    headers = _get_auth_headers()

    create_response = client.post(
        "/tasks",
        params={"title": "Old title", "description": "Old desc"},
        headers=headers
    )
    task_id = create_response.json()["id"]

    update_response = client.put(
        f"/tasks/{task_id}",
        params={"title": "New title", "description": "New desc"},
        headers=headers
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "New title"


def test_delete_task():
    headers = _get_auth_headers()

    create_response = client.post(
        "/tasks",
        params={"title": "Temporary task", "description": None},
        headers=headers
    )
    task_id = create_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Task deleted successfully"}


def test_cannot_access_tasks_without_auth():
    response = client.get("/tasks")
    assert response.status_code == 401    