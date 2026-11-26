from app.domain.categoria import Categoria
from app.infrastructure.models.categoria_model import CategoriaModel


def a_dominio(modelo: CategoriaModel) -> Categoria:
    return Categoria(
        id=modelo.id,
        nombre=modelo.nombre,
        tarifa_hora=modelo.tarifa_hora,
        descripcion=modelo.descripcion,
        plataforma=modelo.plataforma,
    )


def a_modelo(entidad: Categoria) -> CategoriaModel:
    return CategoriaModel(
        id=entidad.id,
        nombre=entidad.nombre,
        tarifa_hora=entidad.tarifa_hora,
        descripcion=entidad.descripcion,
        plataforma=entidad.plataforma,
    )
