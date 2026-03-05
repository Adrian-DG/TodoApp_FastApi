from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, status, Body, HTTPException
from pydantic import BaseModel, Field
from tables import Users
from passlib.context import CryptContext
from routers.dependencies import db_dependency
from jose import jwt

router = APIRouter()

__SECRET_KEY = "fbce05c95e1fd3d56e6d245582d754f97aeeab1509ea539049eea871e7e42ffd"
__ALGORITHM = "HS256"
__ACCESS_TOKEN_EXPIRE_MINUTES = 30

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=3, max_length=20)
    first_name: str = Field(min_length=3, max_length=20)
    last_name: str = Field(min_length=3, max_length=20)
    role: str

class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=3, max_length=20)

class LoginResponse(BaseModel):
    access_token: str
    token_type: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency, request: CreateUserRequest = Body()) -> None:
    """Create a new user account with hashed password."""
    new_user = Users(
        username=request.username,
        hashed_password=bcrypt_context.hash(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        role=request.role
    )
    db.add(new_user)
    db.commit()

@router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponse)
def login_user(db: db_dependency, request: LoginRequest = Body()) -> LoginResponse:
    user = db.query(Users).filter(Users.username == request.username).first()
    if not user or not bcrypt_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    return LoginResponse(access_token=__create_access_token(user.id, user.username, user.role), token_type='bearer')
    

def __create_access_token(user_id: int, username: str, role: str) -> str:
    encode = { "user_id": user_id, "username": username, "role": role, "exp": datetime.now(timezone.utc) + timedelta(minutes=__ACCESS_TOKEN_EXPIRE_MINUTES) } 
    encoded_jwt = jwt.encode(encode, __SECRET_KEY, algorithm=__ALGORITHM)
    return encoded_jwt