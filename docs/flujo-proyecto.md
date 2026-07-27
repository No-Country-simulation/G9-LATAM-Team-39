# Flujo del proyecto — de ENCEVI al usuario final

Documento de referencia para todo el equipo. Explica las dos fases del sistema, qué script hace qué, y quién es responsable de cada tramo.

---

## Resumen en una línea

**Fase 1 (una vez):** datos públicos → dataset etiquetado → modelo entrenado → OCI.
**Fase 2 (cada consulta):** usuario → API Java → servicio Python → modelo → respuesta.

---

## FASE 1 — Construcción del modelo

Se ejecuta **una sola vez** durante el proyecto. Produce el archivo `model.joblib`.

### Paso 1 · Microdatos de ENCEVI 2018 (INEGI)

13 archivos CSV con 28,953 viviendas encuestadas: `encevi.csv`, `electro.csv`, `focos.csv`, `pantalla.csv`, `aireacond.csv`, etc.

Es la materia prima. No se toca a mano.

### Paso 2 · `Energia.py` → base con las 5 variables

**Responsables: pareja de Dataset (nosotros dos).**

El script lee los 13 CSV y calcula el consumo **aparato por aparato** (potencia × horas × cantidad), luego lo agrega por hogar. Produce:

- `01_base_hogares_2018_mvp.csv` — 28,763 hogares con las 5 variables del contrato.
- `02_base_hogares_2026_mvp.csv` — escenario con equipos eficientes (para recomendaciones, **no** para entrenar).

### Paso 3 · `etiquetar_dataset.py` → agrega la categoría

**Responsables: pareja de Dataset (nosotros dos).**

Toma la base anterior y **reemplaza la columna `categoria`** por una calculada con cuatro factores:

```
puntaje = consumo + horario_pico + horas_alto_consumo + intensidad
0-4 → EFICIENTE   |   5-8 → MODERADO   |   9+ → INEFICIENTE
```

Los umbrales de cada factor se calculan con **percentiles del propio dataset**, no son valores fijos.

> **Por qué se reemplaza:** el etiquetado original usaba terciles de `consumo_kwh` únicamente. Eso hacía que el modelo diera 100 % de accuracy con `consumo_kwh` explicando el 100 % y las otras 4 variables el 0 % — el usuario llenaría 5 campos y solo 1 contaría. Con el sistema multifactor las 5 aportan.

**Salida:** `dataset_entrenamiento.csv` con **exactamente 6 columnas**:
`consumo_kwh`, `uso_horario_pico`, `cantidad_equipos`, `tipo_inmueble`, `horas_alto_consumo`, `categoria`.

Ni una columna más. El puntaje y los factores parciales se calculan y se descartan (si se guardaran, el modelo tendría la respuesta escondida en una columna).

Ejecución (sin argumentos, toma los archivos por defecto):
```bash
python etiquetar_dataset.py
```

Lee `01_base_hogares_2018_mvp.csv` de la raíz del proyecto y escribe `dataset_entrenamiento.csv`. Si los archivos están en otra carpeta, se ajustan las constantes `ARCHIVO_ENTRADA` y `ARCHIVO_SALIDA` al inicio del script.

### Paso 4 · Notebook → entrenar y serializar

**Responsables: pareja de Modelo (los otros dos de Data Science).**

Aquí empieza su trabajo. Reciben `dataset_entrenamiento.csv` y hacen:

1. **EDA** — explorar y entender los datos (distribuciones, correlaciones, balance de clases).
2. **Preparar variables** — codificar `tipo_inmueble` (one-hot) y `uso_horario_pico` (0/1).
3. **Separar** train/test (ej. 70/30, estratificado por categoría).
4. **Entrenar y comparar** los tres modelos candidatos: Regresión Logística, Árbol de Decisión, Random Forest.
5. **Evaluar** con accuracy, F1 por clase y matriz de confusión.
6. **Serializar** el mejor con `joblib.dump(modelo, "model.joblib")`.

**Nota metodológica que deben documentar:** como la etiqueta se deriva de reglas, el modelo tenderá a reaprenderlas y el accuracy será muy alto (~99 %). Es esperado y correcto para el entregable, pero hay que explicarlo con honestidad en el notebook, no presentarlo como un hallazgo.

Deben verificar además que **ninguna variable quede en 0 % de importancia**. Si eso pasa, avisar a la pareja de Dataset.

