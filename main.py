import json

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from database import Base, engine, get_db
from models import Task, User
from redis_client import (
    delete_cached_value,
    get_cached_value,
    set_cached_value,
)
from schemas import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    TokenResponse,
    UserCreate,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI Task Manager",
    description="Task management API with JWT authentication and Redis caching.",
    version="1.0.0",
)


@app.get("/")
def read_root():
    return {"message": "Hello, this is my API"}


@app.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.username == user_data.username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    new_user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )

    db.add(new_user)
    db.commit()

    return {"message": "User registered successfully"}


@app.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )

    if not user or not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        data={"sub": user.username}
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


def get_authenticated_user(
    current_user: dict,
    db: Session,
) -> User:
    user = (
        db.query(User)
        .filter(User.username == current_user["sub"])
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    return user


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = get_authenticated_user(
        current_user,
        db,
    )

    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        owner_id=user.id,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    delete_cached_value(
        f"tasks:{user.username}"
    )

    return new_task


@app.get(
    "/tasks",
    response_model=list[TaskResponse],
)
def get_tasks(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = get_authenticated_user(
        current_user,
        db,
    )

    cache_key = f"tasks:{user.username}"

    cached = get_cached_value(cache_key)

    if cached:
        return json.loads(cached)

    tasks = (
        db.query(Task)
        .filter(Task.owner_id == user.id)
        .all()
    )

    tasks_data = [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
        }
        for task in tasks
    ]

    set_cached_value(
        cache_key,
        json.dumps(tasks_data),
    )

    return tasks_data


@app.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = get_authenticated_user(
        current_user,
        db,
    )

    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.owner_id == user.id,
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    update_data = task_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    delete_cached_value(
        f"tasks:{user.username}"
    )

    return task


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = get_authenticated_user(
        current_user,
        db,
    )

    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.owner_id == user.id,
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()

    delete_cached_value(
        f"tasks:{user.username}"
    )

    return {
        "message": "Task deleted successfully"
    }
