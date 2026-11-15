import itertools

import pytest

from app.application.services.auth_service import (
    MAX_INTENTOS,
    MSG_CREDENCIALES,
    AuthService,
    Seguridad,
)
from app.domain.excepciones import NoAutenticadoError


class UsuarioRepoFalso:
    def __init__(self):
        self.usuarios = {}
        self._siguiente_id = 1

    def buscar_por_correo(self, correo):
        return self.usuarios.get(correo)

    def buscar_por_id(self, id):
        for u in self.usuarios.values():
            if u.id == id:
                return u
        return None

    def crear(self, usuario):
        usuario.id = self._siguiente_id
        self._siguiente_id += 1
        self.usuarios[usuario.correo] = usuario
        return usuario

    def actualizar(self, usuario):
        self.usuarios[usuario.correo] = usuario
        return usuario


class RefreshRepoFalso:
    def __init__(self):
        self.tokens = []

    def crear(self, token):
        token.id = len(self.tokens) + 1
        self.tokens.append(token)
        return token

    def buscar_por_hash(self, h):
        return next((t for t in self.tokens if t.token_hash == h), None)

    def revocar(self, id, reemplazado_por=None):
        for t in self.tokens:
            if t.id == id:
                t.revocado = True
                t.reemplazado_por = reemplazado_por

    def revocar_todos(self, usuario_id):
        for t in self.tokens:
            if t.usuario_id == usuario_id:
                t.revocado = True


def seguridad_falsa():
    contador = itertools.count(1)
    return Seguridad(
        hashear_password=lambda p: "hash:" + p,
        verificar_password=lambda p, h: h == "hash:" + p,
        crear_access_token=lambda uid, perfil: f"access-{uid}-{perfil}",
        generar_refresh_token=lambda: f"refresh-{next(contador)}",
        hashear_refresh=lambda t: "hash:" + t,
    )


@pytest.fixture
def service():
    return AuthService(UsuarioRepoFalso(), RefreshRepoFalso(), seguridad_falsa())


def test_login_correcto_devuelve_sesion(service):
    service.registrar("ana@gamer.cl", "clave-segura-123")
    sesion = service.login("ana@gamer.cl", "clave-segura-123")
    assert sesion.access_token == "access-1-cliente"
    assert sesion.refresh_token == "refresh-1"


def test_error_generico_igual_para_correo_inexistente_y_clave_mala(service):
    service.registrar("ana@gamer.cl", "clave-segura-123")
    with pytest.raises(NoAutenticadoError) as e1:
        service.login("nadie@gamer.cl", "clave-segura-123")
    with pytest.raises(NoAutenticadoError) as e2:
        service.login("ana@gamer.cl", "clave-incorrecta")
    assert e1.value.mensaje == MSG_CREDENCIALES
    assert e2.value.mensaje == MSG_CREDENCIALES


def test_bloqueo_tras_5_intentos(service):
    service.registrar("ana@gamer.cl", "clave-segura-123")
    for _ in range(MAX_INTENTOS):
        with pytest.raises(NoAutenticadoError):
            service.login("ana@gamer.cl", "mala")
    with pytest.raises(NoAutenticadoError):
        service.login("ana@gamer.cl", MSG_CREDENCIALES)

def test_refresh_reutilizado_revoca_todas_las_sesiones():
    refresh_repo = RefreshRepoFalso()
    service = AuthService(UsuarioRepoFalso(), refresh_repo, seguridad_falsa())
    service.registrar("ana@gamer.cl", "clave-segura-123")
    sesion = service.login("ana@gamer.cl", "clave-segura-123")
    service.refrescar(sesion.refresh_token)
    with pytest.raises(NoAutenticadoError):
        service.refrescar(sesion.refresh_token)
    assert all(t.revocado for t in refresh_repo.tokens)