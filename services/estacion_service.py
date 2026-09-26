from repositories import estacion_repo

def validar_disponibilidad_reserva(estacion_id):
    estacion = estacion_repo.obtener(estacion_id)

    if estacion is None:
        raise ValueError("Estacion inexistente, ingrese nuevamente")

    if estacion.estado != "disponible":
        raise ValueError(f"Estacion no disponible (estado: {estacion.estado})")
    