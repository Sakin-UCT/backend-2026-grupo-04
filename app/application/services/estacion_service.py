from app.domain.estacion import Estacion, EstadoEstacion
from app.domain.excepciones import RecursoNoEncontradoError, ReglaNegocioError


class EstacionService:
    def __init__(self, estacion_repo, categoria_repo):
        self.estacion_repo = estacion_repo
        self.categoria_repo = categoria_repo

    def obtener(self, estacion_id: int):
        estacion = self.estacion_repo.obtener_por_id(estacion_id)
        if estacion is None:
            raise RecursoNoEncontradoError(
                f"No existe una estación con el ID {estacion_id}"
            )
        return estacion

    def validar_disponible(self, estacion_id: int):
        # RN2: no se reserva una estación en mantención o fuera de servicio
        estacion = self.obtener(estacion_id)
        if estacion.estado != EstadoEstacion.DISPONIBLE:
            raise ReglaNegocioError(
                f"Estación no disponible (estado: {estacion.estado.value})"
            )
        return estacion

    def crear(self, datos):
        pass  # parte para tu, kevin