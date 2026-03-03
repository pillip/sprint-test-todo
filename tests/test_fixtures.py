"""Tests for shared test fixtures."""

import pytest


class TestTestDbFixture:
    async def test_provides_empty_initialized_database(self, test_db):
        cursor = await test_db.execute("SELECT COUNT(*) FROM todos")
        row = await cursor.fetchone()
        assert row[0] == 0

    async def test_has_correct_schema(self, test_db):
        cursor = await test_db.execute("PRAGMA table_info(todos)")
        columns = await cursor.fetchall()
        assert len(columns) == 7


class TestSeededDbFixture:
    async def test_provides_database_with_6_rows(self, seeded_db):
        cursor = await seeded_db.execute("SELECT COUNT(*) FROM todos")
        row = await cursor.fetchone()
        assert row[0] == 6

    async def test_covers_all_categories(self, seeded_db):
        cursor = await seeded_db.execute("SELECT DISTINCT category FROM todos ORDER BY category")
        rows = await cursor.fetchall()
        categories = {r[0] for r in rows}
        assert categories == {"health", "personal", "shopping", "work"}

    async def test_covers_both_completion_states(self, seeded_db):
        cursor = await seeded_db.execute(
            "SELECT DISTINCT is_completed FROM todos ORDER BY is_completed"
        )
        rows = await cursor.fetchall()
        states = {r[0] for r in rows}
        assert states == {0, 1}
