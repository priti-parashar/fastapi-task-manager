from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import json

from database import engine, SessionLocal
from models import Base, User, Task
from auth import hash_password, verify_password, create_access_token, get_current_user
from redis_client import redis_client

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, this is my API"}


@app.post("/register")
def register(username: str, password: str):
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
        hashed_password = hash_password(password)
        new_user = User(username=username, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User registered successfully"}
    finally:
        db.close()


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        token = create_access_token(data={"sub": user.username})
        return {"access_token": token, "token_type": "bearer"}
    finally:
        db.close()


@app.post("/tasks")
def create_task(
    title: str,
    description: str = None,
    current_user: dict = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_user["sub"]).first()
        new_task = Task(title=title, description=description, owner_id=user.id)
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        # invalidate cache since the task list has changed
        redis_client.delete(f"tasks:{current_user['sub']}")

        return new_task
    finally:
        db.close()


@app.get("/tasks")
def get_tasks(current_user: dict = Depends(get_current_user)):
    cache_key = f"tasks:{current_user['sub']}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_user["sub"]).first()
        tasks = db.query(Task).filter(Task.owner_id == user.id).all()

        tasks_data = [
            {"id": t.id, "title": t.title, "description": t.description}
            for t in tasks
        ]
        redis_client.setex(cache_key, 30, json.dumps(tasks_data))
        return tasks_data
    finally:
        db.close()


@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    title: str,
    description: str = None,
    current_user: dict = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_user["sub"]).first()
        task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        task.title = title
        task.description = description
        db.commit()
        db.refresh(task)

        redis_client.delete(f"tasks:{current_user['sub']}")

        return task
    finally:
        db.close()


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user: dict = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_user["sub"]).first()
        task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        db.delete(task)
        db.commit()

        redis_client.delete(f"tasks:{current_user['sub']}")

        return {"message": "Task deleted successfully"}
    finally:
        db.close()