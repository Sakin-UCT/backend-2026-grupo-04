from datetime import date
from typing import Literal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.presentation.dependencies import get_db
from app.presentation.schemas.reserva_schema import ReservaCreate, ReservaUpdate, ReservaResponse, ReservaPaginada
from app.application.services.reserva_service import ReservaService
from app.application.services.estacion_service import EstacionService
from app.infrastructure.repositories.reserva_repo import ReservaRepository
from app.infrastructure.repositories.estacion_repo import EstacionRepository
from app.infrastructure.repositories.cliente_repo import ClienteRepository
from app.infrastructure.repositories.categoria_repo import CategoriaRepository

router = APIRouter(prefix="/reservas", tags=["Reservas"])


def get_reserva_service(db: Session = Depends(get_db)):
    estacion_service = EstacionService(EstacionRepository(db), CategoriaRepository(db))
    return ReservaService(
        ReservaRepository(db),
        estacion_service,
        ClienteRepository(db),
        CategoriaRepository(db),
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ReservaResponse,
    summary="Crear una reserva",
    description="Crea una reserva confirmada para un cliente, estación, fecha y turno. "
                "El costo se calcula con la tarifa de la categoría de la estación.",
    responses={
        400: {"description": "RN2: la estación está en mantención o fuera de servicio"},
        404: {"description": "El cliente o la estación no existe"},
        409: {"description": "RN1: la estación ya está reservada en esa fecha y turno"},
        422: {"description": "Datos inválidos"},
    },
)
def crear_reserva(
    datos: ReservaCreate,
    service: ReservaService = Depends(get_reserva_service),
):
    return service.crear(datos)


@router.get(
    "",
    response_model=ReservaPaginada,
    summary="Listar reservas con filtro, orden y paginación",
    description="Filtra por fecha, ordena por el campo indicado y pagina el resultado. "
                "El total y el total de páginas se calculan sobre las reservas filtradas.",
    responses={422: {"description": "Parámetros de consulta inválidos"}},
)
def listar_reservas(
    fecha: date | None = Query(None, description="Filtra por fecha (AAAA-MM-DD)"),
    ordenar_por: Literal["fecha", "costo", "id"] = Query("fecha", description="Campo de orden"),
    direccion: Literal["asc", "desc"] = Query("asc", description="Dirección del orden"),
    pagina: int = Query(1, ge=1, description="Número de página, desde 1"),
    limite: int = Query(20, ge=1, le=100, description="Elementos por página (1 a 100)"),
    service: ReservaService = Depends(get_reserva_service),
):
    return service.listar(fecha, ordenar_por, direccion, pagina, limite)


@router.get(
    "/{reserva_id}",
    response_model=ReservaResponse,
    summary="Obtener una reserva por ID",
    description="Devuelve los datos de una reserva.",
    responses={404: {"description": "La reserva no existe"}},
)
def obtener_reserva(
    reserva_id: int,
    service: ReservaService = Depends(get_reserva_service),
):
    return service.obtener(reserva_id)


@router.patch(
    "/{reserva_id}",
    response_model=ReservaResponse,
    summary="Cambiar el estado de una reserva",
    description="Actualiza el estado de la reserva. Solo se puede completar "
                "una reserva que estaba en curso.",
    responses={
        400: {"description": "RN3: no se puede completar una reserva que no estaba en curso"},
        404: {"description": "La reserva no existe"},
        422: {"description": "Estado inválido"},
    },
)
def cambiar_estado_reserva(
    reserva_id: int,
    datos: ReservaUpdate,
    service: ReservaService = Depends(get_reserva_service),
):
    return service.cambiar_estado(reserva_id, datos.estado)


@router.delete(
    "/{reserva_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una reserva",
    description="Elimina una reserva existente.",
    responses={404: {"description": "La reserva no existe"}},
)
def eliminar_reserva(
    reserva_id: int,
    service: ReservaService = Depends(get_reserva_service),
):
    service.eliminar(reserva_id)