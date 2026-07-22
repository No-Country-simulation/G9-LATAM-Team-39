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

## Endpoint interno

`POST /predict` — recibe las 5 variables del contrato y devuelve **solo**:

```json
{ "categoria": "Ineficiente", "probabilidad": 0.81 }
```

El costo, la moneda y las recomendaciones NO se calculan aquí; los agrega el backend.

## Responsabilidades del módulo

- Descargar y cargar el modelo entrenado desde OCI al arrancar.
- Validar los datos recibidos desde el backend.
- Aplicar las **mismas transformaciones** usadas en el entrenamiento.
- Realizar la predicción y obtener la probabilidad (`predict_proba` cuando el modelo lo soporte).
- Devolver categoría y probabilidad.
- Gestionar errores de carga o predicción.

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
