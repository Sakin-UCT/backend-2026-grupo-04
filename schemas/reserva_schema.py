from datetime import date
from pydantic import BaseModel
from domain.reserva import EstadoReserva

class ReservaCreate(BaseModel):
    #lo que se manda para crear una reserva nueva
    cliente_id: int
    estacion_id: int
    fecha: date
    turno: str

class ReservaUpdate(BaseModel):
    #lo que se manda para cambiar el estado de una reserva
    estado: EstadoReserva