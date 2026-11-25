from datetime import datetime, timedelta, timezone
import os
from typing import Any

from app.domain.excepciones import NoAutenticadoError, ReglaNegocioError
from app.domain.usuario import TokenRecuperacion
from app.infrastructure.security.jwt_handler import (
    crear_token_recuperacion,
    decodificar_token_recuperacion,
)
from app.infrastructure.security.password import hashear_password
from app.infrastructure.security.token_hash import hashear_refresh

MENSAJE_SOLICITUD_GENERICO = "Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña."
MENSAJE_RESTABLECER_OK = "Contraseña actualizada correctamente."


class RecuperacionService:
    def __init__(
        self,
        usuario_repo: Any,
        token_recuperacion_repo: Any,
        refresh_repo: Any,
        enviador: Any,
    ):
        self.usuario_repo = usuario_repo
        self.token_recuperacion_repo = token_recuperacion_repo
        self.refresh_repo = refresh_repo
        self.enviador = enviador

    def solicitar(self, correo: str) -> dict[str, str | None]:
        usuario = self.usuario_repo.buscar_por_correo(correo)
        token_debug: str | None = None

        if usuario is not None and usuario.activo and usuario.id is not None:
            ahora = datetime.now(timezone.utc)
            self.token_recuperacion_repo.invalidar_pendientes(usuario.id)

            token_plano = crear_token_recuperacion(usuario.id)
            token_hash = hashear_refresh(token_plano)

            entidad_token = TokenRecuperacion(
                usuario_id=usuario.id,
                token_hash=token_hash,
                expira_en=ahora + timedelta(minutes=15),
                usado=False,
                creado_en=ahora,
            )
            self.token_recuperacion_repo.crear(entidad_token)
            self.enviador.enviar_recuperacion(usuario.correo, token_plano)

            entorno = os.getenv("APP_ENV", os.getenv("ENV", "dev")).lower()
            if entorno in {"dev", "development", "test"}:
                token_debug = token_plano

        return {"mensaje": MENSAJE_SOLICITUD_GENERICO, "token_debug": token_debug}

    def restablecer(self, token: str, nueva_password: str) -> dict[str, str]:
        if len(nueva_password) < 12:
            raise ReglaNegocioError(
                "La contraseña no cumple con la política de seguridad."
            )

        try:
            payload = decodificar_token_recuperacion(token)
            usuario_id = int(payload["sub"])
        except (NoAutenticadoError, KeyError, TypeError, ValueError) as err:
            raise ReglaNegocioError(
                "El enlace de recuperación es inválido o ha expirado."
            ) from err

        token_hash = hashear_refresh(token)
        marcado = self.token_recuperacion_repo.marcar_usado(token_hash)
        if not marcado:
            raise ReglaNegocioError(
                "El enlace de recuperación es inválido o ha expirado."
            )

        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if usuario is None or not usuario.activo:
            raise ReglaNegocioError("No fue posible restablecer la contraseña.")

        usuario.password_hash = hashear_password(nueva_password)
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        self.usuario_repo.actualizar(usuario)

        self.refresh_repo.revocar_todos(usuario_id)

        return {"mensaje": MENSAJE_RESTABLECER_OK}
