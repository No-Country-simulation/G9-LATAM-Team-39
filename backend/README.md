# Backend

API REST principal del proyecto, desarrollada con Java y Spring Boot. Valida la entrada, llama al servicio de inferencia para obtener la clasificación, completa la respuesta con costo estimado y recomendaciones, y guarda cada análisis para poder consultarlo después.

> Arquitectura global, flujo completo y **contrato único** de la API: ver `../docs/` y `../docs/contrato-api.md`. Este README es operativo.

> Reparto por frentes: ver "Frentes de trabajo" en la documentación de No Country.

## Cómo correr

```bash
# desde backend/
./mvnw spring-boot:run
```

- API: `http://localhost:8080`
- Swagger UI: `http://localhost:8080/swagger-ui.html`

## Variables de entorno

| Variable | Descripción | Ejemplo |
|---|---|---|
| `INFERENCE_SERVICE_URL` | URL del servicio Python de inferencia | `http://localhost:8000` |
| `TARIFA_REFERENCIA_KWH` | Tarifa por kWh (R$) | `0.75` |
| `MONEDA` | Moneda de referencia | `BRL` |
| `SPRING_DATASOURCE_URL` | Conexión a la base de datos | `jdbc:h2:mem:energiai` |
| `SPRING_DATASOURCE_USERNAME` | Usuario de la base de datos | `sa` |
| `SPRING_DATASOURCE_PASSWORD` | Contraseña de la base de datos | — |

> El motor de base de datos **todavía no está decidido** (ver `../docs/decisiones.md`, D12). El ejemplo usa H2 en memoria por ser lo más rápido de levantar; la decisión final la cierra este frente.

## Endpoints

Los dos son **obligatorios** según la descripción del proyecto. Detalle completo en `../docs/contrato-api.md`.

| Endpoint | Qué hace |
|---|---|
| `POST /analisis-energetico` | Recibe los datos de consumo, devuelve categoría, probabilidad, costo y recomendaciones |
| `GET /resultados/{id}` | Recupera un análisis previo por su identificador |
| `GET /resultados` *(opcional)* | Lista los análisis más recientes; útil para la demo |

## Responsabilidades del módulo

- Exponer los **dos endpoints** según el contrato único (`../docs/contrato-api.md`).
- **Validación** de entrada (campos requeridos, tipos, rangos) y **manejo de errores** con códigos HTTP claros (400, 404, 502, 500).
- Llamar al `inference-service` para obtener `categoria` + `probabilidad`. Se le envían **solo las 5 variables obligatorias**, nunca el campo `equipos`.
- Calcular `costo_estimado_mensual = consumo_kwh × TARIFA_REFERENCIA_KWH`.
- Completar `id`, `fecha_analisis`, `moneda` y `tarifa_referencia_kwh` en la respuesta.
- Generar `recomendaciones` por reglas según categoría y variables de mayor impacto.
- Usar el campo opcional `equipos` para las **recomendaciones específicas por aparato** (tabla y lógica de desglose en `../docs/consumo-por-aparato.md`).
- **Persistir cada análisis** (ver abajo).
- Documentar endpoints con OpenAPI/Swagger.

## Persistencia (obligatoria)

No es opcional: el endpoint `GET /resultados/{id}` no puede existir sin guardar los análisis. Registro mínimo:

| Campo | Descripción |
|---|---|
| `id` | UUID generado por el backend |
| `fecha_analisis` | timestamp |
| las 5 entradas | tal como llegaron |
| `equipos` | lista opcional (JSON o texto) |
| `categoria`, `probabilidad` | respuesta del modelo |
| `costo_estimado_mensual` | calculado |

**Qué NO se guarda aquí:** los microdatos de ENCEVI, el dataset de entrenamiento ni el modelo. El modelo vive en OCI Object Storage; la base de datos solo guarda el historial de consultas.

## Sobre `consumo_kwh`

Es **siempre obligatorio**. Si el usuario no conoce su consumo, el **frontend** lo estima a partir de los aparatos seleccionados y envía el valor ya calculado. El backend nunca recibe una petición sin ese campo y **no estima nada**.

## Estado de integración

Mientras el modelo real no esté listo, trabajar contra un **mock** del `inference-service` que respete el contrato. No bloquear el avance del backend por el modelo.

## Estructura sugerida

