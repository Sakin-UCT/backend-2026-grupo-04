# Diagramas de autenticación — Javier

## 1. Responsabilidad

Implementación de la autenticación de usuarios, administración de
sesiones y protección de los endpoints de estaciones y reservas.

## 2. Arquitectura

```mermaid
flowchart TD
    A[Petición HTTP] --> B[Router auth.py]
    B --> C[Schemas Pydantic]
    C --> D[AuthService]
    D --> E[Entidades de dominio]
    D --> F[Repositorios]
    D --> G[Funciones de seguridad inyectadas]
    F --> H[Mappers]
    H --> I[Modelos ORM]
    I --> J[(PostgreSQL)]
```

El router recibe las peticiones HTTP y delega las operaciones
al servicio de autenticación.

AuthService contiene las reglas de negocio y recibe los
repositorios y funciones criptográficas mediante inyección
de dependencias.

Los repositorios gestionan la persistencia de las entidades
de dominio utilizando los mappers y modelos ORM.

## 3. Registro de usuario

```mermaid
sequenceDiagram
    participant C as Cliente HTTP
    participant R as Router
    participant S as AuthService
    participant U as UsuarioRepository
    participant BD as PostgreSQL

    C->>R: POST /auth/registro
    R->>S: registrar correo y password
    S->>U: buscar_por_correo
    U->>BD: Consultar usuario
    BD-->>U: Resultado
    U-->>S: Usuario existente o None

    alt Correo registrado
        S-->>R: ConflictoError
        R-->>C: HTTP 409
    else Correo disponible
        S->>S: Hashear password con Argon2id
        S->>U: Crear usuario con perfil cliente
        U->>BD: Guardar usuario
        U-->>S: Usuario creado
        S-->>R: Usuario
        R-->>C: HTTP 201
    end
```

La contraseña nunca se almacena en texto plano.
El usuario registrado recibe el perfil cliente.

## 4. Inicio de sesión

```mermaid
sequenceDiagram
    participant C as Cliente HTTP
    participant R as Router
    participant S as AuthService
    participant U as UsuarioRepository
    participant T as RefreshTokenRepository

    C->>R: POST /auth/login
    R->>S: login correo y password
    S->>U: buscar_por_correo
    U-->>S: Usuario

    alt Credenciales válidas y usuario activo
        S->>S: Reiniciar intentos fallidos
        S->>U: Actualizar usuario
        S->>S: Generar access token
        S->>S: Generar refresh token y hash
        S->>T: Guardar hash del refresh token
        T-->>S: RefreshToken
        S-->>R: Sesion
        R->>R: Establecer cookies
        R-->>C: HTTP 200 y access token
    else Credenciales inválidas o cuenta bloqueada
        S-->>R: NoAutenticadoError
        R-->>C: HTTP 401
    end
```

El access token tiene una duración de 15 minutos.
El refresh token tiene una duración de 7 días.

El refresh token se almacena en una cookie HttpOnly.
En PostgreSQL se almacena únicamente su hash SHA-256.

## 5. Bloqueo de cuenta

```mermaid
flowchart TD
    A[Intento de login] --> B{Usuario existe y activo}
    B -->|No| C[HTTP 401]
    B -->|Sí| D{Cuenta bloqueada}
    D -->|Sí| C
    D -->|No| E{Password correcta}
    E -->|Sí| F[Reiniciar intentos fallidos]
    F --> G[Emitir sesión]
    E -->|No| H[Aumentar intentos fallidos]
    H --> I{Cinco intentos o más}
    I -->|Sí| J[Bloquear durante 15 minutos]
    I -->|No| K[Actualizar usuario]
    J --> K
    K --> C
```

Los errores de credenciales utilizan un mensaje genérico
para no revelar si el correo existe.

## 6. Renovación de sesión

```mermaid
flowchart TD
    A[POST /auth/refresh] --> B{CSRF válido}
    B -->|No| C[HTTP 403]
    B -->|Sí| D[Obtener refresh token de cookie]
    D --> E[Calcular hash]
    E --> F[Buscar token en repositorio]
    F --> G{Token existe}
    G -->|No| H[HTTP 401]
    G -->|Sí| I{Token revocado}
    I -->|Sí| J[Revocar todos los tokens del usuario]
    J --> H
    I -->|No| K{Token expirado}
    K -->|Sí| H
    K -->|No| L{Usuario activo}
    L -->|No| H
    L -->|Sí| M[Emitir nueva sesión]
    M --> N[Revocar refresh token anterior]
    N --> O[Actualizar cookies]
    O --> P[HTTP 200]
```

Cada renovación genera un nuevo refresh token.

Si se intenta reutilizar un token revocado, se revocan
todos los refresh tokens asociados al usuario.

## 7. Cierre de sesión

```mermaid
sequenceDiagram
    participant C as Cliente HTTP
    participant R as Router
    participant S as AuthService
    participant T as RefreshTokenRepository

    C->>R: POST /auth/logout con CSRF
    R->>R: Verificar CSRF
    R->>S: logout refresh token
    S->>T: buscar_por_hash

    opt Token existente y no revocado
        S->>T: Revocar token
    end

    S-->>R: Operación completada
    R->>R: Eliminar cookies
    R-->>C: HTTP 204
```

El cierre de sesión revoca el refresh token y elimina
las cookies de autenticación.

El access token previamente emitido puede continuar
siendo válido hasta su expiración, ya que no existe
una lista de revocación de access tokens.

## 8. Protección de endpoints

| Endpoint | Autenticación | Perfil |
| --- | --- | --- |
| POST /auth/registro | No | Público |
| POST /auth/login | No | Público |
| POST /auth/refresh | Refresh y CSRF | Usuario activo |
| POST /auth/logout | CSRF | Según sesión |
| GET /auth/me | Bearer JWT | Cualquiera |
| GET /estaciones | No | Público |
| GET /estaciones/{id} | No | Público |
| POST /estaciones | Bearer JWT | Cualquiera |
| PATCH /estaciones/{id} | Bearer JWT | Encargado |
| GET /reservas | Bearer JWT | Cualquiera |
| GET /reservas/{id} | Bearer JWT | Cualquiera |
| POST /reservas | Bearer JWT | Cualquiera |
| PATCH /reservas/{id} | Bearer JWT | Cualquiera |
| DELETE /reservas/{id} | Bearer JWT | Cualquiera |

## 9. Pruebas

### Unitarias

Archivo: tests/unit/test_auth_service.py

- Inicio de sesión correcto.
- Mensaje genérico para credenciales inválidas.
- Bloqueo después de cinco intentos fallidos.
- Revocación de sesiones por reutilización de refresh token.

### End-to-end

Archivo: tests/e2e/test_acceso_negocio.py

- Rechazo de peticiones sin autenticación.
- Registro de usuario.
- Inicio de sesión.
- Consulta del usuario autenticado.
- Creación y consulta de una reserva.
- Eliminación de la reserva de prueba.
- Cierre de sesión.
- Rechazo de refresh token revocado.

Las pruebas E2E utilizan httpx contra una instancia real
de la API conectada a PostgreSQL.

## 10. Archivos asociados

- app/domain/excepciones.py
- app/application/services/auth_service.py
- app/application/services/estacion_service.py
- app/application/services/reserva_service.py
- app/presentation/routers/auth.py
- app/presentation/routers/estaciones.py
- app/presentation/routers/reservas.py
- tests/unit/test_auth_service.py
- tests/e2e/test_acceso_negocio.py
- docs/diagramas/auth_javier.md