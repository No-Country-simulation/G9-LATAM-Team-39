# Data Science

Preparación de datos, análisis exploratorio, entrenamiento y evaluación del modelo de Machine Learning, y serialización del modelo final que se sube a OCI.

> **Contrato único** de variables y estrategia de datos: ver `../docs/` y `../docs/reglas-etiquetado.md`. Este README es operativo.

> Reparto por frentes: ver "Frentes de trabajo" en la documentación de No Country.

## Cómo correr

```bash
# desde data-science/
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook   # abrir notebooks/03_modelado.ipynb
```

## Estrategia de datos (importante)

El dataset se **genera de forma sintética**. La descripción del proyecto pide construir una base propia *"generada manualmente o simulada"* y **definir y justificar los criterios** de cada perfil de eficiencia. Por eso:

1. Se construye un **generador sintético** que produce directamente las 5 variables del contrato + la etiqueta.
2. Las **reglas de etiquetado** (Eficiente / Moderado / Ineficiente) se definen y **justifican** explícitamente (ver `../docs/reglas-etiquetado.md`).
3. **ENCEVI 2018 (INEGI)** se usa **solo como calibración y respaldo público** de los rangos (equipos por tipo de vivienda, horas de uso), y se cita en el notebook. **No** se descargan ni procesan sus microdatos: ENCEVI registra el monto pagado en pesos, no kWh, y no mapea al contrato sin una estimación costosa y con error alto.

## Responsabilidades del módulo

- Construir el generador de dataset sintético + reglas de etiquetado.
- Calibrar rangos con ENCEVI y documentar la justificación.
- Análisis exploratorio (EDA).
- Entrenar y **comparar** modelos supervisados (Regresión Logística, Árbol, Random Forest).
- Comparar métricas (accuracy, F1 por clase, matriz de confusión) y seleccionar el modelo final.
- Serializar el modelo con Joblib y subirlo a OCI Object Storage.

## Nota metodológica

Como la etiqueta se deriva de reglas propias, el modelo supervisado tenderá a re-aprender esas reglas. Es esperado y correcto para el entregable "modelo supervisado entrenado, evaluado y serializado". El valor está en la justificación de las reglas y una evaluación honesta.

## Variables

Features del modelo: `consumo_kwh`, `uso_horario_pico`, `cantidad_equipos`, `tipo_inmueble`, `horas_alto_consumo`.
Target: `categoria` ∈ {`EFICIENTE`, `MODERADO`, `INEFICIENTE`}.
(El costo, la moneda y las recomendaciones NO son del modelo; los calcula el backend.)

## Estructura

```
data-science/
├── data/
│   ├── raw/         # referencias/calibración (no versionar datos pesados; documentar origen)
│   └── processed/   # dataset sintético generado, listo para entrenar
├── notebooks/
│   ├── 01_generar_dataset.ipynb
│   ├── 02_eda.ipynb
│   └── 03_modelado.ipynb
├── models/          # modelo serializado + metadatos (si el tamaño lo permite)
├── src/             # funciones reutilizables (generación, transformación, entrenamiento)
└── requirements.txt
```

## Estado

La generación del dataset y el análisis exploratorio todavía no han comenzado.
