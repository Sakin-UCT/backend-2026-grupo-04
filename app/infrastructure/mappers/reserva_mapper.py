from app.domain.reserva import Reserva
from app.infrastructure.models.reserva_model import ReservaModel


def a_dominio(modelo: ReservaModel) -> Reserva:
    return Reserva(
        id=modelo.id,
        cliente_id=modelo.cliente_id,
        estacion_id=modelo.estacion_id,
        inicio=modelo.inicio,
        fin=modelo.fin,
        estado=modelo.estado,
    )


def a_modelo(entidad: Reserva) -> ReservaModel:
    return ReservaModel(
        id=entidad.id,
        cliente_id=entidad.cliente_id,
        estacion_id=entidad.estacion_id,
        inicio=entidad.inicio,
        fin=entidad.fin,
        estado=entidad.estado,
    )