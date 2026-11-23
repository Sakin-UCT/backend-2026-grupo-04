from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.application.services.recuperacion_service import RecuperacionService
from app.infrastructure.correo.enviador import EnviadorCorreo
from app.infrastructure.repositories.refresh_token_repo import RefreshTokenRepository
from app.infrastructure.repositories.token_recuperacion_repo import TokenRecuperacionRepository
from app.infrastructure.repositories.usuario_repo import UsuarioRepository
from app.presentation.dependencies import get_db
from app.presentation.schemas.recuperacion_schema import (
    MensajeRecuperacionResponse,
    RestablecerPassword,
    SolicitudRecuperacion,
)

router = APIRouter(prefix="/auth", tags=["Autenticación y Recuperación"])


def get_recuperacion_service(db: Session = Depends(get_db)) -> RecuperacionService:
    return RecuperacionService(
        usuario_repo=UsuarioRepository(db),
        token_recuperacion_repo=TokenRecuperacionRepository(db),
        refresh_repo=RefreshTokenRepository(db),
        enviador=EnviadorCorreo(),
    )


@router.post(
    "/recuperar",
    response_model=MensajeRecuperacionResponse,
    status_code=status.HTTP_200_OK,
    summary="Solicitar recuperación de contraseña",
    description="Genera un token de recuperación de un solo uso y envía instrucciones al correo si existe.",
)
def solicitar_recuperacion(
    datos: SolicitudRecuperacion,
    service: RecuperacionService = Depends(get_recuperacion_service),
):
    return service.solicitar(datos.correo)


@router.post(
    "/restablecer",
    response_model=MensajeRecuperacionResponse,
    status_code=status.HTTP_200_OK,
    summary="Restablecer contraseña",
    description="Valida el token de recuperación, actualiza la contraseña y revoca sesiones activas.",
)
def restablecer_password(
    datos: RestablecerPassword,
    service: RecuperacionService = Depends(get_recuperacion_service),
):
    return service.restablecer(datos.token, datos.nueva_password)