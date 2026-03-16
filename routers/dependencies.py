"""Shared dependency providers for routers.

Exposes typed dependencies for database sessions and authenticated users.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from database import SessionLocal


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


