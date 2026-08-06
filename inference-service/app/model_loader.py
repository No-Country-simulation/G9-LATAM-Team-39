"""
Carga del modelo de Machine Learning.

Este modulo funciona en DOS modos, y se cambia entre ellos con una sola
variable de entorno: MODEL_SOURCE.

    MODEL_SOURCE=local   -> lee el modelo del disco (desarrollo). Es el valor
                            por defecto: si no defines nada, corre en local.
    MODEL_SOURCE=oci     -> descarga el modelo desde OCI Object Storage
                            (produccion) y luego lo carga igual.

La idea: el mismo servicio corre en tu maquina y en produccion sin tocar el
codigo. Solo cambias la variable de entorno.
"""

import os
import joblib
from dotenv import load_dotenv

# Lee el archivo .env (si existe) y carga sus variables. Debe ir antes de los
# os.getenv de abajo, para que ya esten disponibles cuando se lean.
# En local no es obligatorio (hay valores por defecto); es clave para activar OCI.
load_dotenv()

# -----------------------------------------------------------------------------
# Configuracion por variables de entorno
# -----------------------------------------------------------------------------

# Modo: 'local' (por defecto) o 'oci'.
MODEL_SOURCE = os.getenv("MODEL_SOURCE", "local")

# Ruta del modelo en disco. En modo local es de donde se lee; en modo OCI es
# donde se guarda el archivo descargado antes de cargarlo.
MODEL_PATH = os.getenv("MODEL_PATH", "../data-science/models/modelo_energiai.joblib")

# Datos de OCI (solo se usan en modo 'oci'). Los provee el encargado de OCI.
OCI_NAMESPACE = os.getenv("OCI_NAMESPACE")
OCI_BUCKET = os.getenv("OCI_BUCKET")
OCI_MODEL_OBJECT = os.getenv("OCI_MODEL_OBJECT", "modelo_energiai.joblib")
OCI_CONFIG_FILE = os.getenv("OCI_CONFIG_FILE", "~/.oci/config")

# Donde guardar el modelo descargado de OCI (en produccion, /tmp es lo tipico).
OCI_DESTINO_LOCAL = os.getenv("OCI_DESTINO_LOCAL", "/tmp/modelo_energiai.joblib")


# -----------------------------------------------------------------------------
# Punto de entrada
# -----------------------------------------------------------------------------

def cargar_modelo():
    """Devuelve el modelo entrenado, listo para predecir.

    Elige local u OCI segun MODEL_SOURCE. En ambos casos, el resultado es el
    mismo objeto de modelo cargado con joblib: quien lo use no nota diferencia.
    """
    if MODEL_SOURCE == "oci":
        print("[model_loader] Modo OCI: descargando modelo desde Object Storage...")
        ruta = _descargar_desde_oci()
    else:
        print("[model_loader] Modo local: leyendo modelo del disco...")
        ruta = MODEL_PATH

    return _cargar_joblib(ruta)


# -----------------------------------------------------------------------------
# Carga desde disco (comun a los dos modos)
# -----------------------------------------------------------------------------

def _cargar_joblib(ruta: str):
    """Lee un archivo .joblib del disco y lo devuelve como modelo."""
    if not os.path.exists(ruta):
        raise FileNotFoundError(
            f"No se encontro el modelo en '{ruta}'. "
            f"En modo local, revisa MODEL_PATH. En modo OCI, revisa que la "
            f"descarga se haya completado."
        )
    modelo = joblib.load(ruta)
    print(f"[model_loader] Modelo cargado: {ruta}")
    if hasattr(modelo, "feature_names_in_"):
        print(f"[model_loader] Columnas esperadas: {list(modelo.feature_names_in_)}")
    if hasattr(modelo, "classes_"):
        print(f"[model_loader] Clases: {list(modelo.classes_)}")
    return modelo


# -----------------------------------------------------------------------------
# Descarga desde OCI (solo modo 'oci')
# -----------------------------------------------------------------------------

def _descargar_desde_oci() -> str:
    """Descarga el modelo desde OCI Object Storage y devuelve la ruta local.

    Requiere las variables OCI_* definidas y el SDK 'oci' instalado.
    Devuelve la ruta del archivo descargado, que luego carga _cargar_joblib.
    """
    # Validar que estan los datos necesarios antes de intentar conectar.
    faltan = [v for v in ("OCI_NAMESPACE", "OCI_BUCKET") if not os.getenv(v)]
    if faltan:
        raise ValueError(
            f"Modo OCI activado pero faltan variables de entorno: {faltan}. "
            f"Las provee el encargado de OCI."
        )

    import oci  # se importa aqui para que en modo local no haga falta tenerlo

    # Cargar la configuracion de credenciales (~/.oci/config).
    config = oci.config.from_file(os.path.expanduser(OCI_CONFIG_FILE))
    cliente = oci.object_storage.ObjectStorageClient(config)

    # Descargar el objeto (el modelo) del bucket.
    respuesta = cliente.get_object(OCI_NAMESPACE, OCI_BUCKET, OCI_MODEL_OBJECT)

    # Guardar el contenido descargado en un archivo local.
    with open(OCI_DESTINO_LOCAL, "wb") as f:
        for trozo in respuesta.data.raw.stream(1024 * 1024, decode_content=False):
            f.write(trozo)

    print(f"[model_loader] Modelo descargado de OCI a: {OCI_DESTINO_LOCAL}")
    return OCI_DESTINO_LOCAL
