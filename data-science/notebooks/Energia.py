
from pathlib import Path
import numpy as np
import pandas as pd


# 0. CONFIGURACIÓN GENERAL
DATA_DIR = Path(__file__).resolve().parent  # Aquí deben estar los 13 CSV
OUTPUT_DIR = DATA_DIR / "salidas_energiai"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DIAS_PROMEDIO_MES = 365.25 / 12
CLAVES_HOGAR = ["folio", "foliohog"]


# 1. SUPUESTOS TEÓRICOS EDITABLES
# Estos valores son supuestos de trabajo. Están juntos para que el equipo pueda actualizarlos sin buscar números dentro de todo el script.

# Potencia de focos cuando el hogar no reporta watts válidos
POTENCIA_FOCOS_W = {
    "fluorescente": 18.0,
    "led": 10.0,
    "incandescente": 60.0,
    "desconocido": 24.0,
}

# Otros electrodomésticos de la tabla ELECTRO
# id_electro:
# 1 microondas, 2 licuadora, 3 batidora, 4 cafetera,
# 5 tostador/sandwichera, 6 parrilla u horno eléctrico,
# 7 secadora de pelo, 8 tenaza/plancha para cabello,
# 9 secadora de ropa, 10 máquina de coser eléctrica.
POTENCIA_ELECTRO_W = {
    1: 1200,
    2: 400,
    3: 250,
    4: 900,
    5: 1000,
    6: 1500,
    7: 1500,
    8: 60,
    9: 3000,
    10: 100,
}

# Equipos de tecnología de OTROS_EQ
# 1 módem, 2 decodificador, 3 tablet, 4 laptop,
# 5 computadora de escritorio, 6 impresora, 7 radio,
# 8 estéreo, 9 DVD/Blu-ray, 10 consola, 11 regulador, 12 no-break.
POTENCIA_TECNOLOGIA_W = {
    1: 12,
    2: 15,
    3: 10,
    4: 65,
    5: 150,
    6: 50,
    7: 15,
    8: 80,
    9: 20,
    10: 120,
    11: 10,
    12: 15,
}

# Potencias base de pantallas por tecnología
POTENCIA_PANTALLA_BASE_W = {
    1: 100,  # OLED
    2: 80,   # LED
    3: 160,  # LCD o plasma
    4: 90,   # Analógica
    9: 100,  # No sabe
}

# Multiplicador por tamaño de pantalla
MULTIPLICADOR_TAMANIO_PANTALLA = {
    1: 0.65,  # menor de 30"
    2: 0.85,  # 30-39"
    3: 1.00,  # 40-49"
    4: 1.35,  # 50-60"
    5: 1.70,  # más de 60"
    9: 1.00,
}

# Ventiladores: primera aproximación según código de tipo
POTENCIA_VENTILADOR_W = {
    1: 60,
    2: 75,
    3: 45,
    4: 55,
    5: 60,
    9: 60,
}

# Aires acondicionados: capacidad ENCEVI -> BTU/h representativos
CAPACIDAD_AIRE_BTU = {
    1: 7500,   # menos de 9,000 BTU
    2: 9000,
    3: 12000,
    4: 18000,
    5: 24000,
    6: 30000,  # representa "más de 24,000"
    9: 12000,
}

# EER preliminar por tipo de aire acondicionado
# Potencia aproximada en watts = BTU/h / EER
EER_AIRE = {
    1: 8.5,    # portátil
    2: 9.5,    # ventana
    3: 10.5,   # central
    4: np.nan, # evaporativo; se calcula con potencia fija
    5: 10.5,   # minisplit encendido/apagado
    6: 13.0,   # minisplit inverter
    7: 10.0,   # otro
    9: 10.0,
}

# Factor de carga: el compresor no trabaja al 100% todo el tiempo
FACTOR_CARGA_AIRE = {
    1: 0.80,
    2: 0.75,
    3: 0.75,
    4: 1.00,
    5: 0.75,
    6: 0.65,
    7: 0.75,
    9: 0.75,
}

POTENCIA_EVAPORATIVO_KW = 0.35

# Calefactores eléctricos
POTENCIA_CALEFACTOR_W = {
    1: 1500,  # eléctrico con aceite térmico
    2: 1500,  # eléctrico de resistencia
    3: 1500,  # eléctrico de torre
    # 4 es gas; no se suma a kWh
}

# Calentadores de agua eléctricos
POTENCIA_CALENTADOR_AGUA_W = {
    4: 5500,  # eléctrico instantáneo
    5: 4000,  # eléctrico con depósito
}

# Lavadoras por tipo
POTENCIA_LAVADORA_W = {
    1: 400,   # manual
    2: 500,   # semiautomática
    3: 600,   # automática tapa superior
    4: 500,   # automática frontal
    9: 550,
}

# Planchas
POTENCIA_PLANCHA_W = {
    1: 1400,  # vapor
    2: 1200,  # seca
    9: 1300,
}

# Refrigerador: consumo mensual base según capacidad
# Es preferible usar kWh/mes y no potencia × 24 h, porque trabaja por ciclos.
KWH_REFRIGERADOR_MES = {
    1: 18,  # compacto
    2: 28,  # pequeño
    3: 40,  # mediano
    4: 55,  # grande
    5: 72,  # extragrande
    9: 40,
}

# Bomba de agua: capacidad ENCEVI -> HP representativos
CAPACIDAD_BOMBA_HP = {
    1: 0.25,
    2: 0.50,
    3: 0.75,
    4: 1.00,
    5: 1.50,
}
EFICIENCIA_MOTOR_BOMBA = 0.75


# 2. FUNCIONES GENERALES DE LIMPIEZA
def leer_csv(nombre_archivo):
    """
    Lee un CSV como texto para conservar códigos y ceros a la izquierda.
    """
    ruta = DATA_DIR / nombre_archivo

    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta}. "
            "Verifica que los 13 CSV estén en la misma carpeta."
        )

    df = pd.read_csv(
        ruta,
        dtype=str,
        encoding="utf-8-sig",
        low_memory=False,
    )

    # Limpieza básica de nombres de columnas
    df.columns = [
        str(col).strip().lstrip("\ufeff")
        for col in df.columns
    ]

    # Limpieza básica de texto
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = (
                df[col]
                .str.strip()
                .replace(
                    {
                        "": pd.NA,
                        " ": pd.NA,
                        "NA": pd.NA,
                        "N/A": pd.NA,
                        "nan": pd.NA,
                    }
                )
            )

    # Normalizar llaves
    for llave in CLAVES_HOGAR:
        if llave in df.columns:
            df[llave] = df[llave].astype("string").str.strip()

    return df


def a_numero(
    serie,
    codigos_invalidos=(),
    minimo=None,
    maximo=None,
):
    """
    Convierte una serie a número y elimina códigos de no sabe/no aplica.
    """
    resultado = pd.to_numeric(serie, errors="coerce")

    if codigos_invalidos:
        resultado = resultado.mask(
            resultado.isin(list(codigos_invalidos))
        )

    if minimo is not None:
        resultado = resultado.mask(resultado < minimo)

    if maximo is not None:
        resultado = resultado.mask(resultado > maximo)

    return resultado


def horas_decimales(
    df,
    columna_horas,
    columna_minutos,
):
    """
    Convierte horas y minutos en horas decimales.
    """
    horas = a_numero(
        df[columna_horas],
        codigos_invalidos=(99,),
        minimo=0,
        maximo=24,
    )

    minutos = a_numero(
        df[columna_minutos],
        codigos_invalidos=(99,),
        minimo=0,
        maximo=59,
    ).fillna(0)

    return horas + minutos / 60


def rellenar_mediana_por_grupo(
    df,
    columna,
    grupos,
):
    """
    Completa un dato faltante con hogares parecidos. Si el grupo no alcanza, usa la mediana general para no perder el registro.
    """
    mediana_grupo = df.groupby(grupos)[columna].transform("median")
    df[columna] = (
        df[columna]
        .fillna(mediana_grupo)
        .fillna(df[columna].median())
    )
    return df


def dias_del_periodo_recibo(
    fila,
    numero_medidor,
):
    """
    Calcula los días del periodo del recibo usando día y mes.
    ENCEVI no registra año; se supone fin en 2018.
    Si el periodo cruza diciembre-enero, el inicio se coloca en 2017.
    """
    inicio_dia = fila.get(f"inicia{numero_medidor}")
    inicio_mes = fila.get(f"mes_inic{numero_medidor}")
    final_dia = fila.get(f"final{numero_medidor}")
    final_mes = fila.get(f"mes_final{numero_medidor}")

    valores = [
        inicio_dia,
        inicio_mes,
        final_dia,
        final_mes,
    ]

    if any(pd.isna(valor) for valor in valores):
        return np.nan

    try:
        inicio_dia = int(inicio_dia)
        inicio_mes = int(inicio_mes)
        final_dia = int(final_dia)
        final_mes = int(final_mes)

        if not (1 <= inicio_dia <= 31):
            return np.nan
        if not (1 <= final_dia <= 31):
            return np.nan
        if not (1 <= inicio_mes <= 12):
            return np.nan
        if not (1 <= final_mes <= 12):
            return np.nan

        anio_final = 2018
        anio_inicio = (
            2018
            if (inicio_mes, inicio_dia) <= (final_mes, final_dia)
            else 2017
        )

        fecha_inicio = pd.Timestamp(
            anio_inicio,
            inicio_mes,
            inicio_dia,
        )
        fecha_final = pd.Timestamp(
            anio_final,
            final_mes,
            final_dia,
        )

        dias = (fecha_final - fecha_inicio).days + 1

        # Se consideran razonables periodos de 20 a 100 días
        if 20 <= dias <= 100:
            return float(dias)

        return np.nan

    except (ValueError, TypeError):
        return np.nan


# 3. CARGA DE LOS 13 ARCHIVOS
print("Cargando archivos...")

