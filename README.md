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
