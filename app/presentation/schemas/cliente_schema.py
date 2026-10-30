from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class ClienteBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    correo: EmailStr
    telefono: Optional[str] = None

class ClienteCreate(ClienteBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Benito Carbonell",
                "correo": "benito@example.com",
                "telefono": "+56912345678"
            }
        }
    )

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Benito Actualizado",
                "correo": "benito.nuevo@example.com",
                "telefono": "+56987654321"
            }
        }
    )

class ClienteResponse(ClienteBase):
    id: int
    fecha_registro: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Benito Carbonell",
                "correo": "benito@example.com",
                "telefono": "+56912345678",
                "fecha_registro": "2026-10-27T20:38:00"
            }
        }
    )