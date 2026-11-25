from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable
from app.domain.excepciones import (
    ConflictoError,
    NoAutenticadoError,
    ReglaNegocioError,
)
from app.domain.usuario import Perfil, RefreshToken, Usuario

MAX_INTENTOS = 5
MINUTOS_BLOQUEO = 15
DIAS_REFRESH = 7
LARGO_MIN_PASSWORD = 12
MSG_CREDENCIALES = "Credenciales inválidas"


@dataclass
class Seguridad:
    hashear_password: Callable[[str], str]
    verificar_password: Callable[[str, str], bool]
    crear_access_token: Callable[[int, str], str]
    generar_refresh_token: Callable[[], str]
    hashear_refresh: Callable[[str], str]


@dataclass
class Sesion:
    access_token: str
    refresh_token: str
    refresh_id: int | None = None


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


class AuthService:
    def __init__(self, usuario_repo, refresh_repo, seguridad: Seguridad):
        self.usuario_repo = usuario_repo
        self.refresh_repo = refresh_repo
        self.seguridad = seguridad

    def registrar(self, correo: str, password: str) -> Usuario:
        if len(password) < LARGO_MIN_PASSWORD:
            raise ReglaNegocioError(
                f"La contraseña debe tener mínimo {LARGO_MIN_PASSWORD} caracteres"
            )
        existen = self.usuario_repo.buscar_por_correo(correo)
        if existen:
            raise ConflictoError("El correo ya está registrado")
        usuario = Usuario(
            correo=correo,
            password_hash=self.seguridad.hashear_password(password),
            perfil=Perfil.CLIENTE,
        )
        return self.usuario_repo.crear(usuario)

    def login(self, correo: str, password: str) -> Sesion:
        usuario = self.usuario_repo.buscar_por_correo(correo)
        if not usuario:
            raise NoAutenticadoError(MSG_CREDENCIALES)
        if usuario.bloqueado_hasta and usuario.bloqueado_hasta > _ahora():
            raise NoAutenticadoError(MSG_CREDENCIALES)
        if not usuario.activo:
            raise NoAutenticadoError(MSG_CREDENCIALES)

        if not self.seguridad.verificar_password(password, usuario.password_hash):
            usuario.intentos_fallidos += 1
            if usuario.intentos_fallidos >= MAX_INTENTOS:
                usuario.bloqueado_hasta = _ahora() + timedelta(minutes=MINUTOS_BLOQUEO)
            self.usuario_repo.actualizar(usuario)
            raise NoAutenticadoError(MSG_CREDENCIALES)
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        self.usuario_repo.actualizar(usuario)

        return self._emitir_sesion(usuario)

    def refrescar(self, refresh_token: str) -> Sesion:
        h = self.seguridad.hashear_refresh(refresh_token)
        token = self.refresh_repo.buscar_por_hash(h)
        if not token:
            raise NoAutenticadoError(MSG_CREDENCIALES)
        if token.revocado:
            self.refresh_repo.revocar_todos(token.usuario_id)
            raise NoAutenticadoError(MSG_CREDENCIALES)
        if token.expira_en <= _ahora():
            raise NoAutenticadoError(MSG_CREDENCIALES)
        usuario = self.usuario_repo.buscar_por_id(token.usuario_id)
        if not usuario or not usuario.activo:
            raise NoAutenticadoError(MSG_CREDENCIALES)

        nueva = self._emitir_sesion(usuario)
        self.refresh_repo.revocar(token.id, reemplazado_por=nueva.refresh_id)
        return nueva

    def logout(self, refresh_token: str | None) -> None:
        if not refresh_token:
            return

        h = self.seguridad.hashear_refresh(refresh_token)
        token = self.refresh_repo.buscar_por_hash(h)

        if token and not token.revocado:
            self.refresh_repo.revocar(token.id)

    def me(self, usuario_id: int) -> Usuario:
        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario or not usuario.activo:
            raise NoAutenticadoError(MSG_CREDENCIALES)
        return usuario

    def _emitir_sesion(self, usuario: Usuario) -> Sesion:
        claro = self.seguridad.generar_refresh_token()
        token = RefreshToken(
            usuario_id=usuario.id,
            token_hash=self.seguridad.hashear_refresh(claro),
            expira_en=_ahora() + timedelta(days=DIAS_REFRESH),
        )
        guardado = self.refresh_repo.crear(token)
        access = self.seguridad.crear_access_token(usuario.id, usuario.perfil.value)
        return Sesion(
            access_token=access,
            refresh_token=claro,
            refresh_id=guardado.id,
        )
