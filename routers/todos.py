"""Todo management router.

Contains CRUD endpoints and filtering/pagination behavior for todo items.
"""

from fastapi import APIRouter, HTTPException, Body, status, Path, Depends
from typing import List
from pydantic import BaseModel, Field
from routers.dependencies import db_dependency, user_dependency
from tables import Todos



# Router for todo-related endpoints.
router = APIRouter(tags=["todos"], prefix="/todos")



class TodoResponse(BaseModel):
    """Response schema returned to clients for todo resources."""

    id: int
    title: str
    description: str
    priority: int
    completed: bool

    class Config:
        from_attributes = True


class PaginationFilterRequest(BaseModel):
    """Query parameter schema for pagination and filtering."""

    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=1, le=100, default=10)
    param: str | None = Field(default=None)
    is_completed: bool | None = Field(default=False)

class TodoRequest(BaseModel):
    """Request body schema for creating/updating todos."""

    title: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=2, max_length=200)
    priority: int = Field(ge=1, le=5, default=1)
    is_completed: bool = Field(default=False)


@router.get("", response_model=List[TodoResponse], status_code=status.HTTP_200_OK)
def read_todos(db: db_dependency, user: user_dependency, filter_request: PaginationFilterRequest = Depends()) -> List[TodoResponse]:
    """Return paginated todos filtered by role, text, and completion status."""
    # Start with base query.
    query = db.query(Todos)

    # Non-admin users can only view their own todos.
    if user.get("role") != "admin":
        query = query.filter(Todos.owner_id == user.get("user_id"))

    # Optional title contains filter.
    if filter_request.param:
        query = query.filter(Todos.title.contains(filter_request.param))

    # Optional completion-state filter.
    if filter_request.is_completed is not None:
        query = query.filter(Todos.completed == filter_request.is_completed)

    # Calculate SQL offset for page-based pagination.
    offset = (filter_request.page - 1) * filter_request.page_size
    # Execute paginated query.
    todos = query.offset(offset).limit(filter_request.page_size).all()

    # Convert ORM models to validated response schemas.
    return [TodoResponse.model_validate(todo) for todo in todos]


@router.get("/{todo_id}", response_model=TodoResponse, status_code= status.HTTP_200_OK)
def read_todo(db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0)) -> TodoResponse:
    """Return a single todo by id for the authenticated owner."""
    # Fetch todo scoped to the authenticated user.
    todo = (db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get("user_id")).first())
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id {todo_id} not found")
    # Return serialized response object.
    return TodoResponse.model_validate(todo)


@router.post("", status_code= status.HTTP_201_CREATED)
def create_todo(db: db_dependency, user: user_dependency, todo_request: TodoRequest = Body()) -> None:
    """Create a new todo item for the authenticated user."""
    # Map request data into ORM model.
    todo_model = Todos(
        title=todo_request.title,
        description=todo_request.description,
        priority=todo_request.priority,
        completed=todo_request.is_completed,
        owner_id=user.get("user_id")
    )
    # Persist and commit the new todo.
    db.add(todo_model)
    db.commit()


@router.put("/{todo_id}", status_code= status.HTTP_204_NO_CONTENT)
def update_todo(db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0), todo_request: TodoRequest = Body()) -> None:
    """Update an existing todo if it belongs to the authenticated user."""
    # Locate todo scoped to user ownership.
    todo = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get("user_id")).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id {todo_id} not found")
    # Apply each request field to the existing ORM instance.
    for key, value in todo_request.model_dump().items():
        setattr(todo, key, value)
    # Persist updated values.
    db.add(todo)
    db.commit()

@router.delete("/{todo_id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_todo(db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0)) -> None:
    """Delete a todo by id if it belongs to the authenticated user."""
    # Locate todo scoped to user ownership.
    todo = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get("user_id")).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id {todo_id} not found")
    # Delete and commit removal.
    db.delete(todo)
    db.commit()


