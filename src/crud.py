"""CRUD operations for todos using parameterized SQL queries."""

from datetime import datetime, timezone

import aiosqlite


def _row_to_dict(row: aiosqlite.Row) -> dict:
    """Convert an aiosqlite.Row to a plain dict."""
    return dict(row)


async def create_todo(db: aiosqlite.Connection, todo_data: dict) -> dict:
    """Insert a new todo and return the created row as a dict."""
    now = datetime.now(timezone.utc).isoformat()
    cursor = await db.execute(
        "INSERT INTO todos (title, description, category, is_completed, created_at, updated_at) "
        "VALUES (?, ?, ?, 0, ?, ?)",
        (
            todo_data["title"],
            todo_data.get("description"),
            todo_data["category"],
            now,
            now,
        ),
    )
    await db.commit()
    todo_id = cursor.lastrowid
    return await get_todo(db, todo_id)


async def get_todos(
    db: aiosqlite.Connection,
    category: str | None = None,
    is_completed: bool | None = None,
) -> list[dict]:
    """List todos with optional filters, ordered by created_at DESC."""
    query = "SELECT * FROM todos"
    conditions = []
    params = []

    if category is not None:
        conditions.append("category = ?")
        params.append(category)

    if is_completed is not None:
        conditions.append("is_completed = ?")
        params.append(1 if is_completed else 0)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY created_at DESC"

    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    return [_row_to_dict(row) for row in rows]


async def get_todo(db: aiosqlite.Connection, todo_id: int) -> dict | None:
    """Get a single todo by id, or None if not found."""
    cursor = await db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    row = await cursor.fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


async def update_todo(
    db: aiosqlite.Connection, todo_id: int, todo_data: dict
) -> dict | None:
    """Update a todo by id. Returns updated dict or None if not found."""
    now = datetime.now(timezone.utc).isoformat()
    cursor = await db.execute(
        "UPDATE todos SET title = ?, description = ?, category = ?, "
        "is_completed = ?, updated_at = ? WHERE id = ?",
        (
            todo_data["title"],
            todo_data.get("description"),
            todo_data["category"],
            1 if todo_data["is_completed"] else 0,
            now,
            todo_id,
        ),
    )
    await db.commit()
    if cursor.rowcount == 0:
        return None
    return await get_todo(db, todo_id)


async def delete_todo(db: aiosqlite.Connection, todo_id: int) -> bool:
    """Delete a todo by id. Returns True if deleted, False if not found."""
    cursor = await db.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    await db.commit()
    return cursor.rowcount > 0
