# FastAPI Task Manager

A RESTful task management API built with FastAPI, featuring JWT authentication, PostgreSQL, and Redis caching.

## Features
- User registration & login with JWT authentication
- Create, read, update, delete tasks (CRUD)
- Task ownership — users only see their own tasks
- PostgreSQL database (via SQLAlchemy)
- Redis caching for faster task retrieval

## Tech Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL (Neon)
- **Cache:** Redis (Upstash)
- **Auth:** JWT (JSON Web Tokens)

## Setup

1. Clone the repo

2. Create a virtual environment and install dependencies

3. Create a `.env` file with:

4. Run the server

5. Visit `http://127.0.0.1:8000/docs` for the interactive API docs

## API Endpoints
- `POST /register` — create a new user
- `POST /login` — get JWT access token
- `GET /tasks` — get logged-in user's tasks
- `POST /tasks` — create a task
- `PUT /tasks/{id}` — update a task
- `DELETE /tasks/{id}` — delete a task



