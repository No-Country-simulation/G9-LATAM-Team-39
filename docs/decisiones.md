# Registro de decisiones

Bitácora de las decisiones importantes del proyecto y su porqué. Sirve para no re-discutir lo ya acordado y para responder al jurado cuando pregunte "¿por qué hicieron X?".

**Cómo agregar una decisión:** copiar el formato, poner la decisión, por qué, qué alternativas se descartaron y qué consecuencias trae.

---

## D1 — Arquitectura de dos servicios (Java + Python)

**Decisión:** el modelo se entrena y se sirve en Python (FastAPI); el backend principal es Java (Spring Boot) y consume la inferencia por HTTP.

**Por qué:** mantiene el modelo de Scikit-learn en su entorno nativo sin reimplementarlo en Java, y respeta la directriz de API "preferentemente Java".

**Alternativas descartadas:** un solo servicio Python (no respeta la preferencia de Java); reimplementar la inferencia en Java (costoso y con riesgo de diferencias con el entrenamiento).

**Consecuencias:** un salto de red y dos despliegues; se mitiga con contrato JSON único y respuestas simuladas (mock) mientras el modelo no está listo.

---

## D2 — Datos derivados de ENCEVI, no simulados

> **Corrige la decisión inicial.** El proyecto arrancó con un generador de datos sintéticos; se reemplazó al conseguir los microdatos reales.

**Decisión:** el dataset se construye a partir de los microdatos de ENCEVI 2018 (INEGI), calculando el consumo aparato por aparato (potencia × horas × cantidad) en `Energia.py`. Resultado: 28,763 hogares reales.

**Por qué:** la descripción del proyecto permite datos "recopilados de fuentes públicas" o "simulados". Habiendo microdatos disponibles, los hogares reales son más defendibles ante el jurado que los generados.

**Alternativas descartadas:** dataset sintético con distribuciones calibradas (era el plan inicial, viable pero más débil); usar ENCEVI sin transformar (no contiene `consumo_kwh`, solo el monto pagado en pesos).

**Consecuencias:** `consumo_kwh` es una estimación física, no una lectura de medidor, y hay que declararlo. Queda pendiente verificar si el periodo de facturación de CFE es bimestral: la mediana de 96 kWh/mes parece baja frente al promedio residencial mexicano (~200-250).

---

## D3 — Etiquetado multifactor, no por percentiles de una variable

**Decisión:** la categoría se asigna con un sistema de puntos que combina cuatro factores (consumo, horario pico, horas de alto consumo, intensidad por equipo), implementado en `etiquetar_dataset.py`.

**Por qué:** la versión inicial usaba terciles de `consumo_kwh`. Medido con un modelo entrenado, daba 100 % de accuracy con `consumo_kwh` explicando el 100 % de la decisión y las otras cuatro variables en 0 %. El usuario llenaría cinco campos y solo uno afectaría el resultado; además, si la categoría depende de una sola variable, no se justifica usar machine learning.

**Alternativas descartadas:** terciles de consumo (univariado); umbrales absolutos fijos en kWh (no se adaptaban a la escala real de los datos: el 74.8 % de los hogares caía en un solo tramo).

**Consecuencias:** las cinco variables aportan al modelo (58.8 / 20.8 / 14.4 / 5.7 / 0.3 %) y el accuracy baja a 99.4 %. Los cortes del puntaje son criterio del equipo y quedan documentados en `reglas-etiquetado.md`.

---

## D4 — Umbrales calculados por percentiles del dataset

**Decisión:** los umbrales de cada puntaje no se escriben fijos: se calculan con los percentiles del propio dataset en cada ejecución.

**Por qué:** los umbrales absolutos iniciales (150/250/350/500 kWh) eran criterio nuestro y no funcionaban con los datos reales. Al derivarlos de la distribución, dejan de ser arbitrarios y se recalibran solos si la escala cambia.

