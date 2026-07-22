# Registro de decisiones

Bitácora de las decisiones importantes del proyecto y su porqué. Sirve para no re-discutir lo ya acordado y para responder al jurado cuando pregunte "¿por qué hicieron X?".

**Cómo agregar una decisión:** copiar el formato de abajo, poner fecha, la decisión, por qué, qué alternativas se descartaron y qué consecuencias trae.

---

## D1 — Arquitectura de dos servicios (Java + Python)

**Decisión:** el modelo se entrena y se sirve en Python (FastAPI); el backend principal es Java (Spring Boot) y consume la inferencia por HTTP.

**Por qué:** mantiene el modelo de Scikit-learn en su entorno nativo sin reimplementarlo en Java, y respeta la directriz de API "preferentemente Java".

**Alternativas descartadas:** un solo servicio Python (no respeta la preferencia de Java); reimplementar la inferencia en Java (costoso y con riesgo de diferencias con el entrenamiento).

**Consecuencias:** un salto de red y dos despliegues; se mitiga con contrato JSON único y respuestas simuladas (mock) mientras el modelo real no está listo.

---

## D2 — Dataset sintético, no ETL de microdatos

**Decisión:** el dataset se genera de forma sintética con reglas propias; ENCEVI 2018 se usa solo para calibrar rangos y como respaldo público.

**Por qué:** la descripción del proyecto pide una base "generada manualmente o simulada" y definir/justificar los criterios. ENCEVI no contiene consumo en kWh (registra pesos pagados) y no mapea al contrato sin una estimación costosa.

**Alternativas descartadas:** descargar y procesar los microdatos de ENCEVI (13 tablas, sin kWh, sin la etiqueta objetivo; alto costo y error).

**Consecuencias:** control total del contrato y de la etiqueta; el modelo tenderá a re-aprender las reglas, lo cual es esperado y se documenta con honestidad.

---

## D3 — OCI Object Storage como servicio de OCI

**Decisión:** cumplir el requisito obligatorio de OCI con Object Storage, guardando ahí el modelo que el `inference-service` descarga al arrancar.

**Por qué:** es el camino más barato y confiable para cerrar el requisito, y se puede probar desde el Sprint 1 con un archivo dummy.

**Alternativas descartadas (por ahora):** OCI Compute o Functions para alojar la API (más superficie de despliegue; quedan como mejora opcional).

**Consecuencias:** el requisito de OCI se cierra temprano; el riesgo de despliegue baja.

---

## D4 — Modelos candidatos a comparar (Random Forest no es obligatorio)

**Decisión:** comparar Regresión Logística, Árbol de Decisión y Random Forest, y elegir el mejor por métricas.

**Por qué:** la descripción del proyecto los recomienda pero permite otros; no hay obligación de usar Random Forest.

**Consecuencias:** la elección del modelo se justifica con accuracy, F1 por clase y matriz de confusión, no por preferencia.

---

## D5 — Frontend opcional

**Decisión:** el frontend es opcional y no bloquea el MVP; se aborda solo si hay capacidad tras cerrar el flujo vertical.

**Por qué:** la descripción del proyecto indica que el front-end no es obligatorio; el equipo es 4 Data Science + 4 Backend.

**Consecuencias:** el esfuerzo se concentra en dataset → modelo → API → OCI.

---

## D6 — Contrato JSON en un solo lugar

**Decisión:** el contrato de la API vive únicamente en `docs/contrato-api.md`; los README enlazan, no copian.

**Por qué:** evita que el contrato se desincronice entre módulos.

**Consecuencias:** cualquier cambio de contrato se hace en un solo archivo y se avisa al equipo.

---

## D7 — Tarifa y moneda de referencia

**Decisión:** costo estimado = `consumo_kwh × 0.75`, con tarifa **R$ 0,75/kWh** y moneda **BRL**.

**Por qué:** es la tarifa de referencia de la descripción del proyecto (contexto Brasil). No es peso mexicano.

**Consecuencias:** los cálculos de costo y los ejemplos usan reales (BRL).
