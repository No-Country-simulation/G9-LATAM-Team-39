# Consumo por aparato — referencia para recomendaciones

Tabla de consumo promedio por electrodoméstico, derivada de los microdatos de **ENCEVI 2018 (INEGI)**. La usa el **backend** para desglosar el consumo del usuario y generar recomendaciones concretas.

> Estos valores **no entran al modelo**. El modelo solo usa las 5 variables del contrato. Ver `decisiones.md` (D10).

---

## 1. De dónde salen estos números

No son estimaciones de catálogo ni valores inventados. Se calcularon así:

1. `Energia.py` procesa las 13 tablas de ENCEVI y calcula el consumo mensual de cada grupo de aparatos por hogar (potencia × horas de uso × cantidad).
2. Sobre esa base (28,763 hogares reales) se promedia el consumo **por unidad** de cada aparato, considerando solo los hogares que declaran tenerlo.

---

## 2. Tabla de referencia

| Aparato | Clave (`equipos`) | kWh/mes por unidad | % de hogares |
|---|---|---|---|
| Aire acondicionado | `aire_acondicionado` | **86.1** | 18.2 % |
| Calentador de agua eléctrico | `calentador_electrico` | **84.0** | 2.4 % |
| Refrigerador | `refrigerador` | **39.2** | 88.2 % |
| Calefactor eléctrico | `calefactor` | **22.9** | 3.1 % |
| Focos (todo el hogar) | `focos` | **16.9** | — |
| Pantalla / TV | `pantalla` | **11.4** | 91.3 % |
| Lavadora | `lavadora` | **9.8** | 71.5 % |
| Plancha | `plancha` | **8.2** | 59.0 % |
| Ventilador | `ventilador` | **6.8** | 53.6 % |
| Bomba de agua | `bomba_agua` | **5.0** | 17.3 % |

**Lectura rápida:** el aire acondicionado consume ~13 veces más que un ventilador y ~2 veces más que un refrigerador. Es casi siempre el mayor gasto en los hogares que lo tienen.

Los focos se reportan por hogar completo, no por unidad.

La clave `otros` existe en el catálogo del contrato pero **no tiene valor en esta tabla**: es la opción de escape para aparatos que no están en la lista. Al calcular el desglose, el backend le asigna 0 o la ignora.

---

## 3. Los dos usos de la tabla

### Uso A — Estimar el consumo (lo hace el FRONTEND)

La mayoría de las personas no conoce sus kWh: conoce cuánto paga. Por eso **el formulario ofrece dos caminos y siempre envía `consumo_kwh` ya resuelto** — el backend nunca recibe una petición sin ese campo:

- **"Sí conozco mi consumo"** → el usuario escribe `consumo_kwh`. **Este dato manda siempre.**
- **"No lo sé"** → selecciona sus aparatos y se estima:

```
consumo_estimado = Σ (kWh_del_aparato × cantidad_seleccionada)
```

**Excepción — `focos`:** su valor (16.9) ya corresponde a **todo el hogar**, no a un foco. Siempre se suma **×1**, sin importar cuántos focos declare el usuario. Multiplicarlo daría un consumo absurdo (16.9 × 10 focos = 169 kWh).

Ejemplo: 1 aire + 1 refrigerador + 1 lavadora + focos
`86.1 + 39.2 + 9.8 + 16.9 = 152.0 kWh/mes`

**Si el usuario elige "no lo sé" y no selecciona ningún aparato:** el formulario no deja continuar; pide el consumo o al menos un aparato. No se inventa un valor por defecto. Si aun así llegara una petición sin `consumo_kwh`, el backend responde `400 VALIDATION_ERROR`.

> Nunca se piden ambos a la vez. Así no hay dos fuentes que se contradigan.

### Uso B — Desglosar y recomendar (lo hace el BACKEND)

Con la lista de aparatos se calcula el peso de cada uno sobre el total:

```
peso_aparato = (kWh_del_aparato × cantidad) / suma_de_todos
```

**Si el usuario dio su consumo real, se reparte proporcionalmente sobre ESE total**, no sobre la suma de la tabla. El dato del usuario siempre gana.

Ejemplo: el usuario reporta 200 kWh y tiene 1 aire + 1 refri + 1 lavadora (suma de tabla: 135.1).
- Aire: 86.1 / 135.1 = 63.7 % → **127.4 kWh** de sus 200
- Refrigerador: 29.0 % → 58.0 kWh
- Lavadora: 7.3 % → 14.5 kWh

---

## 4. Recomendaciones por aparato

Se disparan las recomendaciones de los **dos aparatos con mayor peso** en el desglose, más las generales según categoría.

> Por qué dos y no uno: solo el 18 % de los hogares tiene aire acondicionado. En el resto, el refrigerador domina el desglose (≈42 %) y casi todos los usuarios recibirían el mismo consejo. Mostrar los dos principales da variedad y más valor.

| Aparato dominante | Recomendación |
|---|---|
| `aire_acondicionado` | Ajustar el termostato a 24 °C y dar mantenimiento a los filtros. Es tu mayor consumo. |
| `calentador_electrico` | Evaluar un calentador de gas o solar; el eléctrico es de los aparatos más costosos. |
| `refrigerador` | Verificar los sellos de la puerta y alejarlo de fuentes de calor (estufa, sol directo). |
| `calefactor` | Usar solo en las habitaciones ocupadas y por periodos cortos. |
| `pantalla` | Desconectar en lugar de dejar en reposo; el consumo fantasma es real. |
| `lavadora` | Lavar con carga completa y con agua fría cuando sea posible. |
| `plancha` | Planchar por lotes: la mayor parte de la energía se va en calentar. |
| `ventilador` | Es una alternativa mucho más económica que el aire acondicionado. |
| `bomba_agua` | Revisar fugas en la instalación; una fuga hace trabajar la bomba de más. |
| `focos` | Sustituir focos incandescentes o ahorradores por LED. |

Ejemplo de mensaje generado:

> *"Tu aire acondicionado representa cerca del 64 % de tu consumo (≈127 kWh de 200). Ajustar el termostato a 24 °C es tu mayor oportunidad de ahorro."*

---

## 5. Escenario de equipos eficientes (opcional)

`Energia.py` también genera `02_base_hogares_2026_mvp.csv`: los mismos hogares recalculados con equipos eficientes actuales. El ahorro promedio ronda el **30–35 %**.

Sirve para una recomendación de cierre con respaldo de datos:

> *"Cambiando a equipos eficientes podrías reducir tu consumo alrededor de un 33 %, unos R$ 32 al mes."*

El monto se calcula sobre el consumo de cada usuario: `consumo_kwh × 0.33 × 0.75`. El valor del ejemplo corresponde al consumo promedio de la base (131.5 kWh/mes).

---

## 6. Límites que conviene declarar

- Son **promedios**, no mediciones del hogar del usuario. El desglose es orientativo.
- Provienen de una estimación física simplificada, no de medidores inteligentes.
- El dato que el usuario reporta de su recibo **siempre tiene prioridad** sobre la estimación.
- Si se corrige el tema del periodo bimestral de CFE (ver `decisiones.md`, D2), estos promedios deben recalcularse.
