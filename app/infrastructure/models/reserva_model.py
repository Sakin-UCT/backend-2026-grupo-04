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

