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

## Estructura del proyecto

```
app/
├── main.py                  # crea la app, incluye routers y manejadores de errores
├── presentation/            # capa de presentación (HTTP)
│   ├── routers/
│   ├── schemas/
│   └── dependencies.py
├── application/
│   └── services/            # casos de uso y reglas de negocio
├── domain/                  # entidades, enums y excepciones (Python puro)
└── infrastructure/          # acceso a datos
    ├── database.py
    ├── models/
    ├── mappers.py
    ├── repositories/
    └── seeders/
migrations/                  # migraciones de Alembic
tests_manual/                # pruebas manuales (.http) y su evidencia
compose.yml                  # PostgreSQL y pgAdmin
.env.example                 # plantilla de variables de entorno
requirements.txt
```

## Arquitectura por capas
 
Cada capa solo conoce a la que tiene debajo:
 
```
presentation → application → domain ← infrastructure
```
 
| Capa | Qué contiene | Función |
|---|---|---|
| **Presentación** (`app/presentation`) | Routers, schemas (DTOs) y `dependencies.py` | Recibe la solicitud HTTP, valida los datos con los schemas, llama al service y devuelve la respuesta con su código HTTP. Un router no consulta la base de datos ni contiene reglas de negocio. `get_db()` entrega una sesión de BD por solicitud y la cierra al terminar. |
| **Aplicación** (`app/application/services`) | Services | Implementan los casos de uso y las reglas de negocio (RN1, RN2, RN3), calculan el costo y lanzan las excepciones de dominio. Reciben los repositorios en su constructor. |
| **Dominio** (`app/domain`) | Entidades, enums y excepciones | Modelo del negocio en Python puro, sin SQLAlchemy ni FastAPI. Define `RecursoNoEncontradoError`, `ReglaNegocioError` y `ConflictoError`. |
| **Infraestructura** (`app/infrastructure`) | `database.py`, modelos ORM, mappers, repositorios y seeders | Persistencia en PostgreSQL. Los repositorios reciben una `Session`, y reciben y devuelven entidades de dominio, convirtiéndolas con los mappers desde y hacia los modelos ORM. |
 
Las excepciones de dominio las lanzan los services y `main.py` las convierte a JSON, por lo que los routers no arman `HTTPException` a mano.
 
## Recorrido de una solicitud
 
Una solicitud, por ejemplo `POST /reservas`, recorre estos pasos:
 
1. El **router** recibe la solicitud HTTP y FastAPI valida el cuerpo con el schema (si falla, responde 422).
2. La dependencia del router arma `Service(Repositorio(db))`, con `db` entregada por `get_db()`.
3. El **service** aplica las reglas de negocio: consulta lo que necesita a los repositorios y, si algo no se cumple, lanza una excepción de dominio.
4. El **repositorio** trabaja con la `Session`, y usa los **mappers** para convertir entre entidades de dominio y **modelos ORM**.
5. **PostgreSQL** ejecuta la consulta.
6. El resultado vuelve por el mismo camino: entidad de dominio → service → router, que lo convierte en un schema de respuesta con su código HTTP (200, 201 o 204).
7. Si hubo una excepción, `main.py` la convierte a la respuesta de error estándar.
Diagrama del recorrido (router → service → repositorio → BD):

```mermaid
flowchart TD
    cliente(["Cliente HTTP o /docs"])

    subgraph PRES["presentation"]
        router["Router (FastAPI)<br/>recibe HTTP, valida el DTO y llama al service"]
    end
    subgraph APP["application"]
        service["Service<br/>reglas de negocio (RN1, RN2, RN3) y costo"]
    end
    subgraph DOM["domain"]
        entidad["Entidades y excepciones<br/>Python puro"]
    end
    subgraph INFRA["infrastructure"]
        repo["Repository<br/>consultas con Session"]
        mapper["Mapper<br/>entidad a modelo y modelo a entidad"]
        modelo["Modelo ORM (SQLAlchemy)"]
    end
    bd[("PostgreSQL")]

    cliente -->|"JSON"| router
    router -->|"DTO"| service
    service -->|"entidad"| repo
    service -.->|"usa"| entidad
    repo --> mapper
    mapper --> modelo
    modelo --> bd
```

Ejemplo concreto, `POST /reservas`:

```mermaid
sequenceDiagram
    actor C as Cliente
    participant R as Router reservas
    participant S as ReservaService
    participant ER as EstacionRepository
    participant RR as ReservaRepository
    participant DB as PostgreSQL

    C->>R: POST /reservas (JSON)
    R->>R: valida ReservaCreate (422 si es inválido)
    Note over R: Depends(get_db) arma el Service con sus repositorios
    R->>S: crear_reserva(datos)
    S->>ER: obtener_por_id(estacion_id)
    ER->>DB: SELECT estaciones
    DB-->>ER: fila
    ER-->>S: Estacion (entidad)
    Note over S: RN2: si no está disponible, ReglaNegocioError (400)
    S->>RR: existe_conflicto(estacion_id, fecha, turno)
    RR->>DB: SELECT EXISTS reservas activas
    DB-->>RR: true o false
    RR-->>S: bool
    Note over S: RN1: si hay conflicto, ConflictoError (409)
    Note over S: costo = tarifa_hora x horas del turno
    S->>RR: guardar(Reserva)
    RR->>DB: INSERT reservas
    DB-->>RR: fila con id
    RR-->>S: Reserva (entidad con id)
    S-->>R: Reserva
    R-->>C: 201 + ReservaResponse
```
 
