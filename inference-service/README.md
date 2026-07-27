# Inference Service

Servicio independiente en Python que carga el modelo de Machine Learning **desde OCI Object Storage** y ejecuta la inferencia. Funciona como puente entre el backend Java y el modelo serializado.

> Arquitectura global y **contrato único**: ver `../docs/` y `../docs/contrato-api.md`. Este README es operativo.

> Reparto por frentes: ver "Frentes de trabajo" en la documentación de No Country.

## Cómo correr

```bash
# desde inference-service/
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

## Variables de entorno (OCI)

| Variable | Descripción |
|---|---|
| `OCI_BUCKET` | Nombre del bucket de Object Storage |
| `OCI_NAMESPACE` | Namespace de OCI |
| `OCI_MODEL_OBJECT` | Nombre del objeto del modelo (ej. `model.joblib`) |
| `OCI_CONFIG_FILE` | Ruta al config de OCI (ej. `~/.oci/config`) |

## Carga del modelo desde OCI (requisito obligatorio)

Al arrancar, el servicio **descarga `OCI_MODEL_OBJECT` desde el bucket** de Object Storage y lo carga con Joblib. Esto cubre el requisito obligatorio de OCI del hackathon.

**Probar primero con un `.joblib` dummy** (ver `../docs/guia-oci.md`) antes de tener el modelo real. Si la descarga y carga funcionan con el dummy, el requisito de OCI queda cerrado desde el Sprint 1.

**Si el modelo no carga, el servicio no debe levantar.** Es preferible fallar al arrancar, con un mensaje claro en el log, a quedar respondiendo peticiones sin modelo. El backend ya contempla este caso: si el servicio no responde, devuelve `502 INFERENCE_UNAVAILABLE`.

## Endpoint interno

`POST /predict` — recibe las 5 variables del contrato y devuelve **solo**:

```json
{ "categoria": "Ineficiente", "probabilidad": 0.81 }
```

El costo, la moneda y las recomendaciones NO se calculan aquí; los agrega el backend. El campo `equipos` **nunca llega** a este servicio.

## Entrada y codificación de variables

El modelo fue entrenado con estas columnas y espera exactamente las mismas, en el mismo formato.

| Variable | Cómo llega | Cómo se codifica |
|---|---|---|
| `consumo_kwh` | número | tal cual |
| `uso_horario_pico` | booleano | **0 / 1** |
| `cantidad_equipos` | entero | tal cual |
| `tipo_inmueble` | texto | **one-hot** |
| `horas_alto_consumo` | número | tal cual |

**`tipo_inmueble` solo admite tres valores: `Casa`, `Departamento` y `Otro`.** El dataset se normaliza a estos tres antes de entrenar (ver `../docs/decisiones.md`, D11), así que el modelo no conoce ningún otro. Si llegara un valor distinto, el one-hot generaría una columna desconocida y la predicción sería inválida: conviene validarlo y devolver un error en vez de predecir.

**El orden de las columnas importa.** Scikit-learn no siempre avisa si llegan desordenadas y las predicciones salen mal en silencio. Reordenar siempre según lo que espera el modelo:

```python
X = X[modelo.feature_names_in_]
```

## Responsabilidades del módulo

- Descargar y cargar el modelo entrenado desde OCI al arrancar (una sola vez, no en cada petición).
- Validar los datos recibidos desde el backend, incluido el catálogo de `tipo_inmueble`.
- Aplicar las mismas transformaciones del entrenamiento (ver la tabla de arriba) y **respetar el orden de columnas**.
- Realizar la predicción y obtener la probabilidad (`predict_proba` cuando el modelo lo soporte).
- Devolver categoría y probabilidad.
- Gestionar errores de carga o predicción.

> **Sobre la probabilidad:** como la etiqueta se deriva de reglas deterministas, el modelo suele devolver valores muy altos (cercanos a 1.0). Es esperado y está documentado en `../docs/reglas-etiquetado.md`; no es un error del servicio.

## Tecnologías

Python 3.11, FastAPI, Uvicorn, Scikit-learn, Pandas, Joblib, SDK de OCI (`oci`).

## Estructura sugerida

```
inference-service/
├── app/
│   ├── main.py          # FastAPI + endpoint /predict
│   ├── model_loader.py  # descarga desde OCI + joblib.load
│   └── schema.py        # modelos Pydantic del contrato
└── requirements.txt
```

## Estado

El servicio FastAPI todavía no ha sido inicializado.
