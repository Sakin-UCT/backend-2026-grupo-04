import os
from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.orm import Session
from app.application.services.auth_service import AuthService, Seguridad
from app.domain.usuario import Usuario
from app.infrastructure.repositories.refresh_token_repo import RefreshTokenRepo
from app.infrastructure.repositories.usuario_repo import UsuarioRepo
from app.infrastructure.security.jwt_handler import crear_access_token
from app.infrastructure.security.password import hashear_password, verificar_password
from app.infrastructure.security.token_hash import generar_refresh_token, hashear_refresh
from app.presentation.dependencies import get_db
from app.presentation.schemas.auth_schema import LoginRequest, RegistroRequest, TokenResponse, UsuarioResponse
from app.presentation.security.csrf import generar_csrf_token, verificar_csrf
from app.presentation.security.usuario_actual import get_usuario_actual

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"
SEGUNDOS_REFRESH = 7 * 24 * 3600


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    seguridad = Seguridad(
        hashear_password=hashear_password,
        verificar_password=verificar_password,
        crear_access_token=crear_access_token,
        generar_refresh_token=generar_refresh_token,
        hashear_refresh=hashear_refresh,
    )
    return AuthService(UsuarioRepo(db), RefreshTokenRepo(db), seguridad)


def _poner_cookies(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=SEGUNDOS_REFRESH,
        path="/auth",
    )
    response.set_cookie(
        key="csrf_token",
        value=generar_csrf_token(),
        httponly=False,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=SEGUNDOS_REFRESH,
        path="/",
    )


@router.post("/registro", response_model=UsuarioResponse, status_code=201)
def registro(
    datos: RegistroRequest,
    service: AuthService = Depends(get_auth_service),
):
    return service.registrar(datos.correo, datos.password)


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"description": "Credenciales inválidas"}},
)
def login(
    datos: LoginRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    sesion = service.login(datos.correo, datos.password)
    _poner_cookies(response, sesion.refresh_token)
    return TokenResponse(access_token=sesion.access_token, token_type="bearer")


@router.post(
    "/refresh",
    response_model=TokenResponse,
    dependencies=[Depends(verificar_csrf)],
    responses={
        401: {"description": "Refresh inválido"},
        403: {"description": "CSRF inválido"},
    },
)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    service: AuthService = Depends(get_auth_service),
):
    sesion = service.refrescar(refresh_token or "")
    _poner_cookies(response, sesion.refresh_token)
    return TokenResponse(access_token=sesion.access_token, token_type="bearer")


@router.post(
    "/logout",
    status_code=204,
    dependencies=[Depends(verificar_csrf)],
    responses={403: {"description": "CSRF inválido"}},
)
def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    service: AuthService = Depends(get_auth_service),
):
    service.logout(refresh_token)
    response.delete_cookie("refresh_token", path="/auth")
    response.delete_cookie("csrf_token", path="/")


@router.get(
    "/me",
    response_model=UsuarioResponse,
    responses={401: {"description": "Token ausente o inválido"}},
)
def me(
    usuario: Usuario = Depends(get_usuario_actual),
    service: AuthService = Depends(get_auth_service),
):
    return service.me(usuario.id)