"""SQLAlchemy ORM table definitions."""

from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class Users(Base):
    """User account model used for authentication and ownership."""

    __tablename__ = "users"

    # Primary key and identity.
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # Profile information.
    first_name = Column(String)
    last_name = Column(String)
    # Login and authorization fields.
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String)

    def __str__(self):
        """Human-readable display for logging/debugging."""
        return f"{self.first_name} {self.last_name}"


class Todos(Base):
    """Todo item model owned by a user."""

    __tablename__ = "todos"

    # Primary key and todo content.
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    # Priority and completion state.
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    # Owner relation to the users table.
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)