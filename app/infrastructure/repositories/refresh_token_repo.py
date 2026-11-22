from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.excepciones import ConflictoError
from app.domain.usuario import RefreshToken
from app.infrastructure.mappers import usuario_mapper
from app.infrastructure.models.refresh_token_model import RefreshTokenModel


class RefreshTokenRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def crear(self, token: RefreshToken) -> RefreshToken:
        modelo = usuario_mapper.refresh_token_a_modelo(token)
        modelo.id = None
        try:
            self.db.add(modelo)
            self.db.commit()
            self.db.refresh(modelo)
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictoError("No se pudo registrar la sesión") from exc
        return usuario_mapper.refresh_token_a_dominio(modelo)

    def buscar_por_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        modelo = self.db.scalar(stmt)
        if modelo is None:
            return None
        return usuario_mapper.refresh_token_a_dominio(modelo)

    def revocar(self, token_id: int, reemplazado_por: int | None = None) -> None:
        stmt = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.id == token_id)
            .values(revocado=True, reemplazado_por=reemplazado_por)
        )
        try:
            self.db.execute(stmt)
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictoError("No se pudo revocar la sesión") from exc

    def revocar_todos(self, usuario_id: int) -> None:
        stmt = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.usuario_id == usuario_id)
            .where(RefreshTokenModel.revocado.is_(False))
            .values(revocado=True)
        )
        try:
            self.db.execute(stmt)
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictoError("No se pudieron revocar las sesiones") from exc