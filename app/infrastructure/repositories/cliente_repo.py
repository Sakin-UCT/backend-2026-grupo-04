from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.infrastructure.models.cliente_model import ClienteModel
from app.domain.cliente import Cliente
from app.infrastructure.mappers import cliente_to_domain, cliente_to_model

class ClienteRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self) -> list[Cliente]:
        modelos = self.db.query(ClienteModel).all()
        return [cliente_to_domain(m) for m in modelos]

    def obtener_por_id(self, cliente_id: int) -> Cliente | None:
        modelo = self.db.query(ClienteModel).filter(ClienteModel.id == cliente_id).first()
        return cliente_to_domain(modelo) if modelo else None

    def guardar(self, cliente: Cliente) -> Cliente:
        modelo = cliente_to_model(cliente)
        try:
            self.db.add(modelo)
            self.db.commit()
            self.db.refresh(modelo)
            return cliente_to_domain(modelo)
        except IntegrityError:
            self.db.rollback()
            raise Exception("ConflictoError: El correo ya está registrado o hay un error de integridad.")

    def actualizar(self, cliente: Cliente) -> Cliente:
        modelo = self.db.query(ClienteModel).filter(ClienteModel.id == cliente.id).first()
        if not modelo:
            return None
        
        modelo.nombre = cliente.nombre
        modelo.correo = cliente.correo
        modelo.telefono = cliente.telefono
        
        try:
            self.db.commit()
            self.db.refresh(modelo)
            return cliente_to_domain(modelo)
        except IntegrityError:
            self.db.rollback()
            raise Exception("ConflictoError: Error al actualizar.")

    def eliminar(self, cliente_id: int) -> bool:
        modelo = self.db.query(ClienteModel).filter(ClienteModel.id == cliente_id).first()
        if not modelo:
            return False
        try:
            self.db.delete(modelo)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise Exception("ConflictoError: No se puede eliminar el cliente porque tiene reservas asociadas.")