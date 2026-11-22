# Flujo de Recuperación de Contraseña e Invalidación de Sesiones

Este documento detalla el ciclo completo de recuperación de contraseña (`POST /auth/recuperar` y `POST /auth/restablecer`), destacando el almacenamiento exclusivo del hash del token, el consumo atómico de un solo uso y el punto exacto donde se invalidan todas las sesiones activas (`refresh_tokens`).

## 1. Solicitud de Recuperación (`POST /auth/recuperar`)

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario
    participant R as Router (/auth/recuperar)
    participant S as RecuperacionService
    participant UR as UsuarioRepository
    participant TR as TokenRecuperacionRepository
    participant JWT as jwt_handler / token_hash
    participant SMTP as EnviadorCorreo (Mailpit)

    U->>R: POST /auth/recuperar { correo }
    R->>S: solicitar(correo)
    S->>UR: buscar_por_correo(correo)
    UR-->>S: Usuario | None

    alt Usuario existe y está activo
        S->>TR: invalidar_pendientes(usuario_id)
        Note over TR: UPDATE tokens_recuperacion SET usado = true<br/>WHERE usuario_id = :id AND usado = false
        S->>JWT: crear_token_recuperacion(usuario_id)
        JWT-->>S: token_plano (JWT type="recuperacion", 15 min)
        S->>JWT: hashear_refresh(token_plano)
        JWT-->>S: token_hash (SHA-256)
        S->>TR: crear(TokenRecuperacion con token_hash)
        S->>SMTP: enviar_recuperacion(correo, token_plano)
    else Usuario no existe o está inactivo
        Note over S: No realiza acciones ni revela existencia del correo
    end

    S-->>R: { mensaje genérico }
    R-->>U: 200 OK (misma respuesta en ambos casos)