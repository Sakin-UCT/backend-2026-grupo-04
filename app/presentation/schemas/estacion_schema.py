from pydantic import BaseModel, ConfigDict, Field
from app.domain.estacion import EstadoEstacion

class EstacionCreate(BaseModel):

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {"codigo": "PC-01", "ubicacion": "Sala principal, fila A", "categoria_id": 1}]
        },
    )

    codigo: str = Field(
        min_length=3,
        max_length=20,
        description="Codigo unico de la estacion (3 a 20 caracteres).",
    )
    ubicacion: str = Field(
        min_length=3,
        max_length=100,
        description="Donde está la estación dentro del local.",
    )
    categoria_id: int = Field(gt=0, description="Id de la categoría de la estación.")

class EstacionUpdate(BaseModel):

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"estado": "en_mantencion"}]},
    )

    estado: EstadoEstacion = Field(
        description="Nuevo estado: disponible, en_mantencion o fuera_de_servicio."
    )

class EstacionResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "codigo": "PC-01",
                    "ubicacion": "Sala principal, fila A",
                    "estado": "disponible",
                    "categoria_id": 1,
                }]
        },
    )

    id: int
    codigo: str
    ubicacion: str
    estado: EstadoEstacion
    categoria_id: int