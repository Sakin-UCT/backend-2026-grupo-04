from datetime import date
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.domain.reserva import EstadoReserva

EJEMPLO_RESERVA = {
    "id": 1,
    "cliente_id": 1,
    "estacion_id": 1,
    "fecha": "2026-11-05",
    "turno": "10:00-11:00",
    "estado": "confirmada",
    "costo": 2500.0,
}


class ReservaCreate(BaseModel):

    cliente_id: int = Field(gt=0)
    estacion_id: int = Field(gt=0)
    fecha: date
    turno: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d-([01]\d|2[0-3]):[0-5]\d$")
    #formato HH:MM-HH:MM con horas 00-23 y minutos 00-59

    @field_validator("turno")
    @classmethod
    def fin_despues_de_inicio(cls, turno: str):
        inicio, fin = turno.split("-")
        if fin <= inicio:
            raise ValueError("La hora de fin debe ser posterior a la de inicio")
        return turno

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"cliente_id": 1, "estacion_id": 1, "fecha": "2026-11-05", "turno": "10:00-11:00"}
            ]}
    )


class ReservaUpdate(BaseModel):
    
    estado: EstadoReserva
    model_config = ConfigDict(json_schema_extra={"examples": [{"estado": "en_curso"}]})

class ReservaResponse(BaseModel):

    id: int
    cliente_id: int
    estacion_id: int
    fecha: date
    turno: str
    estado: EstadoReserva
    costo: float

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [EJEMPLO_RESERVA]})


class ReservaPaginada(BaseModel):
#respuesta de GET /reservas

    items: list[ReservaResponse]
    total: int
    pagina: int
    limite: int
    total_paginas: int

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [EJEMPLO_RESERVA],
                    "total": 1,
                    "pagina": 1,
                    "limite": 20,
                    "total_paginas": 1,
                }]
        }
    )