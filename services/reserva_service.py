from repositories import reserva_repo
from services import estacion_service

def crear_reserva(cliente_id, estacion_id, fecha, turno):
    estacion_service.validar_disponibilidad_reserva(estacion_id)

    hay_conflicto = reserva_repo.existe_conflicto(estacion_id, fecha, turno)
    if hay_conflicto:
        raise ValueError("Estacion ya reservada para este turno")
    nueva_reserva = reserva_repo.crear(cliente_id, estacion_id, fecha, turno)

    return nueva_reserva

def cambiar_estado(reserva_id, nuevo_estado):
    reserva = reserva_repo.obtener(reserva_id)
    if reserva is None:
        raise ValueError("Reserva inexistente")
    
    if nuevo_estado == "completada" and reserva.estado != "en_curso":
        raise ValueError("La reserva aun no completa el ciclo")

    return reserva_repo.actualizar_estado(reserva_id, nuevo_estado)