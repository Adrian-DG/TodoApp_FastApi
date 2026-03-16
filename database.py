"""Database configuration module.

Defines the SQLAlchemy engine, session factory, and declarative base used
throughout the application.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLite connection string for local development.
# SQLALQUEMY_DATABASE_URI = 'sqlite:///./todos.db'
# engine = create_engine(SQLALQUEMY_DATABASE_URI, connect_args={"check_same_thread": False})

# PostgreSQL connection string for production or Docker usage.
SQLALQUEMY_DATABASE_URI = 'postgresql://postgres:password@localhost:5432/TodoApplicationDatabase'

# SQLAlchemy engine (check_same_thread disabled for SQLite + FastAPI usage).
engine = create_engine(SQLALQUEMY_DATABASE_URI)

# Session factory used to create per-request DB sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models.
Base = declarative_base()





