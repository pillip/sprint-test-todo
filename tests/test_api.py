"""Integration tests for FastAPI API endpoints."""

import os
import pytest
import tempfile

from httpx import AsyncClient, ASGITransport

# Set test DB before importing app
_test_db = tempfile.mktemp(suffix=".db")
os.environ["DATABASE_URL"] = _test_db

from src.main import app
from src.database import init_db


@pytest.fixture(autouse=True)
async def setup_db():
    """Initialize a fresh test database for each test."""
    # Remove old test db if it exists
    if os.path.exists(_test_db):
        os.unlink(_test_db)
    await init_db(_test_db)
    yield
    if os.path.exists(_test_db):
        os.unlink(_test_db)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def valid_todo():
    return {"title": "Buy milk", "description": "From the store", "category": "shopping"}


class TestCreateTodo:
    async def test_valid_data_returns_201(self, client, valid_todo):
        resp = await client.post("/api/todos", json=valid_todo)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Buy milk"
        assert data["id"] is not None
        assert data["is_completed"] is False

    async def test_missing_title_returns_422(self, client):
        resp = await client.post("/api/todos", json={"category": "work"})
        assert resp.status_code == 422

    async def test_invalid_category_returns_422(self, client):
        resp = await client.post("/api/todos", json={"title": "Test", "category": "invalid"})
        assert resp.status_code == 422


class TestListTodos:
    async def test_returns_200_with_list(self, client, valid_todo):
        await client.post("/api/todos", json=valid_todo)
        resp = await client.get("/api/todos")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) == 1

    async def test_filter_by_category(self, client):
        await client.post("/api/todos", json={"title": "Work", "category": "work"})
        await client.post("/api/todos", json={"title": "Shop", "category": "shopping"})
        resp = await client.get("/api/todos", params={"category": "work"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["category"] == "work"

    async def test_filter_by_is_completed(self, client):
        create_resp = await client.post("/api/todos", json={"title": "Task", "category": "work"})
        todo_id = create_resp.json()["id"]
        await client.put(
            f"/api/todos/{todo_id}",
            json={"title": "Task", "category": "work", "is_completed": True},
        )
        resp = await client.get("/api/todos", params={"is_completed": "true"})
        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestGetTodo:
    async def test_valid_id_returns_200(self, client, valid_todo):
        create_resp = await client.post("/api/todos", json=valid_todo)
        todo_id = create_resp.json()["id"]
        resp = await client.get(f"/api/todos/{todo_id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Buy milk"

    async def test_invalid_id_returns_404(self, client):
        resp = await client.get("/api/todos/999")
        assert resp.status_code == 404


class TestUpdateTodo:
    async def test_valid_update_returns_200(self, client, valid_todo):
        create_resp = await client.post("/api/todos", json=valid_todo)
        todo_id = create_resp.json()["id"]
        resp = await client.put(
            f"/api/todos/{todo_id}",
            json={"title": "Updated", "category": "work", "is_completed": True},
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated"
        assert resp.json()["is_completed"] is True

    async def test_invalid_id_returns_404(self, client):
        resp = await client.put(
            "/api/todos/999",
            json={"title": "X", "category": "work", "is_completed": False},
        )
        assert resp.status_code == 404

    async def test_invalid_category_returns_422(self, client, valid_todo):
        create_resp = await client.post("/api/todos", json=valid_todo)
        todo_id = create_resp.json()["id"]
        resp = await client.put(
            f"/api/todos/{todo_id}",
            json={"title": "X", "category": "invalid", "is_completed": False},
        )
        assert resp.status_code == 422


class TestDeleteTodo:
    async def test_valid_id_returns_204(self, client, valid_todo):
        create_resp = await client.post("/api/todos", json=valid_todo)
        todo_id = create_resp.json()["id"]
        resp = await client.delete(f"/api/todos/{todo_id}")
        assert resp.status_code == 204

    async def test_invalid_id_returns_404(self, client):
        resp = await client.delete("/api/todos/999")
        assert resp.status_code == 404
