from typing import List, Optional
from app.domain.categoria import CategoriaEstacion

class CategoriaRepository:
    def __init__(self):
        self._categorias: list[CategoriaEstacion] = []
        self._contador_id: int = 1

    def obtener_todas(self) -> List[CategoriaEstacion]:
        return self._categorias

    def obtener_por_id(self, categoria_id: int) -> Optional[CategoriaEstacion]:
        for categoria in self._categorias:
            if categoria.id == categoria_id:
                return categoria
        return None

    def guardar(self, nombre: str, tarifa_hora: float, descripcion: Optional[str]) -> CategoriaEstacion:
        nueva_categoria = CategoriaEstacion(
            id=self._contador_id,
            nombre=nombre,
            tarifa_hora=tarifa_hora,
            descripcion=descripcion
        )
        self._categorias.append(nueva_categoria)
        self._contador_id += 1
        return nueva_categoria

categoria_repo = CategoriaRepository()