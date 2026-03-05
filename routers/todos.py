from fastapi import APIRouter, HTTPException, Body, status, Path, Depends
from typing import List, Annotated
from pydantic import BaseModel, Field
from routers.dependencies import db_dependency
from tables import Todos
from routers.auth import get_current_user

router = APIRouter(tags=["todos"], prefix="/todos")
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: int
    completed: bool

    class Config:
        from_attributes = True
class TodoRequest(BaseModel):
    title: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=2, max_length=200)
    priority: int = Field(ge=1, le=5, default=1)
    is_completed: bool = Field(default=False)


@router.get("", response_model=List[TodoResponse], status_code= status.HTTP_200_OK)
def read_todos(db: db_dependency, user: user_dependency) -> List[TodoResponse]:
    todos = db.query(Todos).filter(Todos.owner_id == user.get("user_id")).all()
    return [TodoResponse.model_validate(todo) for todo in todos]

@router.get("/{todo_id}", response_model=TodoResponse, status_code= status.HTTP_200_OK)
def read_todo(db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0)) -> TodoResponse:
    todo = (db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get("user_id")).first())
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id {todo_id} not found")
    return TodoResponse.model_validate(todo)

@router.post("", status_code= status.HTTP_201_CREATED)
def create_todo(db: db_dependency, user: user_dependency, todo_request: TodoRequest = Body()) -> None:
    todo_model = Todos(
        title=todo_request.title,
        description=todo_request.description,
        priority=todo_request.priority,
        completed=todo_request.is_completed,
        owner_id=user.get("user_id")
    )
    db.add(todo_model)
    db.commit()

@router.put("/{todo_id}", status_code= status.HTTP_204_NO_CONTENT)
def update_todo(db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0), todo_request: TodoRequest = Body()) -> None:
    todo = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get("user_id")).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id {todo_id} not found")
    for key, value in todo_request.model_dump().items():
        setattr(todo, key, value)
    db.add(todo)
    db.commit()

@router.delete("/{todo_id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_todo(db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0)) -> None:
    todo = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get("user_id")).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id {todo_id} not found")
    db.delete(todo)
    db.commit()


