import logging
import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.domain.excepciones import (
    ConflictoError,
    NoAutenticadoError,
    RecursoNoEncontradoError,
    ReglaNegocioError,
    SinPermisoError,
)
from app.infrastructure.database import engine
from app.presentation.routers import clientes, categorias, estaciones, reservas, auth, recuperacion

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

GIT_SHA = os.getenv("GIT_SHA", "desconocido")


app = FastAPI(
    title="API Centro Gamer",
    description="API REST para gestionar clientes, categorías y estaciones de un centro gamer.",
    version="1.0.0",
)


ORIGENES = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
if "*" in ORIGENES:
    raise RuntimeError("CORS_ORIGINS no puede contener '*' si se usan credenciales")


app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
)


app.include_router(auth.router)
app.include_router(recuperacion.router)
app.include_router(clientes.router)
app.include_router(categorias.router)
app.include_router(estaciones.router)
app.include_router(reservas.router)


def _openapi_con_bearer():
    if app.openapi_schema:
        return app.openapi_schema
    esquema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    esquema.setdefault("components", {}).setdefault("securitySchemes", {})["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    app.openapi_schema = esquema
    return esquema


app.openapi = _openapi_con_bearer


@app.get("/", tags=["Raíz"], summary="Estado de la API")
def root():
    return {"mensaje": "API Centro Gamer funcionando. Ver documentación en /docs"}


@app.get("/salud", tags=["Estado"], summary="Salud del servicio")
def salud():
    try:
        with engine.connect() as conexion:
            conexion.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("Fallo de conexión a la BD en /salud: %s", type(exc).__name__)
        return JSONResponse(
            status_code=503,
            content={"estado": "error", "base_datos": "inaccesible", "commit": GIT_SHA},
        )
    return {"estado": "ok", "base_datos": "ok", "commit": GIT_SHA}


CODIGOS_POR_STATUS = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "RESOURCE_NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
}


def _error(status_code: int, code: str, message: str, details=None, headers=None):
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details or []}},
        headers=headers,
    )


@app.exception_handler(StarletteHTTPException)
async def manejador_http_exception(request: Request, exc: StarletteHTTPException):
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    cabeceras = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    return _error(
        exc.status_code,
        CODIGOS_POR_STATUS.get(exc.status_code, "ERROR"),
        str(exc.detail),
        headers=cabeceras,
    )


@app.exception_handler(NoAutenticadoError)
async def manejador_no_autenticado(request: Request, exc: NoAutenticadoError):
    return _error(401, "UNAUTHORIZED", str(exc), headers={"WWW-Authenticate": "Bearer"})


@app.exception_handler(SinPermisoError)
async def manejador_sin_permiso(request: Request, exc: SinPermisoError):
    return _error(403, "FORBIDDEN", str(exc))


@app.exception_handler(RequestValidationError)
async def manejador_validacion(request: Request, exc: RequestValidationError):
    detalles = [
        {
            "campo": ".".join(str(parte) for parte in err["loc"]),
            "mensaje": err["msg"],
        }
        for err in exc.errors()
    ]
    return _error(422, "VALIDATION_ERROR", "Los datos enviados no son válidos", detalles)

@app.exception_handler(RecursoNoEncontradoError)
async def manejador_no_encontrado(request: Request, exc: RecursoNoEncontradoError):
    return _error(404, "RESOURCE_NOT_FOUND", str(exc))
 
 
@app.exception_handler(ReglaNegocioError)
async def manejador_regla_negocio(request: Request, exc: ReglaNegocioError):
    return _error(400, "BUSINESS_RULE_VIOLATION", str(exc))
 
 
@app.exception_handler(ConflictoError)
async def manejador_conflicto(request: Request, exc: ConflictoError):
    return _error(409, "CONFLICT", str(exc))
 
 
@app.exception_handler(Exception)
async def manejador_generico(request: Request, exc: Exception):
    logger.exception("Error no controlado en %s %s", request.method, request.url.path)
    return _error(500, "INTERNAL_ERROR", "Error interno del servidor")