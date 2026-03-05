from fastapi import APIRouter, Depends, HTTPException, Body, status, Path
from database import SessionLocal
from typing import List, Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from tables import Todos


router = APIRouter()

def get_data():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_data)]

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
def read_todos(db: db_dependency) -> List[TodoResponse]:
    todos = db.query(Todos).all()
    return [TodoResponse.model_validate(todo) for todo in todos]

@router.get("/{todo_id}", response_model=TodoResponse, status_code= status.HTTP_200_OK)
def read_todo(db: db_dependency, todo_id: int = Path(gt=0)) -> TodoResponse:
    todo = (db.query(Todos).filter(Todos.id == todo_id).first())
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id {todo_id} not found")
    return TodoResponse.model_validate(todo)

@router.post("", status_code= status.HTTP_201_CREATED)
def create_todo(db: db_dependency, todo_request: TodoRequest = Body()) -> None:
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()

@router.put("/{todo_id}", status_code= status.HTTP_204_NO_CONTENT)
def update_todo(db: db_dependency, todo_id: int = Path(gt=0), todo_request: TodoRequest = Body()) -> None:
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id {todo_id} not found")
    for key, value in todo_request.model_dump().items():
        setattr(todo, key, value)
    db.add(todo)
    db.commit()

@router.delete("/{todo_id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)) -> None:
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id {todo_id} not found")
    db.delete(todo)
    db.commit()


