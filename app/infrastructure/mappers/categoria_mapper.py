from app.domain.categoria import Categoria
from app.infrastructure.models.categoria_model import CategoriaModel


def a_dominio(modelo: CategoriaModel) -> Categoria:
    return Categoria(
        id=modelo.id,
        nombre=modelo.nombre,
        descripcion=modelo.descripcion,
    )


def a_modelo(entidad: Categoria) -> CategoriaModel:
    return CategoriaModel(
        id=entidad.id,
        nombre=entidad.nombre,
        descripcion=entidad.descripcion,
    )