import os
import time
from pathlib import Path

import httpx
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text

RAIZ = Path(__file__).resolve().parent.parent

# 1. Apuntar la app a la BD de prueba, nunca a la de desarrollo
URL_PRUEBA = os.environ.get("TEST_DATABASE_URL")
if not URL_PRUEBA:
    raise RuntimeError("Falta TEST_DATABASE_URL en el entorno")
os.environ["DATABASE_URL"] = URL_PRUEBA
os.environ.setdefault("JWT_SECRET", "solo-para-pruebas")

# 2. Guardia: la limpieza borra datos, así que nunca debe correr sobre una BD ajena
NOMBRE_BD = URL_PRUEBA.rsplit("/", 1)[-1]
if "test" not in NOMBRE_BD:  # TODO: confirmar la regla del nombre con el grupo
    raise RuntimeError(f"'{NOMBRE_BD}' no parece una BD de prueba")

from app.infrastructure.database import SessionLocal, engine  # noqa: E402


@pytest.fixture(scope="session")
def bd_migrada():
    """Aplica las migraciones una sola vez por sesión de pruebas."""
    command.upgrade(Config(str(RAIZ / "alembic.ini")), "head")
    return URL_PRUEBA


def _vaciar_tablas():
    """Vacía las tablas de negocio y conserva el historial de Alembic."""
    with engine.begin() as conexion:
        nombres = (
            conexion.execute(
                text(
                    "SELECT tablename FROM pg_tables "
                    "WHERE schemaname = 'public' AND tablename <> 'alembic_version'"
                )
            )
            .scalars()
            .all()
        )
        if nombres:
            lista = ", ".join(f'"{n}"' for n in nombres)
            conexion.execute(text(f"TRUNCATE {lista} RESTART IDENTITY CASCADE"))


@pytest.fixture
def sesion_bd(bd_migrada):
    """Sesión nueva por prueba. Al terminar, cierra y vacía la BD."""
    sesion = SessionLocal()
    try:
        yield sesion
    finally:
        sesion.close()  # soltar locks antes de truncar
        _vaciar_tablas()


@pytest.fixture
def cliente_api():
    """Cliente HTTP contra la API levantada de verdad (no TestClient)."""
    url = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
    with httpx.Client(base_url=url, timeout=10.0) as cliente:
        yield cliente


@pytest.fixture
def buzon_mailpit():
    """Entrega una función que espera el cuerpo de un correo para un destinatario."""
    url = os.environ.get("MAILPIT_URL", "http://127.0.0.1:8025")
    with httpx.Client(base_url=url, timeout=10.0) as mailpit:
        mailpit.delete("/api/v1/messages")  # bandeja limpia antes de cada prueba

        def esperar_correo(destinatario: str, timeout: float = 10.0) -> str:
            limite = time.monotonic() + timeout
            while time.monotonic() < limite:
                lista = mailpit.get("/api/v1/messages")
                lista.raise_for_status()
                for mensaje in lista.json().get("messages", []):
                    # TODO: verificar los nombres de campo (To, Address, ID, Text)
                    #       en la documentación de la API v1 de Mailpit
                    direcciones = [p["Address"] for p in mensaje.get("To", [])]
                    if destinatario in direcciones:
                        detalle = mailpit.get(f"/api/v1/message/{mensaje['ID']}")
                        detalle.raise_for_status()
                        return detalle.json()["Text"]
                time.sleep(0.5)
            raise AssertionError(f"No llegó ningún correo a {destinatario}")

        yield esperar_correo
