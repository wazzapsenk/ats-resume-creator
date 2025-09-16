from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
from typing import Any

class Base(DeclarativeBase):
    """Base model class with common fields"""
    pass

class TimestampMixin:
    """Mixin for adding timestamp fields"""
    id: Any
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)