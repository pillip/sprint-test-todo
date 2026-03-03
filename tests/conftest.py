"""Shared pytest fixtures for test database management."""

import os
import pytest
import aiosqlite

from src.database import init_db


@pytest.fixture
async def test_db(tmp_path):
    """Provide a fresh initialized temp database connection.

    Creates a new SQLite database in a temp directory, initializes the schema,
    yields the connection, and cleans up after the test.
    """
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)
    conn = await aiosqlite.connect(db_path)
    conn.row_factory = aiosqlite.Row
    yield conn
    await conn.close()


@pytest.fixture
async def seeded_db(tmp_path):
    """Provide a database pre-loaded with 6 sample todos.

    Seed data covers all 4 categories and both completion states,
    matching the development seed data from docs/data_model.md.
    """
    db_path = str(tmp_path / "seeded.db")
    await init_db(db_path)
    conn = await aiosqlite.connect(db_path)
    conn.row_factory = aiosqlite.Row

    seed_sql = """
    INSERT OR IGNORE INTO todos (id, title, description, category, is_completed, created_at, updated_at)
    VALUES
        (1, 'Review pull requests', 'Check the backend PR and the frontend PR', 'work', 0, '2026-03-03T09:00:00', '2026-03-03T09:00:00'),
        (2, 'Buy groceries', 'Milk, eggs, bread, butter', 'shopping', 0, '2026-03-03T09:15:00', '2026-03-03T09:15:00'),
        (3, 'Schedule dentist appointment', NULL, 'health', 0, '2026-03-03T09:30:00', '2026-03-03T09:30:00'),
        (4, 'Call mom', 'Catch up over the weekend', 'personal', 1, '2026-03-02T18:00:00', '2026-03-03T08:00:00'),
        (5, 'Finish quarterly report', 'Due by end of week', 'work', 1, '2026-03-01T10:00:00', '2026-03-02T16:00:00'),
        (6, 'Morning jog', NULL, 'health', 0, '2026-03-03T06:00:00', '2026-03-03T06:00:00');
    """
    await conn.executescript(seed_sql)

    yield conn
    await conn.close()
