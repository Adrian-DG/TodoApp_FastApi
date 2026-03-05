from fastapi import FastAPI
from database import engine
from routers import auth, todos
import tables
from fastapi_pagination import add_pagination

app = FastAPI()
add_pagination(app)

tables.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)