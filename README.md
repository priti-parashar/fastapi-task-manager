# FastAPI Task Manager

[![CI](https://github.com/priti-parashar/fastapi-task-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/priti-parashar/fastapi-task-manager/actions/workflows/ci.yml)

A RESTful task management API built with FastAPI, featuring JWT authentication, PostgreSQL, and Redis caching.

## Features
- User registration & login with JWT authentication
- Create, read, update, delete tasks (CRUD)
- Task ownership — users only see their own tasks
- PostgreSQL database (via SQLAlchemy)
- Redis caching for faster task retrieval, with automatic cache invalidation on writes
- Automated test suite (pytest) covering auth flow and all task endpoints
- CI pipeline (GitHub Actions) running tests against real PostgreSQL and Redis services on every push

## Tech Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL (Neon)
- **Cache:** Redis (Upstash)
- **Auth:** JWT (JSON Web Tokens)
- **Testing:** pytest
- **CI/CD:** GitHub Actions

## Setup

1. Clone the repo
   ```
   git clone https://github.com/priti-parashar/fastapi-task-manager.git
   cd fastapi-task-manager
   ```

2. Create a virtual environment and install dependencies
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   REDIS_URL=redis://localhost:6379/0
   ```

4. Run the server
   ```
   uvicorn main:app --reload
   ```

5. Visit `http://127.0.0.1:8000/docs` for the interactive API docs

## Running Tests

```
pytest
```

Tests run automatically on every push via GitHub Actions, using live PostgreSQL and Redis service containers.

## API Endpoints
- `POST /register` — create a new user
- `POST /login` — get JWT access token
- `GET /tasks` — get logged-in user's tasks
- `POST /tasks` — create a task
- `PUT /tasks/{id}` — update a task
- `DELETE /tasks/{id}` — delete a task



