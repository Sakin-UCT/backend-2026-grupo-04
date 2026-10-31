import math
from app.domain.reserva import Reserva, EstadoReserva
from app.domain.excepciones import RecursoNoEncontradoError, ReglaNegocioError, ConflictoError

class ReservaService:
    def __init__(self, reserva_repo, estacion_service, cliente_repo, categoria_repo):
        self.reserva_repo = reserva_repo
        self.estacion_service = estacion_service
        self.cliente_repo = cliente_repo
        self.categoria_repo = categoria_repo

    def calcular_costo(categoria, turno):
        hora_inicio, hora_fin = turno.split("-")
        h_inicio, m_inicio = map(int, hora_inicio.split(":"))
        h_fin, m_fin = map(int, hora_fin.split(":"))
        duracion_horas = (h_fin + m_fin / 60) - (h_inicio + m_inicio / 60)
        return categoria.tarifa_hora * duracion_horas


def crear_reserva(datos):
    estacion_service.validar_disponibilidad_reserva(datos.estacion_id)

    hay_conflicto = reserva_repositorio.existe_conflicto(datos.estacion_id, datos.fecha, datos.turno)
    if hay_conflicto:
        raise ValueError("Estacion ya reservada para este turno")

    estacion = estacion_repositorio.obtener_por_id(datos.estacion_id)
    categoria = categoria_repo.obtener_por_id(estacion.categoria_id)

    nueva_reserva = reserva_repositorio.guardar(datos)
    nueva_reserva.costo = calcular_costo(categoria, datos.turno)

    return nueva_reserva


def cambiar_estado(reserva_id, nuevo_estado):
    reserva = reserva_repositorio.obtener_por_id(reserva_id)
    if reserva is None:
        raise ValueError("Reserva inexistente")

    if nuevo_estado == "completada" and reserva.estado != "en_curso":
        raise ValueError("La reserva aun no completa el ciclo")

    return reserva_repositorio.actualizar(reserva_id, nuevo_estado)