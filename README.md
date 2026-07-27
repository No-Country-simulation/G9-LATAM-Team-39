# Analizador Inteligente de Consumo Energético — EnergiAI

Proyecto desarrollado para el **Hackathon ONE (Oracle Next Education) – Alura + Oracle con No Country**.

## Objetivo

Analizar información del consumo energético de una vivienda y clasificar su perfil como **Eficiente**, **Moderado** o **Ineficiente**. La aplicación devuelve la categoría estimada, la probabilidad del modelo, el costo mensual de referencia, la tarifa de referencia y recomendaciones de optimización, expuestos mediante una **API REST**. La arquitectura utiliza **al menos un servicio de OCI** (requisito obligatorio).

## Estrategia de datos

El dataset se construye a partir de los **microdatos reales de ENCEVI 2018 (INEGI)**. La descripción del proyecto permite datos *"recopilados de fuentes públicas"* y exige **definir y justificar los criterios** de cada perfil de eficiencia.

El proceso tiene dos pasos:

1. **`Energia.py`** procesa las 13 tablas de ENCEVI y calcula el consumo **aparato por aparato** (potencia × horas × cantidad). Produce una base de 28,763 hogares con las 5 variables del contrato.
2. **`etiquetar_dataset.py`** agrega la columna `categoria` con un sistema de puntos multifactor (consumo + horario pico + horas + intensidad), cuyos umbrales se calculan con los percentiles del propio dataset.

`consumo_kwh` es una **estimación física**, no una lectura de medidor: ENCEVI registra el monto pagado en pesos, no kilovatios. La categoría sale de las reglas del equipo, documentadas en `docs/reglas-etiquetado.md`.

## Arquitectura

Arquitectura de **dos servicios**: Python entrena y sirve el modelo; Java consume la inferencia.

- `backend/`: API REST principal en Java + Spring Boot (validación, orquestación, costo, recomendaciones).
- `inference-service/`: servicio Python (FastAPI) que carga el modelo desde OCI y ejecuta la inferencia.
- `data-science/`: datos, EDA, reglas de etiquetado, entrenamiento, evaluación y serialización del modelo.
- `frontend/`: **opcional**, interfaz mínima de captura y visualización (no bloquea el MVP).
- `docs/`: documentación técnica y funcional. **Única versión válida** del contrato, la arquitectura y el plan.

### Flujo general

1. El usuario captura los datos.
2. El frontend/cliente envía la solicitud al backend Java.
3. El backend valida la información.
4. El backend solicita la predicción al `inference-service` (Python).
5. El servicio de inferencia ejecuta el modelo y devuelve categoría + probabilidad.
6. El backend completa el resultado con costo y recomendaciones.
7. El frontend/cliente presenta el análisis.

## Contrato de la API (resumen)

`POST /analisis-energetico`

**Entrada:**

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

`costo_estimado_mensual = consumo_kwh × 0.75` (tarifa de referencia **R$ 0,75/kWh** de la descripción del proyecto; contexto Brasil, no peso mexicano). El contrato completo y único vive en `docs/contrato-api.md`.

## Tecnologías previstas

**Backend:** Java 17+, Spring Boot 3.x, Maven, API REST, OpenAPI/Swagger.

**Data Science e inferencia:** Python 3.11, Pandas, Scikit-learn, Joblib, FastAPI. Modelos candidatos a comparar: Regresión Logística, Árbol de Decisión, Random Forest (se elige el mejor por métricas; la descripción del proyecto los recomienda pero permite otros).

**Infraestructura:** GitHub, Oracle Cloud Infrastructure (Object Storage como servicio OCI mínimo).

## Estado

Proyecto en etapa inicial. La arquitectura y las tecnologías pueden ajustarse durante el hackathon. Ver `docs/` para la documentación completa, el plan por sprints y los frentes de trabajo.