vivienda = leer_csv("vivienda.csv")
hogar = leer_csv("hogar.csv")
persona = leer_csv("persona.csv")
encevi = leer_csv("encevi.csv")
focos = leer_csv("focos.csv")
electro = leer_csv("electro.csv")
pantalla = leer_csv("pantalla.csv")
otros_eq = leer_csv("otros_eq.csv")
ventilador = leer_csv("ventilador.csv")
aireacond = leer_csv("aireacond.csv")
calefactor = leer_csv("calefactor.csv")
cal_agua = leer_csv("cal_agua.csv")
cambio = leer_csv("cambio.csv")

print("Archivos cargados correctamente.")


# 4. LIMPIEZA DEL ARCHIVO VIVIENDA
print("Limpiando vivienda.csv...")

vivienda_limpia = vivienda[
    [
        "folio",
        "tam_loc",
        "est_socio",
        "factor_sem",
        "region",
        "entidad",
    ]
].copy()

vivienda_limpia["factor_sem"] = a_numero(
    vivienda_limpia["factor_sem"],
    minimo=0,
)

MAPA_REGION = {
    "1": "Calida_extrema",
    "2": "Templada",
    "3": "Tropical",
}

vivienda_limpia["region_climatica"] = (
    vivienda_limpia["region"].map(MAPA_REGION)
)

# Verificar que haya una fila por vivienda
if vivienda_limpia["folio"].duplicated().any():
    raise ValueError(
        "vivienda.csv contiene folios duplicados inesperados."
    )


# 5. LIMPIEZA DEL ARCHIVO HOGAR
print("Limpiando hogar.csv...")

hogar_limpio = hogar[
    [
        "folio",
        "foliohog",
        "tot_integ",
        "tot_hom",
        "tot_muj",
    ]
].copy()

for col in ["tot_integ", "tot_hom", "tot_muj"]:
    hogar_limpio[col] = a_numero(
        hogar_limpio[col],
        minimo=0,
        maximo=30,
    )

# La muestra analizada tiene una fila principal por hogar
if hogar_limpio.duplicated(CLAVES_HOGAR).any():
    raise ValueError(
        "hogar.csv tiene duplicados en folio + foliohog."
    )


# 6. LIMPIEZA Y RESUMEN DEL ARCHIVO PERSONA
print("Limpiando persona.csv...")

persona_limpia = persona[
    [
        "folio",
        "foliohog",
        "id_pobla",
        "edad",
        "sexo",
        "nivel_inst",
    ]
].copy()

persona_limpia["edad_num"] = a_numero(
    persona_limpia["edad"],
    codigos_invalidos=(999,),
    minimo=0,
    maximo=110,
)

persona_limpia["es_menor"] = (
    persona_limpia["edad_num"] < 18
).astype(float)

persona_limpia["es_adulto_mayor"] = (
    persona_limpia["edad_num"] >= 65
).astype(float)

persona_hogar = (
    persona_limpia
    .groupby(CLAVES_HOGAR, as_index=False)
    .agg(
        personas_registradas=("id_pobla", "count"),
        edad_promedio=("edad_num", "mean"),
        menores_hogar=("es_menor", "sum"),
        adultos_mayores_hogar=("es_adulto_mayor", "sum"),
    )
)


# 7. LIMPIEZA DEL ARCHIVO ENCEVI PRINCIPAL
print("Limpiando encevi.csv...")

COLUMNAS_ENCEVI = [
    "folio",
    "foliohog",
    "tipo_viv",
    "total_niv",
    "super_cons",
    "tot_cuart",
    "cuart_dorm",
    "ais_techo",
    "ais_pared",
    "ais_venta",
    "sellos_pv",

    # Recibo
    "cons_med1",
    "cons_med2",
    "inicia1",
    "mes_inic1",
    "final1",
    "mes_final1",
    "inicia2",
    "mes_inic2",
    "final2",
    "mes_final2",
    "tipo_tarif",

    # Focos
    "pot_fluor",
    "pot_led",
    "pot_incan",
    "hora_enc",
    "min_enc",
    "hora_apag",
    "min_apag",

    # Refrigerador
    "uso_refri",
    "tipo_deshi",
    "ptas_refri",
    "cap_refri",
    "uso_ref_a",
    "refri_estu",
    "refri_sol",
    "refri_boil",
    "refri_horn",

    # Lavadora
    "uso_lava",
    "tipo_lava",
    "cap_lava",
    "dias_uso_l",
    "hor_uso_l",
    "min_uso_l",
    "hor_lav3",

    # Plancha
    "uso_plan",
    "tipo_plan",
    "dias_uso_p",
    "hor_uso_p",
    "min_uso_p",
    "hor_plan3",

    # Cantidades generales
    "uso_tv",
    "num_tvs",
    "uso_cel",
    "num_cels",
    "uso_venti",
    "num_venti",
    "uso_aire",
    "num_aire",
    "uso_calef",
    "num_calef",
    "uso_calent",
    "num_calent",

    # Calentamiento de agua
    "uso_cal_d",
    "uso_cal_h",
    "uso_cal_m",
    "comb_calen",

    # Bomba
    "uso_bomba",
    "uso_bom_d",
    "uso_bom_h",
    "uso_bom_m",
    "cap_bomba",

    # Eficiencia y hábitos
    "etiq_ref",
    "sello_ref",
    "etiq_lav",
    "sello_lav",
    "etiq_aire",
    "sello_air",
    "etiq_cal",
    "apaga_foco",
    "apaga_tv",
    "descon_tv",
    "des_horno",
    "des_compu",
    "des_carga",
    "luz_noche",
    "luz_salen",
]

encevi_limpia = encevi[COLUMNAS_ENCEVI].copy()

MAPA_TIPO_VIVIENDA = {
    "1": "Casa",
    "2": "Casa",
    "3": "Casa",
    "4": "Departamento",
    "5": "Vivienda_compartida",
    "6": "Vivienda_compartida",
    "7": "Otro",
}

MAPA_TARIFA = {
    "1": "01",
    "2": "1A",
    "3": "1B",
    "4": "1C",
    "5": "1D",
    "6": "1E",
    "7": "1F",
    "8": "DAC",
    "9": "No_sabe",
}

encevi_limpia["tipo_inmueble"] = (
    encevi_limpia["tipo_viv"].map(MAPA_TIPO_VIVIENDA)
)

encevi_limpia["tarifa_cfe"] = (
    encevi_limpia["tipo_tarif"].map(MAPA_TARIFA)
)

for col in ["total_niv", "tot_cuart", "cuart_dorm"]:
    encevi_limpia[col] = a_numero(
        encevi_limpia[col],
        codigos_invalidos=(99,),
        minimo=0,
        maximo=50,
    )


# 8. FUSIÓN INICIAL: VIVIENDA + HOGAR + ENCEVI + PERSONA
print("Fusionando vivienda, hogar, encevi y persona...")

base = (
    vivienda_limpia
    .merge(
        hogar_limpio,
        on="folio",
        how="inner",
        validate="1:1",
    )
    .merge(
        encevi_limpia,
        on=CLAVES_HOGAR,
        how="inner",
        validate="1:1",
    )
    .merge(
        persona_hogar,
        on=CLAVES_HOGAR,
        how="left",
        validate="1:1",
    )
)

print("Filas después de la fusión principal:", len(base))


# 9. MENSUALIZACIÓN DEL MONTO PAGADO EN EL RECIBO
print("Mensualizando el último recibo...")

# Convertir fechas del periodo a números
for numero_medidor in [1, 2]:
    for col in [
        f"inicia{numero_medidor}",
        f"mes_inic{numero_medidor}",
        f"final{numero_medidor}",
        f"mes_final{numero_medidor}",
    ]:
        base[col] = a_numero(
            base[col],
            codigos_invalidos=(99,),
        )

    base[f"dias_periodo_m{numero_medidor}_exactos"] = (
        base.apply(
            dias_del_periodo_recibo,
            axis=1,
            numero_medidor=numero_medidor,
        )
    )

    base[f"pago_medidor{numero_medidor}"] = a_numero(
        base[f"cons_med{numero_medidor}"],
        codigos_invalidos=(99999,),
        minimo=0,
        maximo=50000,
    )

# Mediana global de periodos exactos
periodos_validos = pd.concat(
    [
        base["dias_periodo_m1_exactos"],
        base["dias_periodo_m2_exactos"],
    ]
).dropna()

MEDIANA_DIAS_RECIBO = (
    float(periodos_validos.median())
    if not periodos_validos.empty
    else 60.0
)

for numero_medidor in [1, 2]:
    dias_exactos = base[
        f"dias_periodo_m{numero_medidor}_exactos"
    ]

    pago = base[f"pago_medidor{numero_medidor}"]

    base[f"dias_periodo_m{numero_medidor}"] = (
        dias_exactos.fillna(MEDIANA_DIAS_RECIBO)
    )

    base[f"calidad_periodo_m{numero_medidor}"] = np.where(
        pago.isna(),
        pd.NA,
        np.where(
            dias_exactos.notna(),
            "exacto",
            "imputado_mediana",
        ),
    )

    base[f"pago_mensual_m{numero_medidor}"] = (
        pago
        * DIAS_PROMEDIO_MES
        / base[f"dias_periodo_m{numero_medidor}"]
    )

base["pago_mensual_observado"] = base[
    ["pago_mensual_m1", "pago_mensual_m2"]
].sum(axis=1, min_count=1)


# 10. LIMPIEZA Y CÁLCULO DE FOCOS
print("Limpiando focos.csv y calculando kWh de iluminación...")

focos_limpios = focos.merge(
    base[
        CLAVES_HOGAR
        + ["pot_fluor", "pot_led", "pot_incan"]
    ],
    on=CLAVES_HOGAR,
    how="left",
    validate="m:1",
)

for col in [
    "foco_num",
    "foco_fluor",
    "foco_led",
    "foco_incan",
]:
    focos_limpios[f"{col}_num"] = (
        a_numero(
            focos_limpios[col],
            codigos_invalidos=(99,),
            minimo=0,
            maximo=50,
        )
        .fillna(0)
    )

