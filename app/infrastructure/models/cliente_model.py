from sqlalchemy import Column, DateTime, Integer, String, func
from app.infrastructure.database import Base

class ClienteModel(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(150), unique=True, index=True, nullable=False)
    telefono = Column(String(50), nullable=True)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)