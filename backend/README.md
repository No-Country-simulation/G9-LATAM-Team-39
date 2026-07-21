# Backend

Este módulo contendrá la API REST principal del proyecto, desarrollada con Java y Spring Boot.

## Responsabilidades previstas

- Recibir solicitudes de análisis energético.
- Validar los datos de entrada.
- Exponer el endpoint de análisis energético.
- Comunicarse con el servicio de inferencia en Python.
- Calcular o completar el costo mensual estimado.
- Integrar las recomendaciones de optimización.
- Gestionar errores y respuestas HTTP.
- Documentar los endpoints con OpenAPI/Swagger.
- Guardar y consultar resultados si se implementa persistencia.

## Endpoint principal previsto

`POST /analisis-energetico`

## Datos de entrada previstos

- `consumo_kwh`
- `uso_horario_pico`
- `cantidad_equipos`
- `tipo_inmueble`
- `horas_alto_consumo`

## Datos de salida previstos

- `categoria`
- `probabilidad`
- `costo_estimado_mensual`
- `moneda`
- `tarifa_referencia_kwh`
- `recomendaciones`

## Estado

La estructura del proyecto Spring Boot todavía no ha sido inicializada.