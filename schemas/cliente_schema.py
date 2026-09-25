from datetime import datetime
from pydantic import BaseModel, EmailStr

class ClienteBase(BaseModel):
    nombre: str
    correo: EmailStr

class ClienteCreate(ClienteBase):
    pass  

class ClienteResponse(ClienteBase):
    id: int
    fecha_registro: datetime

    class Config:
        from_attributes = True