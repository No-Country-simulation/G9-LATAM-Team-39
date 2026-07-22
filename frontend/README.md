# Frontend

> **Módulo opcional.** La descripción del proyecto indica que el front-end **no es obligatorio para el MVP**. No debe bloquear la ruta crítica (dataset → modelo → API → OCI). Solo se aborda cuando el flujo vertical ya funciona.

Interfaz de usuario del Analizador Inteligente de Consumo Energético: captura los datos de consumo y muestra el resultado que devuelve el backend.

> Contrato de la API: ver `../docs/contrato-api.md` (fuente única). Este README es operativo.

> Reparto por frentes: ver "Frentes de trabajo" en la documentación de No Country.

## Alcance mínimo (si se hace)

- Formulario con las 5 variables de entrada.
- Enviar `POST /analisis-energetico` al backend.
- Mostrar estados de carga y errores.
- Presentar categoría, probabilidad, costo estimado, moneda y recomendaciones.

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