focos_limpios["horas_focos_dia"] = horas_decimales(
    focos_limpios,
    "foco_hor",
    "foco_min",
)

focos_limpios = rellenar_mediana_por_grupo(
    focos_limpios,
    "horas_focos_dia",
    ["id_focos"],
)

# Usar potencia reportada; si falta, usar supuesto
focos_limpios["w_fluor"] = (
    a_numero(
        focos_limpios["pot_fluor"],
        codigos_invalidos=(888, 999),
        minimo=1,
        maximo=300,
    )
    .fillna(POTENCIA_FOCOS_W["fluorescente"])
)

focos_limpios["w_led"] = (
    a_numero(
        focos_limpios["pot_led"],
        codigos_invalidos=(888, 999),
        minimo=1,
        maximo=300,
    )
    .fillna(POTENCIA_FOCOS_W["led"])
)

focos_limpios["w_incan"] = (
    a_numero(
        focos_limpios["pot_incan"],
        codigos_invalidos=(888, 999),
        minimo=1,
        maximo=300,
    )
    .fillna(POTENCIA_FOCOS_W["incandescente"])
)

focos_con_tipo = (
    focos_limpios["foco_fluor_num"]
    + focos_limpios["foco_led_num"]
    + focos_limpios["foco_incan_num"]
)

focos_limpios["focos_tipo_desconocido"] = (
    focos_limpios["foco_num_num"] - focos_con_tipo
).clip(lower=0)

focos_limpios["potencia_total_area_w"] = (
    focos_limpios["foco_fluor_num"]
    * focos_limpios["w_fluor"]
    + focos_limpios["foco_led_num"]
    * focos_limpios["w_led"]
    + focos_limpios["foco_incan_num"]
    * focos_limpios["w_incan"]
    + focos_limpios["focos_tipo_desconocido"]
    * POTENCIA_FOCOS_W["desconocido"]
)

focos_limpios["kwh_iluminacion_area"] = (
    focos_limpios["potencia_total_area_w"]
    * focos_limpios["horas_focos_dia"]
    * DIAS_PROMEDIO_MES
    / 1000
)

focos_hogar = (
    focos_limpios
    .groupby(CLAVES_HOGAR, as_index=False)
    .agg(
        cantidad_focos=("foco_num_num", "sum"),
        focos_fluorescentes=("foco_fluor_num", "sum"),
        focos_led=("foco_led_num", "sum"),
        focos_incandescentes=("foco_incan_num", "sum"),
        kwh_iluminacion=("kwh_iluminacion_area", "sum"),
    )
)

focos_hogar["porcentaje_focos_eficientes"] = np.where(
    focos_hogar["cantidad_focos"] > 0,
    (
        focos_hogar["focos_fluorescentes"]
        + focos_hogar["focos_led"]
    )
    / focos_hogar["cantidad_focos"]
    * 100,
    np.nan,
)


# 11. LIMPIEZA Y CÁLCULO DE OTROS ELECTRODOMÉSTICOS
print("Limpiando electro.csv y calculando kWh...")

electro_limpio = electro.copy()

electro_limpio["id_electro_num"] = a_numero(
    electro_limpio["id_electro"],
    minimo=1,
    maximo=10,
)

electro_limpio["usa_equipo"] = (
    electro_limpio["elect_uso"] == "1"
)

electro_limpio["dias_uso_mes"] = a_numero(
    electro_limpio["elect_dia"],
    codigos_invalidos=(99,),
    minimo=0,
    maximo=31,
)

# Código 98 = menos de un día al mes
electro_limpio.loc[
    electro_limpio["elect_dia"] == "98",
    "dias_uso_mes",
] = 0.5

electro_limpio["horas_uso_dia"] = horas_decimales(
    electro_limpio,
    "elect_hor",
    "elect_min",
)

# Imputación solo entre hogares que sí usan ese aparato
for col in ["dias_uso_mes", "horas_uso_dia"]:
    medianas = (
        electro_limpio[electro_limpio["usa_equipo"]]
        .groupby("id_electro_num")[col]
        .median()
    )

    mascara = electro_limpio["usa_equipo"]

    electro_limpio.loc[mascara, col] = (
        electro_limpio.loc[mascara, col]
        .fillna(
            electro_limpio.loc[
                mascara,
                "id_electro_num",
            ].map(medianas)
        )
        .fillna(
            electro_limpio.loc[mascara, col].median()
        )
    )

    electro_limpio.loc[~mascara, col] = 0

electro_limpio["potencia_w"] = (
    electro_limpio["id_electro_num"]
    .map(POTENCIA_ELECTRO_W)
)

electro_limpio["kwh_electro"] = (
    electro_limpio["potencia_w"]
    / 1000
    * electro_limpio["horas_uso_dia"]
    * electro_limpio["dias_uso_mes"]
)

electro_limpio["kwh_electro_alto"] = np.where(
    electro_limpio["potencia_w"] >= 1000,
    electro_limpio["kwh_electro"],
    0,
)

electro_hogar = (
    electro_limpio
    .groupby(CLAVES_HOGAR, as_index=False)
    .agg(
        cantidad_electrodomesticos=("usa_equipo", "sum"),
        kwh_electrodomesticos=("kwh_electro", "sum"),
        kwh_electrodomesticos_alto=(
            "kwh_electro_alto",
            "sum",
        ),
    )
)


# 12. LIMPIEZA Y CÁLCULO DE PANTALLAS
print("Limpiando pantalla.csv y calculando kWh...")

pantalla_limpia = pantalla.copy()

pantalla_limpia["tipo_num"] = a_numero(
    pantalla_limpia["panta_tipo"],
    minimo=1,
    maximo=9,
).fillna(9)

pantalla_limpia["tam_num"] = a_numero(
    pantalla_limpia["panta_tam"],
    minimo=1,
    maximo=9,
).fillna(9)

pantalla_limpia["dias_semana"] = a_numero(
    pantalla_limpia["panta_dia"],
    codigos_invalidos=(9,),
    minimo=1,
    maximo=8,
)

# Código 8 = menos de un día por semana
pantalla_limpia["dias_semana"] = (
    pantalla_limpia["dias_semana"].replace({8: 0.5})
)

pantalla_limpia["horas_dia"] = horas_decimales(
    pantalla_limpia,
    "panta_hor",
    "panta_min",
)

pantalla_limpia = rellenar_mediana_por_grupo(
    pantalla_limpia,
    "dias_semana",
    ["tipo_num", "tam_num"],
)

pantalla_limpia = rellenar_mediana_por_grupo(
    pantalla_limpia,
    "horas_dia",
    ["tipo_num", "tam_num"],
)

pantalla_limpia["potencia_w"] = (
    pantalla_limpia["tipo_num"]
    .map(POTENCIA_PANTALLA_BASE_W)
    * pantalla_limpia["tam_num"]
    .map(MULTIPLICADOR_TAMANIO_PANTALLA)
)

pantalla_limpia["kwh_pantallas"] = (
    pantalla_limpia["potencia_w"]
    / 1000
    * pantalla_limpia["horas_dia"]
    * pantalla_limpia["dias_semana"]
    * (365.25 / 7 / 12)
)

# panta_uso3 corresponde a después de las 18:00 y hasta las 00:00
pantalla_limpia["pantalla_en_pico"] = (
    pantalla_limpia["panta_uso3"].notna()
).astype(int)

pantalla_hogar = (
    pantalla_limpia
    .groupby(CLAVES_HOGAR, as_index=False)
    .agg(
        cantidad_pantallas=("id_panta", "count"),
        kwh_pantallas=("kwh_pantallas", "sum"),
        usa_pantalla_en_pico=("pantalla_en_pico", "max"),
    )
)


# 13. LIMPIEZA Y CÁLCULO DE EQUIPOS DE TECNOLOGÍA
print("Limpiando otros_eq.csv y calculando kWh...")

tecnologia_limpia = otros_eq.copy()

tecnologia_limpia["id_equipo_num"] = a_numero(
    tecnologia_limpia["id_eq_tec"],
    minimo=1,
    maximo=12,
)

tecnologia_limpia["usa_equipo"] = (
    tecnologia_limpia["eqt_uso"] == "1"
)

tecnologia_limpia["cantidad"] = (
    a_numero(
        tecnologia_limpia["eqt_num"],
        codigos_invalidos=(99,),
        minimo=0,
        maximo=50,
    )
    .fillna(0)
)

tecnologia_limpia.loc[
    ~tecnologia_limpia["usa_equipo"],
    "cantidad",
] = 0

tecnologia_limpia["dias_mes"] = a_numero(
    tecnologia_limpia["eqt_dia"],
    codigos_invalidos=(99,),
    minimo=0,
    maximo=31,
)

tecnologia_limpia["horas_dia"] = horas_decimales(
    tecnologia_limpia,
    "eqt_hor",
    "eqt_min",
)

for col in ["dias_mes", "horas_dia"]:
    medianas = (
        tecnologia_limpia[tecnologia_limpia["usa_equipo"]]
        .groupby("id_equipo_num")[col]
        .median()
    )

    mascara = tecnologia_limpia["usa_equipo"]

    tecnologia_limpia.loc[mascara, col] = (
        tecnologia_limpia.loc[mascara, col]
        .fillna(
            tecnologia_limpia.loc[
                mascara,
                "id_equipo_num",
            ].map(medianas)
        )
        .fillna(
            tecnologia_limpia.loc[mascara, col].median()
        )
    )

    tecnologia_limpia.loc[~mascara, col] = 0

tecnologia_limpia["potencia_w"] = (
    tecnologia_limpia["id_equipo_num"]
    .map(POTENCIA_TECNOLOGIA_W)
)

tecnologia_limpia["kwh_tecnologia"] = (
    tecnologia_limpia["cantidad"]
    * tecnologia_limpia["potencia_w"]
    / 1000
    * tecnologia_limpia["horas_dia"]
    * tecnologia_limpia["dias_mes"]
)

