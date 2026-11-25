import jwt
import hashlib
import pytest
from datetime import datetime, timedelta, timezone

from app.domain.excepciones import NoAutenticadoError
from app.infrastructure.security.jwt_handler import (
    crear_access_token,
    crear_token_recuperacion,
    decodificar_access_token,
    decodificar_token_recuperacion,
)
from app.infrastructure.security.password import hashear_password, verificar_password
from app.infrastructure.security.token_hash import generar_refresh_token, hashear_refresh


SECRETO = "secreto-de-prueba-con-mas-de-32-caracteres-ok"
OTRO_SECRETO = "otro-secreto-distinto-con-mas-de-32-caracteres"


@pytest.fixture(autouse=True)
def fijar_secreto(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", SECRETO)


def _payload(**cambios):
    ahora = datetime.now(timezone.utc)
    base = {
        "sub": "1",
        "perfil": "cliente",
        "type": "access",
        "exp": ahora + timedelta(minutes=15),
    }
    base.update(cambios)
    return base


def test_hash_argon2id_verifica_y_no_es_la_contrasena():
    password = "una-clave-larga-123"
    hash_ = hashear_password(password)

    assert hash_ != password
    assert hash_.startswith("$argon2id$")
    assert verificar_password(password, hash_) is True
    assert verificar_password("otra-clave-distinta", hash_) is False


def test_jwt_valido_se_decodifica_con_sub_y_type_correctos():
    token = crear_access_token(7, "cliente")

    datos = decodificar_access_token(token)

    assert datos["sub"] == "7"
    assert datos["type"] == "access"
    assert datos["perfil"] == "cliente"


def test_jwt_rechazado_lanza_no_autenticado():

    token_firma_mala = jwt.encode(_payload(), OTRO_SECRETO, algorithm="HS256")
    with pytest.raises(NoAutenticadoError):
        decodificar_access_token(token_firma_mala)

    vencido = datetime.now(timezone.utc) - timedelta(minutes=1)
    token_vencido = jwt.encode(_payload(exp=vencido), SECRETO, algorithm="HS256")
    with pytest.raises(NoAutenticadoError):
        decodificar_access_token(token_vencido)

    token_none = jwt.encode(_payload(), None, algorithm="none")
    with pytest.raises(NoAutenticadoError):
        decodificar_access_token(token_none)

    with pytest.raises(NoAutenticadoError):
        decodificar_access_token(crear_token_recuperacion(1))

    with pytest.raises(NoAutenticadoError):
        decodificar_token_recuperacion(crear_access_token(1, "cliente"))

    sin_exp = _payload()
    del sin_exp["exp"]
    token_sin_exp = jwt.encode(sin_exp, SECRETO, algorithm="HS256")
    with pytest.raises(NoAutenticadoError):
        decodificar_access_token(token_sin_exp)

def test_refresh_token_opaco_y_hash_sha256():
    token_a = generar_refresh_token()
    token_b = generar_refresh_token()

    assert token_a != token_b
    assert len(token_a) >= 43

    hash_a = hashear_refresh(token_a)
    assert hash_a == hashlib.sha256(token_a.encode("utf-8")).hexdigest()
    assert len(hash_a) == 64
    assert hash_a != token_a
    assert hashear_refresh(token_a) == hash_a
    assert hashear_refresh(token_b) != hash_a