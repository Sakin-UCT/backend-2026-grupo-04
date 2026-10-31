from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    tarifa_hora: float = Field(..., gt=0)
    descripcion: Optional[str] = Field(None, max_length=255)
    plataforma: Optional[str] = Field(None, max_length=100)

class CategoriaCreate(CategoriaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "VIP Gaming",
                "tarifa_hora": 5000.0,
                "descripcion": "Estación de alto rendimiento",
                "plataforma": "PC Master Race"
            }
        }
    )

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    tarifa_hora: Optional[float] = Field(None, gt=0)
    descripcion: Optional[str] = Field(None, max_length=255)
    plataforma: Optional[str] = Field(None, max_length=100)

class CategoriaResponse(CategoriaBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "VIP Gaming",
                "tarifa_hora": 5000.0,
                "descripcion": "Estación de alto rendimiento",
                "plataforma": "PC Master Race"
            }
        }
    )