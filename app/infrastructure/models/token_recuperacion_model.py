from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from app.infrastructure.database import Base


class TokenRecuperacionModel(Base):
    __tablename__ = "tokens_recuperacion"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    expira_en = Column(DateTime(timezone=True), nullable=False)
    usado = Column(Boolean, default=False, nullable=False)
    creado_en = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )