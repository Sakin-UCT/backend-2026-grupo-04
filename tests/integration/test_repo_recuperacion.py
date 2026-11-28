from datetime import UTC, datetime, timedelta

import pytest

from app.domain.usuario import Perfil, TokenRecuperacion
from app.infrastructure.models.cliente_model import ClienteModel
from app.infrastructure.models.token_recuperacion_model import TokenRecuperacionModel
from app.infrastructure.models.usuario_model import UsuarioModel
from app.infrastructure.repositories.token_recuperacion_repo import (
    TokenRecuperacionRepository,
)


@pytest.fixture
def usuario_prueba(db_session):
    ahora = datetime.now(UTC)
    marca = int(ahora.timestamp() * 1_000_000)

    cliente = ClienteModel(
        nombre="Cliente Test Recuperacion",
        correo=f"cliente_recup_{marca}@gamer.cl",
        telefono="+56912345678",
        fecha_registro=ahora,
    )
    db_session.add(cliente)
    db_session.commit()
    db_session.refresh(cliente)

    usuario = UsuarioModel(
        correo=f"usuario_recup_{marca}@gamer.cl",
        password_hash="hash_dummy_para_test_integracion",
        perfil=Perfil.CLIENTE.value,
        cliente_id=cliente.id,
        intentos_fallidos=0,
        bloqueado_hasta=None,
        activo=True,
        fecha_creacion=ahora,
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)

    yield usuario

    db_session.query(TokenRecuperacionModel).filter(
        TokenRecuperacionModel.usuario_id == usuario.id
    ).delete()
    db_session.query(UsuarioModel).filter(UsuarioModel.id == usuario.id).delete()
    db_session.query(ClienteModel).filter(ClienteModel.id == cliente.id).delete()
    db_session.commit()


def test_marcar_usado_es_unico_y_atomico(db_session, usuario_prueba):
    repo = TokenRecuperacionRepository(db_session)
    ahora = datetime.now(UTC)
    token_hash = f"hash_unico_{int(ahora.timestamp() * 1_000_000)}"

    guardado = repo.crear(
        TokenRecuperacion(
            usuario_id=usuario_prueba.id,
            token_hash=token_hash,
            expira_en=ahora + timedelta(minutes=15),
            usado=False,
            creado_en=ahora,
        )
    )
    assert guardado.id is not None

    primer_intento = repo.marcar_usado(token_hash)
    segundo_intento = repo.marcar_usado(token_hash)

    assert primer_intento is True
    assert segundo_intento is False


def test_token_caducado_no_se_puede_marcar_usado(db_session, usuario_prueba):
    repo = TokenRecuperacionRepository(db_session)
    ahora = datetime.now(UTC)
    token_hash = f"hash_expirado_{int(ahora.timestamp() * 1_000_000)}"

    repo.crear(
        TokenRecuperacion(
            usuario_id=usuario_prueba.id,
            token_hash=token_hash,
            expira_en=ahora - timedelta(minutes=1),
            usado=False,
            creado_en=ahora - timedelta(minutes=16),
        )
    )

    resultado = repo.marcar_usado(token_hash)

    assert resultado is False


def test_invalidar_pendientes_y_contar_recientes(db_session, usuario_prueba):
    repo = TokenRecuperacionRepository(db_session)
    ahora = datetime.now(UTC)
    marca = int(ahora.timestamp() * 1_000_000)
    hash_1 = f"hash_pendiente_1_{marca}"
    hash_2 = f"hash_pendiente_2_{marca}"

    repo.crear(
        TokenRecuperacion(
            usuario_id=usuario_prueba.id,
            token_hash=hash_1,
            expira_en=ahora + timedelta(minutes=15),
            usado=False,
            creado_en=ahora - timedelta(minutes=2),
        )
    )
    repo.crear(
        TokenRecuperacion(
            usuario_id=usuario_prueba.id,
            token_hash=hash_2,
            expira_en=ahora + timedelta(minutes=15),
            usado=False,
            creado_en=ahora,
        )
    )

    recientes = repo.contar_recientes(
        usuario_id=usuario_prueba.id,
        desde=ahora - timedelta(minutes=15),
    )
    assert recientes == 2

    repo.invalidar_pendientes(usuario_prueba.id)

    assert repo.marcar_usado(hash_1) is False
    assert repo.marcar_usado(hash_2) is False
