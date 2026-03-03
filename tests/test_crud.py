"""Tests for CRUD operations."""

import pytest
import aiosqlite

from src.database import init_db
from src.crud import create_todo, get_todos, get_todo, update_todo, delete_todo


@pytest.fixture
async def db(tmp_path):
    """Provide a fresh initialized database connection."""
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)
    conn = await aiosqlite.connect(db_path)
    conn.row_factory = aiosqlite.Row
    yield conn
    await conn.close()


@pytest.fixture
def sample_todo():
    return {"title": "Buy milk", "description": "From the store", "category": "shopping"}


class TestCreateTodo:
    async def test_returns_complete_todo(self, db, sample_todo):
        result = await create_todo(db, sample_todo)
        assert result["id"] is not None
        assert result["title"] == "Buy milk"
        assert result["description"] == "From the store"
        assert result["category"] == "shopping"
        assert result["is_completed"] == 0
        assert result["created_at"] is not None
        assert result["updated_at"] is not None

    async def test_creates_with_none_description(self, db):
        todo_data = {"title": "Test", "category": "work"}
        result = await create_todo(db, todo_data)
        assert result["description"] is None


class TestGetTodos:
    async def test_returns_all_sorted_desc(self, db):
        await create_todo(db, {"title": "First", "category": "work"})
        await create_todo(db, {"title": "Second", "category": "personal"})
        todos = await get_todos(db)
        assert len(todos) == 2
        assert todos[0]["title"] == "Second"  # Most recent first
        assert todos[1]["title"] == "First"

    async def test_returns_empty_list(self, db):
        todos = await get_todos(db)
        assert todos == []

    async def test_filter_by_category(self, db):
        await create_todo(db, {"title": "Work task", "category": "work"})
        await create_todo(db, {"title": "Shop task", "category": "shopping"})
        todos = await get_todos(db, category="work")
        assert len(todos) == 1
        assert todos[0]["category"] == "work"

    async def test_filter_by_is_completed(self, db):
        todo = await create_todo(db, {"title": "Task", "category": "work"})
        await update_todo(db, todo["id"], {
            "title": "Task", "category": "work",
            "is_completed": True, "description": None
        })
        completed = await get_todos(db, is_completed=True)
        assert len(completed) == 1
        incomplete = await get_todos(db, is_completed=False)
        assert len(incomplete) == 0

    async def test_filter_by_both(self, db):
        await create_todo(db, {"title": "Work1", "category": "work"})
        todo2 = await create_todo(db, {"title": "Work2", "category": "work"})
        await update_todo(db, todo2["id"], {
            "title": "Work2", "category": "work",
            "is_completed": True, "description": None
        })
        await create_todo(db, {"title": "Shop1", "category": "shopping"})
        todos = await get_todos(db, category="work", is_completed=False)
        assert len(todos) == 1
        assert todos[0]["title"] == "Work1"


class TestGetTodo:
    async def test_returns_existing(self, db, sample_todo):
        created = await create_todo(db, sample_todo)
        result = await get_todo(db, created["id"])
        assert result is not None
        assert result["title"] == "Buy milk"

    async def test_returns_none_for_nonexistent(self, db):
        result = await get_todo(db, 999)
        assert result is None


class TestUpdateTodo:
    async def test_updates_fields_and_timestamp(self, db, sample_todo):
        created = await create_todo(db, sample_todo)
        original_updated_at = created["updated_at"]
        update_data = {
            "title": "Updated title",
            "description": "Updated desc",
            "category": "work",
            "is_completed": True,
        }
        result = await update_todo(db, created["id"], update_data)
        assert result["title"] == "Updated title"
        assert result["is_completed"] == 1
        assert result["updated_at"] >= original_updated_at

    async def test_returns_none_for_nonexistent(self, db):
        result = await update_todo(db, 999, {
            "title": "X", "category": "work",
            "is_completed": False, "description": None
        })
        assert result is None


class TestDeleteTodo:
    async def test_returns_true_for_existing(self, db, sample_todo):
        created = await create_todo(db, sample_todo)
        result = await delete_todo(db, created["id"])
        assert result is True
        # Verify it's gone
        assert await get_todo(db, created["id"]) is None

    async def test_returns_false_for_nonexistent(self, db):
        result = await delete_todo(db, 999)
        assert result is False
