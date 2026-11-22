from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.domain.excepciones import NoAutenticadoError
from app.domain.usuario import Usuario
from app.infrastructure.repositories.usuario_repo import UsuarioRepository
from app.infrastructure.security.jwt_handler import decodificar_access_token
from app.presentation.dependencies import get_db

bearer_scheme = HTTPBearer(auto_error=False)


def get_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    if credenciales is None or not credenciales.credentials:
        raise NoAutenticadoError("Token de autenticación no proporcionado.")

    payload = decodificar_access_token(credenciales.credentials)
    sub = payload.get("sub")
    if sub is None:
        raise NoAutenticadoError("Token inválido.")

    try:
        usuario_id = int(sub)
    except (TypeError, ValueError) as err:
        raise NoAutenticadoError("Identificador de usuario inválido en el token.") from err

    repo = UsuarioRepository(db)
    usuario = repo.buscar_por_id(usuario_id)

    if usuario is None or not usuario.activo:
        raise NoAutenticadoError("Usuario no encontrado o inactivo.")

    return usuario