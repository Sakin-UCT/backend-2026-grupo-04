from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.application.services.categoria_service import CategoriaService
from app.domain.usuario import Usuario
from app.infrastructure.repositories.categoria_repo import CategoriaRepository
from app.presentation.dependencies import get_db
from app.presentation.schemas.categoria_schema import CategoriaCreate, CategoriaResponse
from app.presentation.security.permisos import requiere_perfil

router = APIRouter(prefix="/categorias", tags=["Categorías"])


def get_categoria_service(db: Session = Depends(get_db)) -> CategoriaService:
    return CategoriaService(CategoriaRepository(db))


@router.post(
    "",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva categoría de estación",
    description="Registra una nueva categoría de estación. Requiere perfil encargado.",
    responses={
        201: {"description": "Categoría creada exitosamente"},
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso: se requiere perfil encargado"},
        409: {"description": "Conflicto: la categoría ya existe"},
        422: {"description": "Error de validación en los datos enviados"},
    },
)
def crear_categoria(
    datos: CategoriaCreate,
    service: CategoriaService = Depends(get_categoria_service),
    _usuario: Usuario = Depends(requiere_perfil("encargado")),
):
    return service.crear(datos)


@router.get(
    "",
    response_model=list[CategoriaResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todas las categorías",
    description="Obtiene el listado completo de categorías de estación registradas.",
)
def listar_categorias(
    service: CategoriaService = Depends(get_categoria_service),
):
    return service.listar()


@router.get(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener una categoría por ID",
    description="Devuelve el detalle de una categoría específica según su identificador único.",
)
def obtener_categoria(
    categoria_id: int,
    service: CategoriaService = Depends(get_categoria_service),
):
    return service.obtener(categoria_id)
