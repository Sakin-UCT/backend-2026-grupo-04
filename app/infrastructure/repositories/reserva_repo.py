from datetime import date

from sqlalchemy import exists, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.excepciones import ConflictoError
from app.domain.reserva import EstadoReserva, Reserva
from app.infrastructure.mappers import reserva_to_domain, reserva_to_model
from app.infrastructure.models.reserva_model import ReservaModel

COLUMNAS_ORDENABLES = {
    "fecha": ReservaModel.fecha,
    "costo": ReservaModel.costo,
    "id": ReservaModel.id,
}
DIRECCIONES = ("asc", "desc")


class ReservaRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self):
        modelos = self.db.scalars(select(ReservaModel).order_by(ReservaModel.id)).all()
        return [reserva_to_domain(m) for m in modelos]

    def obtener_por_id(self, reserva_id: int):
        modelo = self.db.get(ReservaModel, reserva_id)
        return reserva_to_domain(modelo) if modelo is not None else None

    def guardar(self, reserva: Reserva):
        modelo = reserva_to_model(reserva)
        self.db.add(modelo)
        self._confirmar()
        self.db.refresh(modelo)
        return reserva_to_domain(modelo)

    def actualizar(self, reserva: Reserva):
        if reserva.id is None:
            return None
        modelo = self.db.get(ReservaModel, reserva.id)
        if modelo is None:
            return None
        modelo.cliente_id = reserva.cliente_id
        modelo.estacion_id = reserva.estacion_id
        modelo.fecha = reserva.fecha
        modelo.turno = reserva.turno
        modelo.costo = reserva.costo
        modelo.estado = EstadoReserva(reserva.estado).value
        self._confirmar()
        self.db.refresh(modelo)
        return reserva_to_domain(modelo)

    def eliminar(self, reserva_id: int):
        modelo = self.db.get(ReservaModel, reserva_id)
        if modelo is None:
            return False
        self.db.delete(modelo)
        self._confirmar()
        return True

    def existe_conflicto(self, estacion_id: int, fecha: date, turno: str):
        activos = (EstadoReserva.CONFIRMADA.value, EstadoReserva.EN_CURSO.value)
        consulta = select(
            exists().where(
                ReservaModel.estacion_id == estacion_id,
                ReservaModel.fecha == fecha,
                ReservaModel.turno == turno,
                ReservaModel.estado.in_(activos),
            )
        )
        return bool(self.db.scalar(consulta))

    def listar_filtrado(
        self,
        fecha: date | None = None,
        ordenar_por: str | None = None,
        direccion: str = "asc",
        pagina: int = 1,
        limite: int = 20,
    ) -> tuple[list[Reserva], int]:
        columna = COLUMNAS_ORDENABLES.get(ordenar_por or "id")
        if columna is None:
            raise ValueError(f"ordenar_por debe ser uno de {sorted(COLUMNAS_ORDENABLES)}")
        if direccion not in DIRECCIONES:
            raise ValueError("direccion debe ser 'asc' o 'desc'")
        if pagina < 1 or limite < 1:
            raise ValueError("pagina y limite deben ser mayores o iguales a 1")

        filtros = []
        if fecha is not None:
            filtros.append(ReservaModel.fecha == fecha)

        total = self.db.scalar(
            select(func.count()).select_from(ReservaModel).where(*filtros)
        ) or 0

        orden = [columna.desc() if direccion == "desc" else columna.asc()]
        if columna is not ReservaModel.id:
            orden.append(ReservaModel.id.asc())

        consulta = (
            select(ReservaModel)
            .where(*filtros)
            .order_by(*orden)
            .offset((pagina - 1) * limite)
            .limit(limite)
        )
        modelos = self.db.scalars(consulta).all()
        return [reserva_to_domain(m) for m in modelos], total

    def _confirmar(self):
        try:
            self.db.commit()
        except IntegrityError as error:
            self.db.rollback()
            raise ConflictoError(
                "No se pudo guardar la reserva: el turno ya está reservado o el cliente o la estación no existen"
            ) from error
        except SQLAlchemyError:
            self.db.rollback()
            raise