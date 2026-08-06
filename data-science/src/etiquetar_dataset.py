"""
===============================================================================
ETIQUETADO DEL DATASET DE ENTRENAMIENTO — EnergiAI
===============================================================================

Equipo: este script es el ultimo paso antes de entrenar el modelo. Aqui les
explico que hace y por que lo hicimos asi, para que no quede como una caja negra.

QUE HACE
--------
Toma la base que sale de Energia.py (los hogares reales de ENCEVI ya convertidos
a las 5 variables de la API) y le agrega la columna "categoria":
EFICIENTE, MODERADO o INEFICIENTE.

Eso es todo. No genera hogares, no inventa datos, no toca las 5 variables.
Solo calcula la etiqueta que el modelo va a aprender a predecir.

POR QUE NO USAMOS EL ETIQUETADO ORIGINAL POR TERCILES
-----------------------------------------------------
La primera version asignaba la categoria cortando consumo_kwh en terciles
(percentil 33 y 67). El problema: la etiqueta dependia de UNA SOLA variable.

Lo medimos entrenando un modelo con esa etiqueta y salio esto:
    accuracy 100%  |  consumo_kwh 100% de importancia  |  las otras 4 en 0%

Traducido: el usuario llenaba 5 campos en el formulario y solo 1 afectaba el
resultado. Ademas, si la categoria solo depende del consumo, no hace falta
machine learning: bastan dos "if". El modelo no se justificaria.

Con el sistema multifactor de este script la importancia quedo asi:
    consumo 58.8%  |  horas 20.8%  |  equipos 14.4%
    pico 5.7%      |  tipo de inmueble 0.3%
Las 5 variables aportan, que es lo que necesitamos.

COMO FUNCIONA EL ETIQUETADO
---------------------------
Sumamos "puntos de ineficiencia" de cuatro factores. Mas puntos = peor perfil:

    puntaje = P1 consumo + P2 horario pico + P3 horas + P4 intensidad

    0 a 4 puntos  -> EFICIENTE
    5 a 8 puntos  -> MODERADO
    9 o mas       -> INEFICIENTE

DE DONDE SALEN LOS UMBRALES (importante)
----------------------------------------
No los inventamos. Se calculan con los PERCENTILES del propio dataset cada vez
que corre el script. Nosotros solo decidimos en que percentiles cortar.

Esto tiene una ventaja concreta: si la base cambia (por ejemplo si corregimos el
tema del periodo bimestral de CFE y los consumos se duplican), los umbrales se
recalculan solos. Nadie tiene que acordarse de actualizar numeros a mano.

QUE SALE Y QUE NO SALE
----------------------
El CSV final tiene EXACTAMENTE 6 columnas: las 5 de la API + categoria.

El puntaje y los factores parciales NO se guardan. Si los guardaramos, el modelo
tendria la respuesta escondida en una columna y sacaria 100% de accuracy sin
aprender nada. Eso se llama data leakage y es un error grave.

USO
---
    python etiquetar_dataset.py

Corre sin argumentos: lee 01_base_hogares_2018_mvp.csv de la raiz del proyecto
y escribe dataset_entrenamiento.csv. Si los archivos estan en otra carpeta, se
ajustan las constantes ARCHIVO_ENTRADA / ARCHIVO_SALIDA mas abajo.
===============================================================================
"""

import argparse
import numpy as np
import pandas as pd


# =============================================================================
# CONFIGURACION — esto es lo unico que conviene tocar si queremos ajustar algo
# =============================================================================

# --- Archivos de entrada y salida ---
# Estos son los nombres por defecto. Asumen que los CSV estan en la RAIZ del
# proyecto, es decir en la misma carpeta desde donde ejecutan el script.
#
# Si el archivo esta dentro de una carpeta, agreguen la ruta aqui. Ejemplos:
#     ARCHIVO_ENTRADA = "salidas_energiai/01_base_hogares_2018_mvp.csv"
#     ARCHIVO_ENTRADA = "data/processed/01_base_hogares_2018_mvp.csv"
#     ARCHIVO_ENTRADA = "../data-science/01_base_hogares_2018_mvp.csv"
#
# Tambien se pueden pasar por linea de comandos sin tocar el codigo:
#     python etiquetar_dataset.py --in otra_base.csv --out otra_salida.csv
# Lo que se pase por linea de comandos gana sobre estos valores.
ARCHIVO_ENTRADA = "01_base_hogares_2018_mvp.csv"
ARCHIVO_SALIDA = "dataset_entrenamiento.csv"

