from sqlalchemy import Column, ForeignKey, Integer, String
from app.infrastructure.database import Base

class EstacionModel(Base):

    __tablename__ = "estaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), unique=True, nullable=False)
    ubicacion = Column(String(100), nullable=False)
    estado = Column(String(20), nullable=False, default="disponible", server_default="disponible")
    categoria_id = Column(Integer, ForeignKey("categorias_estacion.id"), nullable=False)