```
backend/
├── src/main/java/.../controller/
├── src/main/java/.../service/
├── src/main/java/.../dto/
├── src/main/java/.../model/        # entidad del análisis persistido
├── src/main/java/.../repository/   # acceso a la base de datos
├── src/main/java/.../client/       # cliente HTTP al inference-service
└── src/main/resources/application.yml
```


# EnergiAI - Backend API

Backend REST del proyecto **EnergiAI**, desarrollado para el Hackathon ONE G9 - Alura + Oracle.

La API recibe información sobre el consumo energético de una vivienda o pequeño establecimiento, se comunica con el servicio de inferencia para obtener la clasificación energética y devuelve información como:

- Categoría energética: `EFICIENTE`, `MODERADO` o `INEFICIENTE`.
- Probabilidad de la predicción.
- Estimación del costo mensual.
- Recomendaciones de ahorro energético.
- Historial de análisis.

## Tecnologías

- Java 21
- Spring Boot
- Maven
- PostgreSQL
- Spring Data JPA / Hibernate
- Swagger / OpenAPI
- FastAPI como servicio de inferencia
- Modelo de Machine Learning serializado con Joblib
- OCI Object Storage para almacenamiento del modelo

## Requisitos

Antes de iniciar el backend es necesario tener instalado:

- Java JDK 21
- PostgreSQL
- Python y el servicio `inference-service` configurado
- Git

Verificar Java:

```bash
java -version
```

Debe utilizar Java 21.

También se puede verificar la versión utilizada por Maven:

### Windows PowerShell

```powershell
.\mvnw.cmd -version
```

### Linux/macOS

```bash
./mvnw -version
```

---

# 1. Configurar PostgreSQL

El backend utiliza una base de datos PostgreSQL llamada:

```text
energiai
```

La configuración se encuentra en:

```text
src/main/resources/application.yaml
```

Ejemplo:

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/energiai
    username: postgres
    password: ${DB_PASSWORD}
```

Crear la base de datos antes de iniciar la aplicación:

```sql
CREATE DATABASE energiai;
```

La contraseña de PostgreSQL no se almacena directamente en el repositorio.

En Windows PowerShell:

```powershell
$env:DB_PASSWORD="TU_PASSWORD_POSTGRES"
```

En CMD:

```cmd
set DB_PASSWORD=TU_PASSWORD_POSTGRES
```

En Linux/macOS:

```bash
export DB_PASSWORD="TU_PASSWORD_POSTGRES"
```

---

# 2. Configurar el servicio de inferencia

El backend se comunica con el servicio FastAPI mediante:

```text
http://localhost:8000
```

La URL puede configurarse mediante:

```text
INFERENCE_SERVICE_URL
```

En PowerShell:

```powershell
$env:INFERENCE_SERVICE_URL="http://localhost:8000"
```

En CMD:

```cmd
set INFERENCE_SERVICE_URL=http://localhost:8000
```

Si no se especifica la variable, el backend utiliza por defecto:

```text
http://localhost:8000
```

> El servicio de inferencia debe estar iniciado antes de realizar un análisis energético.

---

# 3. Iniciar el servicio de inferencia

Desde la raíz del proyecto:

```text
energy-analysis-api/
```

entrar a:

```bash
cd inference-service
```

Activar el entorno virtual.

### Windows

```cmd
.venv\Scripts\activate
```

Después iniciar FastAPI:

```bash
uvicorn app.main:app --reload --port 8000
```

Si se utiliza OCI, el archivo:

```text
inference-service/.env
```

debe contener la configuración correspondiente.

Ejemplo:

```env
MODEL_SOURCE=oci

MODEL_PATH=../data-science/models/modelo_energiai.joblib

