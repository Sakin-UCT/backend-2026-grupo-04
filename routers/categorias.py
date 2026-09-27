# Endpoints para la gestión de categorías de estación
from fastapi import APIRouter, HTTPException, status               
from typing import List
from app.schemas.categoria_schema import CategoriaCreate, CategoriaResponse
from app.repositories.categoria_repo import categoria_repositorio

router = APIRouter(prefix="/categorias", tags=["CategoriasEstacion"])

@router.post("", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def crear_categoria(categoria_in: CategoriaCreate):
    return categoria_repositorio.guardar(categoria_in)

@router.get("", response_model=List[CategoriaResponse], status_code=status.HTTP_200_OK)
def listar_categorias():
    return categoria_repositorio.obtener_todos()

@router.get("/{categoria_id}", response_model=CategoriaResponse, status_code=status.HTTP_200_OK)
def obtener_categoria(categoria_id: int):
    categoria = categoria_repositorio.obtener_por_id(categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": f"No existe una categoría con el ID {categoria_id}",
                    "details": []
                }
            }
        )
    return categoria