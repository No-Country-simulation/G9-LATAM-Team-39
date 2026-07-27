# Contrato de la API

**Única versión válida.** Cualquier cambio se hace aquí y se avisa al equipo. Los módulos enlazan a este archivo; no lo copian.

Tarifa de referencia: **R$ 0,75 / kWh** (contexto Brasil). Moneda: **BRL**.

---

## 1. `POST /analisis-energetico`

Endpoint principal. Recibe los datos de consumo, devuelve la clasificación con recomendaciones y costo.

### Entrada

```json
{
  "consumo_kwh": 420,
  "uso_horario_pico": true,
  "cantidad_equipos": 10,
  "tipo_inmueble": "Casa",
  "horas_alto_consumo": 8,
  "equipos": ["aire_acondicionado", "refrigerador", "lavadora"]
}
```

| Campo | Tipo | Requerido | Validación |
|---|---|---|---|
| `consumo_kwh` | number | sí | `> 0` y `<= 2000` · siempre viene (ver nota) |
| `uso_horario_pico` | boolean | sí | `true` / `false` |
| `cantidad_equipos` | integer | sí | `>= 1` y `<= 60` |
| `tipo_inmueble` | string | sí | `Casa` \| `Departamento` \| `Otro` |
| `horas_alto_consumo` | number | sí | `>= 0` y `<= 24` |
| `equipos` | string[] | **no** | catálogo de equipos (ver abajo) |

> **Nota sobre `consumo_kwh`:** es **siempre obligatorio**. Si el usuario no conoce su consumo, el **frontend** lo estima a partir de los aparatos seleccionados (ver `consumo-por-aparato.md`) y envía el valor ya calculado. El backend nunca recibe una petición sin este campo.

### Sobre el campo `equipos` (opcional)

Lista de los aparatos que el usuario selecciona en el formulario.

- **Es opcional**: la API funciona sin él. Si no viene, se omiten las recomendaciones específicas por aparato.
- **NO entra al modelo.** El modelo solo usa las 5 variables obligatorias. Este campo lo consume el backend para elegir recomendaciones.
- El frontend usa la selección para **calcular `cantidad_equipos`** automáticamente (contando los seleccionados) y, si el usuario no conoce su consumo, para **estimar `consumo_kwh`** antes de enviar.
- El backend **no estima nada** con este campo: solo lo usa para elegir recomendaciones y para el desglose por aparato.

Catálogo (mismas claves que la tabla de `consumo-por-aparato.md`): `aire_acondicionado`, `calentador_electrico`, `refrigerador`, `calefactor`, `focos`, `pantalla`, `lavadora`, `plancha`, `ventilador`, `bomba_agua`, `otros`.

### Salida (200 OK)

```json
{
  "id": "a3f1c9e2-5b7d-4e88-9c21-77f0b2d4e1a9",
  "categoria": "Ineficiente",
  "probabilidad": 0.81,
  "costo_estimado_mensual": 315.00,
  "moneda": "BRL",
  "tarifa_referencia_kwh": 0.75,
  "recomendaciones": [
    "Reducir el uso de equipos durante horarios pico",
    "Evaluar aparatos con alto consumo energético",
    "Distribuir actividades de mayor consumo a lo largo del día"
  ],
  "fecha_analisis": "2026-07-23T18:40:00Z"
}
```

| Campo | Origen |
|---|---|
| `id` | backend (identificador para consultar después) |
| `categoria` | modelo |
| `probabilidad` | modelo |
| `costo_estimado_mensual` | backend: `consumo_kwh × 0.75` |
| `moneda` / `tarifa_referencia_kwh` | backend (fijos) |
| `recomendaciones` | backend, por reglas |
| `fecha_analisis` | backend |

---

## 2. `GET /resultados/{id}`

Endpoint de consulta. Recupera un análisis previamente realizado. **Obligatorio según la descripción del proyecto** ("endpoint para consulta de resultados").

### Salida (200 OK)

```json
{
  "id": "a3f1c9e2-5b7d-4e88-9c21-77f0b2d4e1a9",
  "fecha_analisis": "2026-07-23T18:40:00Z",
  "entrada": {
    "consumo_kwh": 420,
    "uso_horario_pico": true,
    "cantidad_equipos": 10,
    "tipo_inmueble": "Casa",
    "horas_alto_consumo": 8,
    "equipos": ["aire_acondicionado", "refrigerador", "lavadora"]
  },
  "resultado": {
    "categoria": "Ineficiente",
    "probabilidad": 0.81,
    "costo_estimado_mensual": 315.00,
    "moneda": "BRL",
    "recomendaciones": ["..."]
  }
}
```

Si el `id` no existe: **404** con `error: "NOT_FOUND"`.

### `GET /resultados` (opcional)

Lista los análisis más recientes. Útil para la demo y para el historial. Soporta `?limit=10`.

---

## 3. Persistencia

El endpoint de consulta obliga a **guardar cada análisis**. Registro mínimo:

| Campo | Descripción |
|---|---|
| `id` | UUID generado por el backend |
| `fecha_analisis` | timestamp |
| las 5 entradas | tal como llegaron |
| `equipos` | lista opcional (JSON o texto) |
| `categoria`, `probabilidad` | respuesta del modelo |
| `costo_estimado_mensual` | calculado |

**Qué NO se guarda aquí:** los microdatos de ENCEVI, el dataset de entrenamiento ni el modelo. El modelo vive en **OCI Object Storage**; la base de datos solo guarda el historial de consultas.

---

## 4. Errores

```json
{
  "error": "VALIDATION_ERROR",
  "mensaje": "Descripción legible del problema",
  "campos": { "consumo_kwh": "Debe ser mayor que 0" }
}
```

| Situación | HTTP | `error` |
|---|---|---|
| Campo faltante o fuera de rango | 400 | `VALIDATION_ERROR` |
| `tipo_inmueble` o `equipos` fuera del catálogo | 400 | `VALIDATION_ERROR` |
| `id` inexistente en consulta | 404 | `NOT_FOUND` |
| Servicio de inferencia no responde | 502 | `INFERENCE_UNAVAILABLE` |
| Error interno | 500 | `INTERNAL_ERROR` |

---

## 5. Contrato interno (backend → inference-service)

### `POST /predict` (Python / FastAPI)

**Entrada:** solo las 5 variables obligatorias. **No** se envía `equipos`.

```json
{
  "consumo_kwh": 420,
  "uso_horario_pico": true,
  "cantidad_equipos": 10,
  "tipo_inmueble": "Casa",
  "horas_alto_consumo": 8
}
```

**Salida:**

```json
{ "categoria": "Ineficiente", "probabilidad": 0.81 }
```

El servicio de inferencia **solo clasifica**. Costo, moneda, recomendaciones, id y persistencia son responsabilidad del backend.

---

## 6. Recomendaciones (backend, por reglas)

> Tabla de consumo por aparato y lógica de desglose: ver `consumo-por-aparato.md`.

| Disparador | Recomendación |
|---|---|
| `uso_horario_pico = true` | Reducir el uso de equipos durante horarios pico |
| `horas_alto_consumo` alto | Distribuir actividades de mayor consumo a lo largo del día |
| ratio kWh/equipo alto | Evaluar aparatos con alto consumo energético |
| `equipos` incluye `aire_acondicionado` | Ajustar el termostato a 24 °C; es de los mayores consumos del hogar |
| `equipos` incluye `calentador_electrico` | Evaluar un calentador de gas o solar |
| categoría `Eficiente` | Mantener los hábitos actuales; monitorear el consumo mensual |
