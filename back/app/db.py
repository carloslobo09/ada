from collections.abc import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    """SQLite ignora las FK salvo que se active el pragma por conexion."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


_settings = get_settings()

_connect_args = (
    {"check_same_thread": False} if _settings.db_url.startswith("sqlite") else {}
)

_engine = create_engine(_settings.db_url, connect_args=_connect_args, future=True)

_SessionFactory = sessionmaker(
    bind=_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_session() -> Iterator[Session]:
    session = _SessionFactory()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Crea las tablas, ejecuta seeds iniciales. Idempotente."""
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=_engine)
    _seed_initial_data()


def _seed_initial_data() -> None:
    from app.repositories.prompt_version_repo import PromptVersionRepository
    from app.repositories.tipo_documento_repo import TipoDocumentoRepository
    from app.repositories.usuario_repo import UsuarioRepository
    from app.services.auth_service import AuthService, seed_default_users_if_missing
    from app.services.prompt_version_service import seed_default_prompt_version_if_missing
    from app.services.seed.dni_v1 import (
        DNI_CROSS_VALIDATION_CONFIG_V1,
        DNI_EXTRACTION_FIELDS_V1,
        DNI_PROMPT_V1,
    )
    from app.services.tipo_documento_service import seed_default_tipo_documento_if_missing

    session = _SessionFactory()
    try:
        usuario_repo = UsuarioRepository(session)
        auth = AuthService(usuario_repo, _settings)
        seed_default_users_if_missing(
            usuario_repo, auth_service=auth, password=_settings.seed_password
        )

        tipo_repo = TipoDocumentoRepository(session)
        tipo = seed_default_tipo_documento_if_missing(
            tipo_repo,
            nombre="DNI Argentino",
            descripcion=(
                "Documento Nacional de Identidad emitido por el Registro Nacional "
                "de las Personas de la Republica Argentina."
            ),
        )

        prompt_repo = PromptVersionRepository(session)
        seed_default_prompt_version_if_missing(
            prompt_repo,
            tipo_documento_id=tipo.id,
            prompt_text=DNI_PROMPT_V1,
            extraction_fields=DNI_EXTRACTION_FIELDS_V1,
            cross_validation_config=DNI_CROSS_VALIDATION_CONFIG_V1,
        )
    finally:
        session.close()
