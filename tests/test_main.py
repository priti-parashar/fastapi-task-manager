import uuid

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def unique_username():
    return f"testuser_{uuid.uuid4().hex[:8]}"


def register_user(username: str, password: str):
    return client.post(
        "/register",
        json={
            "username": username,
            "password": password,
        },
    )


def login_user(username: str, password: str):
    return client.post(
        "/login",
        data={
            "username": username,
            "password": password,
        },
    )


def get_auth_headers():
    username = unique_username()
    password = "testpass123"

    register_response = register_user(
        username,
        password,
    )

    assert register_response.status_code == 201

    login_response = login_user(
        username,
        password,
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_read_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Hello, this is my API"
    }


def test_register_and_login():
    username = unique_username()
    password = "testpass123"

    response = register_user(
        username,
        password,
    )

    assert response.status_code == 201

    assert response.json() == {
        "message": "User registered successfully"
    }

    response = login_user(
        username,
        password,
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_duplicate_registration():
    username = unique_username()
    password = "testpass123"

    register_user(
        username,
        password,
    )

    response = register_user(
        username,
        password,
    )

    assert response.status_code == 409


def test_invalid_login():
    username = unique_username()
    password = "testpass123"

    register_user(
        username,
        password,
    )

    response = login_user(
        username,
        "wrongpassword",
    )

    assert response.status_code == 401


def test_create_and_get_task():
    headers = get_auth_headers()

    response = client.post(
        "/tasks",
        json={
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
        },
        headers=headers,
    )

    assert response.status_code == 201

    created_task = response.json()

    assert created_task["title"] == "Buy groceries"
    assert created_task["completed"] is False
    assert "id" in created_task

    response = client.get(
        "/tasks",
        headers=headers,
    )

    assert response.status_code == 200

    tasks = response.json()

    assert any(
        task["title"] == "Buy groceries"
        for task in tasks
    )


def test_update_task():
    headers = get_auth_headers()

    create_response = client.post(
        "/tasks",
        json={
            "title": "Old title",
            "description": "Old description",
        },
        headers=headers,
    )

    task_id = create_response.json()["id"]

    update_response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "New title",
            "completed": True,
        },
        headers=headers,
    )

    assert update_response.status_code == 200

    updated_task = update_response.json()

    assert updated_task["title"] == "New title"
    assert updated_task["completed"] is True


def test_delete_task():
    headers = get_auth_headers()

    create_response = client.post(
        "/tasks",
        json={
            "title": "Temporary task",
            "description": None,
        },
        headers=headers,
    )

    task_id = create_response.json()["id"]

    response = client.delete(
        f"/tasks/{task_id}",
        headers=headers,
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "Task deleted successfully"
    }


def test_cannot_access_tasks_without_auth():
    response = client.get("/tasks")

    assert response.status_code == 401


def test_task_not_found():
    headers = get_auth_headers()

    response = client.delete(
        "/tasks/999999999",
        headers=headers,
    )

    assert response.status_code == 404


def test_user_cannot_access_another_users_task():
    first_user_headers = get_auth_headers()
    second_user_headers = get_auth_headers()

    create_response = client.post(
        "/tasks",
        json={
            "title": "Private task",
            "description": "Only owner can access",
        },
        headers=first_user_headers,
    )

    task_id = create_response.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Hacked"},
        headers=second_user_headers,
    )

    assert response.status_code == 404
