import math
from app.domain.reserva import Reserva, EstadoReserva
from app.domain.excepciones import RecursoNoEncontradoError, ReglaNegocioError, ConflictoError

def calcular_costo(categoria, turno):
    hora_inicio, hora_fin = turno.split("-")
    h_inicio, m_inicio = map(int, hora_inicio.split(":"))
    h_fin, m_fin = map(int, hora_fin.split(":"))
    duracion_horas = (h_fin + m_fin / 60) - (h_inicio + m_inicio / 60)
    return categoria.tarifa_hora * duracion_horas

class ReservaService:
    def __init__(self, reserva_repo, estacion_service, cliente_repo, categoria_repo):
        self.reserva_repo = reserva_repo
        self.estacion_service = estacion_service
        self.cliente_repo = cliente_repo
        self.categoria_repo = categoria_repo

    def obtener(self, reserva_id: int):
        reserva = self.reserva_repo.obtener_por_id(reserva_id)
        if reserva is None:
            raise RecursoNoEncontradoError(f"No existe la reserva con el ID: {reserva_id}")
        return reserva

    def crear(self, datos):
        cliente = self.cliente_repo.obtener_por_id(datos.cliente_id)
        if cliente is None:
            raise RecursoNoEncontradoError(f"No existe el cliente con el ID: {datos.cliente_id}")
        estacion = self.estacion_service.validar_disponible(datos.estacion_id)
        if self.reserva_repo.existe_conflicto(datos.estacion_id, datos.fecha, datos.turno): 
            raise ConflictoError(f"La estación ya está reservada para la fecha {datos.fecha} y el turno {datos.turno}")
        categoria = self.categoria_repo.obtener_por_id(estacion.categoria_id)
        costo = calcular_costo(categoria, datos.turno)
        reserva = Reserva(
            cliente_id = datos.cliente_id,
            estacion_id = datos.estacion_id,
            fecha = datos.fecha,
            turno = datos.turno,
            costo = costo,
            estado = EstadoReserva.CONFIRMADA
        )
        return self.reserva_repo.guardar(reserva)

    def cambiar_estado(self, reserva_id: int, nuevo_estado):
        reserva = self.obtener(reserva_id)
        if nuevo_estado == EstadoReserva.COMPLETADA and reserva.estado != EstadoReserva.EN_CURSO:
            raise ReglaNegocioError("Una reserva solo puede completarse si estaba en curso")
        reserva.estado = nuevo_estado
        return self.reserva_repo.actualizar(reserva)

    def eliminar(self, reserva_id: int):
        self.obtener(reserva_id)
        self.reserva_repo.eliminar(reserva_id)


    def listar(self, fecha, ordenar_por, direccion, pagina, limite):
        items, total = self.reserva_repo.listar_filtrado(fecha, ordenar_por, direccion, pagina, limite)
        total_paginas = math.ceil(total / limite)
        return { 
            "items": items,
            "total": total,
            "pagina": pagina,
            "limite": limite,
            "total_paginas": total_paginas,
        }