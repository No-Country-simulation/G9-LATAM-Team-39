# Contrato de la API — `POST /analisis-energetico`

**Fuente única.** Cualquier cambio se hace aquí y se avisa al equipo. Los módulos enlazan a este archivo; no lo copian.

Tarifa de referencia: **R$ 0,75 / kWh** (contexto Brasil, según la descripción del proyecto). Moneda: **BRL**.

---

## Endpoint público (backend)

### `POST /analisis-energetico`

### Entrada

```json
{
  "consumo_kwh": 420,
  "uso_horario_pico": true,
  "cantidad_equipos": 10,
  "tipo_inmueble": "Casa",
  "horas_alto_consumo": 8
}
```

| Campo | Tipo | Requerido | Validación | Descripción |
|---|---|---|---|---|
| `consumo_kwh` | number | sí | `> 0` y `<= 2000` | Consumo mensual en kWh |
| `uso_horario_pico` | boolean | sí | `true`/`false` | Uso de equipos en horario de mayor demanda |
| `cantidad_equipos` | integer | sí | `>= 1` y `<= 60` | Número total de equipos eléctricos |
| `tipo_inmueble` | string | sí | ∈ catálogo | `Apartamento` \| `Casa` \| `Casa grande` |
| `horas_alto_consumo` | number | sí | `>= 0` y `<= 24` | Horas diarias de uso de equipos de alto consumo |

### Salida (200 OK)

```json
{
  "categoria": "Ineficiente",
  "probabilidad": 0.81,
  "costo_estimado_mensual": 315.00,
  "moneda": "BRL",
  "tarifa_referencia_kwh": 0.75,
  "recomendaciones": [
    "Reducir el uso de equipos durante horarios pico",
    "Evaluar aparatos con alto consumo energético",
    "Distribuir actividades de mayor consumo a lo largo del día"
  ]
}
```

| Campo | Tipo | Origen | Descripción |
|---|---|---|---|
| `categoria` | string | modelo | `Eficiente` \| `Moderado` \| `Ineficiente` |
| `probabilidad` | number | modelo | Confianza de la clase predicha (0–1) |
| `costo_estimado_mensual` | number | backend | `consumo_kwh × tarifa_referencia_kwh` |
| `moneda` | string | backend | `BRL` |
| `tarifa_referencia_kwh` | number | backend | `0.75` |
| `recomendaciones` | string[] | backend | Reglas según categoría y factores |

### Regla de costo

```
costo_estimado_mensual = consumo_kwh * 0.75
```
Ejemplo: `420 * 0.75 = 315.00`

---

## Errores

Formato uniforme:

```json
{
  "error": "VALIDATION_ERROR",
  "mensaje": "Descripción legible del problema",
  "campos": {
    "consumo_kwh": "Debe ser mayor que 0"
  }
}
```

| Situación | HTTP | `error` |
|---|---|---|
| Campo faltante o fuera de rango | 400 | `VALIDATION_ERROR` |
| `tipo_inmueble` fuera del catálogo | 400 | `VALIDATION_ERROR` |
| Servicio de inferencia no responde | 502 | `INFERENCE_UNAVAILABLE` |
| Error interno | 500 | `INTERNAL_ERROR` |

---

## Contrato interno (backend → inference-service)

### `POST /predict` (Python / FastAPI)

**Entrada:** las mismas 5 variables de la entrada pública.

**Salida:**

```json
{ "categoria": "Ineficiente", "probabilidad": 0.81 }
```

El `inference-service` **solo** clasifica. El costo, la moneda y las recomendaciones los agrega el backend. Así, si cambia la tarifa o las recomendaciones, no se toca el modelo.

---

## Recomendaciones (backend, por reglas)

Se seleccionan según la categoría y el factor de mayor peso (ver `reglas-etiquetado.md`):

| Disparador | Recomendación |
|---|---|
| `uso_horario_pico = true` | Reducir el uso de equipos durante horarios pico |
| `horas_alto_consumo` alto | Distribuir actividades de mayor consumo a lo largo del día |
| ratio kWh/equipo alto | Evaluar aparatos con alto consumo energético |
| categoría `Eficiente` | Mantener los hábitos actuales; monitorear el consumo mensual |
