# EnergiAI — Ciencia de Datos

Documentación del frente de **Dataset derivado de ENCEVI + reglas de etiquetado** y
**EDA + comparación de modelos + serialización + notebook**, parte del MVP de EnergiAI
para el Hackathon ONE (Alura + Oracle con No Country).

## Qué contiene esta carpeta

| Archivo | Descripción |
|---|---|
| `src/Energia.py` | Procesa los 13 CSV de la encuesta ENCEVI 2018 (INEGI) y calcula el consumo eléctrico teórico por hogar, aparato por aparato. Genera `data/processed/01_base_hogares_2018_mvp.csv` con las 5 variables del contrato de la API. |
| `src/etiquetar_dataset.py` | Toma la base de `Energia.py` y agrega la columna `categoria` (EFICIENTE / MODERADO / INEFICIENTE) con un sistema de puntos multifactor. Genera `data/processed/dataset_entrenamiento.csv`. |
| `notebooks/EnergiAI_EDA_Modelado.ipynb` | Notebook de EDA, comparación de modelos, evaluación y serialización. |
| `models/reporte_metricas.json` | Métricas del modelo elegido, en formato consultable sin abrir el notebook. |
| `models/modelo_energiai.joblib` | Modelo serializado, listo para cargar con `joblib.load()`; se sube a OCI Object Storage para producción. |

## Cómo correr

```bash
# desde data-science/
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

jupyter notebook notebooks/EnergiAI_EDA_Modelado.ipynb
```

## Cómo reproducir el pipeline completo desde cero

Requiere los 13 CSV de ENCEVI 2018 en `data/raw/`
(`aireacond.csv`, `cal_agua.csv`, `calefactor.csv`, `cambio.csv`, `electro.csv`,
`encevi.csv`, `focos.csv`, `hogar.csv`, `otros_eq.csv`, `pantalla.csv`, `persona.csv`,
`ventilador.csv`, `vivienda.csv`).

```bash
# desde data-science/
python src/Energia.py
python src/etiquetar_dataset.py --in data/processed/01_base_hogares_2018_mvp.csv --out data/processed/dataset_entrenamiento.csv
```

Luego abrir `notebooks/EnergiAI_EDA_Modelado.ipynb` y ejecutar todas las celdas
(`Run All`).

## Dataset: origen y criterio de etiquetado

Los datos son hogares **reales** de la encuesta ENCEVI 2018 (INEGI), no simulados.
`Energia.py` calcula el consumo de cada hogar sumando el consumo estimado de cada
aparato declarado (potencia de referencia × horas de uso × cantidad), no usa el pago
en pesos reportado en el recibo como variable aproximada ni indicador indirecto de consumo.

**Variables del contrato de la API:**

| Variable | Tipo | Descripción |
|---|---|---|
| `consumo_kwh` | número | Consumo mensual estimado en kWh |
| `uso_horario_pico` | booleano | Uso de algún aparato en horario de mayor demanda |
| `cantidad_equipos` | entero | Número total de equipos (no incluye focos) |
| `tipo_inmueble` | texto | `Casa` / `Departamento` / `Otro` |
| `horas_alto_consumo` | número | Horas equivalentes de carga intensiva (≥1000 W) |
| `categoria` (objetivo) | texto | `EFICIENTE` / `MODERADO` / `INEFICIENTE` |

### Por qué el etiquetado es multifactor y no solo por consumo

Una primera versión etiquetaba por terciles de `consumo_kwh`. Al medir la importancia
de variables del modelo entrenado con esa etiqueta, `consumo_kwh` explicaba el 100%
de la decisión y las otras cuatro variables el 0%: el formulario tendría 5 campos pero
solo 1 afectaría el resultado, y el problema se resolvería con dos condicionales, sin
necesidad de machine learning.

`etiquetar_dataset.py` reemplaza esto con un sistema de puntos que combina cuatro
factores — consumo (ajustado por tipo de vivienda), uso en horario pico, horas de alto
consumo e intensidad de consumo por equipo — usando los **percentiles del propio
dataset** como cortes (no valores fijos), para que los umbrales se recalculen solos si
la base cambia.

### Límite declarado

`consumo_kwh` en el dataset de entrenamiento es una estimación física derivada de los
aparatos declarados por el hogar, no una lectura de medidor — ENCEVI registra el monto
pagado en pesos, no kilovatios directamente. En producción, este valor lo reporta el
propio usuario a partir de su recibo de luz.

## Resultados del notebook

**Balance de clases** (dataset final, `dataset_entrenamiento.csv`, ~28,764 hogares):

| Categoría | Porcentaje |
|---|---|
| EFICIENTE | ~24% |
| MODERADO | ~28% |
| INEFICIENTE | ~48% |

Ninguna clase por debajo del 15%, umbral que el propio script de etiquetado revisa
como señal de alerta.

**Comparación de modelos** (Regresión Logística, Árbol de Decisión, Random Forest),
evaluados con accuracy, F1-macro y validación cruzada de 5 folds. El modelo elegido
queda documentado automáticamente en `models/reporte_metricas.json` tras correr el
notebook, junto con sus métricas exactas de la corrida.

**Nota sobre el accuracy alto:** como la etiqueta se deriva de reglas propias sobre las
mismas variables de entrada, el modelo tiende a re-aprender esas reglas con métricas
muy altas (~99%). Es un resultado esperado, no una señal de fuga de datos: la curva de
aprendizaje (sección 7.6 del notebook) **confirma una brecha pequeña entre entrenamiento
y validación cruzada, sin evidencia fuerte de sobreajuste.**

## Qué recibe Backend / inference-service

- `models/modelo_energiai.joblib`: pipeline completo de scikit-learn (preprocesamiento
  + clasificador) — recibe un DataFrame con las 5 columnas del contrato y devuelve la
  categoría directamente vía `.predict()`, sin necesidad de reimplementar la
  codificación de variables en Java o Python.
- `models/reporte_metricas.json`: métricas y metadatos del modelo, para documentación
  sin necesidad de correr el notebook.
- Función `generar_recomendaciones()` (sección 8 del notebook): lógica de reglas para
  las recomendaciones de texto, lista para portar al backend o al inference-service.
- Tarifa de referencia usada: **$0.75 por kWh**.

## Estructura

```
data-science/
├── data/
│   ├── processed/
│   │   └── dataset_entrenamiento.csv       # Dataset final procesado
│   └── raw/
│       └── encevi_2018_base_de_datos_csv.zip # ZIP original de la ENCEVI
├── models/
│   └── modelo_energiai.joblib              # Modelo entrenado y serializado
├── notebooks/
│   ├── EnergiAI_EDA_Modelado.ipynb         # EDA, experimentación y modelado
│   └── README.md                           # Documentación específica de notebooks
├── src/
│   ├── Energia.py                          # Procesamiento de variables ENCEVI
│   └── etiquetar_dataset.py                # Reglas de etiquetado del dataset
├── README.md                               # Documentación general del proyecto
└── requirements.txt                        # Dependencias y librerías del proyecto
```

## Estado

Dataset construido y etiquetado. EDA, comparación de modelos y serialización
completos. Modelo listo para consumo por el inference-service.