### Paso 5 · Subir el modelo a OCI

**Responsable: encargado de OCI.**

`model.joblib` se sube a **OCI Object Storage**. Con esto se cumple el requisito obligatorio de OCI.

Procedimiento completo en `docs/guia-oci.md`. Se prueba primero con un archivo dummy, sin esperar al modelo real.

---

## FASE 2 — Producción

Se ejecuta en **cada consulta** del usuario. Aquí ya no existen ENCEVI, ni los scripts, ni las reglas de puntajes: solo el modelo entrenado.

### 1. Frontend

**Responsables: los del equipo de Java, con capacidad libre. Opcional, fuera de la ruta crítica.**

Formulario con las 5 variables, más una lista multiseleccionable de equipos (ver `decisiones.md`, D10) que:
- cuenta los seleccionados para llenar `cantidad_equipos`,
- se envía como campo opcional `equipos` para recomendaciones específicas,
- permite estimar `consumo_kwh` si el usuario no lo conoce.

El módulo es opcional, pero la lista de equipos ya está decidida e implementada del lado del backend.

### 2. Backend Java (Spring Boot)

**Responsables: pareja de API (2 compañeros).**

- Expone `POST /analisis-energetico` y `GET /resultados/{id}`.
- **Valida** la entrada y maneja errores con códigos HTTP claros.
- Llama al servicio de inferencia.
- Calcula `costo_estimado_mensual = consumo_kwh × 0.75`.
- Genera **recomendaciones** por reglas.
- **Guarda el análisis** en la base de datos (necesario para el endpoint de consulta).
- Documenta todo con Swagger.

Trabaja contra un **mock** del servicio Python hasta que el modelo esté listo. No debe quedar bloqueado.

### 3. Servicio de inferencia (Python / FastAPI)

**Responsables: pareja de inference-service (nosotros dos).**

- **Al arrancar:** descarga `model.joblib` desde OCI Object Storage y lo carga en memoria (una sola vez).
- Expone `POST /predict`: recibe las 5 variables, devuelve `categoria` + `probabilidad`.
- **No** calcula costo ni recomendaciones. Solo clasifica.

### 4. Respuesta al usuario

El backend arma el JSON final y lo devuelve al frontend.

---

## Dónde vive cada cosa

| Elemento | Dónde | Cuándo se usa |
|---|---|---|
| Microdatos ENCEVI | archivos CSV de INEGI | Fase 1, una vez |
| `Energia.py` | repo, `data-science/` | Fase 1, una vez |
| `etiquetar_dataset.py` | repo, `data-science/` | Fase 1, una vez |
| Reglas de puntajes | dentro de `etiquetar_dataset.py` | Fase 1, una vez |
| `dataset_entrenamiento.csv` | repo, `data-science/data/` | Fase 1, para entrenar |
| **`model.joblib`** | **OCI Object Storage** | Fase 2, en cada consulta |
| Historial de análisis | **base de datos** | Fase 2, se escribe siempre |

**La confusión más común:** las reglas de puntajes **no existen en producción**. Se usan una vez para etiquetar y ahí termina su función. En producción manda el modelo, que ya las aprendió.

---

## Responsables por frente

| Frente | Quiénes | Entregable |
|---|---|---|
| Dataset + reglas + calibración ENCEVI | pareja de Dataset | `dataset_entrenamiento.csv` |
| EDA + modelos + serialización + notebook | pareja de Modelo | `model.joblib` + notebook |
| API Spring Boot (endpoints, validación, Swagger) | pareja de API | API documentada |
| inference-service Python + integración | pareja de Inferencia | servicio `/predict` |
| OCI Object Storage + despliegue | 1 responsable | requisito OCI cerrado |
| Frontend (opcional) | equipo de Java con capacidad libre | formulario |
| Entregables (video, 3 ejemplos, enlaces) | líder de proyecto | entrega en plataforma |

---

## Dependencias críticas

```
Dataset  →  Modelo  →  Servicio Python  →  Backend
                ↓
              OCI  (se puede arrancar YA, con archivo dummy)
```

- La **pareja de Modelo depende** de que Dataset entregue. Es la dependencia más apretada.
- **OCI no depende de nadie.** Puede y debe arrancar hoy con un `.joblib` dummy.
- **Backend no depende del modelo** si trabaja contra el mock del contrato.
