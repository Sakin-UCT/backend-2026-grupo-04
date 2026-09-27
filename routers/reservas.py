import math
from fastapi import APIRouter, HTTPException
from repositories import reserva_repo
from schemas.reserva_schema import ReservaCreate, ReservaUpdate
from services import reserva_service

router = APIRouter(prefix="/reservas", tags=["Reservas"])

@router.get("/{reserva_id}")
def obtener_reserva(reserva_id: int):
    reserva = reserva_repo.obtener(reserva_id)
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva

@router.post("")
def crear_reserva(datos: ReservaCreate):
    try:
        reserva = reserva_service.crear_reserva(datos.cliente_id, datos.estacion_id, datos.fecha, datos.turno)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return reserva

@router.patch("/{reserva_id}")
def actualizar_estado_reserva(reserva_id: int, datos: ReservaUpdate):
    try:
        reserva = reserva_service.cambiar_estado(reserva_id, datos.estado)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return reserva

@router.delete("/{reserva_id}", status_code=204)
def eliminar_reserva(reserva_id: int):
    eliminado = reserva_repo.eliminar(reserva_id)
    if eliminado is False:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

@router.get("")
def listar_reservas(fecha: str | None = None, ordenar_por: str | None = None, direccion: str = "asc", pagina: int = 1, limite: int = 20):
    reservas = reserva_repo.listar()
    if fecha is not None:
        reservas = [r for r in reservas if r.fecha == fecha]

    if ordenar_por is not None:
        reservas = sorted(reservas, key=lambda r: getattr(r, ordenar_por), reverse=(direccion == "desc"))

    total = len(reservas)
    inicio = (pagina - 1) * limite
    fin = inicio + limite
    reservas_pagina = reservas[inicio:fin]

    return {
    "items": reservas_pagina,
    "total": total,
    "pagina": pagina,
    "limite": limite,
    "total_paginas": math.ceil(total / limite),
    }