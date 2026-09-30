from dataclasses import dataclass
from enum import Enum

class EstadoEstacion(str, Enum):
    DISPONIBLE = "disponible"
    EN_MANTENCION = "en_mantencion"
    FUERA_DE_SERVICIO = "fuera_de_servicio"

@dataclass
class Estacion:

    id: int
    codigo: str
    ubicacion: str
    categoria_id: int
    estado: EstadoEstacion = EstadoEstacion.DISPONIBLE