## Modelo de datos
 
| Entidad | Tabla | Campos |
|---|---|---|
| Cliente | `clientes` | `id`, `nombre`, `correo` (único), `telefono`, `fecha_registro` |
| CategoriaEstacion | `categorias_estacion` | `id`, `nombre`, `tarifa_hora`, `descripcion`, `plataforma` |
| Estacion | `estaciones` | `id`, `codigo` (único), `ubicacion`, `estado`, `categoria_id` (FK) |
| Reserva | `reservas` | `id`, `cliente_id` (FK), `estacion_id` (FK), `fecha`, `turno`, `estado`, `costo` |
 
Relaciones 1:N: una categoría tiene muchas estaciones, un cliente tiene muchas reservas y una estación tiene muchas reservas.
 
Los estados se guardan como texto en la base de datos y el dominio los maneja como `Enum`:
 
- **Estación:** `disponible`, `en_mantencion`, `fuera_de_servicio`
- **Reserva:** `confirmada`, `en_curso`, `completada`, `cancelada`, `no_show`
El turno se escribe como un rango horario, por ejemplo `"10:00-11:00"`.
 
### Diagrama de datos

```mermaid
erDiagram
    CATEGORIAS_ESTACION ||--o{ ESTACIONES : "clasifica"
    CLIENTES ||--o{ RESERVAS : "realiza"
    ESTACIONES ||--o{ RESERVAS : "es reservada en"

    CLIENTES {
        int id PK
        string nombre
        string correo UK
        string telefono
        datetime fecha_registro
    }
    CATEGORIAS_ESTACION {
        int id PK
        string nombre UK
        float tarifa_hora
        string descripcion
        string plataforma
    }
    ESTACIONES {
        int id PK
        string codigo UK
        string ubicacion
        string estado "disponible por defecto"
        int categoria_id FK
    }
    RESERVAS {
        int id PK
        int cliente_id FK
        int estacion_id FK
        date fecha
        string turno "formato HH:MM-HH:MM"
        string estado
        float costo
    }
```

Un índice único parcial sobre `reservas` (`estacion_id`, `fecha`, `turno`, solo para `confirmada` y `en_curso`) respalda la regla RN1 desde la propia base de datos.

### Diagrama de clases (dominio)

```mermaid
classDiagram
    class EstadoEstacion {
        <<enumeration>>
        DISPONIBLE
        EN_MANTENCION
        FUERA_DE_SERVICIO
    }
    class EstadoReserva {
        <<enumeration>>
        CONFIRMADA
        EN_CURSO
        COMPLETADA
        CANCELADA
        NO_SHOW
    }
    class Cliente {
        +int id
        +str nombre
        +str correo
        +str telefono
        +datetime fecha_registro
    }
    class Categoria {
        +int id
        +str nombre
        +float tarifa_hora
        +str descripcion
        +str plataforma
    }
    class Estacion {
        +int id
        +str codigo
        +str ubicacion
        +EstadoEstacion estado
        +int categoria_id
    }
    class Reserva {
        +int id
        +int cliente_id
        +int estacion_id
        +date fecha
        +str turno
        +EstadoReserva estado
        +float costo
    }

    Categoria "1" --> "0..*" Estacion : clasifica
    Cliente "1" --> "0..*" Reserva : realiza
    Estacion "1" --> "0..*" Reserva : es reservada en
    Estacion ..> EstadoEstacion : estado
    Reserva ..> EstadoReserva : estado
```

## Reglas de negocio
 
- **RN1:** no se puede crear una reserva si ya existe otra `confirmada` o `en_curso` para la misma estación, fecha y turno.
- **RN2:** no se puede reservar una estación que esté `en_mantencion` o `fuera_de_servicio`.
- **RN3:** una reserva no puede pasar a `completada` si antes no estaba `en_curso`.
**Costo de la reserva** = `tarifa_hora` de la categoría de la estación × duración del turno en horas.
 
## Contrato REST
 
