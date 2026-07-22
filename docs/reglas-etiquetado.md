# Reglas de etiquetado — Perfil de eficiencia energética (v1)

**Objetivo:** definir de forma reproducible y justificada la variable objetivo `categoria` ∈ {`EFICIENTE`, `MODERADO`, `INEFICIENTE`} a partir de las 5 variables de entrada. Estas reglas se usan para (1) etiquetar el dataset sintético y (2) documentar el criterio ante los jueces.

> **v1 = punto de partida.** Los umbrales son deliberadamente explícitos para poder ajustarlos. Data Science debe validar que producen un dataset razonablemente balanceado y ajustar si hace falta.

---

## Enfoque: sistema de puntos de ineficiencia

No usamos el consumo bruto como único criterio, porque un hogar grande consume más sin ser necesariamente ineficiente. En su lugar sumamos **puntos de ineficiencia** de cuatro factores. A mayor puntaje, peor perfil.

```
score = P_consumo + P_pico + P_horas + P_intensidad_equipos
```

### Paso 0 — Ajuste por tipo de inmueble

El consumo se normaliza según el tamaño esperado del inmueble, para no castigar a las viviendas grandes:

```
consumo_ajustado = consumo_kwh / factor_tipo
```

| `tipo_inmueble` | `factor_tipo` |
|---|---|
| `Apartamento` | 0.85 |
| `Casa` | 1.00 |
| `Casa grande` | 1.25 |

Interpretación: un consumo de 420 kWh "pesa" más en un apartamento (ajustado ≈ 494) que en una casa grande (ajustado = 336).

### P_consumo — magnitud del consumo (sobre `consumo_ajustado`)

| `consumo_ajustado` (kWh) | Puntos |
|---|---|
| < 150 | 0 |
| 150 – 249 | 2 |
| 250 – 349 | 4 |
| 350 – 499 | 6 |
| ≥ 500 | 8 |

### P_pico — uso en horario de mayor demanda

| `uso_horario_pico` | Puntos |
|---|---|
| `false` | 0 |
| `true` | 2 |

### P_horas — horas diarias de alto consumo

| `horas_alto_consumo` | Puntos |
|---|---|
| ≤ 2 | 0 |
| 3 – 5 | 2 |
| 6 – 8 | 3 |
| > 8 | 4 |

### P_intensidad_equipos — kWh por equipo (proxy de eficiencia de los aparatos)

```
ratio = consumo_kwh / max(cantidad_equipos, 1)
```

| `ratio` (kWh/equipo) | Puntos |
|---|---|
| < 20 | 0 |
| 20 – 39 | 1 |
| 40 – 59 | 2 |
| ≥ 60 | 3 |

Interpretación: muchos equipos con consumo total moderado → ratio bajo → aparatos/uso eficientes. Pocos equipos que consumen mucho → ratio alto → aparatos ineficientes.

---

## Clasificación final

Puntaje máximo posible = 8 + 2 + 4 + 3 = **17**.

| `score` | `categoria` |
|---|---|
| ≤ 4 | `EFICIENTE` |
| 5 – 9 | `MODERADO` |
| ≥ 10 | `INEFICIENTE` |

---

## Ejemplos verificados

### Ejemplo 1 — el de la descripción del proyecto (esperado: Ineficiente)

Entrada: `consumo_kwh=420, uso_horario_pico=true, cantidad_equipos=10, tipo_inmueble="Casa", horas_alto_consumo=8`

- `consumo_ajustado = 420 / 1.00 = 420` → P_consumo = **6**
- `uso_horario_pico = true` → P_pico = **2**
- `horas_alto_consumo = 8` (6–8) → P_horas = **3**
- `ratio = 420 / 10 = 42` (40–59) → P_intensidad = **2**
- **score = 13 → INEFICIENTE** ✓

### Ejemplo 2 — eficiente

Entrada: `consumo_kwh=120, uso_horario_pico=false, cantidad_equipos=6, tipo_inmueble="Apartamento", horas_alto_consumo=1`

- `consumo_ajustado = 120 / 0.85 = 141` → P_consumo = **0**
- P_pico = **0**
- `horas ≤ 2` → P_horas = **0**
- `ratio = 120 / 6 = 20` (20–39) → P_intensidad = **1**
- **score = 1 → EFICIENTE** ✓

### Ejemplo 3 — moderado

Entrada: `consumo_kwh=280, uso_horario_pico=false, cantidad_equipos=8, tipo_inmueble="Casa", horas_alto_consumo=4`

- `consumo_ajustado = 280` → P_consumo = **4**
- P_pico = **0**
- `horas 3–5` → P_horas = **2**
- `ratio = 280 / 8 = 35` → P_intensidad = **1**
- **score = 7 → MODERADO** ✓

---

## Guía para generar el dataset sintético

Muestrear cada variable en rangos plausibles (calibrar con ENCEVI 2018 y consumo residencial brasileño), aplicar las reglas y obtener la etiqueta.

| Variable | Rango de muestreo sugerido |
|---|---|
| `consumo_kwh` | 50 – 800 (distribución sesgada a valores medios; opcionalmente condicionada al tipo) |
| `uso_horario_pico` | Bernoulli(p ≈ 0.4) |
| `cantidad_equipos` | 3 – 25 |
| `tipo_inmueble` | categórico: Apartamento / Casa / Casa grande |
| `horas_alto_consumo` | 0 – 14 |

Recomendaciones:
- Generar varios miles de filas, aplicar las reglas y **revisar el balance de clases**. Si una clase queda muy pequeña, ajustar umbrales o el muestreo (o rebalancear).
- Documentar en el notebook la calibración de rangos con ENCEVI como justificación.
- Fijar una semilla aleatoria para reproducibilidad.

---

## Qué se puede ajustar (parámetros)

- `factor_tipo` por tipo de inmueble.
- Umbrales de cada tabla de puntos.
- Cortes finales (`≤4`, `5–9`, `≥10`).
- Pesos relativos (hoy el consumo domina con máx. 8 pts; se puede rebalancear).

Todo cambio se registra en `decisiones.md`.
