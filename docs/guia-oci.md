# Guía de OCI — Object Storage

**Objetivo:** cerrar el requisito obligatorio de OCI en el Sprint 1. Se usa **Object Storage** para guardar el modelo (`.joblib`) y que el `inference-service` lo descargue al arrancar.

> Plantilla. Reemplaza los valores entre `[corchetes]` y marca cada paso como hecho al ejecutarlo. Completa esta guía **mientras** la ejecutas, no antes.

Valores del entorno (llénalos una vez y reúsalos):

- Región: `[tu-región, ej. mx-queretaro-1]`
- Compartment: `[nombre-del-compartment]`
- Namespace: `[se-obtiene-en-el-paso-3]`
- Bucket: `[nombre-del-bucket, ej. energiai-models]`
- Objeto del modelo: `model.joblib`

---

## Prerrequisitos

- [ ] Cuenta de OCI activa (Free Tier sirve).
- [ ] Un usuario con permisos para crear y leer buckets en el compartment elegido.
- [ ] OCI CLI instalado (opcional pero recomendado): `bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"`

---

## Paso 1 — Crear el bucket

Por consola web:
1. Menú → **Storage** → **Buckets**.
2. Seleccionar el **compartment** correcto.
3. **Create Bucket** → nombre `[nombre-del-bucket]` → resto por defecto → **Create**.

- [ ] Bucket creado.

---

## Paso 2 — Credenciales (API key + archivo de configuración)

El SDK necesita un archivo `~/.oci/config`.

1. En la consola: ícono de perfil → **My profile** → **API keys** → **Add API key**.
2. **Generate API key pair**, descargar la **llave privada** (`.pem`) y guardarla (ej. `~/.oci/oci_api_key.pem`).
3. Al terminar, OCI muestra un bloque de **Configuration file preview**. Copiar ese contenido a `~/.oci/config`. Se ve así:

```ini
[DEFAULT]
user=ocid1.user.oc1..[...]
fingerprint=[xx:xx:...]
tenancy=ocid1.tenancy.oc1..[...]
region=[tu-región]
key_file=~/.oci/oci_api_key.pem
```

- [ ] Archivo `~/.oci/config` creado y `key_file` apuntando a la llave privada.

> No subir la llave privada ni el `config` al repositorio. Agregar `.oci/` y `*.pem` al `.gitignore`.

---

## Paso 3 — Obtener el namespace y subir un `.joblib` dummy

El namespace es un identificador de tu tenancy que necesita el SDK.

Con OCI CLI:
```bash
# obtener el namespace (anótalo en los valores del entorno de arriba)
oci os ns get

# crear un archivo dummy y subirlo (aún sin modelo real)
python -c "import joblib; joblib.dump({'dummy': True}, 'model.joblib')"
oci os object put \
  --bucket-name [nombre-del-bucket] \
  --file model.joblib \
  --name model.joblib
```

- [ ] Namespace anotado.
- [ ] `model.joblib` dummy subido al bucket.

---

## Paso 4 — Descargar el modelo desde el `inference-service`

El servicio Python descarga el objeto al arrancar. Fragmento de referencia (ajustar a la estructura real del servicio):

```python
import io
import os
import joblib
import oci

def cargar_modelo():
    config = oci.config.from_file(
        os.environ.get("OCI_CONFIG_FILE", "~/.oci/config")
    )
    client = oci.object_storage.ObjectStorageClient(config)

    namespace = os.environ["OCI_NAMESPACE"]
    bucket = os.environ["OCI_BUCKET"]
    objeto = os.environ.get("OCI_MODEL_OBJECT", "model.joblib")

    resp = client.get_object(namespace, bucket, objeto)
    return joblib.load(io.BytesIO(resp.data.content))
```

- [ ] El servicio descarga el objeto y `joblib.load` no falla (con el dummy).

Si este paso corre con el dummy, **el requisito obligatorio de OCI queda cerrado**. Sustituir el dummy por el modelo real es solo repetir el Paso 3 cuando Data Science lo entregue.

---

## Variables de entorno del `inference-service`

```
OCI_BUCKET=[nombre-del-bucket]
OCI_NAMESPACE=[tu-namespace]
OCI_MODEL_OBJECT=model.joblib
OCI_CONFIG_FILE=~/.oci/config
```

---

## Checklist final

- [ ] Bucket creado.
- [ ] Credenciales configuradas (`~/.oci/config`).
- [ ] Namespace obtenido.
- [ ] `.joblib` (dummy o real) subido.
- [ ] `inference-service` lo descarga y lo carga al arrancar.
- [ ] Llaves y config fuera del repositorio (`.gitignore`).

## Pendiente / notas del equipo

- [ ] Anotar aquí cualquier ajuste real (permisos, políticas de IAM, errores encontrados).
- [ ] Decidir si además se usa OCI Compute para alojar la API (opcional, no bloqueante).
