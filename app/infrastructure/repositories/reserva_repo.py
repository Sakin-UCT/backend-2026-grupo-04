from domain.reserva import EstadoReserva, Reserva

class ReservaRepository:
    def __init__(self):
        self._reservas = []
        self._siguiente_id = 1

    def obtener_todos(self):
        return list(self._reservas)

    def obtener_por_id(self, reserva_id):
        for reserva in self._reservas:
            if reserva.id == reserva_id:
                return reserva
        return None

    def guardar(self, datos):
        nueva_reserva = Reserva(
            id=self._siguiente_id,
            cliente_id=datos.cliente_id,
            estacion_id=datos.estacion_id,
            fecha=datos.fecha,
            turno=datos.turno,
            costo=0,
            estado=EstadoReserva.CONFIRMADA,
        )
        self._siguiente_id += 1
        self._reservas.append(nueva_reserva)
        return nueva_reserva

    def actualizar(self, reserva_id, nuevo_estado):
        reserva = self.obtener_por_id(reserva_id)
        if reserva is None:
            return None
        reserva.estado = nuevo_estado
        return reserva

    def existe_conflicto(self, estacion_id, fecha, turno):
        for reserva in self._reservas:
            mismo_turno = (
                reserva.estacion_id == estacion_id
                and reserva.fecha == fecha
                and reserva.turno == turno
            )
            esta_activa = reserva.estado in (EstadoReserva.CONFIRMADA, EstadoReserva.EN_CURSO)
            if mismo_turno and esta_activa:
                return True
        return False

    def eliminar(self, reserva_id):
        reserva = self.obtener_por_id(reserva_id)
        if reserva is None:
            return False
        self._reservas.remove(reserva)
        return True

reserva_repositorio = ReservaRepository()
#llamar a esto