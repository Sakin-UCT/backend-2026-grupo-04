from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.infrastructure.models.categoria_model import CategoriaModel
from app.domain.categoria import Categoria
from app.domain.excepciones import ConflictoError
from app.infrastructure.mappers import categoria_to_domain, categoria_to_model


class CategoriaRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self) -> list[Categoria]:
        modelos = self.db.query(CategoriaModel).all()
        return [categoria_to_domain(m) for m in modelos]

    # Alias temporal por si algún service todavía llama al nombre viejo
    obtener_todas = obtener_todos

    def obtener_por_id(self, categoria_id: int) -> Categoria | None:
        modelo = self.db.query(CategoriaModel).filter(CategoriaModel.id == categoria_id).first()
        return categoria_to_domain(modelo) if modelo else None

    def guardar(self, categoria: Categoria) -> Categoria:
        modelo = categoria_to_model(categoria)
        try:
            self.db.add(modelo)
            self.db.commit()
            self.db.refresh(modelo)
            return categoria_to_domain(modelo)
        except IntegrityError:
            self.db.rollback()
            raise ConflictoError("La categoría ya existe.")