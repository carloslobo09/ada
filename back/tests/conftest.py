from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.db as ada_db
from app.api.dependencies import get_storage
from app.config import Settings, get_settings
from app.db import Base, get_session
from app.main import app as fastapi_app
from app.storage.filesystem import FilesystemStorage

SEED_PASSWORD = "ada2026"
ADMIN_EMAIL = "admin@ada.local"
ENTRENADOR_EMAIL = "entrenador@ada.local"
CLIENTE_EMAIL = "cliente@ada.local"


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        extractor_mode="mock",
        db_url=f"sqlite:///{tmp_path / 'test.db'}",
        upload_dir=tmp_path / "uploads",
        seed_password=SEED_PASSWORD,
    )


@pytest.fixture
def client(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    engine = create_engine(settings.db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    monkeypatch.setattr(ada_db, "_engine", engine)
    monkeypatch.setattr(ada_db, "_SessionFactory", SessionFactory)
    monkeypatch.setattr(ada_db, "_settings", settings)

    def override_session() -> Iterator[Session]:
        session = SessionFactory()
        try:
            yield session
        finally:
            session.close()

    def override_storage() -> FilesystemStorage:
        return FilesystemStorage(settings.upload_dir)

    fastapi_app.dependency_overrides[get_settings] = lambda: settings
    fastapi_app.dependency_overrides[get_session] = override_session
    fastapi_app.dependency_overrides[get_storage] = override_storage

    with TestClient(fastapi_app) as test_client:
        token = _login(test_client, ADMIN_EMAIL, SEED_PASSWORD)
        test_client.headers["Authorization"] = f"Bearer {token}"
        yield test_client

    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def anon_client(client: TestClient) -> Iterator[TestClient]:
    """Cliente sin Authorization header, util para probar rechazos 401."""
    saved = client.headers.pop("Authorization", None)
    try:
        yield client
    finally:
        if saved is not None:
            client.headers["Authorization"] = saved


@pytest.fixture
def admin_token(client: TestClient) -> str:
    return _login(client, ADMIN_EMAIL, SEED_PASSWORD)


@pytest.fixture
def entrenador_token(client: TestClient) -> str:
    return _login(client, ENTRENADOR_EMAIL, SEED_PASSWORD)


@pytest.fixture
def cliente_token(client: TestClient) -> str:
    return _login(client, CLIENTE_EMAIL, SEED_PASSWORD)


@pytest.fixture
def seeded_tipo_id(client: TestClient) -> str:
    tipos = client.get("/document-types").json()
    return next(t["id"] for t in tipos if t["nombre"] == "DNI Argentino")


def _login(client: TestClient, email: str, password: str) -> str:
    saved = client.headers.pop("Authorization", None)
    try:
        response = client.post(
            "/auth/login", json={"email": email, "password": password}
        )
    finally:
        if saved is not None:
            client.headers["Authorization"] = saved
    response.raise_for_status()
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
