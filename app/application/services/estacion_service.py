from repositories.estacion_repo import estacion_repositorio

def validar_disponibilidad_reserva(estacion_id):
    estacion = estacion_repositorio.obtener_por_id(estacion_id)

    if estacion is None:
        raise ValueError("Estacion inexistente, ingrese nuevamente")

    if estacion.estado != "disponible":
        raise ValueError(f"Estacion no disponible (estado: {estacion.estado})")