from app.domain.cliente import Cliente
from app.domain.categoria import Categoria
from app.infrastructure.models.cliente_model import ClienteModel
from app.infrastructure.models.categoria_model import CategoriaModel

from app.domain.estacion import Estacion, EstadoEstacion
from app.domain.reserva import Reserva, EstadoReserva
from app.infrastructure.models.estacion_model import EstacionModel
from app.infrastructure.models.reserva_model import ReservaModel

#_to_domain: ORM  a dominio
#_to_model: dominio a ORM

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

# Estacion (Kevin)
def estacion_to_domain(model: EstacionModel):
    return Estacion(
        id=model.id,
        codigo=model.codigo,
        ubicacion=model.ubicacion,
        categoria_id=model.categoria_id,
        estado=EstadoEstacion(model.estado),
    )
 
def estacion_to_model(estacion: Estacion):
    return EstacionModel(
        id=estacion.id,
        codigo=estacion.codigo,
        ubicacion=estacion.ubicacion,
        categoria_id=estacion.categoria_id,
        estado=EstadoEstacion(estacion.estado).value,
    )
 
# Reserva (Kevin)
def reserva_to_domain(model: ReservaModel):
    return Reserva(
        id=model.id,
        cliente_id=model.cliente_id,
        estacion_id=model.estacion_id,
        fecha=model.fecha,
        turno=model.turno,
        costo=model.costo,
        estado=EstadoReserva(model.estado),
    )
 
def reserva_to_model(reserva: Reserva):
    return ReservaModel(
        id=reserva.id,
        cliente_id=reserva.cliente_id,
        estacion_id=reserva.estacion_id,
        fecha=reserva.fecha,
        turno=reserva.turno,
        costo=reserva.costo,
        estado=EstadoReserva(reserva.estado).value,
    )
 