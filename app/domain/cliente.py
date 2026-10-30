from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(kw_only=True)
class Cliente:
    id: Optional[int] = None
    nombre: str
    correo: str
    telefono: Optional[str] = None
    fecha_registro: Optional[datetime] = None