# Las 5 columnas que exige el contrato de la API. Si la base no las trae, el
# script se detiene: preferimos fallar temprano que entrenar con datos malos.
COLS = ["consumo_kwh", "uso_horario_pico", "cantidad_equipos",
        "tipo_inmueble", "horas_alto_consumo"]

# --- Donde cortamos cada factor ---
# OJO: estos numeros NO son kWh ni horas. Son POSICIONES en la distribucion.
# Ejemplo: 20 significa "el valor que deja al 20% de los hogares por debajo".
# El codigo los convierte a valores reales con np.percentile mas abajo.
#
# Elegimos 4 cortes para el consumo (5 tramos: 0-2-4-6-8 puntos) porque es el
# factor que mas debe pesar, y 3 cortes para los otros dos.
# Si alguien propone otros percentiles: cambiar aqui, correr, y comparar el
# balance de clases y la importancia de variables. Es una prueba de 2 minutos.
CORTES_CONSUMO = [20, 40, 60, 80]   # -> puntos 0, 2, 4, 6, 8
CORTES_HORAS = [40, 70, 90]         # -> puntos 0, 2, 3, 4
CORTES_INTENS = [40, 70, 90]        # -> puntos 0, 1, 2, 3

# --- Normalizacion de tipo_inmueble ---
# El contrato de la API solo acepta tres valores: Casa, Departamento y Otro.
# Pero Energia.py produce ademas "Vivienda_compartida" (1.4% de los hogares).
# Si dejaramos ese cuarto valor, el modelo aprenderia una categoria que la API
# nunca le va a enviar, y al codificar las variables sobraria una columna.
# Por eso lo mapeamos a "Otro": asi el dataset y el contrato coinciden exacto.
NORMALIZAR_TIPO = {
    "Vivienda_compartida": "Otro",
    "Apartamento": "Departamento",
    "Casa grande": "Casa",
}
TIPOS_CONTRATO = ["Casa", "Departamento", "Otro"]

# --- Ajuste por tipo de vivienda ---
# Antes de mirar el consumo lo dividimos por este factor. La razon: una casa
# grande consume mas por ser grande, no por ser ineficiente. Sin este ajuste
# estariamos castigando el tamano en vez del comportamiento.
#
# Dividir entre un numero MENOR que 1 sube el resultado (penaliza mas).
# Dividir entre un numero MAYOR que 1 lo baja (penaliza menos).
# Estos valores si son criterio nuestro, no salen de ENCEVI.
# Solo los tres valores del contrato: despues de normalizar no existe ningun
# otro. (En el generador sintetico inicial habia una categoria "Casa grande"
# con factor 1.25; al adoptar los datos de ENCEVI dejo de existir y ahora se
# mapea a "Casa". Ver decisiones.md, D11.)
FACTOR_TIPO = {
    "Departamento": 0.85,
    "Casa": 1.00,
    "Otro": 1.00,
}

# Cortes del puntaje final. Maximo posible: 8 + 2 + 4 + 3 = 17 puntos.
CORTE_EFICIENTE = 4    # hasta 4 puntos -> EFICIENTE
CORTE_MODERADO = 8     # de 5 a 8       -> MODERADO ; 9 o mas -> INEFICIENTE


# =============================================================================
# FUNCION AUXILIAR
# =============================================================================

def _puntos_por_percentil(serie, cortes_pct, puntos):
    """Convierte percentiles en puntos.

    Trabaja en dos tiempos:
      1) np.percentile traduce las posiciones (ej. 20, 40, 60, 80) a valores
         reales de los datos (ej. 57.1, 83.1, 113.8, 172.7 kWh).
      2) np.searchsorted revisa en que tramo cae cada hogar y le asigna
         los puntos que corresponden a ese tramo.

    Usamos searchsorted en vez de una cadena de "if" porque maneja bien los
    empates: si muchos hogares tienen el mismo valor (pasa con las horas, que
    tienen muchos ceros), todos caen en el mismo tramo sin quedar repartidos
    de forma arbitraria.
    """
    limites = np.percentile(serie, cortes_pct)
    idx = np.searchsorted(limites, serie, side="left")
    return np.array(puntos)[idx]


# =============================================================================
# ETIQUETADO
# =============================================================================

