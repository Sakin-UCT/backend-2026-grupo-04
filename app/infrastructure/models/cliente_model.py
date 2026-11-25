from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from app.infrastructure.database import Base


class UsuarioModel(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint(
            "perfil IN ('encargado', 'cliente')",
            name="ck_usuarios_perfil_valido",
        ),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    correo = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    perfil = Column(String(20), nullable=False)
    cliente_id = Column(
        Integer,
        ForeignKey("clientes.id"),
        nullable=True,
    )
    intentos_fallidos = Column(Integer, nullable=False, default=0, server_default="0")
    bloqueado_hasta = Column(DateTime(timezone=True), nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="true")
    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
