from fastapi import FastAPI
from database import engine
from routers import auth, todos
import tables

app = FastAPI()

tables.Base.metadata.create_all(bind=engine)
app.include_router(auth.router, tags=["auth"], prefix="/auth")
app.include_router(todos.router, tags=["todos"], prefix="/todos")

