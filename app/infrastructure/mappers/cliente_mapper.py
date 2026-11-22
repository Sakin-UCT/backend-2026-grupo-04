from app.domain.cliente import Cliente
from app.infrastructure.models.cliente_model import ClienteModel


def a_dominio(modelo: ClienteModel) -> Cliente:
    return Cliente(
        id=modelo.id,
        nombre=modelo.nombre,
        correo=modelo.correo,
        telefono=modelo.telefono,
    )


def a_modelo(entidad: Cliente) -> ClienteModel:
    return ClienteModel(
        id=entidad.id,
        nombre=entidad.nombre,
        correo=entidad.correo,
        telefono=entidad.telefono,
    )