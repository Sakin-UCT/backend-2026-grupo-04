from fastapi import APIRouter, HTTPException
from repositories import estacion_repo
from schemas.estacion_schema import EstacionCreate
from schemas.estacion_schema import EstacionCreate, EstacionUpdate


router = APIRouter(prefix="/estaciones", tags=["Estaciones"])

@router.get("/{estacion_id}")
def obtener_estacion(estacion_id: int):
    estacion = estacion_repo.obtener(estacion_id)
    if estacion is None:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return estacion

@router.get("")
def listar_estaciones():
    estacion = estacion_repo.listar()
    return estacion

@router.post("")
def crear_estaciones(datos: EstacionCreate):
    estacion = estacion_repo.crear(datos.codigo, datos.ubicacion, datos.categoria_id)
    return estacion

@router.patch("/{estacion_id}")
def actualizar_estado(estacion_id: int, datos: EstacionUpdate):
    estacion = estacion_repo.actualizar_estado(estacion_id, datos.estado)
    if estacion is None:
        raise HTTPException(status_code=404, detail= "estacion no encontrada")
    return estacion

