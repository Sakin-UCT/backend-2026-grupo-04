import os
import re
import time
import httpx
import pytest

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
MAILPIT_API_URL = os.getenv("MAILPIT_API_URL", "http://127.0.0.1:8025").rstrip("/")


def _obtener_token_desde_mailpit(correo: str) -> str | None:
    try:
        resp = httpx.get(f"{MAILPIT_API_URL}/api/v1/messages", timeout=5.0)
        if resp.status_code != 200:
            return None
        mensajes = resp.json().get("messages", [])
        for msg in mensajes:
            destinatarios = [t.get("Address") for t in msg.get("To", [])]
            if correo in destinatarios:
                detalle = httpx.get(
                    f"{MAILPIT_API_URL}/api/v1/message/{msg['ID']}", timeout=5.0
                ).json()
                texto = detalle.get("Text", "")
                match = re.search(r"Token:\s*(\S+)", texto)
                if match:
                    return match.group(1)
    except httpx.HTTPError:
        return None
    return None


@pytest.mark.e2e
def test_flujo_completo_recuperacion_contrasena():
    ts = int(time.time() * 1000)
    correo = f"e2e_recup_{ts}@gamer.cl"
    password_inicial = "ClaveInicialSegura123!"
    password_nueva = "ClaveNuevaSuperSegura456!"

    with httpx.Client(base_url=API_BASE_URL, timeout=10.0) as client:
        
        reg = client.post(
            "/auth/registro",
            json={"correo": correo, "password": password_inicial},
        )
        assert reg.status_code in (200, 201), reg.text

        login_inicial = client.post(
            "/auth/login",
            json={"correo": correo, "password": password_inicial},
        )
        assert login_inicial.status_code == 200, login_inicial.text
        refresh_cookie = login_inicial.cookies.get("refresh_token")
        csrf_cookie = login_inicial.cookies.get("csrf_token")

      
        sol = client.post("/auth/recuperar", json={"correo": correo})
        assert sol.status_code == 200, sol.text
        token_recup = sol.json().get("token_debug") or _obtener_token_desde_mailpit(correo)
        assert token_recup, "No se pudo obtener el token de recuperación ni por JSON debug ni por Mailpit."

        
        rest = client.post(
            "/auth/restablecer",
            json={"token": token_recup, "nueva_password": password_nueva},
        )
        assert rest.status_code == 200, rest.text

        
        reuso = client.post(
            "/auth/restablecer",
            json={"token": token_recup, "nueva_password": "OtraClaveMasSegura789!"},
        )
        assert reuso.status_code in (400, 401), reuso.text

        
        login_viejo = client.post(
            "/auth/login",
            json={"correo": correo, "password": password_inicial},
        )
        assert login_viejo.status_code == 401

        
        if refresh_cookie:
            headers_refresh = {"X-CSRF-Token": csrf_cookie} if csrf_cookie else {}
            cookies_refresh = {"refresh_token": refresh_cookie}
            if csrf_cookie:
                cookies_refresh["csrf_token"] = csrf_cookie
            ref = client.post("/auth/refresh", cookies=cookies_refresh, headers=headers_refresh)
            assert ref.status_code in (401, 403)

        
        login_nuevo = client.post(
            "/auth/login",
            json={"correo": correo, "password": password_nueva},
        )
        assert login_nuevo.status_code == 200, login_nuevo.text