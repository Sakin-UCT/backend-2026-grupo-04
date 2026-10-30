from app.domain.cliente import Cliente
from app.domain.categoria import Categoria
from app.infrastructure.models.cliente_model import ClienteModel
from app.infrastructure.models.categoria_model import CategoriaModel

from app.domain.estacion import Estacion, EstadoEstacion
from app.domain.reserva import Reserva, EstadoReserva
from app.infrastructure.models.estacion_model import EstacionModel
from app.infrastructure.models.reserva_model import ReservaModel

def cliente_to_domain(model: ClienteModel) -> Cliente:
    if not model:
        return None
    return Cliente(
        id=model.id,
        nombre=model.nombre,
        correo=model.correo,
        telefono=model.telefono,
        fecha_registro=model.fecha_registro
    )

def cliente_to_model(entity: Cliente) -> ClienteModel:
    return ClienteModel(
        id=entity.id,
        nombre=entity.nombre,
        correo=entity.correo,
        telefono=entity.telefono,
        fecha_registro=entity.fecha_registro
    )

def categoria_to_domain(model: CategoriaModel) -> Categoria:
    if not model:
        return None
    return Categoria(
        id=model.id,
        nombre=model.nombre,
        tarifa_hora=model.tarifa_hora,
        descripcion=model.descripcion,
        plataforma=model.plataforma
    )

def categoria_to_model(entity: Categoria) -> CategoriaModel:
    return CategoriaModel(
        id=entity.id,
        nombre=entity.nombre,
        tarifa_hora=entity.tarifa_hora,
        descripcion=entity.descripcion,
        plataforma=entity.plataforma
    )