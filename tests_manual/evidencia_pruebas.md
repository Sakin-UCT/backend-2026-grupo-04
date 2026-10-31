# Evidencias de Pruebas Manuales — API Centro Gamer (Grupo 04)

Responsable de Calidad y Pruebas: **Joako (Grupo 04)**

---

## 1. Procedimiento para Restablecer los Datos (Reset Limpio)

Antes de ejecutar la batería de pruebas manuales (`.http`), se debe restablecer la base de datos PostgreSQL desde cero aplicando las migraciones de Alembic y cargando los datos iniciales idempotentes del seeder:

```bash
# 1. Detener contenedores y eliminar volúmenes previos (borra datos antiguos)
docker compose down -v

# 2. Levantar nuevamente el contenedor de PostgreSQL (y pgAdmin) en segundo plano
docker compose up -d

# 3. Aplicar las migraciones para crear las tablas del esquema en la BD limpia
alembic upgrade head

# 4. Poblar la base de datos con los registros iniciales de prueba (idempotente)
python -m app.infrastructure.seeders.seed

# 5. (Opcional) Verificar idempotencia corriendo el seeder una segunda vez sin duplicar datos
python -m app.infrastructure.seeders.seed

# 6. Iniciar el servidor de desarrollo FastAPI
uvicorn app.main:app --reload
```

### Datos base generados por `seed.py`
* **Categorías:** ID `1` (`"PC Gama Alta"`, tarifa `4500.0`/h, `"PC"`) e ID `2` (`"PS5"`, tarifa `3500.0`/h, `"Consola"`).
* **Clientes:** ID `1` (`benito@gamer.cl`) e ID `2` (`joako@gamer.cl`).
* **Estaciones:** ID `1` (`"PC-01"`, estado `"disponible"`, categoría `1`) e ID `2` (`"PS5-01"`, estado `"en_mantencion"`, categoría `2`).
* **Reservas:**
  * ID `1`: Cliente `1`, Estación `1`, Fecha `2026-11-10`, Turno `"10:00-12:00"` (2h), Estado `"confirmada"`, Costo `9000.0`.
  * ID `2`: Cliente `2`, Estación `1`, Fecha `2026-11-10`, Turno `"15:00-16:00"` (1h), Estado `"en_curso"`, Costo `4500.0`.

---

## 2. Tabla de Casos de Prueba Ejecutados

