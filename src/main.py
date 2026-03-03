"""FastAPI application with CRUD API endpoints for todos."""

from contextlib import asynccontextmanager
from typing import Optional

import aiosqlite
from fastapi import FastAPI, HTTPException, Query, Response

from src.crud import create_todo, delete_todo, get_todo, get_todos, update_todo
from src.database import get_db_path, init_db
from src.models import Category, TodoCreate, TodoResponse, TodoUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(title="Todo List API", lifespan=lifespan)


async def _get_db():
    """Get a database connection for the current request."""
    db = await aiosqlite.connect(get_db_path())
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()


@app.post("/api/todos", status_code=201, response_model=TodoResponse)
async def create_todo_endpoint(todo: TodoCreate):
    async for db in _get_db():
        result = await create_todo(db, todo.model_dump())
        return TodoResponse(**result)


@app.get("/api/todos", response_model=list[TodoResponse])
async def list_todos_endpoint(
    category: Optional[Category] = None,
    is_completed: Optional[bool] = None,
):
    async for db in _get_db():
        cat_value = category.value if category else None
        todos = await get_todos(db, category=cat_value, is_completed=is_completed)
        return [TodoResponse(**t) for t in todos]


@app.get("/api/todos/{todo_id}", response_model=TodoResponse)
async def get_todo_endpoint(todo_id: int):
    async for db in _get_db():
        result = await get_todo(db, todo_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Todo not found")
        return TodoResponse(**result)


@app.put("/api/todos/{todo_id}", response_model=TodoResponse)
async def update_todo_endpoint(todo_id: int, todo: TodoUpdate):
    async for db in _get_db():
        result = await update_todo(db, todo_id, todo.model_dump())
        if result is None:
            raise HTTPException(status_code=404, detail="Todo not found")
        return TodoResponse(**result)


@app.delete("/api/todos/{todo_id}", status_code=204)
async def delete_todo_endpoint(todo_id: int):
    async for db in _get_db():
        success = await delete_todo(db, todo_id)
        if not success:
            raise HTTPException(status_code=404, detail="Todo not found")
        return Response(status_code=204)
