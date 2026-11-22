from app.domain.estacion import Estacion
from app.infrastructure.models.estacion_model import EstacionModel


def a_dominio(modelo: EstacionModel) -> Estacion:
    return Estacion(
        id=modelo.id,
        nombre=modelo.nombre,
        categoria_id=modelo.categoria_id,
        estado=modelo.estado,
        precio_hora=modelo.precio_hora,
    )


def a_modelo(entidad: Estacion) -> EstacionModel:
    return EstacionModel(
        id=entidad.id,
        nombre=entidad.nombre,
        categoria_id=entidad.categoria_id,
        estado=entidad.estado,
        precio_hora=entidad.precio_hora,
    )