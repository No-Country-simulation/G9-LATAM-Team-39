/**
 * Punto de entrada del frontend.
 *
 * Orquesta las dos capas: lee el formulario (ui), llama al backend (api),
 * y muestra el resultado (ui). No contiene lógica de DOM ni de red directa,
 * solo el "pegamento" entre ambas.
 */
import { crearAnalisis, obtenerAnalisis, ApiError } from "./api.js";
import { activarNavegacion } from "./navigation.js";
import { iniciarMedidor } from "./meter.js";
import {
  construirEquipos,
  activarTogglePico,
  bloquearDecimalesCantidad,
  activarModal,
  leerFormulario,
  mostrarResultado,
  mostrarError,
  setCargando,
  onAnalizar,
} from "./ui.js";

// Tiempo mínimo (ms) que se muestra el spinner de "Analizando…", aunque el
// backend responda antes. Evita que el spinner "parpadee" cuando la respuesta
// es instantánea (backend local). Ajusta este número a gusto (1500–3000).
const SPINNER_MIN_MS = 3000;

// --- Inicialización cuando el DOM está listo ---
function init() {
  activarNavegacion();
  iniciarMedidor();
  construirEquipos();
  activarTogglePico();
  bloquearDecimalesCantidad();
  activarModal();
  onAnalizar(analizar);
  activarConsulta();
}

// Espera hasta completar el tiempo mínimo del spinner (si ya pasó, no espera).
function esperarMinimo(inicioMs) {
  const transcurrido = Date.now() - inicioMs;
  const restante = SPINNER_MIN_MS - transcurrido;
  return restante > 0
    ? new Promise((r) => setTimeout(r, restante))
    : Promise.resolve();
}

// --- Handler del botón "Analizar" ---
async function analizar() {
  // 1. Leer y validar el formulario.
  let datos;
  try {
    datos = leerFormulario();
  } catch (err) {
    // Errores de validación → modal de error, sin llamar al backend.
    mostrarError(err.message);
    return;
  }

  // 2. Llamar al backend (el modal se abre con el spinner).
  setCargando(true);
  const inicio = Date.now();
  try {
    const resultado = await crearAnalisis(datos);
    await esperarMinimo(inicio);   // garantiza el tiempo mínimo de spinner
    mostrarResultado(resultado);   // reemplaza el spinner con el resultado
  } catch (err) {
    await esperarMinimo(inicio);   // también en error, para no parpadear
    if (err instanceof ApiError) {
      mostrarError(err.message);   // reemplaza el spinner con el error
      if (err.detalle) console.error("Detalle del error:", err.detalle);
    } else {
      mostrarError("Ocurrió un error inesperado.");
      console.error(err);
    }
  } finally {
    // Reactiva el botón (el modal sigue abierto mostrando resultado/error).
    setCargando(false);
  }
}

// --- Handler de "Buscar análisis" por código (id) ---
function activarConsulta() {
  const btn = document.getElementById("buscarAnalisis");
  const input = document.getElementById("consultaId");
  if (!btn || !input) return;

  async function buscar() {
    const id = input.value.trim();
    if (!id) {
      mostrarError("Ingresa un código de análisis para buscar.");
      return;
    }

    setCargando(true, {
      titulo: "Buscando tu análisis…",
      subtitulo: "Estamos recuperando tu resultado guardado.",
    });
    const inicio = Date.now();
    try {
      const resultado = await obtenerAnalisis(id);
      await esperarMinimo(inicio);
      mostrarResultado(resultado, "Análisis recuperado", false);
    } catch (err) {
      await esperarMinimo(inicio);
      if (err instanceof ApiError && err.status === 404) {
        mostrarError("No encontramos ningún análisis con ese código. Verifica que esté bien escrito.");
      } else if (err instanceof ApiError) {
        mostrarError(err.message);
        if (err.detalle) console.error("Detalle del error:", err.detalle);
      } else {
        mostrarError("Ocurrió un error inesperado.");
        console.error(err);
      }
    } finally {
      setCargando(false);
    }
  }

  btn.addEventListener("click", buscar);
  // Permitir buscar con Enter desde el campo.
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") buscar();
  });
}

// Arrancar cuando el documento esté listo.
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
