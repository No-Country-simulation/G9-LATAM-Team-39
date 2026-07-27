# Frontend

> **Módulo opcional.** La descripción del proyecto indica que el front-end **no es obligatorio para el MVP**. No debe bloquear la ruta crítica (dataset → modelo → API → OCI). Solo se aborda cuando el flujo vertical ya funciona.

Interfaz de usuario del Analizador Inteligente de Consumo Energético: captura los datos de consumo y muestra el resultado que devuelve el backend.

> Contrato de la API: ver `../docs/contrato-api.md` (única versión válida). Tabla de consumo por aparato: `../docs/consumo-por-aparato.md`. Este README es operativo.

> Reparto por frentes: ver "Frentes de trabajo" en la documentación de No Country.

---

## Alcance mínimo (si se hace)

- Formulario con las 5 variables de entrada.
- **Lista multiseleccionable de aparatos** (ver abajo, es parte del alcance).
- Enviar `POST /analisis-energetico` al backend.
- Mostrar estados de carga y errores.
- Presentar categoría, probabilidad, costo estimado, moneda y recomendaciones.

## El formulario

| Campo | Control | Notas |
|---|---|---|
| `consumo_kwh` | número | Ver "si el usuario no lo sabe" |
| `uso_horario_pico` | sí / no | |
| `cantidad_equipos` | número | Se puede llenar solo, contando los aparatos seleccionados |
| `tipo_inmueble` | selector | Exactamente 3 opciones: `Casa`, `Departamento`, `Otro` |
| `horas_alto_consumo` | número | Horas diarias de equipos de alto consumo |
| `equipos` | multiselección | **Opcional**, se envía tal cual a la API |

Catálogo de `equipos`: `aire_acondicionado`, `calentador_electrico`, `refrigerador`, `calefactor`, `focos`, `pantalla`, `lavadora`, `plancha`, `ventilador`, `bomba_agua`, `otros`.

---

## Responsabilidad propia: estimar el consumo

**Esta parte la hace el frontend, no el backend** (ver `../docs/decisiones.md`, D10). La mayoría de las personas no conoce sus kWh: conoce cuánto paga.

El formulario ofrece dos caminos y **siempre envía `consumo_kwh` ya resuelto**:

- **"Sí conozco mi consumo"** → el usuario lo escribe. Este dato manda siempre.
- **"No lo sé"** → selecciona sus aparatos y el frontend estima:

```
consumo_estimado = Σ (kWh_del_aparato × cantidad_seleccionada)
```

Los valores por aparato están en `../docs/consumo-por-aparato.md`.

**Excepción — `focos`:** su valor (16.9) corresponde a **todo el hogar**, no a un foco. Siempre se suma ×1, sin importar cuántos declare el usuario.

**Si elige "no lo sé" y no selecciona ningún aparato:** el formulario no deja continuar. Pide el consumo o al menos un aparato. No se inventa un valor por defecto.

> **Por qué aquí y no en el backend:** `consumo_kwh` es obligatorio en el contrato del MVP. Poniendo la estimación en el frontend, el contrato queda intacto y el backend no cambia. Como efecto secundario, quien llame la API directamente (Postman, Swagger) debe conocer su consumo: la estimación es una comodidad de la interfaz, no una función de la API.

---

## Stack sugerido (elegir lo más rápido)

- Opción A: HTML + JS plano (`fetch` al backend). Cero build, ideal para la demo.
- Opción B: Streamlit (Python), si el dueño viene de Data Science.
- Opción C: framework JS (React/Vite), solo si hay tiempo de sobra.

## Variables

| Variable | Descripción |
|---|---|
| `API_BASE_URL` | URL del backend |

## Estado

La tecnología o framework del frontend todavía no ha sido definido. Se decidirá solo si hay capacidad tras cerrar el MVP.
