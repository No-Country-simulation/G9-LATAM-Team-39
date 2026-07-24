# Data Science

Preparación de datos, análisis exploratorio, entrenamiento y evaluación del modelo, y serialización del modelo final que se sube a OCI.

> Flujo completo del proyecto: ver `../docs/flujo-proyecto.md`. Contrato de la API: `../docs/contrato-api.md`. Este README es operativo.

> Reparto por frentes: ver "Frentes de trabajo" en la documentación de No Country.

## Cómo correr

```bash
# desde data-science/
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook   # abrir notebooks/02_modelado.ipynb
```

## Estrategia de datos

El dataset se construye a partir de los **microdatos reales de ENCEVI 2018 (INEGI)**, no de datos simulados. La descripción del proyecto pide una base propia *"recopilada de fuentes públicas"* y **definir y justificar los criterios** de cada perfil de eficiencia.

El proceso tiene dos pasos encadenados:

1. **`Energia.py`** — lee las 13 tablas de ENCEVI y calcula el consumo **aparato por aparato** (potencia × horas de uso × cantidad). Produce `01_base_hogares_2018_mvp.csv` con 28,763 hogares y las 5 variables del contrato. También genera `02_base_hogares_2026_mvp.csv`, un escenario con equipos eficientes que alimenta las recomendaciones (no se usa para entrenar).

2. **`etiquetar_dataset.py`** — agrega la columna `categoria` con un sistema de puntos multifactor. Produce `dataset_entrenamiento.csv` con exactamente 6 columnas.

```bash
python etiquetar_dataset.py
```

Corre sin argumentos. Por defecto busca `01_base_hogares_2018_mvp.csv` **en la carpeta desde donde se ejecuta**, para que se pueda probar rápido dejando el CSV al lado del script.

**Ajusten la ruta según dónde tengan los archivos.** Las dos constantes están al inicio del script:

```python
ARCHIVO_ENTRADA = "01_base_hogares_2018_mvp.csv"          # al lado del script
ARCHIVO_ENTRADA = "data/processed/01_base_hogares_2018_mvp.csv"   # con la estructura de abajo
```

Si el script no encuentra el archivo, lo dice con un mensaje claro indicando qué revisar. También se puede pasar la ruta al vuelo sin tocar el código: `python etiquetar_dataset.py --in ruta/al/archivo.csv`.

### Por qué el etiquetado es multifactor

La versión inicial asignaba la categoría por terciles de `consumo_kwh`. Al medirlo, el modelo daba **100 % de accuracy con `consumo_kwh` explicando el 100 %** y las otras cuatro variables en 0 %: el usuario llenaría cinco campos y solo uno afectaría el resultado.

Con el sistema de puntos (consumo + horario pico + horas + intensidad) las cinco variables aportan: consumo 58.8 %, horas 20.8 %, equipos 14.4 %, pico 5.7 % y tipo de inmueble 0.3 %. Detalle en `../docs/reglas-etiquetado.md`.

## Variables

Features del modelo: `consumo_kwh`, `uso_horario_pico`, `cantidad_equipos`, `tipo_inmueble`, `horas_alto_consumo`.
Target: `categoria` ∈ {`EFICIENTE`, `MODERADO`, `INEFICIENTE`}.

El costo, la moneda y las recomendaciones NO son del modelo; los calcula el backend.

## Entregables del módulo

1. Base derivada de ENCEVI con las 5 variables (`Energia.py`).
2. Dataset etiquetado de 6 columnas (`etiquetar_dataset.py`).
3. **EDA**: distribuciones, correlaciones, balance de clases.
4. **Comparación de modelos**: Regresión Logística, Árbol de Decisión, Random Forest.
5. **Evaluación**: accuracy, F1 por clase, matriz de confusión.
6. **Serialización** con Joblib → subir a OCI Object Storage.

## Nota metodológica

Como la etiqueta se deriva de reglas propias, el modelo tiende a re-aprenderlas y el accuracy resulta muy alto (~99 %). Es esperado y correcto para el entregable "modelo supervisado entrenado, evaluado y serializado", pero **debe documentarse con honestidad** en el notebook: el valor está en la justificación de los criterios y en una evaluación limpia, no en el accuracy.

Verificación obligatoria: que **ninguna variable quede en 0 % de importancia**. Si ocurre, avisar al frente de dataset.

## Estructura

```
data-science/
├── data/
│   ├── raw/         # los 13 CSV de ENCEVI (no versionar: son pesados)
│   └── processed/   # base_mvp y dataset_entrenamiento
├── notebooks/
│   ├── 01_eda.ipynb
│   └── 02_modelado.ipynb
├── src/
│   ├── Energia.py             # ENCEVI -> 5 variables
│   └── etiquetar_dataset.py   # + categoria
├── models/          # model.joblib
└── requirements.txt
```

## Estado

Dataset construido y etiquetado. Pendiente: EDA, comparación de modelos y serialización.
