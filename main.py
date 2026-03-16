"""Application entry point.

Initializes FastAPI, registers pagination support, creates database tables,
and includes authentication and todo routers.
"""

from fastapi import FastAPI
from database import engine
from routers import auth, todos
import tables
from fastapi_pagination import add_pagination

# Create the FastAPI app instance.
app = FastAPI()

# Enable pagination helpers globally.
add_pagination(app)

# Create all SQLAlchemy tables if they do not exist yet.
tables.Base.metadata.create_all(bind=engine)

# Register route groups.
app.include_router(auth.router)
app.include_router(todos.router)