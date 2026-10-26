from fastapi import APIRouter, HTTPException
from repositories.estacion_repo import estacion_repositorio
from schemas.estacion_schema import EstacionCreate, EstacionUpdate

router = APIRouter(prefix="/estaciones", tags=["Estaciones"])

@router.get("/{estacion_id}")
def obtener_estacion(estacion_id: int):
    estacion = estacion_repositorio.obtener_por_id(estacion_id)
    if estacion is None:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return estacion

@router.get("")
def listar_estaciones():
    return estacion_repositorio.obtener_todos()

@router.post("")
def crear_estaciones(datos: EstacionCreate):
    return estacion_repositorio.guardar(datos)

@router.patch("/{estacion_id}")
def actualizar_estado(estacion_id: int, datos: EstacionUpdate):
    estacion = estacion_repositorio.actualizar(estacion_id, datos)
    if estacion is None:
        raise HTTPException(status_code=404, detail="estacion no encontrada")
    return estacion
