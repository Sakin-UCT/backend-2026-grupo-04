from app.domain.categoria import Categoria
from app.infrastructure.repositories.categoria_repo import CategoriaRepository
from app.presentation.schemas.categoria_schema import CategoriaCreate

try:
    from app.domain.excepciones import RecursoNoEncontradoError, ConflictoError
except ImportError:
    class RecursoNoEncontradoError(Exception):
        pass

    class ConflictoError(Exception):
        pass


class CategoriaService:
    def __init__(self, repo: CategoriaRepository):
        self.repo = repo

    def crear(self, datos: CategoriaCreate) -> Categoria:
        nueva_categoria = Categoria(
            id=None,
            nombre=datos.nombre,
            tarifa_hora=datos.tarifa_hora,
            descripcion=datos.descripcion,
            plataforma=datos.plataforma,
        )
        try:
            return self.repo.guardar(nueva_categoria)
        except ConflictoError:
            raise
        except Exception as e:
            if "ConflictoError" in str(e):
                raise ConflictoError(str(e).replace("ConflictoError: ", ""))
            raise

    def listar(self) -> list[Categoria]:
        return self.repo.obtener_todas()

    def obtener(self, categoria_id: int) -> Categoria:
        categoria = self.repo.obtener_por_id(categoria_id)
        if not categoria:
            raise RecursoNoEncontradoError(f"Categoría con id {categoria_id} no encontrada.")
        return categoria