def etiquetar(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Recibe la base con las 5 variables y devuelve el dataset con categoria."""

    # Fallamos temprano si falta algo. Mejor un error claro aqui que un modelo
    # entrenado con columnas equivocadas.
    faltan = [c for c in COLS if c not in df.columns]
    if faltan:
        raise ValueError(
            f"Faltan columnas del contrato: {faltan}\n"
            f"Revisa que estes usando el archivo _mvp de Energia.py, "
            f"no la base intermedia."
        )

    d = df.copy()

    # -------------------------------------------------------------------------
    # PASO 0a — Normalizar tipo_inmueble a los tres valores del contrato
    # -------------------------------------------------------------------------
    # Cualquier valor fuera del contrato cae en "Otro".
    d["tipo_inmueble"] = d["tipo_inmueble"].replace(NORMALIZAR_TIPO)
    fuera = ~d["tipo_inmueble"].isin(TIPOS_CONTRATO)
    if fuera.any() and verbose:
        print(f"Aviso: {fuera.sum()} filas con tipo_inmueble fuera del contrato "
              f"({d.loc[fuera, 'tipo_inmueble'].unique().tolist()}) -> 'Otro'")
    d.loc[fuera, "tipo_inmueble"] = "Otro"

    # -------------------------------------------------------------------------
    # PASO 0b — Ajustar el consumo por tipo de vivienda
    # -------------------------------------------------------------------------
    # Si el tipo no esta en nuestro diccionario usamos factor 1.0 (neutro),
    # para que un valor inesperado no rompa el script.
    factor = d["tipo_inmueble"].map(FACTOR_TIPO).fillna(1.0)
    consumo_ajustado = d["consumo_kwh"] / factor

    # -------------------------------------------------------------------------
    # PUNTAJE 1 — Consumo (0 a 8 puntos)
    # -------------------------------------------------------------------------
    # Es el factor que mas pesa porque el consumo es la senal dominante.
    # Se calcula sobre el consumo YA AJUSTADO, no sobre el crudo.
    p1 = _puntos_por_percentil(consumo_ajustado, CORTES_CONSUMO, [0, 2, 4, 6, 8])

    # -------------------------------------------------------------------------
    # PUNTAJE 2 — Uso en horario pico (0 o 2 puntos)
    # -------------------------------------------------------------------------
    # Binario: no hay percentiles que calcular. Penaliza porque en hora pico la
    # energia es mas cara y mas contaminante.
    # OJO: pandas puede leer esta columna como bool, texto, entero o FLOAT
    # (esto ultimo pasa si el CSV trae algun valor vacio: True se vuelve 1.0).
    # Si solo comparamos texto, "1.0" no coincide con "1" y TODOS quedarian en
    # False sin lanzar ningun error: el puntaje 2 daria 0 a todo el mundo y la
    # variable quedaria en 0% de importancia. Por eso normalizamos primero a
    # numero cuando se puede, y solo si no es numerico comparamos como texto.
    col = d["uso_horario_pico"]
    num = pd.to_numeric(col, errors="coerce")   # True->1.0, "1"->1.0, "si"->NaN
    pico = num.fillna(-1) > 0
    # Para los valores que no son numericos (texto tipo "True", "si"), comparamos
    # el texto en minusculas.
    texto = col.astype(str).str.strip().str.lower()
    pico = pico | texto.isin(["true", "si", "sí", "verdadero", "v", "yes"])
    p2 = np.where(pico, 2, 0)

    # -------------------------------------------------------------------------
    # PUNTAJE 3 — Horas de alto consumo (0 a 4 puntos)
    # -------------------------------------------------------------------------
    # IMPORTANTE: en la base de ENCEVI esta variable NO son horas de reloj.
    # Son "horas equivalentes de una carga de 1.5 kW" (ver la metodologia de
    # Energia.py). Por eso los umbrales salen chicos (0.02, 0.23, 1.95) y no
    # hay que asustarse: la escala es distinta a la intuitiva.
    p3 = _puntos_por_percentil(d["horas_alto_consumo"], CORTES_HORAS, [0, 2, 3, 4])

    # -------------------------------------------------------------------------
    # PUNTAJE 4 — Intensidad: cuanto consume cada aparato (0 a 3 puntos)
    # -------------------------------------------------------------------------
    # La idea: muchos aparatos con consumo total moderado = equipos eficientes.
    # Pocos aparatos que consumen mucho = equipos ineficientes.
    #
    # Con esto evitamos el doble castigo: no penalizamos "tener muchos equipos"
    # (eso seria injusto), penalizamos "consumir mucho POR equipo".
    # El clip(lower=1) evita dividir entre cero si un hogar reporta 0 equipos.
    ratio = d["consumo_kwh"] / d["cantidad_equipos"].clip(lower=1)
    p4 = _puntos_por_percentil(ratio, CORTES_INTENS, [0, 1, 2, 3])

    # -------------------------------------------------------------------------
    # SUMA Y CLASIFICACION
    # -------------------------------------------------------------------------
    score = p1 + p2 + p3 + p4

    d["categoria"] = np.select(
        [score <= CORTE_EFICIENTE, score <= CORTE_MODERADO],
        ["EFICIENTE", "MODERADO"],
        default="INEFICIENTE",
    )

    if verbose:
        # Imprimimos los umbrales porque no quedan guardados en ningun archivo:
        # se calculan al vuelo. Esta salida es la unica evidencia de que valores
        # se usaron en esta corrida. Conviene copiarla al notebook.
        print("Umbrales calculados con los percentiles de ESTE dataset:")
        print("  consumo ajustado (kWh):",
              np.percentile(consumo_ajustado, CORTES_CONSUMO).round(1))
        print("  horas alto consumo    :",
              np.percentile(d["horas_alto_consumo"], CORTES_HORAS).round(2))
        print("  intensidad (kWh/equipo):",
              np.percentile(ratio, CORTES_INTENS).round(1))
        print(f"\nPuntaje: minimo={score.min()} maximo={score.max()} "
              f"promedio={score.mean():.1f} (el maximo posible es 17)")

    # AQUI ESTA LA CLAVE: devolvemos SOLO las 6 columnas.
    # El score, p1, p2, p3 y p4 se quedan fuera a proposito. Si los guardaramos,
    # el modelo veria la respuesta y no aprenderia nada (data leakage).
    return d[COLS + ["categoria"]]


# =============================================================================
# EJECUCION
# =============================================================================

def main():
    p = argparse.ArgumentParser(
        description="Agrega la columna 'categoria' a la base de hogares."
    )
    # Si no pasan nada por linea de comandos, usa los nombres definidos arriba.
    p.add_argument("--in", dest="entrada", default=ARCHIVO_ENTRADA,
                   help=f"CSV de entrada (por defecto: {ARCHIVO_ENTRADA})")
    p.add_argument("--out", dest="salida", default=ARCHIVO_SALIDA,
                   help=f"CSV de salida (por defecto: {ARCHIVO_SALIDA})")
    args = p.parse_args()

    print(f"Leyendo: {args.entrada}")
    try:
        df = pd.read_csv(args.entrada, encoding="utf-8-sig")
    except FileNotFoundError:
        print(f"\nNo encontre el archivo '{args.entrada}'.")
        print("Revisen dos cosas:")
        print("  1) Que esten ejecutando el script desde la carpeta correcta.")
        print("  2) Que ARCHIVO_ENTRADA (arriba del script) apunte a la ruta real.")
        print("     Si el CSV esta en una subcarpeta, incluyanla. Por ejemplo:")
        print('     ARCHIVO_ENTRADA = "salidas_energiai/01_base_hogares_2018_mvp.csv"')
        return

    out = etiquetar(df)
    out.to_csv(args.salida, index=False)

    dist = out["categoria"].value_counts()
    pct = (dist / len(out) * 100).round(1)

    print(f"\nDataset listo: {len(out)} filas -> {args.salida}")
    print("Columnas:", list(out.columns))
    print("\nBalance de clases:")
    for c in ["EFICIENTE", "MODERADO", "INEFICIENTE"]:
        print(f"  {c:<12} {dist.get(c, 0):>6}  ({pct.get(c, 0)} %)")

    # Revision que conviene hacer siempre: si una clase queda muy chica
    # (menos del 15%), el modelo la va a aprender mal. En ese caso hay que
    # mover los cortes del puntaje o los percentiles y volver a correr.
    minimo = pct.min()
    if minimo < 15:
        print(f"\n  AVISO: la clase mas chica tiene {minimo}%. "
              f"Conviene ajustar los cortes y volver a correr.")


if __name__ == "__main__":
    main()
