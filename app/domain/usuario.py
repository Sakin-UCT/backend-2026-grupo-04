from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Perfil(str, Enum):
    ENCARGADO = "encargado"
    CLIENTE = "cliente"


@dataclass(kw_only=True)
class Usuario:
    id: int | None = None
    correo: str
    password_hash: str
    perfil: Perfil
    cliente_id: int | None = None
    intentos_fallidos: int = 0
    bloqueado_hasta: datetime | None = None
    activo: bool = True
    fecha_creacion: datetime | None = None


@dataclass(kw_only=True)
class RefreshToken:
    id: int | None = None
    usuario_id: int
    token_hash: str
    expira_en: datetime
    revocado: bool = False
    reemplazado_por: int | None = None
    creado_en: datetime | None = None


@dataclass(kw_only=True)
class TokenRecuperacion:
    id: int | None = None
    usuario_id: int
    token_hash: str
    expira_en: datetime
    usado: bool = False
    creado_en: datetime | None = None
