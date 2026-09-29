from pydantic import BaseModel
from domain.estacion import EstadoEstacion

class EstacionCrear(BaseModel):
    #lo que se manda para crear una estacion nueva
    codigo: str
    ubicacion: str
    categoria_id: int

class EstacionActualizar(BaseModel):
    #lo que se manda para cambiar el estado de una estacion
    estado: EstadoEstacion