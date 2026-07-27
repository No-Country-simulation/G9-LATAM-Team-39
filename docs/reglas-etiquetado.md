# Reglas de etiquetado — Perfil de eficiencia energética (v3)

**Objetivo:** definir de forma reproducible y justificada la variable objetivo `categoria` ∈ {`EFICIENTE`, `MODERADO`, `INEFICIENTE`}, a partir de las 5 variables de entrada.

**Se aplican sobre hogares reales** derivados de ENCEVI 2018 (28,763 viviendas), no sobre datos simulados. Implementación en `data-science/src/etiquetar_dataset.py`.

---

## Por qué no etiquetamos por terciles del consumo

La primera versión asignaba la categoría cortando `consumo_kwh` en terciles (P33 y P67). Es un método estándar y objetivo, pero **univariado**: la etiqueta dependía de una sola variable.

Al medirlo con un modelo entrenado:

| Variable | Importancia con terciles |
|---|---|
| `consumo_kwh` | **100 %** |
| `horas_alto_consumo` | 0 % |
| `cantidad_equipos` | 0 % |
| `uso_horario_pico` | 0 % |
| Accuracy | 100 % (señal de alarma) |

Dos consecuencias: el usuario llenaría cinco campos y solo uno cambiaría el resultado; y si la categoría depende solo del consumo, **no hace falta machine learning** — bastan dos `if`.

Por eso pasamos a un **sistema de puntuación multifactor**.

---

## Enfoque: puntos de ineficiencia

Cuatro factores suman puntos. A mayor puntaje, peor perfil.

```
puntaje = P1 consumo + P2 horario pico + P3 horas + P4 intensidad
```

| Puntaje total | Categoría |
|---|---|
| 0 a 4 | `EFICIENTE` |
| 5 a 8 | `MODERADO` |
| 9 o más | `INEFICIENTE` |

Máximo posible: 8 + 2 + 4 + 3 = **17 puntos**.

---

## Paso 0 — Ajuste por tipo de vivienda

Antes de evaluar el consumo se normaliza por el tamaño esperado de la vivienda, para no castigar a las casas grandes por serlo:

```
consumo_ajustado = consumo_kwh / factor_tipo
```

| `tipo_inmueble` | `factor_tipo` |
|---|---|
| Departamento (y vivienda compartida) | 0.85 |
| Casa / Otro | 1.00 |

Son los únicos tres valores que acepta el contrato de la API. El script **normaliza** cualquier otro antes de calcular: `Vivienda_compartida` → `Otro`, `Apartamento` → `Departamento`, `Casa grande` → `Casa`. Es decir, "Casa grande" **no** recibe un factor propio; termina con 1.00 como cualquier casa. Ver `decisiones.md` (D11).

Dividir entre un valor menor que 1 **sube** el resultado (penaliza más); entre uno mayor que 1 lo **baja**.

> Estos factores son criterio del equipo, no salen de ENCEVI.

---

## Los cuatro puntajes

Los umbrales **no son valores fijos**: se calculan con los percentiles del propio dataset cada vez que corre el script. Los valores mostrados corresponden al dataset actual y cambian si cambian los datos.

### P1 · Consumo (0 a 8 puntos)

Cortes en los percentiles **20 / 40 / 60 / 80** del consumo ajustado.

| Consumo ajustado | Puntos |
|---|---|
| menos de 57.1 kWh | 0 |
| 57.1 – 83.1 | 2 |
| 83.1 – 113.8 | 4 |
| 113.8 – 172.7 | 6 |
| 172.7 o más | 8 |

### P2 · Uso en horario pico (0 o 2 puntos)

Binario, sin percentiles. Penaliza porque en hora pico la energía es más cara y contaminante.

| ¿Usa equipos en horario pico? | Puntos |
|---|---|
| No | 0 |
| Sí | 2 |

### P3 · Horas de alto consumo (0 a 4 puntos)

Cortes en los percentiles **40 / 70 / 90**.

| Horas equivalentes | Puntos |
|---|---|
| menos de 0.02 | 0 |
| 0.02 – 0.23 | 2 |
| 0.23 – 1.95 | 3 |
| más de 1.95 | 4 |

> **No son horas de reloj.** En la base de ENCEVI esta variable son *horas equivalentes de una carga de 1.5 kW* (ver la metodología de `Energia.py`). Por eso los umbrales son valores pequeños.

### P4 · Intensidad (0 a 3 puntos)

```
intensidad = consumo_kwh / cantidad_equipos
```

Cortes en los percentiles **40 / 70 / 90**.

| kWh por equipo | Puntos |
|---|---|
| menos de 10.6 | 0 |
| 10.6 – 15.1 | 1 |
| 15.1 – 23.6 | 2 |
| 23.6 o más | 3 |

Interpretación: muchos equipos con consumo total moderado → intensidad baja → equipos eficientes. Pocos equipos que consumen mucho → intensidad alta. Así no penalizamos *tener* aparatos, sino consumir mucho **por** aparato.

---

## Resultado

**Balance de clases** sobre 28,763 hogares:

| Categoría | % |
|---|---|
| EFICIENTE | 33.4 % |
| MODERADO | 29.3 % |
| INEFICIENTE | 37.4 % |

**Importancia de variables** en el modelo entrenado:

| Variable | Antes (terciles) | Ahora (multifactor) |
|---|---|---|
| `consumo_kwh` | 100 % | 58.8 % |
| `horas_alto_consumo` | 0 % | 20.8 % |
| `cantidad_equipos` | 0 % | 14.4 % |
| `uso_horario_pico` | 0 % | 5.7 % |
| `tipo_inmueble` | 0 % | 0.3 % |
| Accuracy | 100 % | 99.4 % |

---

## Tres hogares reales de ejemplo

| | Eficiente | Moderado | Ineficiente |
|---|---|---|---|
| Consumo | 4.3 kWh | 105.2 kWh | 221.8 kWh |
| Horario pico | sí | no | sí |
| Equipos | 3 | 14 | 19 |
| Horas equivalentes | 0.0 | 0.11 | 0.27 |
| **P1 consumo** | 0 | 4 | 8 |
| **P2 pico** | 2 | 0 | 2 |
| **P3 horas** | 0 | 2 | 3 |
| **P4 intensidad** | 0 | 0 | 1 |
| **Total** | **2** | **6** | **14** |

---

## Qué se puede ajustar

- Los percentiles de corte (`CORTES_CONSUMO`, `CORTES_HORAS`, `CORTES_INTENS`).
- Los factores por tipo de vivienda.
- Los cortes del puntaje final (`CORTE_EFICIENTE`, `CORTE_MODERADO`).

Cualquier cambio se prueba igual: correr el script y revisar **dos métricas** — que el balance de clases siga razonable (ninguna clase bajo 15 %) y que ninguna variable quede en 0 % de importancia. Registrar el cambio en `decisiones.md`.

---

## Nota sobre el modelo

Como la etiqueta se deriva de estas reglas, el modelo tiende a re-aprenderlas y el accuracy resulta alto (~99 %). Es esperado. El valor del trabajo está en la justificación de los criterios y en la evaluación honesta, no en la métrica.
