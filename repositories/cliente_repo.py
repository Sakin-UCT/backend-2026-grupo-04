from typing import List, Optional
from datetime import datetime
from app.domain.cliente import Cliente

class ClienteRepository:
    def __init__(self):
        self._clientes: list[Cliente] = []
        self._contador_id: int = 1

    def obtener_todos(self) -> List[Cliente]:
        return self._clientes

    def obtener_por_id(self, cliente_id: int) -> Optional[Cliente]:
        for cliente in self._clientes:
            if cliente.id == cliente_id:
                return cliente
        return None

    def guardar(self, nombre: str, correo: str) -> Cliente:
        nuevo_cliente = Cliente(
            id=self._contador_id,
            nombre=nombre,
            correo=correo,
            fecha_registro=datetime.now()
        )
        self._clientes.append(nuevo_cliente)
        self._contador_id += 1
        return nuevo_cliente


cliente_repo = ClienteRepository()