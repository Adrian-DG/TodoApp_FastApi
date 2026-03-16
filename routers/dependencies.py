"""Shared dependency providers for routers.

Exposes typed dependencies for database sessions and authenticated users.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from routers.auth import get_current_user


def get_db():
    """Yield a database session and always close it after request handling."""
    # Open a new SQLAlchemy session for the current request.
    db = SessionLocal()
    try:
        # Provide the session to the endpoint.
        yield db
    finally:
        # Ensure resources are released even if an exception occurs.
        db.close()


# Typed dependency alias for DB session injection.
db_dependency = Annotated[Session, Depends(get_db)]
# Typed dependency alias for authenticated user payload injection.
user_dependency = Annotated[dict, Depends(get_current_user)]
