from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.presentation.dependencies import get_db
from app.presentation.schemas.estacion_schema import EstacionCreate, EstacionUpdate, EstacionResponse
from app.application.services.estacion_service import EstacionService
from app.infrastructure.repositories.estacion_repo import EstacionRepository
from app.infrastructure.repositories.categoria_repo import CategoriaRepository

router = APIRouter(prefix="/estaciones", tags=["Estaciones"])


def get_estacion_service(db: Session = Depends(get_db)):
    # Se arma uno nuevo por solicitud: cada una trae su propia sesión de BD
    estacion_repo = EstacionRepository(db)
    categoria_repo = CategoriaRepository(db)
    return EstacionService(estacion_repo, categoria_repo)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=EstacionResponse,
    summary="Crear una estación",
    description="Registra una estación nueva asociada a una categoría existente. "
                "Queda disponible por defecto.",
    responses={
        404: {"description": "La categoría indicada no existe"},
        422: {"description": "Datos inválidos"},
    },
)
def crear_estacion(
    datos: EstacionCreate,
    service: EstacionService = Depends(get_estacion_service),
):
    return service.crear(datos)


@router.get(
    "",
    response_model=list[EstacionResponse],
    summary="Listar estaciones",
    description="Devuelve todas las estaciones registradas.",
)
def listar_estaciones(service: EstacionService = Depends(get_estacion_service)):
    return service.listar()


@router.get(
    "/{estacion_id}",
    response_model=EstacionResponse,
    summary="Obtener una estación por ID",
    description="Devuelve los datos de una estación.",
    responses={404: {"description": "La estación no existe"}},
)
def obtener_estacion(
    estacion_id: int,
    service: EstacionService = Depends(get_estacion_service),
):
    return service.obtener(estacion_id)


@router.patch(
    "/{estacion_id}",
    response_model=EstacionResponse,
    summary="Cambiar el estado de una estación",
    description="Marca la estación como disponible, en mantención o fuera de servicio.",
    responses={
        404: {"description": "La estación no existe"},
        422: {"description": "Estado inválido"},
    },
)
def cambiar_estado_estacion(
    estacion_id: int,
    datos: EstacionUpdate,
    service: EstacionService = Depends(get_estacion_service),
):
    return service.cambiar_estado(estacion_id, datos.estado)