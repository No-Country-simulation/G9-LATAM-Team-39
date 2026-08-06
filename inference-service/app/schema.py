"""
Modelos de datos (Pydantic) para el servicio de inferencia.

Definen y validan lo que entra y sale de POST /predict, siguiendo el contrato
de la API (ver docs/contrato-api.md).
"""

from enum import Enum
from pydantic import BaseModel, Field


class TipoInmueble(str, Enum):
    """Los tres unicos valores que acepta el contrato."""
    CASA = "Casa"
    DEPARTAMENTO = "Departamento"
    OTRO = "Otro"


class PredictRequest(BaseModel):
    """Entrada de /predict: las 5 variables obligatorias del contrato.

    El backend solo envia estas cinco. Nunca manda 'equipos', costo ni nada mas.
    """
    consumo_kwh: float = Field(..., gt=0, le=2000, description="Consumo mensual en kWh")
    uso_horario_pico: bool = Field(..., description="Usa equipos en horario pico")
    cantidad_equipos: int = Field(..., ge=1, le=60, description="Numero de equipos")
    tipo_inmueble: TipoInmueble = Field(..., description="Casa | Departamento | Otro")
    horas_alto_consumo: float = Field(..., ge=0, le=24, description="Horas de alto consumo")

    model_config = {
        "json_schema_extra": {
            "example": {
                "consumo_kwh": 420,
                "uso_horario_pico": True,
                "cantidad_equipos": 10,
                "tipo_inmueble": "Casa",
                "horas_alto_consumo": 8,
            }
        }
    }


class PredictResponse(BaseModel):
    """Salida de /predict: solo categoria y probabilidad.

    El costo, la moneda y las recomendaciones los agrega el backend, no aqui.
    """
    categoria: str = Field(..., description="EFICIENTE | MODERADO | INEFICIENTE")
    probabilidad: float = Field(..., ge=0, le=1, description="Confianza de la prediccion")
