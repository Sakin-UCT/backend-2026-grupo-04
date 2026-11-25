import hmac
import secrets
from fastapi import Request
from app.domain.excepciones import SinPermisoError


def generar_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def verificar_csrf(request: Request) -> None:
    cookie_token = request.cookies.get("csrf_token")
    header_token = request.headers.get("X-CSRF-Token")

    if not cookie_token or not header_token:
        raise SinPermisoError("Falta el token CSRF en la cookie o en el encabezado.")

    if not hmac.compare_digest(cookie_token, header_token):
        raise SinPermisoError("El token CSRF no coincide.")
