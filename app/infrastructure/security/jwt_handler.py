import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.domain.excepciones import NoAutenticadoError

ALGORITMO = "HS256"
ACCESS_MINUTOS = 15
RECUPERACION_MINUTOS = 15
MENSAJE_ERROR = "Credenciales inválidas o sesión expirada."


def _secreto():
    secreto = os.getenv("JWT_SECRET")
    if not secreto:
        raise ValueError("La variable de entorno JWT_SECRET no está configurada.")
    return secreto


def _crear(claims: dict, tipo: str, minutos: int):
    ahora = datetime.now(timezone.utc)
    payload = {
        **claims,
        "type": tipo,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=minutos),
    }
    return jwt.encode(payload, _secreto(), algorithm=ALGORITMO)


def _decodificar(token: str, tipo: str):
    try:
        datos = jwt.decode(
            token,
            _secreto(),
            algorithms=[ALGORITMO],
            options={"require": ["sub", "exp"]},
        )
    except jwt.PyJWTError:
        raise NoAutenticadoError(MENSAJE_ERROR) from None
    if datos.get("type") != tipo:
        raise NoAutenticadoError(MENSAJE_ERROR)
    return datos


def crear_access_token(usuario_id: int, perfil: str):
    return _crear({"sub": str(usuario_id), "perfil": perfil}, "access", ACCESS_MINUTOS)


def decodificar_access_token(token: str):
    return _decodificar(token, "access")


def crear_token_recuperacion(usuario_id: int):
    return _crear(
        {"sub": str(usuario_id), "jti": str(uuid.uuid4())},
        "recuperacion",
        RECUPERACION_MINUTOS,
    )


def decodificar_token_recuperacion(token: str):
    return _decodificar(token, "recuperacion")