from fastapi import APIRouter, HTTPException
from repositories import estacion_repo

router = APIRouter(prefix="/estaciones", tags=["Estaciones"])

@router.get("/{estacion_id}")
def obtener_estacion(estacion_id: int):
    estacion = estacion_repo.obtener(estacion_id)
    if estacion is None:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return estacion