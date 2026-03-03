"""SQLite database connection management and table initialization."""

import os

import aiosqlite

DATABASE_URL_DEFAULT = "todos.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL CHECK(category IN ('work', 'personal', 'shopping', 'health')),
    is_completed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

CREATE_INDEX_CATEGORY_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_todos_category ON todos(category);"
)

CREATE_INDEX_CREATED_AT_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_todos_created_at ON todos(created_at);"
)


def get_db_path() -> str:
    """Return database file path from DATABASE_URL env var or default."""
    return os.environ.get("DATABASE_URL", DATABASE_URL_DEFAULT)


async def init_db(db_path: str | None = None) -> None:
    """Initialize the database schema (table + indexes). Idempotent."""
    path = db_path or get_db_path()
    async with aiosqlite.connect(path) as db:
        await db.execute(CREATE_TABLE_SQL)
        await db.execute(CREATE_INDEX_CATEGORY_SQL)
        await db.execute(CREATE_INDEX_CREATED_AT_SQL)
        await db.commit()


async def get_db(db_path: str | None = None):
    """Async context manager providing an aiosqlite connection with Row factory."""
    path = db_path or get_db_path()
    db = await aiosqlite.connect(path)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()
