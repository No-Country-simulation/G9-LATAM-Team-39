"""
Servicio de inferencia de EnergiAI (FastAPI).

Carga el modelo al arrancar y expone POST /predict, que recibe las 5 variables
del contrato y devuelve categoria + probabilidad. Solo clasifica: el costo y las
recomendaciones son responsabilidad del backend Java.

IMPORTANTE: el modelo es un Pipeline completo (preprocesamiento + clasificador).
El pipeline hace el one-hot de tipo_inmueble y el escalado por dentro, asi que
aqui NO codificamos nada: le pasamos las 5 variables tal como llegan del contrato.
Si codificaramos a mano, estariamos preprocesando dos veces y el modelo fallaria.
"""

import pandas as pd
from fastapi import FastAPI, HTTPException

from app.schema import PredictRequest, PredictResponse
from app.model_loader import cargar_modelo

app = FastAPI(
    title="EnergiAI - Inference Service",
    description="Clasifica el perfil energetico de una vivienda.",
    version="1.0.0",
)

# El modelo se carga UNA sola vez, al arrancar el servicio, y queda en memoria.
# Si falla la carga, el servicio no debe levantar: es preferible fallar aqui
# a responder peticiones sin modelo.
try:
    modelo = cargar_modelo()
except Exception as e:
    raise RuntimeError(f"No se pudo cargar el modelo al arrancar: {e}")


def _preparar_features(datos: PredictRequest) -> pd.DataFrame:
    """Arma un DataFrame con las 5 variables CRUDAS que espera el pipeline.

    No se hace one-hot ni conversion manual: el ColumnTransformer dentro del
    pipeline se encarga de todo el preprocesamiento. Solo hay que entregar las
    columnas con los mismos nombres y tipos con los que se entreno el modelo:

        consumo_kwh (num), uso_horario_pico (bool), cantidad_equipos (int),
        tipo_inmueble (texto: Casa/Departamento/Otro), horas_alto_consumo (num)
    """
    return pd.DataFrame([{
        "consumo_kwh": datos.consumo_kwh,
        "uso_horario_pico": datos.uso_horario_pico,
        "cantidad_equipos": datos.cantidad_equipos,
        "tipo_inmueble": datos.tipo_inmueble.value,   # el texto: 'Casa', etc.
        "horas_alto_consumo": datos.horas_alto_consumo,
    }])


@app.get("/health")
def health():
    """Chequeo simple de que el servicio esta vivo y con modelo cargado."""
    return {"status": "ok", "modelo_cargado": modelo is not None}


@app.post("/predict", response_model=PredictResponse)
def predict(datos: PredictRequest):
    """Clasifica una vivienda. Devuelve categoria + probabilidad."""
    try:
        X = _preparar_features(datos)
        categoria = modelo.predict(X)[0]
        probabilidad = float(modelo.predict_proba(X)[0].max())
        return PredictResponse(categoria=str(categoria), probabilidad=round(probabilidad, 4))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la prediccion: {e}")
