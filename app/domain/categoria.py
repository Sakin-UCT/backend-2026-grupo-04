from dataclasses import dataclass
from typing import Optional

@dataclass(kw_only=True)
class Categoria:
    id: Optional[int] = None
    nombre: str
    tarifa_hora: float
    descripcion: Optional[str] = None
    plataforma: Optional[str] = None