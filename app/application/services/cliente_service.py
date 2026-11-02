from datetime import datetime
from app.domain.cliente import Cliente
from app.domain.excepciones import RecursoNoEncontradoError


class ClienteService:
    def __init__(self, repo):
        self.repo = repo

    def crear(self, datos) -> Cliente:
        nuevo_cliente = Cliente(
            id=None,
            nombre=datos.nombre,
            correo=datos.correo,
            telefono=datos.telefono,
            fecha_registro=datetime.now(),
        )
        return self.repo.guardar(nuevo_cliente)

    def listar(self) -> list[Cliente]:
        return self.repo.obtener_todos()

    def obtener(self, cliente_id: int) -> Cliente:
        cliente = self.repo.obtener_por_id(cliente_id)
        if cliente is None:
            raise RecursoNoEncontradoError(f"No existe un cliente con el ID {cliente_id}")
        return cliente

    def actualizar(self, cliente_id: int, datos) -> Cliente:
        actual = self.obtener(cliente_id)

        cliente_actualizado = Cliente(
            id=cliente_id,
            nombre=datos.nombre if datos.nombre is not None else actual.nombre,
            correo=datos.correo if datos.correo is not None else actual.correo,
            telefono=datos.telefono if datos.telefono is not None else actual.telefono,
            fecha_registro=actual.fecha_registro,
        )

        resultado = self.repo.actualizar(cliente_actualizado)
        if resultado is None:
            raise RecursoNoEncontradoError(f"No existe un cliente con el ID {cliente_id}")
        return resultado

    def eliminar(self, cliente_id: int) -> None:
        self.obtener(cliente_id)
        self.repo.eliminar(cliente_id)