**Consecuencias:** si se corrige el tema del periodo bimestral, no hay que actualizar nada a mano. Lo que sigue siendo criterio del equipo es **en qué percentiles cortar** (20/40/60/80 y 40/70/90).

---

## D5 — OCI Object Storage como servicio de OCI

**Decisión:** cumplir el requisito obligatorio de OCI con Object Storage, guardando ahí el modelo que el `inference-service` descarga al arrancar.

**Por qué:** es el camino más barato y confiable para cerrar el requisito, y se puede probar desde el Sprint 1 con un archivo dummy.

**Alternativas descartadas (por ahora):** OCI Compute o Functions para alojar la API (más superficie de despliegue; quedan como mejora opcional).

**Consecuencias:** el requisito de OCI se cierra temprano y el riesgo de despliegue baja.

---

## D6 — Modelos candidatos a comparar

**Decisión:** comparar Regresión Logística, Árbol de Decisión y Random Forest, y elegir el mejor por métricas.

**Por qué:** la descripción del proyecto los recomienda pero permite otros; no hay obligación de usar Random Forest.

**Consecuencias:** la elección se justifica con accuracy, F1 por clase y matriz de confusión, no por preferencia.

---

## D7 — Frontend opcional

**Decisión:** el frontend es opcional y no bloquea el MVP; se aborda solo si hay capacidad tras cerrar el flujo vertical.

**Por qué:** la descripción del proyecto indica que el front-end no es obligatorio para el MVP.

**Consecuencias:** el esfuerzo se concentra en dataset → modelo → API → OCI.

---

## D8 — Contrato JSON en un solo lugar

**Decisión:** el contrato de la API vive únicamente en `docs/contrato-api.md`; los README enlazan, no copian.

**Por qué:** evita que el contrato se desincronice entre módulos.

**Consecuencias:** cualquier cambio de contrato se hace en un solo archivo y se avisa al equipo.

---

## D9 — Tarifa y moneda de referencia

**Decisión:** costo estimado = `consumo_kwh × 0.75`, con tarifa **R$ 0,75/kWh** y moneda **BRL**.

**Por qué:** es la tarifa de referencia de la descripción del proyecto (contexto Brasil). No es peso mexicano.

**Consecuencias:** los cálculos de costo y los ejemplos usan reales. La comparación con el recibo de CFE (en pesos) se conserva solo como validación interna del dataset y no se mezcla con el costo del proyecto.

---

## D10 — Selección de aparatos: SÍ se implementa, del lado del backend

**Decisión:** el formulario **incluye** una lista multiseleccionable de aparatos. La selección viaja como campo opcional `equipos` y el **backend** la usa para dos cosas:

1. **Desglosar el consumo** y generar recomendaciones específicas por aparato.
2. **Estimar `consumo_kwh`** cuando el usuario no conoce su consumo mensual (opción "no sé cuánto consumo" en el formulario).

El modelo **no** recibe este campo: sigue trabajando solo con las 5 variables obligatorias.

**Por qué del lado del backend y no del modelo:**
- Las recomendaciones son texto y lógica de negocio; un clasificador devuelve etiquetas, no frases.
- Cambiar una recomendación no debe implicar reentrenar el modelo y volver a subirlo a OCI.
- El contrato obligatorio y el dataset quedan intactos.

**No es improvisación.** Los consumos promedio por aparato salen de los microdatos de ENCEVI 2018 que ya procesamos: 28,763 hogares, consumo calculado aparato por aparato. La tabla completa y la lógica de reparto están en `docs/consumo-por-aparato.md`.

**Alternativas descartadas:** pedir al usuario el consumo individual de cada aparato (nadie conoce ese dato; sería precisión falsa) y reemplazar `consumo_kwh` por una lista de equipos (rompe el MVP obligatorio y duplica información).

**Consecuencias:** la API funciona igual si el campo no viene. Prioridad: se implementa **después** de cerrar el flujo vertical obligatorio (modelo, API, OCI). Si en el futuro se quisiera meter al modelo, habría que regenerar el dataset y reentrenar.