tecnologia_hogar = (
    tecnologia_limpia
    .groupby(CLAVES_HOGAR, as_index=False)
    .agg(
        cantidad_equipos_tecnologia=("cantidad", "sum"),
        kwh_tecnologia=("kwh_tecnologia", "sum"),
    )
)


# 14. LIMPIEZA Y CÁLCULO DE VENTILADORES
print("Limpiando ventilador.csv y calculando kWh...")

ventilador_limpio = ventilador.copy()

ventilador_limpio["tipo_num"] = a_numero(
    ventilador_limpio["venti_tipo"],
    minimo=1,
    maximo=9,
).fillna(9)

ventilador_limpio["dias_uso_anio"] = a_numero(
    ventilador_limpio["venti_dia"],
    codigos_invalidos=(999,),
    minimo=0,
    maximo=365,
)

ventilador_limpio["horas_dia"] = horas_decimales(
    ventilador_limpio,
    "venti_hor",
    "venti_min",
)

ventilador_limpio = rellenar_mediana_por_grupo(
    ventilador_limpio,
    "dias_uso_anio",
    ["tipo_num"],
)

ventilador_limpio = rellenar_mediana_por_grupo(
    ventilador_limpio,
    "horas_dia",
    ["tipo_num"],
)

ventilador_limpio["potencia_w"] = (
    ventilador_limpio["tipo_num"]
    .map(POTENCIA_VENTILADOR_W)
    .fillna(60)
)

ventilador_limpio["kwh_ventiladores"] = (
    ventilador_limpio["potencia_w"]
    / 1000
    * ventilador_limpio["horas_dia"]
    * ventilador_limpio["dias_uso_anio"]
    / 12
)

ventilador_hogar = (
    ventilador_limpio
    .groupby(CLAVES_HOGAR, as_index=False)
    .agg(
        cantidad_ventiladores=("id_venti", "count"),
        kwh_ventiladores=("kwh_ventiladores", "sum"),
    )
)


# 15. LIMPIEZA Y CÁLCULO DE AIRES ACONDICIONADOS SEGÚN BTU
print("Limpiando aireacond.csv y calculando kWh según BTU...")

aire_limpio = aireacond.merge(
    vivienda_limpia[
        ["folio", "region_climatica"]
    ],
    on="folio",
    how="left",
    validate="m:1",
)

aire_limpio["tipo_num"] = a_numero(
    aire_limpio["aire_tipo"],
    minimo=1,
    maximo=9,
).fillna(9)

aire_limpio["capacidad_num"] = a_numero(
    aire_limpio["aire_capa"],
    minimo=1,
    maximo=9,
).fillna(9)

aire_limpio["dias_uso_anio"] = a_numero(
    aire_limpio["aire_dia"],
    codigos_invalidos=(999,),
    minimo=0,
    maximo=365,
)

aire_limpio["horas_dia"] = horas_decimales(
    aire_limpio,
    "aire_hor",
    "aire_min",
)

# Imputar por región y tipo de equipo
aire_limpio = rellenar_mediana_por_grupo(
    aire_limpio,
    "dias_uso_anio",
    ["region_climatica", "tipo_num"],
)

aire_limpio = rellenar_mediana_por_grupo(
    aire_limpio,
    "horas_dia",
    ["region_climatica", "tipo_num"],
)

aire_limpio["btu_h"] = (
    aire_limpio["capacidad_num"]
    .map(CAPACIDAD_AIRE_BTU)
    .fillna(12000)
)

aire_limpio["eer"] = (
    aire_limpio["tipo_num"].map(EER_AIRE)
)

aire_limpio["factor_carga"] = (
    aire_limpio["tipo_num"]
    .map(FACTOR_CARGA_AIRE)
    .fillna(0.75)
)

# Para equipos convencionales: kW = BTU/h / EER / 1000
aire_limpio["potencia_kw"] = (
    aire_limpio["btu_h"]
    / aire_limpio["eer"]
    / 1000
)

# Aire evaporativo: potencia eléctrica fija preliminar
aire_limpio.loc[
    aire_limpio["tipo_num"] == 4,
    "potencia_kw",
] = POTENCIA_EVAPORATIVO_KW

aire_limpio["kwh_aire"] = (
    aire_limpio["potencia_kw"]
    * aire_limpio["horas_dia"]
    * aire_limpio["dias_uso_anio"]
    * aire_limpio["factor_carga"]
    / 12
)

aire_hogar = (
    aire_limpio
    .groupby(CLAVES_HOGAR, as_index=False)
    .agg(
        cantidad_aires=("id_aire", "count"),
        btu_totales=("btu_h", "sum"),
        kwh_aire=("kwh_aire", "sum"),
    )
)


# 16. LIMPIEZA Y CÁLCULO DE CALEFACTORES
print("Limpiando calefactor.csv y calculando kWh...")

calefactor_limpio = calefactor.copy()

calefactor_limpio["tipo_num"] = a_numero(
    calefactor_limpio["calef_tipo"],
    minimo=1,
    maximo=9,
)

calefactor_limpio["dias_uso_anio"] = a_numero(
    calefactor_limpio["calef_dia"],
    codigos_invalidos=(999,),
    minimo=0,
    maximo=365,
)

calefactor_limpio["horas_dia"] = horas_decimales(
    calefactor_limpio,
    "calef_hor",
    "calef_min",
)

calefactor_limpio["potencia_w"] = (
    calefactor_limpio["tipo_num"]
    .map(POTENCIA_CALEFACTOR_W)
)

calefactor_limpio["es_electrico"] = (
    calefactor_limpio["potencia_w"].notna()
)

mascara_electrico = calefactor_limpio["es_electrico"]

for col in ["dias_uso_anio", "horas_dia"]:
    medianas = (
        calefactor_limpio[mascara_electrico]
        .groupby("tipo_num")[col]
        .median()
    )

    calefactor_limpio.loc[
        mascara_electrico,
        col,
    ] = (
        calefactor_limpio.loc[
            mascara_electrico,
            col,
        ]
        .fillna(
            calefactor_limpio.loc[
                mascara_electrico,
                "tipo_num",
            ].map(medianas)
        )
        .fillna(
            calefactor_limpio.loc[
                mascara_electrico,
                col,
            ].median()
        )
    )

calefactor_limpio["kwh_calefaccion"] = (
    calefactor_limpio["potencia_w"]
    / 1000
    * calefactor_limpio["horas_dia"]
    * calefactor_limpio["dias_uso_anio"]
    / 12
)

calefactor_hogar = (
    calefactor_limpio
    .groupby(CLAVES_HOGAR, as_index=False)
    .agg(
        cantidad_calefactores=("id_calefac", "count"),
        calefactores_electricos=("es_electrico", "sum"),
        kwh_calefaccion=("kwh_calefaccion", "sum"),
    )
)


# 17. LIMPIEZA Y CÁLCULO DE CALENTADORES DE AGUA
print("Limpiando cal_agua.csv y calculando kWh...")

cal_agua_limpia = cal_agua.copy()

cal_agua_limpia["tipo_num"] = a_numero(
    cal_agua_limpia["cagua_tipo"],
    minimo=1,
    maximo=8,
)

cal_agua_limpia["potencia_w"] = (
    cal_agua_limpia["tipo_num"]
    .map(POTENCIA_CALENTADOR_AGUA_W)
)

cal_agua_limpia["es_electrico"] = (
    cal_agua_limpia["potencia_w"].notna()
)

# Se usa potencia promedio, no suma de potencias,
# porque el tiempo de ducha es total del hogar y puede ser secuencial.
calentador_hogar = (
    cal_agua_limpia
    .groupby(CLAVES_HOGAR, as_index=False)
    .agg(
        cantidad_calentadores=("id_cagua", "count"),
        calentadores_electricos=("es_electrico", "sum"),
        potencia_promedio_calentador_w=(
            "potencia_w",
            "mean",
        ),
    )
)

uso_agua = base[
    CLAVES_HOGAR
    + ["uso_cal_d", "uso_cal_h", "uso_cal_m"]
].copy()

uso_agua["dias_uso_anio"] = a_numero(
    uso_agua["uso_cal_d"],
    codigos_invalidos=(999,),
    minimo=0,
    maximo=365,
)

uso_agua["horas_ducha_dia"] = horas_decimales(
    uso_agua,
    "uso_cal_h",
    "uso_cal_m",
)

calentador_hogar = calentador_hogar.merge(
    uso_agua[
        CLAVES_HOGAR
        + ["dias_uso_anio", "horas_ducha_dia"]
    ],
    on=CLAVES_HOGAR,
    how="left",
    validate="1:1",
)

calentador_hogar["dias_uso_anio"] = (
    calentador_hogar["dias_uso_anio"]
    .fillna(calentador_hogar["dias_uso_anio"].median())
)

calentador_hogar["horas_ducha_dia"] = (
    calentador_hogar["horas_ducha_dia"]
    .fillna(calentador_hogar["horas_ducha_dia"].median())
)

calentador_hogar["kwh_calentamiento_agua"] = (
    calentador_hogar["potencia_promedio_calentador_w"]
    / 1000
    * calentador_hogar["horas_ducha_dia"]
    * calentador_hogar["dias_uso_anio"]
    / 12
)

calentador_hogar["kwh_calentamiento_agua"] = (
    calentador_hogar["kwh_calentamiento_agua"].fillna(0)
)


# 18. CÁLCULO DE REFRIGERADOR, LAVADORA, PLANCHA Y BOMBA
print("Calculando refrigerador, lavadora, plancha y bomba...")

aparatos_principales = base[
    CLAVES_HOGAR
    + [
        "uso_refri",
        "cap_refri",
        "uso_ref_a",
        "refri_estu",
        "refri_sol",
        "refri_boil",
        "refri_horn",

        "uso_lava",
        "tipo_lava",
        "dias_uso_l",
        "hor_uso_l",
        "min_uso_l",
        "hor_lav3",

        "uso_plan",
        "tipo_plan",
        "dias_uso_p",
        "hor_uso_p",
        "min_uso_p",
        "hor_plan3",

        "uso_bomba",
        "uso_bom_d",
        "uso_bom_h",
        "uso_bom_m",
        "cap_bomba",
    ]
].copy()


