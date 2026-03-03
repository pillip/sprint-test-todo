"""Tests for Pydantic models and Category enum."""

import pytest
from pydantic import ValidationError

from src.models import Category, TodoCreate, TodoUpdate, TodoResponse


class TestCategory:
    def test_category_has_exactly_4_values(self):
        assert len(Category) == 4

    def test_category_values(self):
        assert set(v.value for v in Category) == {"work", "personal", "shopping", "health"}


class TestTodoCreate:
    def test_rejects_empty_title(self):
        with pytest.raises(ValidationError):
            TodoCreate(title="", category="work")

    def test_rejects_title_exceeding_200_chars(self):
        with pytest.raises(ValidationError):
            TodoCreate(title="x" * 201, category="work")

    def test_rejects_description_exceeding_1000_chars(self):
        with pytest.raises(ValidationError):
            TodoCreate(title="Valid", description="x" * 1001, category="work")

    def test_rejects_invalid_category(self):
        with pytest.raises(ValidationError):
            TodoCreate(title="Valid", category="invalid")

    def test_accepts_valid_input(self):
        todo = TodoCreate(title="Buy milk", category="shopping")
        assert todo.title == "Buy milk"
        assert todo.category == Category.shopping
        assert todo.description is None

    def test_accepts_valid_input_with_description(self):
        todo = TodoCreate(title="Buy milk", description="From the store", category="work")
        assert todo.description == "From the store"

    def test_accepts_title_at_max_length(self):
        todo = TodoCreate(title="x" * 200, category="work")
        assert len(todo.title) == 200


class TestTodoUpdate:
    def test_accepts_all_valid_fields_including_is_completed(self):
        todo = TodoUpdate(
            title="Updated",
            description="Updated desc",
            category="personal",
            is_completed=True,
        )
        assert todo.is_completed is True
        assert todo.category == Category.personal

    def test_accepts_is_completed_false(self):
        todo = TodoUpdate(
            title="Test",
            category="work",
            is_completed=False,
        )
        assert todo.is_completed is False

    def test_rejects_empty_title(self):
        with pytest.raises(ValidationError):
            TodoUpdate(title="", category="work", is_completed=False)


class TestTodoResponse:
    def test_creates_from_dict(self):
        data = {
            "id": 1,
            "title": "Test",
            "description": None,
            "category": "work",
            "is_completed": False,
            "created_at": "2026-03-03T10:00:00",
            "updated_at": "2026-03-03T10:00:00",
        }
        resp = TodoResponse(**data)
        assert resp.id == 1
        assert resp.category == Category.work
