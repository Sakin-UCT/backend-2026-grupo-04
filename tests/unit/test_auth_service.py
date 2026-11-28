from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
import pytest
from app.application.services.auth_service import MSG_CREDENCIALES, AuthService, Seguridad
from app.domain.excepciones import NoAutenticadoError
from app.domain.usuario import Perfil, RefreshToken, Usuario


@pytest.fixture
def usuario():
    return Usuario(
        id=1,
        correo="cliente@gamer.cl",
        password_hash="hash_password",
        perfil=Perfil.CLIENTE,
    )


@pytest.fixture
def servicio(usuario):
    usuario_repo = Mock()
    refresh_repo = Mock()

    usuario_repo.buscar_por_correo.return_value = usuario
    usuario_repo.buscar_por_id.return_value = usuario

    def guardar_refresh(token):
        token.id = 1
        return token

    refresh_repo.crear.side_effect = guardar_refresh

    seguridad = Seguridad(
        hashear_password=lambda password: "hash_password",
        verificar_password=lambda password, password_hash: (
            password == "password-segura-123"
            and password_hash == "hash_password"
        ),
        crear_access_token=lambda usuario_id, perfil: "access_token_prueba",
        generar_refresh_token=lambda: "refresh_token_prueba",
        hashear_refresh=lambda token: f"hash_{token}",
    )

    return AuthService(
        usuario_repo=usuario_repo,
        refresh_repo=refresh_repo,
        seguridad=seguridad,
    )


def test_login_correcto(servicio, usuario):
    sesion = servicio.login(
        usuario.correo,
        "password-segura-123",
    )

    assert sesion.access_token == "access_token_prueba"
    assert sesion.refresh_token == "refresh_token_prueba"
    assert sesion.refresh_id == 1

    assert usuario.intentos_fallidos == 0
    assert usuario.bloqueado_hasta is None

    servicio.usuario_repo.actualizar.assert_called_once_with(usuario)
    servicio.refresh_repo.crear.assert_called_once()

    token_guardado = servicio.refresh_repo.crear.call_args.args[0]

    assert token_guardado.usuario_id == usuario.id
    assert token_guardado.token_hash == "hash_refresh_token_prueba"
    assert token_guardado.token_hash != sesion.refresh_token
    assert token_guardado.expira_en > datetime.now(timezone.utc)


def test_login_credenciales_invalidas(servicio, usuario):
    with pytest.raises(NoAutenticadoError) as error_password:
        servicio.login(usuario.correo, "password-incorrecta")

    servicio.usuario_repo.buscar_por_correo.return_value = None

    with pytest.raises(NoAutenticadoError) as error_correo:
        servicio.login("inexistente@gamer.cl", "password-segura-123")

    assert str(error_password.value) == str(error_correo.value)
    assert str(error_password.value) == MSG_CREDENCIALES

    servicio.refresh_repo.crear.assert_not_called()


def test_bloqueo_despues_de_cinco_intentos(servicio, usuario):
    for _ in range(5):
        with pytest.raises(NoAutenticadoError):
            servicio.login(usuario.correo, "password-incorrecta")
    assert usuario.intentos_fallidos == 5
    assert usuario.bloqueado_hasta is not None
    assert usuario.bloqueado_hasta > datetime.now(timezone.utc)
    with pytest.raises(NoAutenticadoError):
        servicio.login(usuario.correo, "password-segura-123")

    assert servicio.usuario_repo.actualizar.call_count == 5
    servicio.refresh_repo.crear.assert_not_called()


def test_reutilizacion_refresh_revoca_todas_las_sesiones(
    servicio,
    usuario,
):
    token_revocado = RefreshToken(
        id=1,
        usuario_id=usuario.id,
        token_hash="hash_refresh_antiguo",
        expira_en=datetime.now(timezone.utc) + timedelta(days=1),
        revocado=True,
    )

    servicio.refresh_repo.buscar_por_hash.return_value = token_revocado

    with pytest.raises(NoAutenticadoError):
        servicio.refrescar("refresh_antiguo")

    servicio.refresh_repo.buscar_por_hash.assert_called_once_with(
        "hash_refresh_antiguo"
    )
    servicio.refresh_repo.revocar_todos.assert_called_once_with(usuario.id)
    servicio.refresh_repo.crear.assert_not_called()