# 18.1 Refrigerador
capacidad_refri = a_numero(
    aparatos_principales["cap_refri"],
    codigos_invalidos=(9,),
    minimo=1,
    maximo=5,
).fillna(3)

edad_refri = a_numero(
    aparatos_principales["uso_ref_a"],
    codigos_invalidos=(99,),
    minimo=0,
    maximo=80,
).fillna(8)

aparatos_principales["kwh_refrigerador"] = (
    capacidad_refri.map(KWH_REFRIGERADOR_MES)
)

# A partir de 10 años aumenta 1.5% por cada año adicional
factor_antiguedad = (
    1
    + np.clip(
        edad_refri - 10,
        0,
        None,
    )
    * 0.015
)

# Penalización por ubicación desfavorable
ubicaciones_desfavorables = sum(
    aparatos_principales[col].eq("1").astype(int)
    for col in [
        "refri_estu",
        "refri_sol",
        "refri_boil",
        "refri_horn",
    ]
)

factor_ubicacion = 1 + 0.04 * ubicaciones_desfavorables

aparatos_principales["kwh_refrigerador"] = (
    aparatos_principales["kwh_refrigerador"]
    * factor_antiguedad
    * factor_ubicacion
)

aparatos_principales.loc[
    aparatos_principales["uso_refri"] != "1",
    "kwh_refrigerador",
] = 0

aparatos_principales["cantidad_refrigeradores"] = (
    aparatos_principales["uso_refri"].eq("1").astype(int)
)


# 18.2 Lavadora
CODIGO_FRECUENCIA_A_USOS_MES = {
    1: 4.345,
    2: 8.690,
    3: 13.035,
    4: 17.380,
    5: 21.725,
    6: 26.070,
    7: DIAS_PROMEDIO_MES,
    8: 2.0,
    9: 1.0,
    10: 4.345,
}

frecuencia_lavadora = a_numero(
    aparatos_principales["dias_uso_l"],
    codigos_invalidos=(99,),
    minimo=1,
    maximo=10,
).map(CODIGO_FRECUENCIA_A_USOS_MES)

horas_lavadora = horas_decimales(
    aparatos_principales,
    "hor_uso_l",
    "min_uso_l",
).fillna(1.5)

tipo_lavadora = a_numero(
    aparatos_principales["tipo_lava"],
    codigos_invalidos=(9,),
    minimo=1,
    maximo=4,
).fillna(9)

aparatos_principales["kwh_lavadora"] = (
    tipo_lavadora.map(POTENCIA_LAVADORA_W)
    / 1000
    * horas_lavadora
    * frecuencia_lavadora.fillna(4.345)
)

aparatos_principales.loc[
    aparatos_principales["uso_lava"] != "1",
    "kwh_lavadora",
] = 0

aparatos_principales["cantidad_lavadoras"] = (
    aparatos_principales["uso_lava"].eq("1").astype(int)
)

aparatos_principales["lavadora_en_pico"] = (
    aparatos_principales["hor_lav3"].notna()
).astype(int)


# 18.3 Plancha
frecuencia_plancha = a_numero(
    aparatos_principales["dias_uso_p"],
    codigos_invalidos=(99,),
    minimo=1,
    maximo=10,
).map(CODIGO_FRECUENCIA_A_USOS_MES)

horas_plancha = horas_decimales(
    aparatos_principales,
    "hor_uso_p",
    "min_uso_p",
).fillna(0.5)

tipo_plancha = a_numero(
    aparatos_principales["tipo_plan"],
    codigos_invalidos=(9,),
    minimo=1,
    maximo=2,
).fillna(9)

aparatos_principales["kwh_plancha"] = (
    tipo_plancha.map(POTENCIA_PLANCHA_W)
    / 1000
    * horas_plancha
    * frecuencia_plancha.fillna(4.345)
)

aparatos_principales.loc[
    aparatos_principales["uso_plan"] != "1",
    "kwh_plancha",
] = 0

aparatos_principales["cantidad_planchas"] = (
    aparatos_principales["uso_plan"].eq("1").astype(int)
)

aparatos_principales["plancha_en_pico"] = (
    aparatos_principales["hor_plan3"].notna()
).astype(int)


# 18.4 Bomba de agua
dias_bomba_mes = a_numero(
    aparatos_principales["uso_bom_d"],
    codigos_invalidos=(98, 99),
    minimo=0,
    maximo=31,
)

horas_bomba_dia = horas_decimales(
    aparatos_principales,
    "uso_bom_h",
    "uso_bom_m",
)

capacidad_bomba = a_numero(
    aparatos_principales["cap_bomba"],
    codigos_invalidos=(9,),
    minimo=1,
    maximo=5,
)

potencia_bomba_kw = (
    capacidad_bomba.map(CAPACIDAD_BOMBA_HP)
    * 0.746
    / EFICIENCIA_MOTOR_BOMBA
)

aparatos_principales["kwh_bomba"] = (
    potencia_bomba_kw
    * horas_bomba_dia
    * dias_bomba_mes
)

aparatos_principales.loc[
    aparatos_principales["uso_bomba"] != "1",
    "kwh_bomba",
] = 0

aparatos_principales["cantidad_bombas"] = (
    aparatos_principales["uso_bomba"].eq("1").astype(int)
)

aparatos_hogar = aparatos_principales[
    CLAVES_HOGAR
    + [
        "kwh_refrigerador",
        "cantidad_refrigeradores",
        "kwh_lavadora",
        "cantidad_lavadoras",
        "lavadora_en_pico",
        "kwh_plancha",
        "cantidad_planchas",
        "plancha_en_pico",
        "kwh_bomba",
        "cantidad_bombas",
    ]
].copy()


# 19. LIMPIEZA Y RESUMEN DEL ARCHIVO CAMBIO
print("Limpiando cambio.csv...")

cambio_limpio = cambio[
    [
        "folio",
        "foliohog",
        "id_cambio",
        "camb_apara",
        "criterio1",
        "criterio2",
    ]
].copy()

cambio_limpio["planea_cambio"] = (
    cambio_limpio["camb_apara"] == "1"
).astype(int)

cambio_hogar = (
    cambio_limpio
    .groupby(CLAVES_HOGAR, as_index=False)
    .agg(
        aparatos_evaluados_para_cambio=("id_cambio", "count"),
        aparatos_con_intencion_cambio=("planea_cambio", "sum"),
    )
)


# 20. FUSIÓN DE TODAS LAS TABLAS RESUMIDAS
print("Fusionando todos los cálculos por hogar...")

tablas_resumidas = [
    focos_hogar,
    electro_hogar,
    pantalla_hogar,
    tecnologia_hogar,
    ventilador_hogar,
    aire_hogar,
    calefactor_hogar,
    calentador_hogar,
    aparatos_hogar,
    cambio_hogar,
]

base_detallada = base.copy()

for tabla in tablas_resumidas:
    base_detallada = base_detallada.merge(
        tabla,
        on=CLAVES_HOGAR,
        how="left",
        validate="1:1",
    )


# 21. RELLENAR CON CERO LOS EQUIPOS QUE NO TIENE EL HOGAR
COLUMNAS_KWH = [
    "kwh_iluminacion",
    "kwh_electrodomesticos",
    "kwh_pantallas",
    "kwh_tecnologia",
    "kwh_ventiladores",
    "kwh_aire",
    "kwh_calefaccion",
    "kwh_calentamiento_agua",
    "kwh_refrigerador",
    "kwh_lavadora",
    "kwh_plancha",
    "kwh_bomba",
]

COLUMNAS_CANTIDAD = [
    "cantidad_focos",
    "focos_fluorescentes",
    "focos_led",
    "focos_incandescentes",
    "cantidad_electrodomesticos",
    "cantidad_pantallas",
    "cantidad_equipos_tecnologia",
    "cantidad_ventiladores",
    "cantidad_aires",
    "cantidad_calefactores",
    "calefactores_electricos",
    "cantidad_calentadores",
    "calentadores_electricos",
    "cantidad_refrigeradores",
    "cantidad_lavadoras",
    "cantidad_planchas",
    "cantidad_bombas",
    "aparatos_evaluados_para_cambio",
    "aparatos_con_intencion_cambio",
]

COLUMNAS_A_CERO = (
    COLUMNAS_KWH
    + COLUMNAS_CANTIDAD
    + [
        "kwh_electrodomesticos_alto",
        "usa_pantalla_en_pico",
        "lavadora_en_pico",
        "plancha_en_pico",
        "btu_totales",
    ]
)

for col in COLUMNAS_A_CERO:
    if col not in base_detallada.columns:
        base_detallada[col] = 0

    base_detallada[col] = (
        pd.to_numeric(
            base_detallada[col],
            errors="coerce",
        )
        .fillna(0)
    )


# 22. CÁLCULO DEL CONSUMO TEÓRICO TOTAL
print("Calculando consumo teórico total...")

base_detallada["consumo_kwh_teorico"] = (
    base_detallada[COLUMNAS_KWH].sum(axis=1)
)

# Nombre obligatorio del proyecto EnergiAI
base_detallada["consumo_kwh"] = (
    base_detallada["consumo_kwh_teorico"]
)


# 23. CÁLCULO DE CANTIDAD DE EQUIPOS
# Los focos NO se incluyen en cantidad_equipos.
# Se conservan por separado porque 20 focos no equivalen a 20 aparatos.

base_detallada["cantidad_equipos"] = (
    base_detallada["cantidad_electrodomesticos"]
    + base_detallada["cantidad_pantallas"]
    + base_detallada["cantidad_equipos_tecnologia"]
    + base_detallada["cantidad_ventiladores"]
    + base_detallada["cantidad_aires"]
    + base_detallada["cantidad_calefactores"]
    + base_detallada["cantidad_calentadores"]
    + base_detallada["cantidad_refrigeradores"]
    + base_detallada["cantidad_lavadoras"]
    + base_detallada["cantidad_planchas"]
    + base_detallada["cantidad_bombas"]
)