| # | Caso de Prueba | Entrada (Método, Ruta y Payload / Query) | Resultado Esperado | Resultado Obtenido |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Crear cliente válido (CRUD POST)** | `POST /clientes/` <br> `{"nombre": "Camila Soto", "correo": "camila.soto@gamer.cl", "telefono": "+56955556666"}` | **201 Created** <br> JSON con `id: 3`, `nombre`, `correo`, `telefono` y `fecha_registro`. | **201 Created** <br> Cliente creado y persistido con `id: 3`. |
| **2** | **Conflicto por correo duplicado** | `POST /clientes/` <br> `{"nombre": "Otro Benito", "correo": "benito@gamer.cl", "telefono": "+56999998888"}` | **409 Conflict** <br> `{"error": {"code": "CONFLICT", "message": "...", "details": []}}` | **409 Conflict** <br> Error controlado con código `CONFLICT` al existir `benito@gamer.cl` en el seed. |
| **3** | **Eliminar cliente con reservas asociadas** | `DELETE /clientes/1` <br> *(El cliente ID 1 posee la reserva ID 1 del seed)* | **409 Conflict** <br> `{"error": {"code": "CONFLICT", "message": "...", "details": []}}` | **409 Conflict** <br> Se impide el borrado por integridad referencial y se retorna estructura estándar de error. |
| **4** | **Recurso inexistente (404)** | `GET /categorias/999` | **404 Not Found** <br> `{"error": {"code": "RESOURCE_NOT_FOUND", "message": "...", "details": []}}` | **404 Not Found** <br> Respuesta JSON con código `RESOURCE_NOT_FOUND`. |
| **5** | **Validación de formato inválido (422)** | `POST /clientes/` <br> `{"nombre": "J", "correo": "correo-sin-arroba", "telefono": "+569123"}` | **422 Unprocessable Entity** <br> `{"error": {"code": "VALIDATION_ERROR", "message": "...", "details": [...]}}` | **422 Unprocessable Entity** <br> Rechazado por Pydantic (`min_length=2` en nombre y formato `EmailStr` en correo). |
| **6** | **Regla de Negocio RN1 (Solapamiento de turno)** | `POST /reservas/` <br> `{"cliente_id": 2, "estacion_id": 1, "fecha": "2026-11-10", "turno": "10:00-12:00"}` | **409 Conflict** <br> `{"error": {"code": "CONFLICT", "message": "...", "details": []}}` | **409 Conflict** <br> Rechaza la reserva porque la Estación 1 ya tiene una reserva `confirmada` en esa fecha y turno. |
| **7** | **Regla de Negocio RN2 (Estación no disponible)** | `POST /reservas/` <br> `{"cliente_id": 1, "estacion_id": 2, "fecha": "2026-11-10", "turno": "12:00-14:00"}` | **400 Bad Request** <br> `{"error": {"code": "BUSINESS_RULE_VIOLATION", "message": "...", "details": []}}` | **400 Bad Request** <br> Rechaza la reserva porque la Estación 2 (`PS5-01`) se encuentra en estado `en_mantencion`. |
| **8** | **Regla de Negocio RN3 (Completar sin estar en_curso)** | `PATCH /reservas/1` <br> `{"estado": "completada"}` *(Reserva ID 1 está `confirmada`)* | **400 Bad Request** <br> `{"error": {"code": "BUSINESS_RULE_VIOLATION", "message": "...", "details": []}}` | **400 Bad Request** <br> Impide pasar a `completada` una reserva que no estaba previamente en estado `en_curso`. |
| **9** | **Consulta con filtro, orden y paginación** | `GET /reservas/?fecha=2026-11-10&ordenar_por=costo&direccion=desc&pagina=1&limite=5` | **200 OK** <br> Objeto paginado (`items`, `total`, `pagina`, `limite`, `total_paginas`) ordenado por costo descendente (`9000.0` primero). | **200 OK** <br> Retorna las reservas del `2026-11-10` ordenadas de mayor a menor costo con metadatos de paginación. |
| **10** | **Persistencia tras reinicio de API y BD** | Crear Categoría ID `3` (`POST /categorias/`), reiniciar Uvicorn y contenedor Docker de PostgreSQL, luego consultar `GET /categorias/3`. | **200 OK** <br> Los datos de la categoría ID `3` permanecen intactos tras el reinicio. | **200 OK** <br> Retorna `"Simulador Racing VR"` (`id: 3`, `tarifa_hora: 6000.0`) desde el volumen persistente de PostgreSQL. |

---

## 3. Pasos para Probar la Persistencia de Datos

Para demostrar que la información ya no vive en memoria RAM sino en el volumen persistente de PostgreSQL:

1. **Crear un registro nuevo mediante la API:**
   Ejecutar desde `tests_manual/pruebas_categorias.http` la petición `POST http://127.0.0.1:8000/categorias/`:
   ```json
   {
     "nombre": "Simulador Racing VR",
     "tarifa_hora": 6000.0,
     "descripcion": "Cockpit con volante Direct Drive, pedales Load Cell y visor VR",
     "plataforma": "Simulador"
   }
   ```
   Verificar que responde `201 Created` devolviendo el registro con `"id": 3`.

2. **Reiniciar la API y el contenedor de Base de Datos (sin `-v`):**
   * Detener el proceso de `uvicorn` en la terminal (`Ctrl + C`).
   * Reiniciar el contenedor de PostgreSQL en Docker:
     ```bash
     docker compose restart
     ```
   * Volver a levantar la API:
     ```bash
     uvicorn app.main:app --reload
     ```

3. **Comprobar la persistencia con un `GET`:**
   Ejecutar la petición:
   ```http
   GET http://127.0.0.1:8000/categorias/3
   Accept: application/json
   ```
   **Resultado comprobado:** La API responde `200 OK` con los datos exactos de `"Simulador Racing VR"`, confirmando que los datos persisten en disco en PostgreSQL tras apagar y encender tanto la API como el motor de base de datos.