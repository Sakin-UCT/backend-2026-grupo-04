import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.domain.excepciones import (
    ConflictoError,
    ReglaNegocioError,
    RecursoNoEncontradoError,
)

from app.presentation.routers import clientes, categorias, estaciones, reservas

logger = logging.getLogger(__name__)

app = FastAPI(title="API Centro Gamer",
    description=(
        "API REST para gestionar clientes, categorías y estaciones de un centro "
        "gamer, y reservar estaciones por turno. Los datos se guardan en "
        "PostgreSQL y el esquema se crea con Alembic."
    )
    ,version="1.0.0")

app.include_router(clientes.router)
app.include_router(categorias.router)
app.include_router(estaciones.router)
app.include_router(reservas.router)


@app.get("/", tags=["Raíz"], summary="Estado de la API")
def root():
    return {"mensaje": "API Centro Gamer funcionando. Ver documentación en /docs"}


CODIGOS_POR_STATUS = {
    400: "BAD_REQUEST",
    404: "RESOURCE_NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
}


def _error(status_code: int, code: str, message: str, details: list | None = None):
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details or []}},
    )


@app.exception_handler(StarletteHTTPException)
async def manejador_http_exception(request: Request, exc: StarletteHTTPException):
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    return _error(
        exc.status_code,
        CODIGOS_POR_STATUS.get(exc.status_code, "ERROR"),
        str(exc.detail),
    )


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