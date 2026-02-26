"""
Tests for the MCP (Model Context Protocol) router.
"""
from __future__ import annotations

from typing import List, Literal, Optional

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pydaadop.models.base.base_mongo_model import BaseMongoModel
from pydaadop.routes.mcp import MCPRouter


# ── Sample models ─────────────────────────────────────────────────────────────

class BookModel(BaseMongoModel):
    title: str
    author: str
    genre: Optional[Literal["fiction", "non-fiction", "science"]] = None

    @staticmethod
    def create_index() -> List[str]:
        return ["title", "author"]


class AuthorModel(BaseMongoModel):
    name: str
    country: str

    @staticmethod
    def create_index() -> List[str]:
        return ["name"]


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def mcp_client() -> TestClient:
    mcp = MCPRouter()
    mcp.register(BookModel)
    mcp.register(AuthorModel)
    app = FastAPI()
    app.include_router(mcp.router)
    return TestClient(app)


# ── GET /_mcp/models ──────────────────────────────────────────────────────────

def test_list_models_returns_200(mcp_client: TestClient):
    response = mcp_client.get("/_mcp/models")
    assert response.status_code == 200


def test_list_models_contains_registered_names(mcp_client: TestClient):
    response = mcp_client.get("/_mcp/models")
    names = response.json()
    assert "BookModel" in names
    assert "AuthorModel" in names


# ── GET /_mcp/models/{name} ───────────────────────────────────────────────────

def test_get_model_known(mcp_client: TestClient):
    response = mcp_client.get("/_mcp/models/BookModel")
    assert response.status_code == 200


def test_get_model_unknown_returns_404(mcp_client: TestClient):
    response = mcp_client.get("/_mcp/models/DoesNotExist")
    assert response.status_code == 404


def test_get_model_has_fields(mcp_client: TestClient):
    response = mcp_client.get("/_mcp/models/BookModel")
    data = response.json()
    assert "fields" in data
    field_names = [f["name"] for f in data["fields"]]
    assert "title" in field_names
    assert "author" in field_names


def test_get_model_has_index_fields(mcp_client: TestClient):
    response = mcp_client.get("/_mcp/models/BookModel")
    data = response.json()
    assert "index_fields" in data
    assert "title" in data["index_fields"]
    assert "author" in data["index_fields"]


def test_get_model_genre_field_has_allowed_values(mcp_client: TestClient):
    response = mcp_client.get("/_mcp/models/BookModel")
    data = response.json()
    genre_field = next((f for f in data["fields"] if f["name"] == "genre"), None)
    assert genre_field is not None
    assert genre_field["allowed_values"] == ["fiction", "non-fiction", "science"]


def test_get_model_has_filter_fields(mcp_client: TestClient):
    response = mcp_client.get("/_mcp/models/BookModel")
    data = response.json()
    assert "filter_fields" in data
    # genre is a Literal → should be filterable
    assert "genre" in data["filter_fields"]


def test_get_model_has_sort_fields(mcp_client: TestClient):
    response = mcp_client.get("/_mcp/models/BookModel")
    data = response.json()
    assert "sort_fields" in data
    assert "title" in data["sort_fields"]


# ── GET /_mcp/context ─────────────────────────────────────────────────────────

def test_context_returns_200(mcp_client: TestClient):
    response = mcp_client.get("/_mcp/context")
    assert response.status_code == 200


def test_context_has_schema_version(mcp_client: TestClient):
    response = mcp_client.get("/_mcp/context")
    data = response.json()
    assert data["schema_version"] == "1.0"


def test_context_has_all_models(mcp_client: TestClient):
    response = mcp_client.get("/_mcp/context")
    data = response.json()
    model_names = [m["name"] for m in data["models"]]
    assert "BookModel" in model_names
    assert "AuthorModel" in model_names


def test_context_has_operations(mcp_client: TestClient):
    response = mcp_client.get("/_mcp/context")
    data = response.json()
    assert "operations" in data
    assert len(data["operations"]) > 0
    methods = {op["method"] for op in data["operations"]}
    assert "GET" in methods
    assert "POST" in methods


def test_context_operations_include_crud_paths(mcp_client: TestClient):
    response = mcp_client.get("/_mcp/context")
    data = response.json()
    paths = {op["path"] for op in data["operations"]}
    # Book-related paths should appear
    assert "/bookmodel/" in paths
    assert "/authormodel/" in paths


# ── Empty registry ────────────────────────────────────────────────────────────

def test_empty_registry_context():
    mcp = MCPRouter()
    app = FastAPI()
    app.include_router(mcp.router)
    tc = TestClient(app)
    response = tc.get("/_mcp/context")
    assert response.status_code == 200
    data = response.json()
    assert data["models"] == []
    assert data["operations"] == []


def test_empty_registry_models():
    mcp = MCPRouter()
    app = FastAPI()
    app.include_router(mcp.router)
    tc = TestClient(app)
    response = tc.get("/_mcp/models")
    assert response.status_code == 200
    assert response.json() == []
