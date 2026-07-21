# Data Science

Este módulo contendrá el proceso de preparación de datos, análisis exploratorio, entrenamiento y evaluación del modelo de Machine Learning.

## Responsabilidades previstas

- Analizar las fuentes de información disponibles.
- Seleccionar las variables relevantes.
- Unir las tablas necesarias.
- Limpiar y transformar los datos.
- Crear variables derivadas.
- Definir y documentar las categorías energéticas.
- Realizar análisis exploratorio.
- Entrenar diferentes modelos supervisados.
- Comparar métricas.
- Seleccionar el modelo final.
- Serializar el modelo para su uso en producción.

## Estructura

### `data/raw/`

Contendrá referencias o datos originales sin modificar.

Los datasets originales de gran tamaño no deben subirse directamente al repositorio. Su origen y método de descarga deberán documentarse.

### `data/processed/`

Contendrá datasets limpios y procesados utilizados para el entrenamiento.

### `notebooks/`

Contendrá notebooks de preparación, análisis exploratorio, modelado y evaluación.

Ejemplos previstos:

- `01_preparacion_dataset.ipynb`
- `02_eda.ipynb`
- `03_modelado.ipynb`

### `models/`

Contendrá el modelo final serializado y sus metadatos, siempre que su tamaño permita almacenarlo en el repositorio.

### `src/`

Contendrá funciones reutilizables para procesamiento, transformación, entrenamiento y predicción.

## Variables mínimas previstas

- `consumo_kwh`
- `uso_horario_pico`
- `cantidad_equipos`
- `tipo_inmueble`
- `horas_alto_consumo`
- `categoria`

## Categoría objetivo

La variable objetivo será:

`categoria`

Con los valores:

- `EFICIENTE`
- `MODERADO`
- `INEFICIENTE`

## Fuente inicial de referencia

Se evaluará el uso de información de la Encuesta Nacional sobre Consumo de Energéticos en Viviendas Particulares, ENCEVI.

La documentación de la fuente no sustituye los microdatos. El equipo deberá identificar, descargar y procesar los archivos de datos correspondientes.

## Estado

La preparación del dataset y el análisis exploratorio todavía no han comenzado.