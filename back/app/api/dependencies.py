from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_session
from app.models.usuario import Usuario
from app.repositories.caso_repo import CasoRepository
from app.repositories.decision_repo import DecisionRepository
from app.repositories.documento_repo import DocumentoRepository
from app.repositories.prompt_version_repo import PromptVersionRepository
from app.repositories.usuario_repo import UsuarioRepository
from app.services.auth_service import (
    AuthService,
    InactiveUserError,
    InvalidTokenError,
)
from app.services.caso_service import CasoService
from app.services.cross_validation.engine import CrossValidationEngine
from app.services.extraction.factory import build_extractor
from app.services.prompt_version_service import (
    PromptVersionNotFoundError,
    PromptVersionService,
)
from app.services.rules.dni_rules import default_dni_rules
from app.services.rules.engine import RuleEngine
from app.services.simulation_service import SimulationService
from app.storage.filesystem import FilesystemStorage

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[Session, Depends(get_session)]


_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)


def get_storage(settings: SettingsDep) -> FilesystemStorage:
    return FilesystemStorage(settings.upload_dir)


def get_prompt_version_service(session: SessionDep) -> PromptVersionService:
    return PromptVersionService(PromptVersionRepository(session))


PromptVersionServiceDep = Annotated[PromptVersionService, Depends(get_prompt_version_service)]


def get_auth_service(session: SessionDep, settings: SettingsDep) -> AuthService:
    return AuthService(UsuarioRepository(session), settings)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_current_user(
    auth_service: AuthServiceDep,
    token: Annotated[str | None, Depends(_oauth2_scheme)] = None,
) -> Usuario:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return auth_service.get_user_from_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalido: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except InactiveUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo.",
        ) from exc


CurrentUserDep = Annotated[Usuario, Depends(get_current_user)]


def require_roles(*allowed: str):
    def checker(user: CurrentUserDep) -> Usuario:
        if user.rol not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol requerido: {', '.join(allowed)}.",
            )
        return user

    return checker


def build_caso_service_for_tipo(
    session: Session,
    settings: Settings,
    storage: FilesystemStorage,
    prompt_version_service: PromptVersionService,
    tipo_documento_id: str,
) -> CasoService:
    try:
        version = prompt_version_service.get_active_or_raise(tipo_documento_id)
    except PromptVersionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"No hay perfil de validacion activo para el tipo de documento {tipo_documento_id}. "
                "Publica una version desde el panel de configuracion."
            ),
        ) from exc

    extractor = build_extractor(settings, version.prompt_text)
    cross_engine = CrossValidationEngine.from_config_dicts(version.cross_validation_config)
    rule_engine = RuleEngine(default_dni_rules())

    return CasoService(
        caso_repository=CasoRepository(session),
        documento_repository=DocumentoRepository(session),
        decision_repository=DecisionRepository(session),
        storage=storage,
        extractor=extractor,
        rule_engine=rule_engine,
        cross_engine=cross_engine,
        tipo_documento_id=tipo_documento_id,
        prompt_version_id=version.id,
    )


def get_simulation_service(
    settings: SettingsDep,
    prompt_version_service: PromptVersionServiceDep,
) -> SimulationService:
    rule_engine = RuleEngine(default_dni_rules())
    return SimulationService(
        settings=settings,
        prompt_version_service=prompt_version_service,
        rule_engine=rule_engine,
    )


SimulationServiceDep = Annotated[SimulationService, Depends(get_simulation_service)]


def get_caso_repository(session: SessionDep) -> CasoRepository:
    return CasoRepository(session)


CasoRepositoryDep = Annotated[CasoRepository, Depends(get_caso_repository)]
