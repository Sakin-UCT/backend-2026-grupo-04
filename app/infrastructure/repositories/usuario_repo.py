from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.excepciones import ConflictoError
from app.domain.usuario import Usuario
from app.infrastructure.mappers import usuario_mapper
from app.infrastructure.models.usuario_model import UsuarioModel


class UsuarioRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def crear(self, usuario: Usuario) -> Usuario:
        modelo = usuario_mapper.a_modelo(usuario)
        modelo.id = None
        try:
            self.db.add(modelo)
            self.db.commit()
            self.db.refresh(modelo)
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictoError("Ya existe un usuario registrado con ese correo") from exc
        return usuario_mapper.a_dominio(modelo)

    def buscar_por_correo(self, correo: str) -> Usuario | None:
        stmt = select(UsuarioModel).where(UsuarioModel.correo == correo)
        modelo = self.db.scalar(stmt)
        if modelo is None:
            return None
        return usuario_mapper.a_dominio(modelo)

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        stmt = select(UsuarioModel).where(UsuarioModel.id == usuario_id)
        modelo = self.db.scalar(stmt)
        if modelo is None:
            return None
        return usuario_mapper.a_dominio(modelo)

    def actualizar(self, usuario: Usuario) -> Usuario:
        stmt = select(UsuarioModel).where(UsuarioModel.id == usuario.id)
        modelo = self.db.scalar(stmt)
        if modelo is None:
            return usuario_mapper.a_dominio(usuario_mapper.a_modelo(usuario))

        modelo.correo = usuario.correo
        modelo.password_hash = usuario.password_hash
        modelo.perfil = usuario.perfil.value if hasattr(usuario.perfil, "value") else str(usuario.perfil)
        modelo.cliente_id = usuario.cliente_id
        modelo.intentos_fallidos = usuario.intentos_fallidos
        modelo.bloqueado_hasta = usuario.bloqueado_hasta
        modelo.activo = usuario.activo

        try:
            self.db.commit()
            self.db.refresh(modelo)
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictoError("Conflicto de integridad al actualizar el usuario") from exc
        return usuario_mapper.a_dominio(modelo)