from app.domain.usuario import Perfil, RefreshToken, TokenRecuperacion, Usuario
from app.infrastructure.models.refresh_token_model import RefreshTokenModel
from app.infrastructure.models.token_recuperacion_model import TokenRecuperacionModel
from app.infrastructure.models.usuario_model import UsuarioModel


def a_dominio(modelo: UsuarioModel) -> Usuario:
    return Usuario(
        id=modelo.id,
        correo=modelo.correo,
        password_hash=modelo.password_hash,
        perfil=Perfil(modelo.perfil),
        cliente_id=modelo.cliente_id,
        intentos_fallidos=modelo.intentos_fallidos,
        bloqueado_hasta=modelo.bloqueado_hasta,
        activo=modelo.activo,
        fecha_creacion=modelo.fecha_creacion,
    )


def a_modelo(entidad: Usuario) -> UsuarioModel:
    return UsuarioModel(
        id=entidad.id,
        correo=entidad.correo,
        password_hash=entidad.password_hash,
        perfil=entidad.perfil.value
        if isinstance(entidad.perfil, Perfil)
        else str(entidad.perfil),
        cliente_id=entidad.cliente_id,
        intentos_fallidos=entidad.intentos_fallidos,
        bloqueado_hasta=entidad.bloqueado_hasta,
        activo=entidad.activo,
        fecha_creacion=entidad.fecha_creacion,
    )


def refresh_token_a_dominio(modelo: RefreshTokenModel) -> RefreshToken:
    return RefreshToken(
        id=modelo.id,
        usuario_id=modelo.usuario_id,
        token_hash=modelo.token_hash,
        expira_en=modelo.expira_en,
        revocado=modelo.revocado,
        reemplazado_por=modelo.reemplazado_por,
        creado_en=modelo.creado_en,
    )


def refresh_token_a_modelo(entidad: RefreshToken) -> RefreshTokenModel:
    return RefreshTokenModel(
        id=entidad.id,
        usuario_id=entidad.usuario_id,
        token_hash=entidad.token_hash,
        expira_en=entidad.expira_en,
        revocado=entidad.revocado,
        reemplazado_por=entidad.reemplazado_por,
        creado_en=entidad.creado_en,
    )


def token_recuperacion_a_dominio(modelo: TokenRecuperacionModel) -> TokenRecuperacion:
    return TokenRecuperacion(
        id=modelo.id,
        usuario_id=modelo.usuario_id,
        token_hash=modelo.token_hash,
        expira_en=modelo.expira_en,
        usado=modelo.usado,
        creado_en=modelo.creado_en,
    )


def token_recuperacion_a_modelo(entidad: TokenRecuperacion) -> TokenRecuperacionModel:
    return TokenRecuperacionModel(
        id=entidad.id,
        usuario_id=entidad.usuario_id,
        token_hash=entidad.token_hash,
        expira_en=entidad.expira_en,
        usado=entidad.usado,
        creado_en=entidad.creado_en,
    )
