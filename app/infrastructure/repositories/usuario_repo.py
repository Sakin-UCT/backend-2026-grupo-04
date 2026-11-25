from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.excepciones import ConflictoError
from app.domain.usuario import Usuario
from app.infrastructure.mappers.usuario_mapper import a_dominio, a_modelo
from app.infrastructure.models.usuario_model import UsuarioModel


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def crear(self, usuario: Usuario) -> Usuario:
        modelo = a_modelo(usuario)
        try:
            self.db.add(modelo)
            self.db.commit()
            self.db.refresh(modelo)
            return a_dominio(modelo)
        except IntegrityError:
            self.db.rollback()
            raise ConflictoError("El correo ya está registrado.")

    def buscar_por_correo(self, correo: str) -> Usuario | None:
        modelo = self.db.query(UsuarioModel).filter(UsuarioModel.correo == correo).first()
        return a_dominio(modelo) if modelo else None

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        modelo = self.db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
        return a_dominio(modelo) if modelo else None

    def actualizar(self, usuario: Usuario) -> Usuario | None:
        modelo = self.db.query(UsuarioModel).filter(UsuarioModel.id == usuario.id).first()
        if not modelo:
            return None

        modelo.correo = usuario.correo
        modelo.password_hash = usuario.password_hash
        modelo.perfil = usuario.perfil.value if hasattr(usuario.perfil, "value") else usuario.perfil
        modelo.cliente_id = usuario.cliente_id
        modelo.intentos_fallidos = usuario.intentos_fallidos
        modelo.bloqueado_hasta = usuario.bloqueado_hasta
        modelo.activo = usuario.activo

        try:
            self.db.commit()
            self.db.refresh(modelo)
            return a_dominio(modelo)
        except IntegrityError:
            self.db.rollback()
            raise ConflictoError("Conflicto de integridad al actualizar el usuario.")
