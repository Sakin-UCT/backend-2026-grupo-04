from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.domain.usuario import Perfil

LARGO_MIN_PASSWORD = 12
LARGO_MAX_PASSWORD = 128


def validar_password_segura(password: str):
    if len(password) < LARGO_MIN_PASSWORD:
        raise ValueError(f"La contraseña debe tener al menos {LARGO_MIN_PASSWORD} caracteres.")
    if len(password) > LARGO_MAX_PASSWORD:
        raise ValueError(f"La contraseña no puede superar los {LARGO_MAX_PASSWORD} caracteres.")
    return password


class RegistroRequest(BaseModel):
    correo: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validar_password(cls, valor: str) -> str:
        return validar_password_segura(valor)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"correo": "cliente@example.com", "password": "una-clave-larga-123"}
        }
    )


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str = Field(..., min_length=1, max_length=LARGO_MAX_PASSWORD)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"correo": "cliente@example.com", "password": "una-clave-larga-123"}
        }
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    correo: EmailStr
    perfil: Perfil