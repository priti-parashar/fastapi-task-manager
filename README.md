# FastAPI Task Manager

A REST API for managing user-specific tasks, built with FastAPI, PostgreSQL, SQLAlchemy, Redis and JWT authentication.

## Features

- User registration and login
- Password hashing with bcrypt
- JWT authentication
- Protected task endpoints
- User-specific task ownership
- Create, read, update and delete tasks
- PostgreSQL persistence with SQLAlchemy
- Redis caching with cache invalidation
- Pydantic request and response validation
- Automated testing with pytest
- GitHub Actions CI
- Docker support

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Redis
- Pydantic
- JWT
- pytest
- Docker
- GitHub Actions

## Setup

Clone the repository:

```bash
git clone https://github.com/priti-parashar/fastapi-task-manager.git
cd fastapi-task-manager
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file based on `.env.example`.

Required environment variables:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/taskmanager
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
```

Run the application:

```bash
uvicorn main:app --reload
```

Open the API documentation:

`http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Register a user |
| POST | `/login` | Login and receive a JWT |
| GET | `/tasks` | Get the current user's tasks |
| POST | `/tasks` | Create a task |
| PUT | `/tasks/{task_id}` | Update a task |
| DELETE | `/tasks/{task_id}` | Delete a task |

Task endpoints require a valid bearer token.

## Running Tests

```bash
pytest
```

## CI

GitHub Actions automatically runs linting, tests and a Docker build on pushes to `main` and on pull requests.

## Security

Passwords are hashed before storage. Protected endpoints require JWT authentication, and users can only modify their own tasks. Secrets and database credentials are supplied through environment variables and are not committed to the repository.



