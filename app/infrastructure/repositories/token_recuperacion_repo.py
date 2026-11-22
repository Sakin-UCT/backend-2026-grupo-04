from datetime import datetime, timezone
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.excepciones import ConflictoError
from app.domain.usuario import TokenRecuperacion
from app.infrastructure.models.token_recuperacion_model import TokenRecuperacionModel


def _a_dominio(modelo: TokenRecuperacionModel) -> TokenRecuperacion:
    return TokenRecuperacion(
        id=modelo.id,
        usuario_id=modelo.usuario_id,
        token_hash=modelo.token_hash,
        expira_en=modelo.expira_en,
        usado=modelo.usado,
        creado_en=modelo.creado_en,
    )


def _a_modelo(entidad: TokenRecuperacion) -> TokenRecuperacionModel:
    return TokenRecuperacionModel(
        id=entidad.id,
        usuario_id=entidad.usuario_id,
        token_hash=entidad.token_hash,
        expira_en=entidad.expira_en,
        usado=entidad.usado,
        creado_en=entidad.creado_en or datetime.now(timezone.utc),
    )


class TokenRecuperacionRepository:
    def __init__(self, db: Session):
        self.db = db

    def crear(self, token: TokenRecuperacion) -> TokenRecuperacion:
        modelo = _a_modelo(token)
        try:
            self.db.add(modelo)
            self.db.commit()
            self.db.refresh(modelo)
            return _a_dominio(modelo)
        except IntegrityError as err:
            self.db.rollback()
            raise ConflictoError("Token de recuperación duplicado o usuario inválido.") from err

    def marcar_usado(self, token_hash: str) -> bool:
        ahora = datetime.now(timezone.utc)
        stmt = (
            update(TokenRecuperacionModel)
            .where(
                TokenRecuperacionModel.token_hash == token_hash,
                TokenRecuperacionModel.usado.is_(False),
                TokenRecuperacionModel.expira_en > ahora,
            )
            .values(usado=True)
        )
        resultado = self.db.execute(stmt)
        self.db.commit()
        return getattr(resultado, "rowcount", 0) == 1

    def contar_recientes(self, usuario_id: int, desde: datetime) -> int:
        stmt = (
            select(func.count())
            .select_from(TokenRecuperacionModel)
            .where(
                TokenRecuperacionModel.usuario_id == usuario_id,
                TokenRecuperacionModel.creado_en >= desde,
            )
        )
        return self.db.scalar(stmt) or 0

    def invalidar_pendientes(self, usuario_id: int) -> None:
        stmt = (
            update(TokenRecuperacionModel)
            .where(
                TokenRecuperacionModel.usuario_id == usuario_id,
                TokenRecuperacionModel.usado.is_(False),
            )
            .values(usado=True)
        )
        self.db.execute(stmt)
        self.db.commit()