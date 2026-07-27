# Backend

API REST principal del proyecto, desarrollada con Java y Spring Boot. Valida la entrada, llama al servicio de inferencia para obtener la clasificación, completa la respuesta con costo estimado y recomendaciones, y guarda cada análisis para poder consultarlo después.

> Arquitectura global, flujo completo y **contrato único** de la API: ver `../docs/` y `../docs/contrato-api.md`. Este README es operativo.

> Reparto por frentes: ver "Frentes de trabajo" en la documentación de No Country.

## Cómo correr

```bash
# desde backend/
./mvnw spring-boot:run
```

- API: `http://localhost:8080`
- Swagger UI: `http://localhost:8080/swagger-ui.html`

## Variables de entorno

| Variable | Descripción | Ejemplo |
|---|---|---|
| `INFERENCE_SERVICE_URL` | URL del servicio Python de inferencia | `http://localhost:8000` |
| `TARIFA_REFERENCIA_KWH` | Tarifa por kWh (R$) | `0.75` |
| `MONEDA` | Moneda de referencia | `BRL` |
| `SPRING_DATASOURCE_URL` | Conexión a la base de datos | `jdbc:h2:mem:energiai` |
| `SPRING_DATASOURCE_USERNAME` | Usuario de la base de datos | `sa` |
| `SPRING_DATASOURCE_PASSWORD` | Contraseña de la base de datos | — |

> El motor de base de datos **todavía no está decidido** (ver `../docs/decisiones.md`, D12). El ejemplo usa H2 en memoria por ser lo más rápido de levantar; la decisión final la cierra este frente.

## Endpoints

Los dos son **obligatorios** según la descripción del proyecto. Detalle completo en `../docs/contrato-api.md`.

| Endpoint | Qué hace |
|---|---|
| `POST /analisis-energetico` | Recibe los datos de consumo, devuelve categoría, probabilidad, costo y recomendaciones |
| `GET /resultados/{id}` | Recupera un análisis previo por su identificador |
| `GET /resultados` *(opcional)* | Lista los análisis más recientes; útil para la demo |

## Responsabilidades del módulo

- Exponer los **dos endpoints** según el contrato único (`../docs/contrato-api.md`).
- **Validación** de entrada (campos requeridos, tipos, rangos) y **manejo de errores** con códigos HTTP claros (400, 404, 502, 500).
- Llamar al `inference-service` para obtener `categoria` + `probabilidad`. Se le envían **solo las 5 variables obligatorias**, nunca el campo `equipos`.
- Calcular `costo_estimado_mensual = consumo_kwh × TARIFA_REFERENCIA_KWH`.
- Completar `id`, `fecha_analisis`, `moneda` y `tarifa_referencia_kwh` en la respuesta.
- Generar `recomendaciones` por reglas según categoría y variables de mayor impacto.
- Usar el campo opcional `equipos` para las **recomendaciones específicas por aparato** (tabla y lógica de desglose en `../docs/consumo-por-aparato.md`).
- **Persistir cada análisis** (ver abajo).
- Documentar endpoints con OpenAPI/Swagger.

## Persistencia (obligatoria)

No es opcional: el endpoint `GET /resultados/{id}` no puede existir sin guardar los análisis. Registro mínimo:

| Campo | Descripción |
|---|---|
| `id` | UUID generado por el backend |
| `fecha_analisis` | timestamp |
| las 5 entradas | tal como llegaron |
| `equipos` | lista opcional (JSON o texto) |
| `categoria`, `probabilidad` | respuesta del modelo |
| `costo_estimado_mensual` | calculado |

**Qué NO se guarda aquí:** los microdatos de ENCEVI, el dataset de entrenamiento ni el modelo. El modelo vive en OCI Object Storage; la base de datos solo guarda el historial de consultas.

## Sobre `consumo_kwh`

Es **siempre obligatorio**. Si el usuario no conoce su consumo, el **frontend** lo estima a partir de los aparatos seleccionados y envía el valor ya calculado. El backend nunca recibe una petición sin ese campo y **no estima nada**.

## Estado de integración

Mientras el modelo real no esté listo, trabajar contra un **mock** del `inference-service` que respete el contrato. No bloquear el avance del backend por el modelo.

## Estructura sugerida

```
backend/
├── src/main/java/.../controller/
├── src/main/java/.../service/
├── src/main/java/.../dto/
├── src/main/java/.../model/        # entidad del análisis persistido
├── src/main/java/.../repository/   # acceso a la base de datos
├── src/main/java/.../client/       # cliente HTTP al inference-service
└── src/main/resources/application.yml
```

## Estado

La estructura del proyecto Spring Boot todavía no ha sido inicializada.
