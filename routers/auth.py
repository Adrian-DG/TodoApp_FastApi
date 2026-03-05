from fastapi import APIRouter, status, Body, Depends
from pydantic import BaseModel, Field
from database import SessionLocal
from tables import Users
from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session

router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_data():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_data)]

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=3, max_length=20)
    first_name: str = Field(min_length=3, max_length=20)
    last_name: str = Field(min_length=3, max_length=20)
    role: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency, request: CreateUserRequest = Body()) -> None:
    new_user = Users(**request.model_dump())
    new_user.hashed_password = bcrypt_context.hash(request.password)
    db.add(new_user)
    db.commit()