| # | Método | Ruta | Descripción | Códigos |
|---|--------|------|-------------|---------|
| 1 | POST | `/clientes` | Crea un cliente | 201, 409 (correo duplicado), 422 |
| 2 | GET | `/clientes` | Lista los clientes | 200 |
| 3 | GET | `/clientes/{cliente_id}` | Obtiene un cliente por id | 200, 404, 422 |
| 4 | PATCH | `/clientes/{cliente_id}` | Actualiza los datos de un cliente | 200, 404, 409 (correo duplicado), 422 |
| 5 | DELETE | `/clientes/{cliente_id}` | Elimina un cliente | 204, 404, 409 (tiene reservas) |
| 6 | POST | `/categorias` | Crea una categoría de estación | 201, 409 (nombre duplicado), 422 |
| 7 | GET | `/categorias` | Lista las categorías | 200 |
| 8 | GET | `/categorias/{categoria_id}` | Obtiene una categoría por id | 200, 404, 422 |
| 9 | POST | `/estaciones` | Crea una estación (nace `disponible`) | 201, 404 (categoría no existe), 409 (código duplicado), 422 |
| 10 | GET | `/estaciones` | Lista las estaciones | 200 |
| 11 | GET | `/estaciones/{estacion_id}` | Obtiene una estación por id | 200, 404, 422 |
| 12 | PATCH | `/estaciones/{estacion_id}` | Cambia el estado de una estación | 200, 404, 422 |
| 13 | POST | `/reservas` | Crea una reserva y calcula su costo (RN1, RN2) | 201, 400 (RN2), 404 (estación o cliente no existe), 409 (RN1), 422 |
| 14 | GET | `/reservas` | Lista reservas con filtro por `fecha`, orden (`ordenar_por`: `fecha`, `costo` o `id`; `direccion`: `asc` o `desc`) y paginación (`pagina`, `limite`) | 200, 422 |
| 15 | GET | `/reservas/{reserva_id}` | Obtiene una reserva por id | 200, 404, 422 |
| 16 | PATCH | `/reservas/{reserva_id}` | Cambia el estado de una reserva (RN3) | 200, 400 (RN3), 404, 422 |
| 17 | DELETE | `/reservas/{reserva_id}` | Elimina una reserva | 204, 404 |
 
### Códigos HTTP
 
| Código | Cuándo se usa |
|---|---|
| 200 | Consulta o actualización exitosa |
| 201 | Creación exitosa (todos los `POST`) |
| 204 | Eliminación exitosa (`DELETE`), sin cuerpo |
| 400 | Se viola una regla de negocio (RN2, RN3) |
| 404 | El recurso no existe |
| 409 | Conflicto: RN1, correo duplicado, o eliminar un recurso con dependientes |
| 422 | Datos de entrada inválidos |
| 500 | Error interno del servidor |
 
### Formato de error
 
Todas las respuestas de error usan la misma estructura:
 
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "mensaje descriptivo",
    "details": []
  }
}
```
 
| Código (`code`) | HTTP | Origen |
|---|---|---|
| `RESOURCE_NOT_FOUND` | 404 | `RecursoNoEncontradoError` |
| `BUSINESS_RULE_VIOLATION` | 400 | `ReglaNegocioError` |
| `CONFLICT` | 409 | `ConflictoError` |
| `VALIDATION_ERROR` | 422 | Validación de Pydantic; `details` trae el campo y el mensaje de cada error |
| `INTERNAL_ERROR` | 500 | Cualquier error no controlado (el detalle solo queda en el log del servidor) |
 
## Pruebas
 
Las pruebas son manuales y están en la carpeta `tests_manual/`, un archivo `.http` por recurso (`pruebas_clientes.http`, `pruebas_categorias.http`, `pruebas_estaciones.http`, `pruebas_reservas.http`). Para ejecutarlas:
 
1. Levanta todo como en la sección **Ejecución** (con la base migrada y con datos).
2. Abre el archivo `.http` en VS Code con la extensión **REST Client** y pulsa *Send Request* sobre cada petición. También puedes probar los mismos endpoints desde `/docs`.
3. Compara cada respuesta con el código esperado.
Los resultados quedan registrados en `tests_manual/evidencia_pruebas.md`.
 
## Alcance
 
- No hay autenticación.
- No hay pagos ni notificaciones automáticas (fuera de alcance).
## Integrantes y responsabilidades

| Integrante | Responsabilidad |
|---|---|
| Javier | Estructura por capas del proyecto; services y routers de Estación y Reserva |
| Benito | `database.py`, Alembic y modelos de Cliente y Categoría; repositorios de Cliente y Categoría; migración inicial |
| Kevin | Modelos de Estación y Reserva; repositorios de Estación y Reserva; diagramas y tabla del contrato REST |
| Joaquin | Services y routers de Cliente y Categoría |
| Joako | Seeders y pruebas |
| Sakin | Coordinación y seguimiento; integración técnica (`main.py`, `dependencies.py`, `compose.yml`, `.env.example`, `.gitignore`, `requirements.txt`) y README |
 
### Flujo de trabajo en Git
 
- Cada integrante trabaja en su rama personal y no hace push directo a `main`.
- Mínimo 5 commits propios con mensajes descriptivos ("Agrega ...", "Corrige ...") y 1 pull request a `main`.
- Los pull requests se fusionan en orden y los conflictos se resuelven antes de fusionar.
- El archivo `.env` nunca se sube.