from collections.abc import Callable
from fastapi import Depends

from app.domain.excepciones import SinPermisoError
from app.domain.usuario import Perfil, Usuario
from app.presentation.security.usuario_actual import get_usuario_actual


def requiere_perfil(*perfiles: str | Perfil) -> Callable[[Usuario], Usuario]:
    perfiles_permitidos = {
        p.value if isinstance(p, Perfil) else str(p) for p in perfiles
    }

    def _validador(usuario: Usuario = Depends(get_usuario_actual)) -> Usuario:
        perfil_usuario = (
            usuario.perfil.value
            if isinstance(usuario.perfil, Perfil)
            else str(usuario.perfil)
        )
        if perfil_usuario not in perfiles_permitidos:
            raise SinPermisoError(
                "No tienes permisos suficientes para realizar esta operación."
            )
        return usuario

    return _validador
