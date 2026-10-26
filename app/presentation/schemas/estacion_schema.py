from pydantic import BaseModel
from domain.estacion import EstadoEstacion

class EstacionCreate(BaseModel):
    #lo que se manda para crear una estacion nueva
    codigo: str
    ubicacion: str
    categoria_id: int

class EstacionUpdate(BaseModel):
    #lo que se manda para cambiar el estado de una estacion
    estado: EstadoEstacion