# 24. CREAR UN IDENTIFICADOR SENCILLO PARA CADA HOGAR
# El folio original de INEGI no se publica. Se crea un ID consecutivo que sirve
# para comparar exactamente el mismo hogar entre la base 2018 y la base moderna.

base_detallada = base_detallada.sort_values(CLAVES_HOGAR).reset_index(drop=True)
base_detallada["id_hogar"] = [
    f"HOGAR_{numero:06d}"
    for numero in range(1, len(base_detallada) + 1)
]

# Escenario 2026 con equipos de referencia actuales
#
# Aquí no se toma el consumo 2018 y se le resta un porcentaje general. Cada grupo
# se vuelve a calcular con una potencia o consumo de referencia actual. Se conserva
# la cantidad de equipos y el tiempo de uso declarado por el hogar, porque no sabemos
# si hoy pasa más o menos tiempo en casa.

TARIFA_PROYECTO_R_POR_KWH = 0.75
POTENCIA_ALTA_REFERENCIA_KW = 1.5

# Valores de referencia actuales. No describen una marca concreta: representan un
# equipo eficiente típico y se pueden sustituir cuando el equipo reúna una muestra
# propia del mercado mexicano.
POTENCIA_ELECTRO_2026_W = {
    1: 1100,  # microondas
    2: 350,   # licuadora
    3: 220,   # batidora
    4: 800,   # cafetera
    5: 900,   # tostador o sandwichera
    6: 1400,  # parrilla u horno eléctrico
    7: 1400,  # secadora de pelo
    8: 50,    # tenaza o plancha para cabello
    9: 2200,  # secadora de ropa eficiente convencional
    10: 80,   # máquina de coser
}

POTENCIA_TECNOLOGIA_2026_W = {
    1: 10,   # módem
    2: 10,   # decodificador
    3: 7,    # tablet
    4: 45,   # laptop
    5: 100,  # computadora de escritorio
    6: 30,   # impresora
    7: 10,   # radio
    8: 50,   # estéreo
    9: 12,   # DVD o Blu-ray
    10: 90,  # consola
    11: 5,   # regulador
    12: 10,  # no-break
}

# Potencia aproximada por tamaño para una pantalla LED actual.
POTENCIA_PANTALLA_2026_W = {
    1: 35,   # menos de 30 pulgadas
    2: 50,   # 30 a 39
    3: 70,   # 40 a 49
    4: 95,   # 50 a 60
    5: 130,  # más de 60
    9: 70,
}

POTENCIA_VENTILADOR_2026_W = {
    1: 35,
    2: 45,
    3: 25,
    4: 35,
    5: 40,
    9: 35,
}

POTENCIA_LAVADORA_2026_W = {
    1: 350,
    2: 400,
    3: 450,
    4: 350,
    9: 400,
}

POTENCIA_PLANCHA_2026_W = {
    1: 1200,
    2: 1100,
    9: 1150,
}

# Consumo anual aproximado por tamaño. Se divide entre 12; no se usa potencia por
# 24 horas porque el compresor trabaja por ciclos.
KWH_REFRIGERADOR_2026_ANIO = {
    1: 150,
    2: 240,
    3: 330,
    4: 450,
    5: 600,
    9: 330,
}

# Un CEER/EER de 15 representa un equipo actual eficiente. Se mantiene la capacidad
# en BTU y el uso reportado, así que un equipo grande todavía consume más.
EER_AIRE_2026 = 15.0
FACTOR_CARGA_AIRE_2026 = 0.60
POTENCIA_EVAPORATIVO_2026_KW = 0.25

POTENCIA_CALEFACTOR_2026_W = {
    1: 1500,
    2: 1500,
    3: 1500,
}

POTENCIA_CALENTADOR_2026_W = {
    4: 5000,
    5: 3500,
}

EFICIENCIA_MOTOR_BOMBA_2026 = 0.85

# Focos: mismo número y mismas horas, pero todos se modelan con LED de 9 W.
focos_limpios["kwh_iluminacion_2026_area"] = (
    focos_limpios["foco_num_num"]
    * 9.0
    * focos_limpios["horas_focos_dia"]
    * DIAS_PROMEDIO_MES
    / 1000
)
focos_2026_hogar = (
    focos_limpios.groupby(CLAVES_HOGAR, as_index=False)
    .agg(kwh_iluminacion_2026=("kwh_iluminacion_2026_area", "sum"))
)

# Electrodomésticos: se recalcula cada registro con una potencia 2026, no con un
# descuento porcentual sobre el consumo antiguo.
electro_limpio["potencia_2026_w"] = electro_limpio["id_electro_num"].map(POTENCIA_ELECTRO_2026_W)
electro_limpio["kwh_electro_2026"] = (
    electro_limpio["potencia_2026_w"] / 1000
    * electro_limpio["horas_uso_dia"]
    * electro_limpio["dias_uso_mes"]
)
electro_limpio["kwh_electro_alto_2026"] = np.where(
    electro_limpio["potencia_2026_w"] >= 1000,
    electro_limpio["kwh_electro_2026"],
    0,
)
electro_2026_hogar = (
    electro_limpio.groupby(CLAVES_HOGAR, as_index=False)
    .agg(
        kwh_electrodomesticos_2026=("kwh_electro_2026", "sum"),
        kwh_electrodomesticos_alto_2026=("kwh_electro_alto_2026", "sum"),
    )
)

# Pantallas: el tamaño y las horas siguen siendo los del hogar, pero la potencia
# sale de una tabla actual por pulgadas.
pantalla_limpia["potencia_2026_w"] = pantalla_limpia["tam_num"].map(POTENCIA_PANTALLA_2026_W)
pantalla_limpia["kwh_pantallas_2026"] = (
    pantalla_limpia["potencia_2026_w"] / 1000
    * pantalla_limpia["horas_dia"]
    * pantalla_limpia["dias_semana"]
    * (365.25 / 7 / 12)
)
pantalla_2026_hogar = (
    pantalla_limpia.groupby(CLAVES_HOGAR, as_index=False)
    .agg(kwh_pantallas_2026=("kwh_pantallas_2026", "sum"))
)

# Tecnología: misma cantidad y uso, potencia actual por tipo de equipo.
tecnologia_limpia["potencia_2026_w"] = tecnologia_limpia["id_equipo_num"].map(POTENCIA_TECNOLOGIA_2026_W)
tecnologia_limpia["kwh_tecnologia_2026"] = (
    tecnologia_limpia["cantidad"]
    * tecnologia_limpia["potencia_2026_w"] / 1000
    * tecnologia_limpia["horas_dia"]
    * tecnologia_limpia["dias_mes"]
)
tecnologia_2026_hogar = (
    tecnologia_limpia.groupby(CLAVES_HOGAR, as_index=False)
    .agg(kwh_tecnologia_2026=("kwh_tecnologia_2026", "sum"))
)

# Ventiladores: se usan motores eficientes de referencia y se conserva el uso anual.
ventilador_limpio["potencia_2026_w"] = ventilador_limpio["tipo_num"].map(POTENCIA_VENTILADOR_2026_W).fillna(35)
ventilador_limpio["kwh_ventiladores_2026"] = (
    ventilador_limpio["potencia_2026_w"] / 1000
    * ventilador_limpio["horas_dia"]
    * ventilador_limpio["dias_uso_anio"]
    / 12
)
ventilador_2026_hogar = (
    ventilador_limpio.groupby(CLAVES_HOGAR, as_index=False)
    .agg(kwh_ventiladores_2026=("kwh_ventiladores_2026", "sum"))
)

# Aire acondicionado: capacidad, horas y días son los originales. Cambia la
# eficiencia del equipo, que es justo lo que se quiere simular.
aire_limpio["potencia_2026_kw"] = aire_limpio["btu_h"] / EER_AIRE_2026 / 1000
aire_limpio.loc[aire_limpio["tipo_num"] == 4, "potencia_2026_kw"] = POTENCIA_EVAPORATIVO_2026_KW
aire_limpio["factor_carga_2026"] = np.where(
    aire_limpio["tipo_num"] == 4,
    1.0,
    FACTOR_CARGA_AIRE_2026,
)
aire_limpio["kwh_aire_2026"] = (
    aire_limpio["potencia_2026_kw"]
    * aire_limpio["horas_dia"]
    * aire_limpio["dias_uso_anio"]
    * aire_limpio["factor_carga_2026"]
    / 12
)
aire_2026_hogar = (
    aire_limpio.groupby(CLAVES_HOGAR, as_index=False)
    .agg(kwh_aire_2026=("kwh_aire_2026", "sum"))
)

# Refrigerador: capacidad declarada y consumo anual actual por tamaño.
aparatos_principales["kwh_refrigerador_2026"] = np.where(
    aparatos_principales["uso_refri"] == "1",
    capacidad_refri.map(KWH_REFRIGERADOR_2026_ANIO).fillna(330) / 12,
    0,
)

# Lavadora y plancha: se vuelven a aplicar las fórmulas con potencias actuales.
aparatos_principales["kwh_lavadora_2026"] = (
    tipo_lavadora.map(POTENCIA_LAVADORA_2026_W) / 1000
    * horas_lavadora
    * frecuencia_lavadora.fillna(4.345)
)
aparatos_principales.loc[aparatos_principales["uso_lava"] != "1", "kwh_lavadora_2026"] = 0

aparatos_principales["kwh_plancha_2026"] = (
    tipo_plancha.map(POTENCIA_PLANCHA_2026_W) / 1000
    * horas_plancha
    * frecuencia_plancha.fillna(4.345)
)
aparatos_principales.loc[aparatos_principales["uso_plan"] != "1", "kwh_plancha_2026"] = 0

