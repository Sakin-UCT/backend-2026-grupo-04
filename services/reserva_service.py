from repositories.reserva_repo import reserva_repositorio
from services import estacion_service

def crear_reserva(datos):
    estacion_service.validar_disponibilidad_reserva(datos.estacion_id)

    hay_conflicto = reserva_repositorio.existe_conflicto(datos.estacion_id, datos.fecha, datos.turno)
    if hay_conflicto:
        raise ValueError("Estacion ya reservada para este turno")
    nueva_reserva = reserva_repositorio.guardar(datos)

    return nueva_reserva

def cambiar_estado(reserva_id, nuevo_estado):
    reserva = reserva_repositorio.obtener_por_id(reserva_id)
    if reserva is None:
        raise ValueError("Reserva inexistente")

    if nuevo_estado == "completada" and reserva.estado != "en_curso":
        raise ValueError("La reserva aun no completa el ciclo")

    return reserva_repositorio.actualizar(reserva_id, nuevo_estado)