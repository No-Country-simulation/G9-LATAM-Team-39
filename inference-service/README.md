# Inference Service — EnergiAI

Servicio Python (FastAPI) que carga el modelo entrenado y clasifica el perfil
energético de una vivienda. Solo clasifica: el costo y las recomendaciones son
responsabilidad del backend Java.

> Arquitectura global y **contrato único**: ver `../docs/` y `../docs/contrato-api.md`.
> Este README es operativo.

## Cómo correr en local

```bash
# desde inference-service/
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- API:  http://localhost:8000
- Docs: http://localhost:8000/docs  (Swagger automático, útil para la demo)

> Arrancar siempre **desde `inference-service/`**. La ruta por defecto del modelo
> es relativa a esta carpeta.

### Configuración con `.env`

El servicio lee su configuración de un archivo `.env` en `inference-service/`
(gracias a `python-dotenv`, incluido en el `requirements.txt`). Para empezar,
copia la plantilla y ajústala:

```bash
cp .env.example .env
```

En local no hace falta cambiar nada: el `.env` viene con `MODEL_SOURCE=local` y
la ruta al modelo ya configurada. El `.env` real **no se sube al repo** (está en
`.gitignore`); solo se versiona `.env.example` como plantilla.

## Endpoints

| Endpoint | Qué hace |
|---|---|
| `GET /health` | Verifica que el servicio está vivo y el modelo cargado |
| `POST /predict` | Recibe las 5 variables, devuelve `categoria` + `probabilidad` |

`POST /predict` devuelve **solo** categoría y probabilidad:

```json
{ "categoria": "INEFICIENTE", "probabilidad": 1.0 }
```

El campo `equipos` **nunca llega** a este servicio. El costo y las recomendaciones
los agrega el backend.

## El modelo es un Pipeline completo (importante)

El `modelo_energiai.joblib` no es solo un clasificador: es un **Pipeline** con dos pasos:

```
[ ColumnTransformer (preprocesa) ] → [ RandomForestClassifier (clasifica) ]
```

El `ColumnTransformer` hace **por dentro** el one-hot de `tipo_inmueble` y el
escalado de las variables numéricas. Entrada esperada: las **5 variables crudas**,
con `tipo_inmueble` como texto (`Casa` / `Departamento` / `Otro`).

```
consumo_kwh, uso_horario_pico, cantidad_equipos, tipo_inmueble, horas_alto_consumo
```

### Corrección aplicada al conectar el modelo real

La primera versión del servicio hacía one-hot y conversión de tipos **a mano** en
`main.py` (`_preparar_features`). Al conectar el modelo real dio error 500:

```
ufunc 'isnan' not supported for the input types
```

**Causa:** el servicio preprocesaba y el pipeline volvía a preprocesar → doble
codificación. **Solución:** `_preparar_features` ahora entrega las 5 variables
**crudas** y deja que el pipeline haga todo el preprocesamiento. Es el único cambio;
el resto del servicio quedó igual.

> Este arreglo aplica igual a local y a OCI: cambia *cómo se usa* el modelo, no
> *de dónde viene*. Al activar OCI no hay que volver a tocar `_preparar_features`.

## Estado: probado en local con el modelo real

El servicio se probó de punta a punta con `modelo_energiai.joblib` (el real, no un
dummy) desde `/docs`. Las tres categorías se distinguen correctamente:

| Entrada | Resultado |
|---|---|
| `consumo 30, Casa, 6 equipos, pico no, 0 horas` | **EFICIENTE** (prob 0.98) |
| `consumo 45, Departamento, 4 equipos, pico no, 0.2 horas` | **MODERADO** |
| `consumo 420, Casa, 12 equipos, pico sí, 8 horas` | **INEFICIENTE** (prob 1.0) |

Ejemplo EFICIENTE para copiar en `/docs`:

```json
{
  "consumo_kwh": 30,
  "uso_horario_pico": false,
  "cantidad_equipos": 6,
  "tipo_inmueble": "Casa",
  "horas_alto_consumo": 0.0
}
```

Ejemplo INEFICIENTE:

```json
{
  "consumo_kwh": 420,
  "uso_horario_pico": true,
  "cantidad_equipos": 12,
  "tipo_inmueble": "Casa",
  "horas_alto_consumo": 8
}
```

La validación también funciona: un `tipo_inmueble` fuera de `Casa/Departamento/Otro`
(por ejemplo `"Mansion"`) se rechaza con error 422 antes de llegar al modelo.

## Versión de scikit-learn (pendiente de alinear)

El modelo se entrenó con **scikit-learn 1.8.0**. El servicio debe usar la misma
versión, o al cargar el `.joblib` aparece un `InconsistentVersionWarning` que
advierte de posibles resultados inválidos. En `requirements.txt`:

```
scikit-learn==1.8.0
```

y luego `pip install -r requirements.txt --upgrade`.

## Carga del modelo: local ahora, OCI después

`app/model_loader.py` decide de dónde sale el modelo según la variable
`MODEL_SOURCE`, que se define en el `.env`:

- `MODEL_SOURCE=local` (por defecto): lee el `.joblib` del disco. La ruta por
  defecto apunta a `../data-science/models/modelo_energiai.joblib`.
- `MODEL_SOURCE=oci`: descargará el modelo desde OCI Object Storage (requisito
  obligatorio del hackathon). La función `_cargar_desde_oci()` tiene el esqueleto
  listo; se completa cuando exista el bucket.

Para activar OCI, se editan estas variables en el `.env` (los valores los provee
el encargado de OCI):

```
MODEL_SOURCE=oci
OCI_NAMESPACE=<namespace>
OCI_BUCKET=<bucket>
OCI_MODEL_OBJECT=modelo_energiai.joblib
OCI_CONFIG_FILE=~/.oci/config
```

Las credenciales reales de OCI (el archivo de config y las llaves `.pem`) viven
en `~/.oci/`, **fuera del proyecto**, y nunca se suben al repo.

**Si el modelo no carga, el servicio no debe levantar.** El backend ya contempla
este caso: si el servicio no responde, devuelve `502`.

## Estructura

```
inference-service/
├── .env                 # config real (NO se sube al repo)
├── .env.example         # plantilla de variables (sí se sube)
├── app/
│   ├── main.py          # FastAPI + /predict + /health
│   ├── model_loader.py  # carga local (por defecto) / OCI, según .env
│   └── schema.py        # validación de las 5 variables
└── requirements.txt
```

El modelo vive en `data-science/models/` (no se duplica aquí). Al pasar a OCI, se
descargará desde el bucket.
