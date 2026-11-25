import os
import secrets
import uuid

import httpx
import pytest

API_BASE_URL = os.getenv("API_BASE_URL")
ENCARGADO_CORREO = "encargado@gamer.cl"
ENCARGADO_PASSWORD = os.getenv("SEED_ENCARGADO_PASSWORD")

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not API_BASE_URL or not ENCARGADO_PASSWORD,
        reason="Faltan API_BASE_URL o SEED_ENCARGADO_PASSWORD en las variables de entorno.",
    ),
]


def _login(client: httpx.Client, correo: str, password: str) -> str:
    resp = client.post("/auth/login", json={"correo": correo, "password": password})
    assert resp.status_code == 200, f"Login fallido ({resp.status_code}): {resp.text}"
    return resp.json()["access_token"]


def _bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_patch_estacion_exige_perfil_encargado():
    with httpx.Client(base_url=API_BASE_URL.rstrip("/"), timeout=10.0) as client:
        token_encargado = _login(client, ENCARGADO_CORREO, ENCARGADO_PASSWORD)

        # estacion existente y != de la actual
        listado = client.get("/estaciones", headers=_bearer(token_encargado))
        assert listado.status_code == 200, listado.text
        assert listado.json(), "No hay estaciones cargadas: falta ejecutar el seeder."
        estacion = listado.json()[0]
        url = f"/estaciones/{estacion['id']}"
        estado_original = estacion["estado"]
        estado_nuevo = (
            "en_mantencion" if estado_original != "en_mantencion" else "disponible"
        )
        cuerpo = {"estado": estado_nuevo}

        # sin token: 401
        sin_token = client.patch(url, json=cuerpo)
        assert sin_token.status_code == 401, sin_token.text

        # token recien registrado: 403
        correo_cliente = f"e2e_permisos_{uuid.uuid4().hex[:12]}@gamer.cl"
        password_cliente = secrets.token_urlsafe(16)
        registro = client.post(
            "/auth/registro",
            json={"correo": correo_cliente, "password": password_cliente},
        )
        assert registro.status_code in (200, 201), registro.text
        token_cliente = _login(client, correo_cliente, password_cliente)

        como_cliente = client.patch(url, json=cuerpo, headers=_bearer(token_cliente))
        assert como_cliente.status_code == 403, como_cliente.text

        intacta = client.get(url, headers=_bearer(token_encargado))
        assert intacta.json()["estado"] == estado_original

        # token del encargado: 200 y si cambia
        try:
            como_encargado = client.patch(
                url, json=cuerpo, headers=_bearer(token_encargado)
            )
            assert como_encargado.status_code == 200, como_encargado.text
            assert como_encargado.json()["estado"] == estado_nuevo

            verificada = client.get(url, headers=_bearer(token_encargado))
            assert verificada.status_code == 200, verificada.text
            assert verificada.json()["estado"] == estado_nuevo
        finally:
            # se deja la estacion como estaba
            client.patch(
                url, json={"estado": estado_original}, headers=_bearer(token_encargado)
            )
