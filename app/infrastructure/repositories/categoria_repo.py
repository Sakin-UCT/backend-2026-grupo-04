from typing import List, Optional
from domain.categoria import CategoriaEstacion  # Import corregido sin 'app.'

class CategoriaRepository:
    def __init__(self):
        self._categorias: list[CategoriaEstacion] = []
        self._contador_id: int = 1

    def obtener_todos(self) -> List[CategoriaEstacion]:
        return self._categorias

    def obtener_por_id(self, categoria_id: int) -> Optional[CategoriaEstacion]:
        for categoria in self._categorias:
            if categoria.id == categoria_id:
                return categoria
        return None

    def guardar(self, datos) -> CategoriaEstacion:
        nueva_categoria = CategoriaEstacion(
            id=self._contador_id,
            nombre=datos.nombre,
            tarifa_hora=datos.tarifa_hora,
            descripcion=datos.descripcion
        )
        self._categorias.append(nueva_categoria)
        self._contador_id += 1
        return nueva_categoria

    def actualizar(self, categoria_id: int, datos) -> Optional[CategoriaEstacion]:
        categoria = self.obtener_por_id(categoria_id)
        if not categoria:
            return None
            
        if hasattr(datos, "nombre") and datos.nombre is not None:
            categoria.nombre = datos.nombre
        if hasattr(datos, "tarifa_hora") and datos.tarifa_hora is not None:
            categoria.tarifa_hora = datos.tarifa_hora
        if hasattr(datos, "descripcion") and datos.descripcion is not None:
            categoria.descripcion = datos.descripcion
            
        return categoria

    def eliminar(self, categoria_id: int) -> bool:
        categoria = self.obtener_por_id(categoria_id)
        if categoria:
            self._categorias.remove(categoria)
            return True
        return False

categoria_repo = CategoriaRepository()