from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from routers import clientes, categorias, estaciones, reservas

app = FastAPI(title="API Centro Gamer", version="1.0.0")

app.include_router(clientes.router)
app.include_router(categorias.router)
app.include_router(estaciones.router)
app.include_router(reservas.router)


@app.get("/")
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