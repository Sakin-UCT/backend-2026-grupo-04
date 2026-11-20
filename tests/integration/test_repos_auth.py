from datetime import datetime, timedelta, timezone
import pytest

from app.domain.excepciones import ConflictoError
from app.domain.usuario import Perfil, RefreshToken, Usuario
from app.infrastructure.repositories.refresh_token_repo import RefreshTokenRepository
from app.infrastructure.repositories.usuario_repo import UsuarioRepository


def _construir_usuario(correo: str, cliente_id: int | None = None) -> Usuario:
    ahora = datetime.now(timezone.utc)
    return Usuario(
        id=None,
        correo=correo,
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$test_salt$test_hash",
        perfil=Perfil.CLIENTE,
        cliente_id=cliente_id,
        intentos_fallidos=0,
        bloqueado_hasta=None,
        activo=True,
        fecha_creacion=ahora,
    )


def test_crear_buscar_y_conflicto_correo_usuario(db_session):
    repo = UsuarioRepository(db_session)
    usuario = _construir_usuario("jugador@centro.cl")

    creado = repo.crear(usuario)
    assert creado.id is not None
    assert creado.correo == "jugador@centro.cl"

    encontrado = repo.buscar_por_correo("jugador@centro.cl")
    assert encontrado is not None
    assert encontrado.id == creado.id

    with pytest.raises(ConflictoError):
        repo.crear(_construir_usuario("jugador@centro.cl"))


def test_refresh_token_crear_buscar_y_revocar(db_session):
    usuario_repo = UsuarioRepository(db_session)
    token_repo = RefreshTokenRepository(db_session)

    usuario = usuario_repo.crear(_construir_usuario("refresh@centro.cl"))
    ahora = datetime.now(timezone.utc)
    token = RefreshToken(
        id=None,
        usuario_id=usuario.id,
        token_hash="hash_refresh_unico_001",
        expira_en=ahora + timedelta(days=7),
        revocado=False,
        reemplazado_por=None,
        creado_en=ahora,
    )

    creado = token_repo.crear(token)
    assert creado.id is not None

    buscado = token_repo.buscar_por_hash("hash_refresh_unico_001")
    assert buscado is not None
    assert buscado.revocado is False

    token_repo.revocar(creado.id)
    revocado = token_repo.buscar_por_hash("hash_refresh_unico_001")
    assert revocado is not None
    assert revocado.revocado is True


def test_refresh_token_revocado_y_revocar_todos(db_session):
    usuario_repo = UsuarioRepository(db_session)
    token_repo = RefreshTokenRepository(db_session)

    usuario = usuario_repo.crear(_construir_usuario("multi_refresh@centro.cl"))
    ahora = datetime.now(timezone.utc)

    t1 = token_repo.crear(
        RefreshToken(
            id=None,
            usuario_id=usuario.id,
            token_hash="hash_multi_001",
            expira_en=ahora + timedelta(days=7),
            revocado=False,
            reemplazado_por=None,
            creado_en=ahora,
        )
    )
    t2 = token_repo.crear(
        RefreshToken(
            id=None,
            usuario_id=usuario.id,
            token_hash="hash_multi_002",
            expira_en=ahora + timedelta(days=7),
            revocado=False,
            reemplazado_por=None,
            creado_en=ahora,
        )
    )

    token_repo.revocar(t1.id)
    reutilizado = token_repo.buscar_por_hash("hash_multi_001")
    assert reutilizado is not None
    assert reutilizado.revocado is True

    token_repo.revocar_todos(usuario.id)
    segundo = token_repo.buscar_por_hash("hash_multi_002")
    assert segundo is not None
    assert segundo.revocado is True
    assert t2.usuario_id == usuario.id