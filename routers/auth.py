from fastapi import APIRouter, status, Body
from pydantic import BaseModel, Field
from tables import Users
from passlib.context import CryptContext
from routers.dependencies import db_dependency

router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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


