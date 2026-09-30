# API Centro Gamer

API REST en Python + FastAPI para un centro gamer: permite gestionar clientes y estaciones de juego, y reservar estaciones por turno.

Proyecto del curso Desarrollo de Backend (ICINF1108).

## Cómo correr el proyecto (con uv)

bash
uv venv
source .venv/bin/activate        # Linux / Mac
# .venv\Scripts\activate         # Windows
uv pip install -r requirements.txt
uv run uvicorn main:app --reload


Documentación interactiva: http://localhost:8000/docs

## Estructura del proyecto


domain/
schemas/
repositories/
services/
routers/
tests_manual/
main.py
README.md
requirements.txt
.gitignore

## Módulos y responsables

| Módulo | Domain / Schema / Repo | Services / Routers |
|---|---|---|
| Cliente y CategoriaEstacion | Persona B | Persona D (routers) |
| Estacion y Reserva | Persona E | Persona C |

`main.py` (conexión de routers y manejo global de errores) y este `README.md` están a cargo de quien integra el proyecto.

## Reglas de negocio

- **RN1:** no se puede reservar la misma estación en el mismo turno y fecha si ya existe una reserva `confirmada` o `en_curso`.
- **RN2:** no se puede reservar una estación que esté en `mantencion` o `fuera_de_servicio`.
- **RN3:** una reserva no puede pasar a `completada` sin haber pasado antes por `en_curso`.

## Alcance

- No hay autenticación.
- No hay base de datos real: todo se guarda en memoria y **se reinicia al reiniciar el servidor**.
- No hay pagos ni notificaciones automáticas (fuera de alcance).

## Formato de error estándar

Todas las respuestas de error de la API usan la misma estructura, definida en un manejador global en `main.py`:

json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "mensaje descriptivo",
    "details": []
  }
}


Si un `HTTPException` se lanza con `detail` como texto simple, el manejador lo convierte automáticamente a este formato. Los errores de validación (422) también lo usan, con `code: "VALIDATION_ERROR"` y el detalle por campo en `details`.
