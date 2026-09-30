from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

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
