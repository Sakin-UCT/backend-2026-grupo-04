from app.domain.categoria import Categoria
from app.domain.excepciones import RecursoNoEncontradoError, ConflictoError


class CategoriaService:
    def __init__(self, repo):
        self.repo = repo

    def crear(self, datos) -> Categoria:
        nueva_categoria = Categoria(
            id=None,
            nombre=datos.nombre,
            tarifa_hora=datos.tarifa_hora,
            descripcion=datos.descripcion,
            plataforma=datos.plataforma,
        )
        return self.repo.guardar(nueva_categoria)

    def listar(self) -> list[Categoria]:
        return self.repo.obtener_todos()

    def obtener(self, categoria_id: int) -> Categoria:
        categoria = self.repo.obtener_por_id(categoria_id)
        if categoria is None:
            raise RecursoNoEncontradoError(f"No existe una categoría con el ID {categoria_id}")
        return categoria