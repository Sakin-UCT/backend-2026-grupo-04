from datetime import datetime, timedelta, timezone
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.usuario import Perfil, TokenRecuperacion
from app.infrastructure.models.token_recuperacion_model import TokenRecuperacionModel
from app.infrastructure.models.usuario_model import UsuarioModel
from app.infrastructure.repositories.token_recuperacion_repo import TokenRecuperacionRepository

DB_URL = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")


@pytest.fixture
def db_session():
    if not DB_URL:
        pytest.skip("TEST_DATABASE_URL / DATABASE_URL no configurada")
    engine = create_engine(DB_URL)
    SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionTesting()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def usuario_prueba(db_session):
    usuario = UsuarioModel(
        correo=f"test_recup_{int(datetime.now(timezone.utc).timestamp() * 1000)}@gamer.cl",
        password_hash="hash_dummy_para_test_integracion",
        perfil=Perfil.CLIENTE.value,
        intentos_fallidos=0,
        bloqueado_hasta=None,
        activo=True,
        fecha_creacion=datetime.now(timezone.utc),
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)

    yield usuario

    db_session.query(TokenRecuperacionModel).filter(
        TokenRecuperacionModel.usuario_id == usuario.id
    ).delete()
    db_session.query(UsuarioModel).filter(UsuarioModel.id == usuario.id).delete()
    db_session.commit()


def test_marcar_usado_es_unico_y_atomico(db_session, usuario_prueba):
    repo = TokenRecuperacionRepository(db_session)
    ahora = datetime.now(timezone.utc)
    token_hash = f"hash_unico_{int(ahora.timestamp() * 1000)}"

    repo.crear(
        TokenRecuperacion(
            usuario_id=usuario_prueba.id,
            token_hash=token_hash,
            expira_en=ahora + timedelta(minutes=15),
            usado=False,
            creado_en=ahora,
        )
    )

    primer_intento = repo.marcar_usado(token_hash)
    segundo_intento = repo.marcar_usado(token_hash)

    assert primer_intento is True
    assert segundo_intento is False


def test_token_caducado_no_se_puede_marcar_usado(db_session, usuario_prueba):
    repo = TokenRecuperacionRepository(db_session)
    ahora = datetime.now(timezone.utc)
    token_hash = f"hash_expirado_{int(ahora.timestamp() * 1000)}"

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