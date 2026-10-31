from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.estacion import Estacion, EstadoEstacion
from app.domain.excepciones import ConflictoError
from app.infrastructure.mappers import estacion_to_domain, estacion_to_model
from app.infrastructure.models.estacion_model import EstacionModel


class EstacionRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self):
        modelos = self.db.scalars(
            select(EstacionModel).order_by(EstacionModel.id)).all()
        return [estacion_to_domain(m) for m in modelos]

    def obtener_por_id(self, estacion_id: int):
        modelo = self.db.get(EstacionModel, estacion_id)
        return estacion_to_domain(modelo) if modelo is not None else None

    def obtener_por_codigo(self, codigo: str):
        modelo = self.db.scalars(
            select(EstacionModel).where(EstacionModel.codigo == codigo)
        ).first()
        return estacion_to_domain(modelo) if modelo is not None else None

    def guardar(self, estacion: Estacion):
        modelo = estacion_to_model(estacion)
        self.db.add(modelo)
        self._confirmar()
        self.db.refresh(modelo)
        return estacion_to_domain(modelo)

    def actualizar(self, estacion: Estacion):
        if estacion.id is None:
            return None
        modelo = self.db.get(EstacionModel, estacion.id)
        if modelo is None:
            return None
        modelo.codigo = estacion.codigo
        modelo.ubicacion = estacion.ubicacion
        modelo.categoria_id = estacion.categoria_id
        modelo.estado = EstadoEstacion(estacion.estado).value
        self._confirmar()
        self.db.refresh(modelo)
        return estacion_to_domain(modelo)

    def _confirmar(self):
        try:
            self.db.commit()
        except IntegrityError as error:
            self.db.rollback()
            raise ConflictoError(
                "No se pudo guardar la estación: el código ya existe o la categoría no existe"
            ) from error
        except SQLAlchemyError:
            self.db.rollback()
            raise