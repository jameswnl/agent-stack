"""Integration tests for auth and authenticated API flows."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from src.db.database import get_db
from src.main import app


@pytest.fixture
def api_client(test_engine, tmp_path, monkeypatch, mock_embeddings):
    """Create a TestClient with an isolated DB and user data directory."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    from src.api import services

    monkeypatch.setattr(services, "get_embeddings", lambda: mock_embeddings)
    monkeypatch.setattr(services, "get_chat_model", lambda: None)
    app.dependency_overrides[get_db] = override_get_db
    app.state.user_data_dir = tmp_path / "users"
    app.state.user_data_dir.mkdir(parents=True, exist_ok=True)
    app.state.ingest_base_dir = tmp_path / "ingest"
    app.state.ingest_base_dir.mkdir(parents=True, exist_ok=True)

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def _auth_headers(client: TestClient, email: str = "user@example.com") -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": "Example User",
        },
    )
    assert response.status_code == 201
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
def test_register_login_and_me(api_client: TestClient):
    """Register, login, and fetch the current user."""
    register_response = api_client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "password": "password123",
            "full_name": "New User",
        },
    )
    assert register_response.status_code == 201
    token = register_response.json()["access_token"]

    login_response = api_client.post(
        "/api/v1/auth/login",
        json={
            "email": "new@example.com",
            "password": "password123",
        },
    )
    assert login_response.status_code == 200
    assert login_response.json()["access_token"]

    me_response = api_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "new@example.com"


@pytest.mark.integration
def test_protected_routes_require_auth(api_client: TestClient, sample_documents_dir):
    """Protected routes reject unauthenticated requests."""
    docs_response = api_client.post(
        "/api/v1/documents/index",
        json={"source_path": str(sample_documents_dir)},
    )
    chat_response = api_client.post("/api/v1/chat", json={"query": "What is installation?"})

    assert docs_response.status_code == 401
    assert chat_response.status_code == 401


@pytest.mark.integration
def test_index_and_chat_flow(api_client: TestClient, sample_documents_dir):
    """Index user documents and query them through the authenticated chat API."""
    headers = _auth_headers(api_client)
    ingest_path = app.state.ingest_base_dir / "shared_docs"
    ingest_path.mkdir(parents=True, exist_ok=True)
    for source_file in sample_documents_dir.iterdir():
        (ingest_path / source_file.name).write_text(source_file.read_text())

    index_response = api_client.post(
        "/api/v1/documents/index",
        json={
            "source_path": str(ingest_path),
            "chunk_size": 120,
            "chunk_overlap": 20,
        },
        headers=headers,
    )
    assert index_response.status_code == 200
    assert index_response.json()["document_count"] == 3
    assert index_response.json()["chunk_count"] > 0

    chat_response = api_client.post(
        "/api/v1/chat",
        json={"query": "What configuration values should be set?"},
        headers=headers,
    )
    assert chat_response.status_code == 200
    assert "What configuration values should be set?" in chat_response.json()["answer"]
    assert isinstance(chat_response.json()["citations"], list)


@pytest.mark.integration
def test_user_document_isolation(api_client: TestClient, sample_documents_dir, tmp_path):
    """Each user gets an isolated persisted vector store."""
    user1_headers = _auth_headers(api_client, email="user1@example.com")
    user2_headers = _auth_headers(api_client, email="user2@example.com")

    user1_docs = app.state.ingest_base_dir / "user1_docs"
    user1_docs.mkdir(exist_ok=True)
    (user1_docs / "private.md").write_text("# Private\n\nSecret token value alpha.")

    index_response = api_client.post(
        "/api/v1/documents/index",
        json={"source_path": str(user1_docs)},
        headers=user1_headers,
    )
    assert index_response.status_code == 200

    missing_chat = api_client.post(
        "/api/v1/chat",
        json={"query": "Secret token value alpha"},
        headers=user2_headers,
    )
    assert missing_chat.status_code == 404

    visible_chat = api_client.post(
        "/api/v1/chat",
        json={"query": "Secret token value alpha"},
        headers=user1_headers,
    )
    assert visible_chat.status_code == 200
    assert "Secret token value alpha" in visible_chat.json()["answer"]


@pytest.mark.integration
def test_index_rejects_source_path_outside_allowed_base(api_client: TestClient, tmp_path):
    """User-supplied source paths outside the ingest root are rejected."""
    headers = _auth_headers(api_client, email="outside@example.com")
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    (outside_dir / "secret.md").write_text("secret")

    response = api_client.post(
        "/api/v1/documents/index",
        json={"source_path": str(outside_dir)},
        headers=headers,
    )

    assert response.status_code == 400
    assert "outside allowed ingestion directory" in response.json()["detail"]
