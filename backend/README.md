# Backend

API REST principal del proyecto, desarrollada con Java y Spring Boot. Valida la entrada, llama al servicio de inferencia para obtener la clasificación, y completa la respuesta con costo estimado y recomendaciones.

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

## Responsabilidades del módulo

- Exponer `POST /analisis-energetico` según el contrato único (`../docs/contrato-api.md`).
- **Validación** de entrada (campos requeridos, tipos, rangos) y **manejo de errores** con códigos HTTP claros.
- Llamar al `inference-service` para obtener `categoria` + `probabilidad`.
- Calcular `costo_estimado_mensual = consumo_kwh × TARIFA_REFERENCIA_KWH`.
- Completar `moneda` y `tarifa_referencia_kwh` en la respuesta.
- Generar `recomendaciones` por reglas según categoría y variables de mayor impacto.
- Documentar endpoints con OpenAPI/Swagger.
- *(Opcional)* Persistir y consultar resultados si se implementa persistencia.

## Estado de integración

Mientras el modelo real no esté listo, trabajar contra un **mock** del `inference-service` que respete el contrato. No bloquear el avance del backend por el modelo.

## Estructura sugerida

```
backend/
├── src/main/java/.../controller/
├── src/main/java/.../service/
├── src/main/java/.../dto/
├── src/main/java/.../client/      # cliente HTTP al inference-service
└── src/main/resources/application.yml
```

## Estado

La estructura del proyecto Spring Boot todavía no ha sido inicializada.
