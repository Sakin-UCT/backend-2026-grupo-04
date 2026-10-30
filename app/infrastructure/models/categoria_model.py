from sqlalchemy import Column, Float, Integer, String
from app.infrastructure.database import Base

class CategoriaModel(Base):
    __tablename__ = "categorias_estacion"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    tarifa_hora = Column(Float, nullable=False)
    descripcion = Column(String(255), nullable=True)
    plataforma = Column(String(100), nullable=True)