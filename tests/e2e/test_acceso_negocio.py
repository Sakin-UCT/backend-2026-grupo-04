import os
import secrets
from datetime import date, timedelta
from uuid import uuid4
import httpx
import pytest

pytestmark = pytest.mark.e2e


def test_acceso_y_negocio():
    api_base_url = os.getenv("API_BASE_URL")

    assert api_base_url, "Falta configurar API_BASE_URL"

    correo = f"e2e_acceso_{uuid4().hex}@gamer.cl"
    password = secrets.token_urlsafe(18)

    with httpx.Client(
        base_url=api_base_url.rstrip("/"),
        timeout=10.0,
    ) as client:
        respuesta = client.get("/reservas")
        assert respuesta.status_code == 401, respuesta.text

        respuesta = client.post(
            "/auth/registro",
            json={
                "correo": correo,
                "password": password,
            },
        )

        assert respuesta.status_code == 201, respuesta.text

        usuario = respuesta.json()

        assert usuario["correo"] == correo
        assert usuario["perfil"] == "cliente"
        assert "password_hash" not in usuario

        respuesta = client.post(
            "/auth/login",
            json={
                "correo": correo,
                "password": password,
            },
        )
        assert respuesta.status_code == 200, respuesta.text
        access_token = respuesta.json()["access_token"]
        refresh_token = client.cookies.get("refresh_token")
        csrf_token = client.cookies.get("csrf_token")
        assert access_token
        assert refresh_token
        assert csrf_token
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        respuesta = client.get("/auth/me", headers=headers)
        assert respuesta.status_code == 200, respuesta.text
        assert respuesta.json()["correo"] == correo
        assert respuesta.json()["perfil"] == "cliente"
        respuesta = client.get("/clientes", headers=headers)
        assert respuesta.status_code == 200, respuesta.text
        clientes = respuesta.json()
        assert clientes, "No hay clientes. Ejecuta el seeder."
        cliente_id = clientes[0]["id"]
        respuesta = client.get("/estaciones")
        assert respuesta.status_code == 200, respuesta.text
        estaciones = respuesta.json()
        estacion = next(
            (
                estacion
                for estacion in estaciones
                if estacion["estado"] == "disponible"
            ),
            None,
        )
        assert estacion is not None, "No hay estaciones disponibles."
        datos_reserva = {
            "cliente_id": cliente_id,
            "estacion_id": estacion["id"],
            "fecha": (date.today() + timedelta(days=1)).isoformat(),
            "turno": "10:00-11:00",
        }

        respuesta = client.post(
            "/reservas",
            json=datos_reserva,
            headers=headers,
        )
        assert respuesta.status_code == 201, respuesta.text
        reserva = respuesta.json()
        reserva_id = reserva["id"]
        try:
            assert reserva["cliente_id"] == cliente_id
            assert reserva["estacion_id"] == estacion["id"]
            assert reserva["estado"] == "confirmada"
            assert reserva["costo"] > 0

            respuesta = client.get(
                f"/reservas/{reserva_id}",
                headers=headers,
            )

            assert respuesta.status_code == 200, respuesta.text
            assert respuesta.json()["id"] == reserva_id

        finally:
            respuesta = client.delete(
                f"/reservas/{reserva_id}",
                headers=headers,
            )

            assert respuesta.status_code == 204, respuesta.text

        respuesta = client.post(
            "/auth/logout",
            headers={
                "X-CSRF-Token": csrf_token,
            },
        )

        assert respuesta.status_code == 204, respuesta.text
        assert client.cookies.get("refresh_token") is None
        assert client.cookies.get("csrf_token") is None

        with httpx.Client(
            base_url=api_base_url.rstrip("/"),
            timeout=10.0,
        ) as cliente_reutilizacion:
            cliente_reutilizacion.cookies.set(
                "refresh_token",
                refresh_token,
                path="/auth",
            )

            cliente_reutilizacion.cookies.set(
                "csrf_token",
                csrf_token,
                path="/auth",
            )

            respuesta = cliente_reutilizacion.post(
                "/auth/refresh",
                headers={
                    "X-CSRF-Token": csrf_token,
                },
            )

            assert respuesta.status_code == 401, respuesta.text