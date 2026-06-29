from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import AuthServiceDep, CurrentUserDep
from app.schemas.auth import LoginRequest, LoginResponse, TokenResponse, UsuarioOut
from app.services.auth_service import InactiveUserError, InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["auth"])


def _authenticate_or_raise(auth_service, email: str, password: str):
    try:
        return auth_service.authenticate(email, password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas.",
        ) from exc
    except InactiveUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo.",
        ) from exc


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, auth_service: AuthServiceDep) -> LoginResponse:
    user = _authenticate_or_raise(auth_service, payload.email, payload.password)
    token = auth_service.create_access_token(user)
    return LoginResponse(access_token=token, user=UsuarioOut.model_validate(user))


@router.post("/token", response_model=TokenResponse)
def token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
) -> TokenResponse:
    """Endpoint OAuth2 estandar para que Swagger UI pueda autorizar via el boton 'Authorize'.

    Usa `username` para el email (asi lo nombra el flujo password de OAuth2).
    Para el frontend, usar `POST /auth/login` que recibe JSON y devuelve tambien el usuario.
    """
    user = _authenticate_or_raise(auth_service, form.username, form.password)
    access_token = auth_service.create_access_token(user)
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UsuarioOut)
def me(user: CurrentUserDep) -> UsuarioOut:
    return UsuarioOut.model_validate(user)
