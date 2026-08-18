# Frontend — EnergiAI

Interfaz web del Analizador Inteligente de Consumo Energético. El usuario captura
los datos de su vivienda, y la app muestra su perfil energético (Eficiente /
Moderado / Ineficiente), el costo mensual estimado y recomendaciones.

> Contrato de la API: ver `../docs/contrato-api.md` (única versión válida).
> Este README es operativo.

## Estructura

```
frontend/
├── index.html          # estructura (HTML)
├── css/
│   └── styles.css      # estilos
└── js/
    ├── config.js       # configuración: URL del backend y catálogo de equipos
    ├── api.js          # capa de comunicación con el backend (fetch)
    ├── ui.js           # manejo del DOM: formulario y resultados
    └── main.js         # punto de entrada; orquesta ui + api
```

Separación por responsabilidades: `api.js` es lo único que habla con el backend;
`ui.js` es lo único que toca el DOM; `main.js` los conecta. Si cambia el backend,
se toca `api.js`/`config.js`; si cambia el diseño, `ui.js`/`css`.

## Cómo correr en local

Usa módulos ES (`import`/`export`), así que **no se abre con doble clic**
(el navegador bloquea módulos vía `file://`). Hay que servirlo por HTTP:

```bash
# desde la carpeta frontend/
python3 -m http.server 5500
```

Luego abrir `http://localhost:5500`. Alternativas: extensión **Live Server** de
VS Code, o `npx serve`.

## El formulario

| Campo | Control | Envía como |
|---|---|---|
| Consumo mensual (kWh) | número | `consumoKwh` |
| ¿Uso en horario pico? | sí / no | `usoHorarioPico` |
| Cantidad de equipos | número | `cantidadEquipos` |
| Tipo de vivienda | selector (Casa / Departamento / Otro) | `tipoInmueble` |
| Equipos de alto consumo | multiselección con horas/día y días/mes | `equiposAltoConsumo` |

**El usuario ingresa su consumo directamente** (lo encuentra en su recibo de luz).
No se estima desde los aparatos: se pide tal cual.

**`horasAltoConsumo` no se envía desde el frontend**: lo calcula el backend a
partir de la lista de equipos de alto consumo (potencia x horas x dias / 1.5).

### Catálogo de equipos de alto consumo

Los códigos coinciden con el enum `EquipoAltoConsumo` del backend
(`../backend/.../catalog/`). Están definidos en `js/config.js`:

`AIRE_ACONDICIONADO`, `CALENTADOR_ELECTRICO`, `HORNO_ELECTRICO`, `SECADORA_ROPA`,
`PARRILLA_ELECTRICA`, `LAVAVAJILLAS`, `BOMBA_AGUA`, `CALEFACTOR_ELECTRICO`.

Si el backend cambia el catálogo, actualizar `CATALOGO_EQUIPOS` en `config.js`.

## Conexión con el backend

El frontend llama a `POST /analisis-energetico` con este cuerpo (AnalisisRequest):

```json
{
  "consumoKwh": 200,
  "usoHorarioPico": true,
  "cantidadEquipos": 8,
  "tipoInmueble": "Casa",
  "equiposAltoConsumo": [
    { "codigoEquipo": "AIRE_ACONDICIONADO", "horasUsoDia": 4, "diasUsoMes": 20 }
  ]
}
```

La respuesta (AnalisisResponse) trae `categoria`, `probabilidad`,
`costoEstimadoMensual`, `moneda`, `fechaAnalisis` y `recomendaciones`.

El frontend maneja los estados de carga y muestra los errores del backend.

## Configuración

En `js/config.js`:

- **`BASE_URL`**: la URL del backend.
  - Local: `http://localhost:8080`
  - Producción: la URL del backend en Render.
- **`ENDPOINTS.analisis`**: la ruta del endpoint (`/analisis-energetico`).
- **`CATALOGO_EQUIPOS`**: los equipos de alto consumo (ver arriba).

## CORS

El backend debe permitir las peticiones del frontend. En el controller Java:

```java
@CrossOrigin(origins = "*")   // en producción, restringir al dominio del frontend
```

Sin esto, el navegador bloquea las llamadas y la app no conecta.

## Despliegue (Vercel)

Al ser estático, se despliega directo: conectar el repo a Vercel con la carpeta
`frontend/` como raíz del proyecto. Antes de desplegar, cambiar `BASE_URL` en
`config.js` por la URL del backend en producción.