# Bomba: misma capacidad y uso, pero con un motor actual de mayor eficiencia.
potencia_bomba_2026_kw = (
    capacidad_bomba.map(CAPACIDAD_BOMBA_HP)
    * 0.746
    / EFICIENCIA_MOTOR_BOMBA_2026
)
aparatos_principales["kwh_bomba_2026"] = (
    potencia_bomba_2026_kw * horas_bomba_dia * dias_bomba_mes
)
aparatos_principales.loc[aparatos_principales["uso_bomba"] != "1", "kwh_bomba_2026"] = 0

aparatos_2026_hogar = aparatos_principales[
    CLAVES_HOGAR
    + [
        "kwh_refrigerador_2026",
        "kwh_lavadora_2026",
        "kwh_plancha_2026",
        "kwh_bomba_2026",
    ]
].copy()

# Calefacción eléctrica de resistencia no se reduce por arte de magia: transformar
# electricidad en calor ya es casi 100 % eficiente. Solo cambia si se sustituye por
# otra tecnología, algo que ENCEVI no permite saber. Por eso se conserva el cálculo.
calefactor_2026_hogar = calefactor_hogar[CLAVES_HOGAR + ["kwh_calefaccion"]].rename(
    columns={"kwh_calefaccion": "kwh_calefaccion_2026"}
)

# Calentamiento de agua: se recalcula con potencias de referencia actuales.
cal_agua_limpia["potencia_2026_w"] = cal_agua_limpia["tipo_num"].map(POTENCIA_CALENTADOR_2026_W)
calentador_2026_hogar = (
    cal_agua_limpia.groupby(CLAVES_HOGAR, as_index=False)
    .agg(potencia_promedio_calentador_2026_w=("potencia_2026_w", "mean"))
    .merge(
        uso_agua[CLAVES_HOGAR + ["dias_uso_anio", "horas_ducha_dia"]],
        on=CLAVES_HOGAR,
        how="left",
        validate="1:1",
    )
)
calentador_2026_hogar["dias_uso_anio"] = calentador_2026_hogar["dias_uso_anio"].fillna(
    calentador_2026_hogar["dias_uso_anio"].median()
)
calentador_2026_hogar["horas_ducha_dia"] = calentador_2026_hogar["horas_ducha_dia"].fillna(
    calentador_2026_hogar["horas_ducha_dia"].median()
)
calentador_2026_hogar["kwh_calentamiento_agua_2026"] = (
    calentador_2026_hogar["potencia_promedio_calentador_2026_w"] / 1000
    * calentador_2026_hogar["horas_ducha_dia"]
    * calentador_2026_hogar["dias_uso_anio"]
    / 12
).fillna(0)

# Unimos los cálculos 2026 a la misma fila de hogar.
for tabla in [
    focos_2026_hogar,
    electro_2026_hogar,
    pantalla_2026_hogar,
    tecnologia_2026_hogar,
    ventilador_2026_hogar,
    aire_2026_hogar,
    aparatos_2026_hogar,
    calefactor_2026_hogar,
    calentador_2026_hogar[CLAVES_HOGAR + ["kwh_calentamiento_agua_2026"]],
]:
    base_detallada = base_detallada.merge(
        tabla,
        on=CLAVES_HOGAR,
        how="left",
        validate="1:1",
    )

COLUMNAS_2026_A_CERO = [
    "kwh_iluminacion_2026",
    "kwh_electrodomesticos_2026",
    "kwh_electrodomesticos_alto_2026",
    "kwh_pantallas_2026",
    "kwh_tecnologia_2026",
    "kwh_ventiladores_2026",
    "kwh_aire_2026",
    "kwh_refrigerador_2026",
    "kwh_lavadora_2026",
    "kwh_plancha_2026",
    "kwh_bomba_2026",
    "kwh_calefaccion_2026",
    "kwh_calentamiento_agua_2026",
]
for columna in COLUMNAS_2026_A_CERO:
    base_detallada[columna] = pd.to_numeric(base_detallada[columna], errors="coerce").fillna(0)

# Variables exactas que recibirá la API
#
# uso_horario_pico se apoya en los bloques horarios declarados. Lavadora y plancha
# valen dos puntos por su potencia; una pantalla nocturna vale uno. No se marca como
# pico a una casa solo porque tuvo la televisión encendida.
base_detallada["puntaje_horario_pico"] = (
    2 * base_detallada["lavadora_en_pico"].clip(0, 1)
    + 2 * base_detallada["plancha_en_pico"].clip(0, 1)
    + base_detallada["usa_pantalla_en_pico"].clip(0, 1)
)
base_detallada["uso_horario_pico"] = base_detallada["puntaje_horario_pico"] >= 2

# horas_alto_consumo no son horas sumadas del reloj. Son horas equivalentes por día
# usando como referencia una carga de 1.5 kW. Ejemplo: 45.66 kWh al mes equivalen a
# 1 hora diaria de una carga de 1.5 kW. Se limita a 24 para que sea una entrada válida.
base_detallada["consumo_alto_2018_kwh_mes"] = (
    base_detallada["kwh_electrodomesticos_alto"]
    + base_detallada["kwh_lavadora"]
    + base_detallada["kwh_plancha"]
    + base_detallada["kwh_aire"]
    + base_detallada["kwh_calefaccion"]
    + base_detallada["kwh_calentamiento_agua"]
    + base_detallada["kwh_bomba"]
)
base_detallada["horas_alto_consumo_2018"] = (
    base_detallada["consumo_alto_2018_kwh_mes"]
    / (POTENCIA_ALTA_REFERENCIA_KW * DIAS_PROMEDIO_MES)
).clip(lower=0, upper=24)

base_detallada["consumo_alto_2026_kwh_mes"] = (
    base_detallada["kwh_electrodomesticos_alto_2026"]
    + base_detallada["kwh_lavadora_2026"]
    + base_detallada["kwh_plancha_2026"]
    + base_detallada["kwh_aire_2026"]
    + base_detallada["kwh_calefaccion_2026"]
    + base_detallada["kwh_calentamiento_agua_2026"]
    + base_detallada["kwh_bomba_2026"]
)
base_detallada["horas_alto_consumo_2026"] = (
    base_detallada["consumo_alto_2026_kwh_mes"]
    / (POTENCIA_ALTA_REFERENCIA_KW * DIAS_PROMEDIO_MES)
).clip(lower=0, upper=24)

# Tabla 2018: detalle, entradas del modelo, etiqueta, costo del reto y comparación
# simple con el recibo. No se publican las columnas intermedias usadas para obtener
# la referencia de pago, porque eran las que hacían que la tabla se repitiera.
base_2018 = pd.DataFrame({
    "id_hogar": base_detallada["id_hogar"],
    "tipo_inmueble": base_detallada["tipo_inmueble"],
    "region_climatica": base_detallada["region_climatica"],
    "numero_personas": base_detallada["tot_integ"],
    "numero_cuartos": base_detallada["tot_cuart"],
    "numero_focos": base_detallada["cantidad_focos"],
    "focos_led": base_detallada["focos_led"],
    "focos_ahorradores": base_detallada["focos_fluorescentes"],
    "focos_incandescentes": base_detallada["focos_incandescentes"],
    "consumo_focos_kwh_mes": base_detallada["kwh_iluminacion"],
    "numero_refrigeradores": base_detallada["cantidad_refrigeradores"],
    "consumo_refrigeradores_kwh_mes": base_detallada["kwh_refrigerador"],
    "numero_lavadoras": base_detallada["cantidad_lavadoras"],
    "consumo_lavadoras_kwh_mes": base_detallada["kwh_lavadora"],
    "numero_planchas": base_detallada["cantidad_planchas"],
    "consumo_planchas_kwh_mes": base_detallada["kwh_plancha"],
    "numero_pantallas": base_detallada["cantidad_pantallas"],
    "consumo_pantallas_kwh_mes": base_detallada["kwh_pantallas"],
    "numero_equipos_tecnologia": base_detallada["cantidad_equipos_tecnologia"],
    "consumo_tecnologia_kwh_mes": base_detallada["kwh_tecnologia"],
    "numero_electrodomesticos": base_detallada["cantidad_electrodomesticos"],
    "consumo_electrodomesticos_kwh_mes": base_detallada["kwh_electrodomesticos"],
    "numero_ventiladores": base_detallada["cantidad_ventiladores"],
    "consumo_ventiladores_kwh_mes": base_detallada["kwh_ventiladores"],
    "numero_aires_acondicionados": base_detallada["cantidad_aires"],
    "capacidad_total_aire_btu": base_detallada["btu_totales"],
    "consumo_aire_acondicionado_kwh_mes": base_detallada["kwh_aire"],
    "numero_calefactores_electricos": base_detallada["calefactores_electricos"],
    "consumo_calefaccion_kwh_mes": base_detallada["kwh_calefaccion"],
    "numero_calentadores_electricos": base_detallada["calentadores_electricos"],
    "consumo_agua_caliente_kwh_mes": base_detallada["kwh_calentamiento_agua"],
    "numero_bombas_agua": base_detallada["cantidad_bombas"],
    "consumo_bombas_agua_kwh_mes": base_detallada["kwh_bomba"],
})

COLUMNAS_CONSUMO = [
    "consumo_focos_kwh_mes",
    "consumo_refrigeradores_kwh_mes",
    "consumo_lavadoras_kwh_mes",
    "consumo_planchas_kwh_mes",
    "consumo_pantallas_kwh_mes",
    "consumo_tecnologia_kwh_mes",
    "consumo_electrodomesticos_kwh_mes",
    "consumo_ventiladores_kwh_mes",
    "consumo_aire_acondicionado_kwh_mes",
    "consumo_calefaccion_kwh_mes",
    "consumo_agua_caliente_kwh_mes",
    "consumo_bombas_agua_kwh_mes",
]

base_2018["consumo_kwh"] = base_2018[COLUMNAS_CONSUMO].sum(axis=1)
base_2018["uso_horario_pico"] = base_detallada["uso_horario_pico"]
base_2018["cantidad_equipos"] = base_detallada["cantidad_equipos"]
base_2018["horas_alto_consumo"] = base_detallada["horas_alto_consumo_2018"]
base_2018["costo_estimado_mensual"] = base_2018["consumo_kwh"] * TARIFA_PROYECTO_R_POR_KWH