OCI_NAMESPACE=TU_NAMESPACE
OCI_BUCKET=TU_BUCKET
OCI_MODEL_OBJECT=modelo_energiai.joblib
OCI_CONFIG_FILE=RUTA_A_TU_CONFIG_OCI
OCI_DESTINO_LOCAL=RUTA_TEMPORAL_MODELO
```

Las credenciales reales de OCI y las llaves `.pem` **no deben subirse al repositorio**.

Cuando OCI funciona correctamente, el servicio mostrará mensajes similares a:

```text
[model_loader] Modo OCI: descargando modelo desde Object Storage...
[model_loader] Modelo descargado de OCI...
[model_loader] Modelo cargado...
Application startup complete.
```

El servicio estará disponible en:

```text
http://localhost:8000
```

---

# 4. Iniciar el backend Spring Boot

Abrir otra terminal y entrar al directorio:

```bash
cd backend
```

Configurar las variables necesarias.

### PowerShell

```powershell
$env:DB_PASSWORD="TU_PASSWORD_POSTGRES"
$env:INFERENCE_SERVICE_URL="http://localhost:8000"
```

Después iniciar Spring Boot:

```powershell
.\mvnw.cmd spring-boot:run
```

### CMD

```cmd
set DB_PASSWORD=TU_PASSWORD_POSTGRES
set INFERENCE_SERVICE_URL=http://localhost:8000
mvnw.cmd spring-boot:run
```

Cuando el backend inicie correctamente deberá aparecer:

```text
Tomcat started on port 8080
Started EnergyAnalysisApiApplication
```

La API estará disponible en:

```text
http://localhost:8080
```

---

# 5. Swagger

La documentación interactiva de la API puede consultarse en:

```text
http://localhost:8080/swagger-ui/index.html
```

Desde Swagger se pueden probar los endpoints disponibles.

Entre ellos:

```text
POST   /api/analisis
GET    /api/analisis
GET    /api/analisis/{id}
PUT    /api/analisis/{id}
DELETE /api/analisis/{id}
```

---

# 6. Ejemplo de análisis

Ejemplo de solicitud:

```json
{
  "consumoKwh": 420.0,
  "usoHorarioPico": true,
  "cantidadEquipos": 5,
  "tipoInmueble": "Departamento",
  "equiposAltoConsumo": [
    {
      "codigoEquipo": "AIRE_ACONDICIONADO",
      "horasUsoDia": 0.4,
      "diasUsoMes": 3
    },
    {
      "codigoEquipo": "HORNO_ELECTRICO",
      "horasUsoDia": 0.4,
      "diasUsoMes": 3
    }
  ]
}
```

La API procesa los datos y devuelve una respuesta similar a:

```json
{
  "id": "UUID_GENERADO",
  "categoria": "MODERADO",
  "probabilidad": 0.66,
  "costoEstimadoMensual": 315.00,
  "moneda": "BRL",
  "fechaAnalisis": "2026-08-17T18:00:00",
  "recomendaciones": [
    "Reducir el uso de equipos eléctricos durante los horarios de mayor consumo.",
    "Desconectar los dispositivos que no estén siendo utilizados."
  ]
}
```

La tarifa financiera de referencia utilizada por el proyecto es:

```text
R$ 0.75 por kWh
```

Por ejemplo:

```text
420 kWh × R$ 0.75 = R$ 315.00
```

---

# 7. Equipos de alto consumo disponibles

Actualmente el backend reconoce los siguientes códigos:

```text
AIRE_ACONDICIONADO
CALENTADOR_ELECTRICO
HORNO_ELECTRICO
SECADORA_ROPA
PARRILLA_ELECTRICA
LAVAVAJILLAS
BOMBA_AGUA
CALEFACTOR_ELECTRICO
```

Los códigos deben enviarse exactamente en el campo:

```json
"codigoEquipo": "AIRE_ACONDICIONADO"
```

---

# 8. Ejecutar pruebas

Para ejecutar las pruebas del servicio de análisis:

### Windows

```powershell
.\mvnw.cmd test -Dtest=AnalisisServiceImplTest
```

Para ejecutar todas las pruebas:

```powershell
.\mvnw.cmd test
```

Un resultado correcto debe finalizar con:

```text
BUILD SUCCESS
```

---

# Arquitectura básica

```text
Cliente / Swagger
       |
       v
Spring Boot :8080
       |
       +------> PostgreSQL :5432
       |
       v
FastAPI :8000
       |
       v
Modelo de Machine Learning
       ^
       |
OCI Object Storage
```

Spring Boot administra la API REST, persistencia, cálculo financiero y recomendaciones.

FastAPI se encarga de cargar el modelo de Machine Learning y realizar la clasificación energética.

OCI Object Storage permite almacenar el modelo entrenado utilizado por el servicio de inferencia.

---

# Importante

Nunca subir al repositorio:

```text
inference-service/.env
~/.oci/config
*.pem
```

Estos archivos contienen configuración o credenciales privadas.

Si FastAPI no está disponible, el backend no podrá realizar nuevas predicciones y deberá responder con el manejo de error correspondiente.











La estructura del proyecto Spring Boot todavía no ha sido inicializada.
