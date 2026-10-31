from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.application.services.cliente_service import ClienteService
from app.infrastructure.repositories.cliente_repo import ClienteRepository
from app.presentation.dependencies import get_db
from app.presentation.schemas.cliente_schema import (
    ClienteCreate,
    ClienteResponse,
    ClienteUpdate,
)

router = APIRouter(prefix="/clientes", tags=["Clientes"])


def get_cliente_service(db: Session = Depends(get_db)) -> ClienteService:
    return ClienteService(ClienteRepository(db))


@router.post(
    "",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo cliente",
    description="Crea un nuevo cliente en el sistema validando que su correo electrónico sea único.",
    responses={
        201: {"description": "Cliente creado exitosamente"},
        409: {"description": "Conflicto: el correo electrónico ya está registrado"},
        422: {"description": "Error de validación en los datos enviados"},
    },
)
def crear_cliente(
    datos: ClienteCreate,
    service: ClienteService = Depends(get_cliente_service),
):
    return service.crear(datos)


@router.get(
    "",
    response_model=list[ClienteResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los clientes",
    description="Obtiene la lista completa de clientes registrados en el centro gamer.",
    responses={
        200: {"description": "Lista de clientes obtenida exitosamente"},
    },
)
def listar_clientes(
    service: ClienteService = Depends(get_cliente_service),
):
    return service.listar()


@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un cliente por ID",
    description="Busca y devuelve los datos de un cliente específico por su ID.",
    responses={
        200: {"description": "Cliente encontrado"},
        404: {"description": "Cliente no encontrado"},
    },
)
def obtener_cliente(
    cliente_id: int,
    service: ClienteService = Depends(get_cliente_service),
):
    return service.obtener(cliente_id)


@router.put(
    "/{cliente_id}",
    response_model=ClienteResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar datos de un cliente",
    description="Actualiza parcial o totalmente los datos (nombre, correo, teléfono) de un cliente existente.",
    responses={
        200: {"description": "Cliente actualizado exitosamente"},
        404: {"description": "Cliente no encontrado"},
        409: {"description": "Conflicto: el nuevo correo ya pertenece a otro cliente"},
        422: {"description": "Error de validación en los datos enviados"},
    },
)
def actualizar_cliente(
    cliente_id: int,
    datos: ClienteUpdate,
    service: ClienteService = Depends(get_cliente_service),
):
    return service.actualizar(cliente_id, datos)


@router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un cliente",
    description="Elimina un cliente del sistema si no posee reservas asociadas.",
    responses={
        204: {"description": "Cliente eliminado exitosamente (sin contenido)"},
        404: {"description": "Cliente no encontrado"},
        409: {"description": "Conflicto: no se puede eliminar un cliente con reservas asociadas"},
    },
)
def eliminar_cliente(
    cliente_id: int,
    service: ClienteService = Depends(get_cliente_service),
):
    service.eliminar(cliente_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)