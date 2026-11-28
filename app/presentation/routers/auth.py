import os
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session
from app.application.services.auth_service import DIAS_REFRESH, AuthService, Seguridad, Sesion
from app.domain.excepciones import NoAutenticadoError
from app.domain.usuario import Usuario
from app.infrastructure.repositories.refresh_token_repo import RefreshTokenRepository
from app.infrastructure.repositories.usuario_repo import UsuarioRepository
from app.infrastructure.security.jwt_handler import crear_access_token
from app.infrastructure.security.password import hashear_password, verificar_password
from app.infrastructure.security.token_hash import generar_refresh_token, hashear_refresh
from app.presentation.dependencies import get_db
from app.presentation.schemas.auth_schemas import LoginRequest, RegistroRequest, TokenResponse, UsuarioResponse
from app.presentation.security.csrf import generar_csrf_token,verificar_csrf
from app.presentation.security.usuario_actual import get_usuario_actual

router = APIRouter(prefix="/auth", tags=["Autenticación"])

COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"
COOKIE_PATH = "/auth"
COOKIE_MAX_AGE = DIAS_REFRESH * 24 * 60 * 60


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    seguridad = Seguridad(
        hashear_password=hashear_password,
        verificar_password=verificar_password,
        crear_access_token=crear_access_token,
        generar_refresh_token=generar_refresh_token,
        hashear_refresh=hashear_refresh,
    )

    return AuthService(
        usuario_repo=UsuarioRepository(db),
        refresh_repo=RefreshTokenRepository(db),
        seguridad=seguridad,
    )


def establecer_cookies(response: Response, sesion: Sesion) -> None:
    response.set_cookie(
        key="refresh_token",
        value=sesion.refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path=COOKIE_PATH,
        max_age=COOKIE_MAX_AGE,
    )

    response.set_cookie(
        key="csrf_token",
        value=generar_csrf_token(),
        httponly=False,
        secure=COOKIE_SECURE,
        samesite="lax",
        path=COOKIE_PATH,
        max_age=COOKIE_MAX_AGE,
    )


def eliminar_cookies(response: Response) -> None:
    response.delete_cookie(
        key="refresh_token",
        path=COOKIE_PATH,
        secure=COOKIE_SECURE,
        httponly=True,
        samesite="lax",
    )

    response.delete_cookie(
        key="csrf_token",
        path=COOKIE_PATH,
        secure=COOKIE_SECURE,
        httponly=False,
        samesite="lax",
    )


@router.post(
    "/registro",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Correo ya registrado"}},
)
def registrar(
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

    establecer_cookies(response, sesion)

    return TokenResponse(access_token=sesion.access_token)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    dependencies=[Depends(verificar_csrf)],
    responses={
        401: {"description": "Sesión inválida o expirada"},
        403: {"description": "Token CSRF inválido"},
    },
)
def refresh(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise NoAutenticadoError("Credenciales inválidas")
    sesion = service.refrescar(refresh_token)
    establecer_cookies(response, sesion)
    return TokenResponse(access_token=sesion.access_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verificar_csrf)],
    responses={403: {"description": "Token CSRF inválido"}},
)
def logout(
    request: Request,
    service: AuthService = Depends(get_auth_service),
):
    refresh_token = request.cookies.get("refresh_token")

    service.logout(refresh_token)

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    eliminar_cookies(response)

    return response


@router.get(
    "/me",
    response_model=UsuarioResponse,
    responses={401: {"description": "Usuario no autenticado"}},
)
def me(
    usuario: Usuario = Depends(get_usuario_actual),
    service: AuthService = Depends(get_auth_service),
):
    return service.me(usuario.id)