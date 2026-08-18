# Notebook de EDA, Modelado y Serialización — EnergiAI

> Documentación general del módulo de Data Science (estrategia de datos, criterios de
> etiquetado, estructura de carpetas): ver `../README.md`.
> Contrato de la API: `../../docs/contrato-api.md`. Reglas de etiquetado en detalle:
> `../../docs/reglas-etiquetado.md`.

Este documento cubre específicamente `EnergiAI_EDA_Modelado.ipynb`: qué hace cada
sección, cómo correrlo y qué produce.

## Cómo correrlo

Requiere `dataset_entrenamiento.csv` ya generado (ver `../README.md` para el proceso
`Energia.py` → `etiquetar_dataset.py`).

```bash
pip install pandas numpy scikit-learn matplotlib seaborn joblib
jupyter notebook EnergiAI_EDA_Modelado.ipynb
```

Ejecutar todas las celdas con `Run All`. El notebook espera el dataset en
`../data/processed/dataset_entrenamiento.csv` (ajustar `RUTA_DATASET` en la sección 1
si la estructura local es distinta).

## Contenido del notebook

| Sección | Qué hace |
|---|---|
| 1–2 | Configuración e imports; carga de `dataset_entrenamiento.csv` |
| 3 | EDA: estructura, nulos, duplicados, estadísticos, distribución de `categoria` y de las 5 variables del contrato |
| 4 | Análisis de patrones: cada variable de entrada contra `categoria`, matriz de correlación |
| 5 | Procesamiento: `ColumnTransformer` (escalado + one-hot) empaquetado en `Pipeline`, split train/test estratificado |
| 6 | Entrenamiento de Regresión Logística, Árbol de Decisión y Random Forest |
| 7 | Evaluación: accuracy, F1-macro, validación cruzada 5-fold, matrices de confusión (absoluta y normalizada), curva de aprendizaje, importancia de variables |
| 8 | Recomendaciones basadas en reglas (`generar_recomendaciones()`) |
| 9 | 3 ejemplos end-to-end siguiendo el contrato de la API |
| 10 | Serialización: `modelo_energiai.joblib` + `reporte_metricas.json` |
| 11 | Resumen |

## Qué produce

- `../models/modelo_energiai.joblib` — pipeline completo (preprocesamiento +
  clasificador), listo para `pipeline.predict(df)` con las 5 columnas del contrato.
- `../models/reporte_metricas.json` — métricas y metadatos del modelo elegido, sin
  necesidad de abrir el notebook.

## Nota sobre el accuracy alto

Random Forest alcanza ~99% de accuracy porque la etiqueta se deriva de reglas propias
sobre las mismas variables de entrada (ver `../README.md`, sección "Nota
metodológica"). La curva de aprendizaje (sección 7.6) confirma una brecha pequeña
entre entrenamiento y validación cruzada, sin evidencia fuerte de sobreajuste.

## Qué recibe Backend / inference-service

- `modelo_energiai.joblib`: recibe un DataFrame con `consumo_kwh`, `uso_horario_pico`,
  `cantidad_equipos`, `tipo_inmueble`, `horas_alto_consumo` y devuelve la categoría vía
  `.predict()`.
- Lógica de recomendaciones (sección 8) y tarifa de referencia ($0.75/kWh), portables
  al backend o al inference-service.
