from datetime import date, datetime, timezone
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.domain.usuario import Perfil
from app.infrastructure.database import SessionLocal
from app.infrastructure.models.categoria_model import CategoriaModel
from app.infrastructure.models.cliente_model import ClienteModel
from app.infrastructure.models.estacion_model import EstacionModel
from app.infrastructure.models.reserva_model import ReservaModel
from app.infrastructure.models.usuario_model import UsuarioModel
from app.infrastructure.security.password import hashear_password

load_dotenv()


def get_or_create_categoria(db: Session, nombre: str, **kwargs) -> CategoriaModel:
    existente = db.query(CategoriaModel).filter(CategoriaModel.nombre == nombre).first()
    if existente:
        return existente

    columnas = {c.name for c in CategoriaModel.__table__.columns}
    datos = {"nombre": nombre, **{k: v for k, v in kwargs.items() if k in columnas}}
    nueva = CategoriaModel(**datos)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


def get_or_create_cliente(db: Session, correo: str, **kwargs) -> ClienteModel:
    existente = db.query(ClienteModel).filter(ClienteModel.correo == correo).first()
    if existente:
        return existente

    columnas = {c.name for c in ClienteModel.__table__.columns}
    datos = {"correo": correo, **{k: v for k, v in kwargs.items() if k in columnas}}
    nuevo = ClienteModel(**datos)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def get_or_create_estacion(db: Session, codigo: str, **kwargs) -> EstacionModel:
    existente = db.query(EstacionModel).filter(EstacionModel.codigo == codigo).first()
    if existente:
        return existente

    columnas = {c.name for c in EstacionModel.__table__.columns}
    datos = {"codigo": codigo, **{k: v for k, v in kwargs.items() if k in columnas}}
    nueva = EstacionModel(**datos)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


def get_or_create_reserva(
    db: Session,
    cliente_id: int,
    estacion_id: int,
    fecha: date,
    turno: str,
    **kwargs,
) -> ReservaModel:
    existente = (
        db.query(ReservaModel)
        .filter(
            ReservaModel.estacion_id == estacion_id,
            ReservaModel.fecha == fecha,
            ReservaModel.turno == turno,
        )
        .first()
    )
    if existente:
        return existente

    columnas = {c.name for c in ReservaModel.__table__.columns}
    datos = {
        "cliente_id": cliente_id,
        "estacion_id": estacion_id,
        "fecha": fecha,
        "turno": turno,
        **{k: v for k, v in kwargs.items() if k in columnas},
    }
    nueva = ReservaModel(**datos)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


def get_or_create_usuario(
    db: Session,
    correo: str,
    password_plana: str,
    perfil: Perfil,
    cliente_id: int | None = None,
) -> UsuarioModel:
    existente = db.query(UsuarioModel).filter(UsuarioModel.correo == correo).first()
    if existente:
        return existente

    nuevo = UsuarioModel(
        correo=correo,
        password_hash=hashear_password(password_plana),
        perfil=perfil.value,
        cliente_id=cliente_id,
        intentos_fallidos=0,
        bloqueado_hasta=None,
        activo=True,
        fecha_creacion=datetime.now(timezone.utc),
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def run_seed() -> None:
    db = SessionLocal()
    try:
        print("Iniciando carga de datos de prueba (seed)...")

        cat_pc = get_or_create_categoria(
            db,
            nombre="PC Gama Alta",
            tarifa_hora=4500.0,
            descripcion="PC Gamer con RTX 4080, 32GB RAM y monitor 240Hz",
            plataforma="PC",
        )
        cat_ps5 = get_or_create_categoria(
            db,
            nombre="PS5",
            tarifa_hora=3500.0,
            descripcion="Consola PlayStation 5 con 2 mandos DualSense y TV 4K 120Hz",
            plataforma="Consola",
        )
        print(f"Categorías listas: IDs {cat_pc.id}, {cat_ps5.id}")

        cli_1 = get_or_create_cliente(
            db,
            correo="benito@gamer.cl",
            nombre="Benito Carbonell",
            telefono="+56911112222",
            fecha_registro=datetime.now(timezone.utc),
        )
        cli_2 = get_or_create_cliente(
            db,
            correo="joako@gamer.cl",
            nombre="Joaquín Pruebas",
            telefono="+56933334444",
            fecha_registro=datetime.now(timezone.utc),
        )
        print(f"Clientes listos: IDs {cli_1.id}, {cli_2.id}")

        est_disponible = get_or_create_estacion(
            db,
            codigo="PC-01",
            ubicacion="Zona VIP - Box 1",
            estado="disponible",
            categoria_id=cat_pc.id,
        )
        est_mantencion = get_or_create_estacion(
            db,
            codigo="PS5-01",
            ubicacion="Zona Consolas - Box 2",
            estado="en_mantencion",
            categoria_id=cat_ps5.id,
        )
        print(
            f"Estaciones listas: IDs {est_disponible.id} ({est_disponible.estado}), "
            f"{est_mantencion.id} ({est_mantencion.estado})"
        )

        res_1 = get_or_create_reserva(
            db,
            cliente_id=cli_1.id,
            estacion_id=est_disponible.id,
            fecha=date(2026, 11, 10),
            turno="10:00-12:00",
            estado="confirmada",
            costo=9000.0,
        )
        res_2 = get_or_create_reserva(
            db,
            cliente_id=cli_2.id,
            estacion_id=est_disponible.id,
            fecha=date(2026, 11, 10),
            turno="15:00-16:00",
            estado="en_curso",
            costo=4500.0,
        )
        print(f"Reservas listas: IDs {res_1.id}, {res_2.id}")

        pass_encargado = os.getenv("SEED_ENCARGADO_PASSWORD")
        pass_cliente = os.getenv("SEED_CLIENTE_PASSWORD")
        if not pass_encargado or not pass_cliente:
            raise ValueError(
                "Faltan SEED_ENCARGADO_PASSWORD o SEED_CLIENTE_PASSWORD en las variables de entorno."
            )

        usr_encargado = get_or_create_usuario(
            db,
            correo="encargado@gamer.cl",
            password_plana=pass_encargado,
            perfil=Perfil.ENCARGADO,
            cliente_id=None,
        )
        usr_cliente = get_or_create_usuario(
            db,
            correo="joako@gamer.cl",
            password_plana=pass_cliente,
            perfil=Perfil.CLIENTE,
            cliente_id=cli_2.id,
        )
        print(f"Usuarios demo listos: IDs {usr_encargado.id}, {usr_cliente.id}")
        print("Seed ejecutado exitosamente (idempotente).")

    except Exception as e:
        db.rollback()
        print(f"Error al ejecutar el seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