# Comparación con el recibo de 2018. La tarifa y el pago vienen de ENCEVI. La
# referencia monetaria se calcula internamente con hogares de la misma tarifa y
# región; en la salida solo quedan los resultados que una persona puede interpretar.
base_2018["tarifa_cfe_reportada"] = base_detallada["tarifa_cfe"]
base_2018["pago_mensual_reportado_pesos"] = base_detallada["pago_mensual_observado"]

referencia_pago = pd.DataFrame({
    "tarifa": base_detallada["tarifa_cfe"],
    "region": base_detallada["region_climatica"],
    "pago": base_detallada["pago_mensual_observado"],
    "kwh": base_2018["consumo_kwh"],
})
referencia_pago["pesos_por_kwh"] = np.where(
    referencia_pago["pago"].notna() & (referencia_pago["kwh"] >= 10),
    referencia_pago["pago"] / referencia_pago["kwh"],
    np.nan,
)
q01 = referencia_pago["pesos_por_kwh"].quantile(0.01)
q99 = referencia_pago["pesos_por_kwh"].quantile(0.99)
referencia_valida = referencia_pago[referencia_pago["pesos_por_kwh"].between(q01, q99)].copy()

mediana_tarifa_region = referencia_valida.groupby(["tarifa", "region"])["pesos_por_kwh"].median()
mediana_region = referencia_valida.groupby("region")["pesos_por_kwh"].median()
mediana_nacional = referencia_valida["pesos_por_kwh"].median()

clave_tarifa_region = pd.MultiIndex.from_arrays([
    base_2018["tarifa_cfe_reportada"],
    base_2018["region_climatica"],
])
costo_interno = pd.Series(
    mediana_tarifa_region.reindex(clave_tarifa_region).to_numpy(),
    index=base_2018.index,
)
costo_interno = (
    costo_interno
    .fillna(base_2018["region_climatica"].map(mediana_region))
    .fillna(mediana_nacional)
)

base_2018["pago_cfe_estimado_referencia_pesos"] = base_2018["consumo_kwh"] * costo_interno
base_2018["diferencia_pago_pesos"] = (
    base_2018["pago_mensual_reportado_pesos"]
    - base_2018["pago_cfe_estimado_referencia_pesos"]
)
relacion_pago = np.where(
    base_2018["pago_cfe_estimado_referencia_pesos"] > 0,
    base_2018["pago_mensual_reportado_pesos"] / base_2018["pago_cfe_estimado_referencia_pesos"],
    np.nan,
)
base_2018["comparacion_con_recibo"] = np.select(
    [
        base_2018["pago_mensual_reportado_pesos"].isna(),
        relacion_pago < 0.70,
        relacion_pago <= 1.30,
    ],
    [
        "Sin informacion suficiente",
        "Pago menor que la referencia",
        "Pago cercano a la referencia",
    ],
    default="Pago mayor que la referencia",
)

# Tabla 2026: no se repite tarifa CFE ni recibo histórico. Solo queda el escenario
# tecnológico, el costo pedido por el reto y el ahorro frente al mismo hogar en 2018.
base_2026 = pd.DataFrame({
    "id_hogar": base_detallada["id_hogar"],
    "tipo_inmueble": base_detallada["tipo_inmueble"],
    "region_climatica": base_detallada["region_climatica"],
    "numero_personas": base_detallada["tot_integ"],
    "numero_cuartos": base_detallada["tot_cuart"],
    "numero_focos": base_detallada["cantidad_focos"],
    "consumo_focos_kwh_mes": base_detallada["kwh_iluminacion_2026"],
    "numero_refrigeradores": base_detallada["cantidad_refrigeradores"],
    "consumo_refrigeradores_kwh_mes": base_detallada["kwh_refrigerador_2026"],
    "numero_lavadoras": base_detallada["cantidad_lavadoras"],
    "consumo_lavadoras_kwh_mes": base_detallada["kwh_lavadora_2026"],
    "numero_planchas": base_detallada["cantidad_planchas"],
    "consumo_planchas_kwh_mes": base_detallada["kwh_plancha_2026"],
    "numero_pantallas": base_detallada["cantidad_pantallas"],
    "consumo_pantallas_kwh_mes": base_detallada["kwh_pantallas_2026"],
    "numero_equipos_tecnologia": base_detallada["cantidad_equipos_tecnologia"],
    "consumo_tecnologia_kwh_mes": base_detallada["kwh_tecnologia_2026"],
    "numero_electrodomesticos": base_detallada["cantidad_electrodomesticos"],
    "consumo_electrodomesticos_kwh_mes": base_detallada["kwh_electrodomesticos_2026"],
    "numero_ventiladores": base_detallada["cantidad_ventiladores"],
    "consumo_ventiladores_kwh_mes": base_detallada["kwh_ventiladores_2026"],
    "numero_aires_acondicionados": base_detallada["cantidad_aires"],
    "capacidad_total_aire_btu": base_detallada["btu_totales"],
    "consumo_aire_acondicionado_kwh_mes": base_detallada["kwh_aire_2026"],
    "numero_calefactores_electricos": base_detallada["calefactores_electricos"],
    "consumo_calefaccion_kwh_mes": base_detallada["kwh_calefaccion_2026"],
    "numero_calentadores_electricos": base_detallada["calentadores_electricos"],
    "consumo_agua_caliente_kwh_mes": base_detallada["kwh_calentamiento_agua_2026"],
    "numero_bombas_agua": base_detallada["cantidad_bombas"],
    "consumo_bombas_agua_kwh_mes": base_detallada["kwh_bomba_2026"],
})
base_2026["consumo_kwh"] = base_2026[COLUMNAS_CONSUMO].sum(axis=1)
base_2026["uso_horario_pico"] = base_detallada["uso_horario_pico"]
base_2026["cantidad_equipos"] = base_detallada["cantidad_equipos"]
base_2026["horas_alto_consumo"] = base_detallada["horas_alto_consumo_2026"]
base_2026["costo_estimado_mensual"] = base_2026["consumo_kwh"] * TARIFA_PROYECTO_R_POR_KWH
base_2026["consumo_2018_kwh"] = base_2018["consumo_kwh"]
base_2026["ahorro_estimado_kwh"] = base_2026["consumo_2018_kwh"] - base_2026["consumo_kwh"]
base_2026["ahorro_estimado_porcentaje"] = np.where(
    base_2026["consumo_2018_kwh"] > 0,
    base_2026["ahorro_estimado_kwh"] / base_2026["consumo_2018_kwh"] * 100,
    np.nan,
)
base_2026["ahorro_estimado_reales"] = base_2026["ahorro_estimado_kwh"] * TARIFA_PROYECTO_R_POR_KWH

# Se quitan hogares sin información energética útil antes de calcular percentiles.
registro_valido = (
    (base_2018["consumo_kwh"] > 0)
    & ((base_2018["numero_focos"] > 0) | (base_2018["cantidad_equipos"] > 0))
)
base_2018 = base_2018.loc[registro_valido].copy().reset_index(drop=True)
base_2026 = base_2026.loc[registro_valido].copy().reset_index(drop=True)

# La etiqueta del modelo usa terciles del consumo 2018. En 2026 se aplican los
# mismos cortes, para que una mejora tecnológica sí pueda cambiar la categoría.
CORTE_EFICIENTE_KWH = base_2018["consumo_kwh"].quantile(1 / 3)
CORTE_MODERADO_KWH = base_2018["consumo_kwh"].quantile(2 / 3)

def asignar_categoria(consumo_kwh):
    if consumo_kwh <= CORTE_EFICIENTE_KWH:
        return "Eficiente"
    if consumo_kwh <= CORTE_MODERADO_KWH:
        return "Moderado"
    return "Ineficiente"

base_2018["categoria"] = base_2018["consumo_kwh"].apply(asignar_categoria)
base_2026["categoria"] = base_2026["consumo_kwh"].apply(asignar_categoria)

# Orden final: primero contexto y detalle; al final quedan juntas las cinco entradas
# del endpoint, la etiqueta y el costo solicitado por el hackathon.
columnas_api_y_salida = [
    "consumo_kwh",
    "uso_horario_pico",
    "cantidad_equipos",
    "tipo_inmueble",
    "horas_alto_consumo",
    "categoria",
    "costo_estimado_mensual",
]

def mover_al_final(tabla, columnas):
    resto = [col for col in tabla.columns if col not in columnas]
    return tabla[resto + columnas]

base_2018 = mover_al_final(base_2018, columnas_api_y_salida)
base_2026 = mover_al_final(base_2026, columnas_api_y_salida)

for tabla in [base_2018, base_2026]:
    columnas_decimales = tabla.select_dtypes(include=["float", "float64"]).columns
    tabla[columnas_decimales] = tabla[columnas_decimales].round(2)

RUTA_2018 = OUTPUT_DIR / "01_base_hogares_2018_mvp.csv"
RUTA_2026 = OUTPUT_DIR / "02_base_hogares_2026_mvp.csv"
base_2018.to_csv(RUTA_2018, index=False, encoding="utf-8-sig")
base_2026.to_csv(RUTA_2026, index=False, encoding="utf-8-sig")

print("\nListo. Se generaron las dos bases dentro de salidas_energiai.")
print(f"Base 2018: {RUTA_2018.resolve()}")
print(f"Base 2026: {RUTA_2026.resolve()}")
print(f"Hogares válidos: {len(base_2018):,}")
print(f"Corte Eficiente: hasta {CORTE_EFICIENTE_KWH:.2f} kWh/mes")
print(f"Corte Moderado: hasta {CORTE_MODERADO_KWH:.2f} kWh/mes")
print("\nCategorías 2018:")
print(base_2018["categoria"].value_counts())
print("\nCategorías 2026 usando los mismos cortes:")
print(base_2026["categoria"].value_counts())
