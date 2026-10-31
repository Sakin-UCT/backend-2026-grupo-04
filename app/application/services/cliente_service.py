from datetime import datetime
from app.domain.cliente import Cliente
from app.infrastructure.repositories.cliente_repo import ClienteRepository
from app.presentation.schemas.cliente_schema import ClienteCreate, ClienteUpdate

try:
    from app.domain.excepciones import RecursoNoEncontradoError, ConflictoError
except ImportError:
    class RecursoNoEncontradoError(Exception):
        pass

    class ConflictoError(Exception):
        pass


class ClienteService:
    def __init__(self, repo: ClienteRepository):
        self.repo = repo

    def crear(self, datos: ClienteCreate) -> Cliente:
        nuevo_cliente = Cliente(
            id=None,
            nombre=datos.nombre,
            correo=datos.correo,
            telefono=datos.telefono,
            fecha_registro=datetime.now(),
        )
        try:
            return self.repo.guardar(nuevo_cliente)
        except ConflictoError:
            raise
        except Exception as e:
            if "ConflictoError" in str(e):
                raise ConflictoError(str(e).replace("ConflictoError: ", ""))
            raise

    def listar(self) -> list[Cliente]:
        return self.repo.obtener_todos()

    def obtener(self, cliente_id: int) -> Cliente:
        cliente = self.repo.obtener_por_id(cliente_id)
        if not cliente:
            raise RecursoNoEncontradoError(f"Cliente con id {cliente_id} no encontrado.")
        return cliente

    def actualizar(self, cliente_id: int, datos: ClienteUpdate) -> Cliente:
        cliente_actual = self.obtener(cliente_id)

        cliente_actualizado = Cliente(
            id=cliente_id,
            nombre=datos.nombre if datos.nombre is not None else cliente_actual.nombre,
            correo=datos.correo if datos.correo is not None else cliente_actual.correo,
            telefono=datos.telefono if datos.telefono is not None else cliente_actual.telefono,
            fecha_registro=cliente_actual.fecha_registro,
        )

        try:
            actualizado = self.repo.actualizar(cliente_actualizado)
            if not actualizado:
                raise RecursoNoEncontradoError(f"Cliente con id {cliente_id} no encontrado.")
            return actualizado
        except ConflictoError:
            raise
        except Exception as e:
            if "ConflictoError" in str(e):
                raise ConflictoError(str(e).replace("ConflictoError: ", ""))
            raise

    def eliminar(self, cliente_id: int) -> None:
        self.obtener(cliente_id)
        try:
            eliminado = self.repo.eliminar(cliente_id)
            if not eliminado:
                raise RecursoNoEncontradoError(f"Cliente con id {cliente_id} no encontrado.")
        except ConflictoError:
            raise
        except Exception as e:
            if "ConflictoError" in str(e):
                raise ConflictoError(str(e).replace("ConflictoError: ", ""))
            raise