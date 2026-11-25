import hashlib
import secrets


def generar_refresh_token():
    return secrets.token_urlsafe(32)


def hashear_refresh(token: str):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
