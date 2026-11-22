from pydantic import BaseModel, EmailStr, field_validator

try:
    from app.presentation.schemas.auth_schema import validar_password_segura
except ImportError:
    def validar_password_segura(password: str) -> str:
        if len(password) < 12:
            raise ValueError("La contraseña debe tener al menos 12 caracteres.")
        return password


class SolicitudRecuperacion(BaseModel):
    correo: EmailStr


class RestablecerPassword(BaseModel):
    token: str
    nueva_password: str

    @field_validator("nueva_password")
    @classmethod
    def validar_nueva_password(cls, valor: str) -> str:
        return validar_password_segura(valor)


class MensajeRecuperacionResponse(BaseModel):
    mensaje: str
    token_debug: str | None = None