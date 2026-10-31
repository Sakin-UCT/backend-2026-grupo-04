from sqlalchemy import Column, Date, Float, ForeignKey, Index, Integer, String, text
from app.infrastructure.database import Base

class ReservaModel(Base):

    __tablename__ = "reservas"
    __table_args__ = (

        Index(
            "uq_reservas_activa_estacion_fecha_turno",
            "estacion_id",
            "fecha",
            "turno",
            unique=True,
            postgresql_where=text("estado IN ('confirmada', 'en_curso')"),
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    estacion_id = Column(Integer, ForeignKey("estaciones.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    turno = Column(String(11), nullable=False)  # "10:00-11:00"
    estado = Column(String(20), nullable=False, default="confirmada", server_default="confirmada")
    costo = Column(Float, nullable=False)