  # API Centro Gamer

API REST en Python + FastAPI para un centro gamer: permite gestionar clientes y estaciones de juego, y reservar estaciones por turno.Los datos se guardan en PostgreSQL y el esquema se crea y versiona con Alembic.

Proyecto del curso Desarrollo de Backend (ICINF1108), UCT. Grupo 04.

## Tecnologías
 
Python, FastAPI, Pydantic v2, SQLAlchemy, Alembic, PostgreSQL (en Docker) y pgAdmin.
 
## Requisitos previos
 
- Python 3.11 o superior
- Docker y Docker Compose
- Git
## Instalación
 
```bash
git clone https://github.com/Sakin-UCT/backend-2026-grupo-04.git
cd backend-2026-grupo-04
 
python -m venv .venv
source .venv/bin/activate        # Linux / Mac
# .venv\Scripts\activate         # Windows
 
pip install -r requirements.txt
```
## Variables de entorno

```bash
cp .env.example .env
```
 
| Variable | Para qué sirve | Valor de ejemplo |
|---|---|---|
| `POSTGRES_USER` | Usuario de PostgreSQL | `gamer` |
| `POSTGRES_PASSWORD` | Clave de PostgreSQL (cámbiala) | `cambiar_esta_clave` |
| `POSTGRES_DB` | Nombre de la base de datos | `centro_gamer` |
| `POSTGRES_PORT` | Puerto de PostgreSQL en tu máquina | `5432` |
| `PGADMIN_DEFAULT_EMAIL` | Correo de acceso a pgAdmin | `admin@example.com` |
| `PGADMIN_DEFAULT_PASSWORD` | Clave de acceso a pgAdmin (cámbiala) | `cambiar_esta_clave` |
| `PGADMIN_PORT` | Puerto de pgAdmin en tu máquina | `5050` |
| `DATABASE_URL` | URL de conexión que usan la app y Alembic | `postgresql+psycopg2://gamer:cambiar_esta_clave@localhost:5432/centro_gamer` |

`DATABASE_URL` debe coincidir con las variables `POSTGRES_*`: si cambias usuario, clave, base o puerto, actualízala también.
 
## Configuración de la base de datos
 
PostgreSQL y pgAdmin corren con Docker Compose:

```bash
docker compose up -d
```
 
Espera unos segundos a que PostgreSQL termine de iniciar. pgAdmin queda en http://localhost:5050 (usa el correo y la clave de tu `.env`). Para conectarlo al servidor, usa como host `postgres_db`, puerto `5432`, y el usuario, clave y base de tu `.env`.
 
Para borrar todo y empezar de cero:

```bash
docker compose down -v
```
## Migraciones y seeders
 
El esquema de la base de datos se crea **solo con Alembic**. No se usa `Base.metadata.create_all`.
 
```bash
alembic upgrade head                      # crea las tablas
python -m app.infrastructure.seeders.seed # carga datos de ejemplo
```
 
Si cambias un modelo ORM, genera una nueva migración y revísala antes de aplicarla:
 
```bash
alembic revision --autogenerate -m "Describe el cambio"
alembic upgrade head
```
 
## Ejecución

Orden completo desde un clon limpio:
 
```bash
cp .env.example .env
docker compose up -d
alembic upgrade head
python -m app.infrastructure.seeders.seed
uvicorn app.main:app --reload
```

La API queda en http://localhost:8000.

## Documentación OpenAPI
 
FastAPI genera la documentación automáticamente a partir de los routers y los schemas:
 
- Swagger UI (interactiva): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Esquema OpenAPI en JSON: http://localhost:8000/openapi.json
Cada endpoint documenta su resumen, descripción y los códigos de respuesta posibles, y los schemas incluyen ejemplos.


