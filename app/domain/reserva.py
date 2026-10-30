from dataclasses import dataclass
from datetime import date
from enum import Enum

class EstadoReserva(str, Enum):
    CONFIRMADA = "confirmada"
    EN_CURSO = "en_curso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"
    NO_SHOW = "no_show"

@dataclass(kw_only=True)
class Reserva:
#tarifa_horas x horas

    id: int | None = None
    cliente_id: int
    estacion_id: int
    fecha: date
    turno: str
    costo: float
    estado: EstadoReserva = EstadoReserva.CONFIRMADA