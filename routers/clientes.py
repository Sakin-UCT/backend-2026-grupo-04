from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate, ClienteResponse
from app.repositories.cliente_repo import cliente_repositorio

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def crear_cliente(cliente_in: ClienteCreate):
    return cliente_repositorio.guardar(cliente_in)

@router.get("", response_model=List[ClienteResponse], status_code=status.HTTP_200_OK)
def listar_clientes():
    return cliente_repositorio.obtener_todos()

@router.get("/{cliente_id}", response_model=ClienteResponse, status_code=status.HTTP_200_OK)
def obtener_cliente(cliente_id: int):
    cliente = cliente_repositorio.obtener_por_id(cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": f"No existe un cliente con el ID {cliente_id}",
                    "details": []
                }
            }
        )
    return cliente

@router.patch("/{cliente_id}", response_model=ClienteResponse, status_code=status.HTTP_200_OK)
def actualizar_cliente(cliente_id: int, cliente_in: ClienteUpdate):
    cliente_actualizado = cliente_repositorio.actualizar(cliente_id, cliente_in)
    if not cliente_actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": f"No existe un cliente con el ID {cliente_id}",
                    "details": []
                }
            }
        )
    return cliente_actualizado

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(cliente_id: int):
    eliminado = cliente_repositorio.eliminar(cliente_id)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": f"No existe un cliente con el ID {cliente_id}",
                    "details": []
                }
            }
        )
    return None