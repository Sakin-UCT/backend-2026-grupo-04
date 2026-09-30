from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class ClienteBase(BaseModel):
    nombre: str
    correo: EmailStr

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None

class ClienteResponse(ClienteBase):
    id: int
    fecha_registro: datetime

    class Config:
        from_attributes = True