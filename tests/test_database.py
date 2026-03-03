"""Tests for database connection and table initialization."""

import os
import pytest
import aiosqlite

from src.database import get_db_path, init_db


class TestGetDbPath:
    def test_returns_default_when_env_unset(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        assert get_db_path() == "todos.db"

    def test_returns_env_var_value_when_set(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "/tmp/test.db")
        assert get_db_path() == "/tmp/test.db"


class TestInitDb:
    @pytest.fixture
    def db_path(self, tmp_path):
        return str(tmp_path / "test.db")

    async def test_creates_table_with_correct_schema(self, db_path):
        await init_db(db_path)
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute("PRAGMA table_info(todos)")
            columns = await cursor.fetchall()
            assert len(columns) == 7
            col_names = [c[1] for c in columns]
            assert col_names == [
                "id", "title", "description", "category",
                "is_completed", "created_at", "updated_at"
            ]

    async def test_creates_indexes(self, db_path):
        await init_db(db_path)
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='todos'"
            )
            indexes = await cursor.fetchall()
            index_names = {row[0] for row in indexes}
            assert "idx_todos_category" in index_names
            assert "idx_todos_created_at" in index_names

    async def test_is_idempotent(self, db_path):
        await init_db(db_path)
        await init_db(db_path)  # Second call should not raise
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute("PRAGMA table_info(todos)")
            columns = await cursor.fetchall()
            assert len(columns) == 7

    async def test_preserves_data_on_reinit(self, db_path):
        await init_db(db_path)
        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                "INSERT INTO todos (title, category, is_completed, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?)",
                ("Test", "work", 0, "2026-01-01T00:00:00", "2026-01-01T00:00:00"),
            )
            await db.commit()
        await init_db(db_path)
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM todos")
            row = await cursor.fetchone()
            assert row[0] == 1
