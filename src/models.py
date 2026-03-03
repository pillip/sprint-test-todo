"""Pydantic schemas and Category enum for the Todo application."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Category(str, Enum):
    """Todo category enum with 4 fixed values."""

    work = "work"
    personal = "personal"
    shopping = "shopping"
    health = "health"


class TodoCreate(BaseModel):
    """Schema for creating a new todo."""

    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    category: Category


class TodoUpdate(BaseModel):
    """Schema for full-replacement update of a todo."""

    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    category: Category
    is_completed: bool


class TodoResponse(BaseModel):
    """Schema for todo API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    category: Category
    is_completed: bool
    created_at: str
    updated_at: str
