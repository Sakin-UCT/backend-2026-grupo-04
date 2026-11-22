```mermaid
erDiagram
    CLIENTES {
        int id PK
    }
    CATEGORIAS {
        int id PK
    }
    ESTACIONES {
        int id PK
        int categoria_id FK
    }
    RESERVAS {
        int id PK
        int cliente_id FK
        int estacion_id FK
    }
    USUARIOS {
        int id PK
        string correo UK
        string password_hash
        string perfil
        int cliente_id FK
        int intentos_fallidos
        datetime bloqueado_hasta
        bool activo
        datetime fecha_creacion
    }
    REFRESH_TOKENS {
        int id PK
        int usuario_id FK
        string token_hash UK
        datetime expira_en
        bool revocado
        int reemplazado_por
        datetime creado_en
    }
    TOKENS_RECUPERACION {
        int id PK
        int usuario_id FK
        string token_hash UK
        datetime expira_en
        bool usado
        datetime creado_en
    }

    CLIENTES ||--o{ USUARIOS : "cliente_id opcional"
    CLIENTES ||--o{ RESERVAS : "cliente_id"
    CATEGORIAS ||--o{ ESTACIONES : "categoria_id"
    ESTACIONES ||--o{ RESERVAS : "estacion_id"
    USUARIOS ||--o{ REFRESH_TOKENS : "usuario_id"
    USUARIOS ||--o{ TOKENS_RECUPERACION : "usuario_id"