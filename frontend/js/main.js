/**
 * Punto de entrada del frontend.
 *
 * Orquesta las dos capas: lee el formulario (ui), llama al backend (api),
 * y muestra el resultado (ui). No contiene lógica de DOM ni de red directa,
 * solo el "pegamento" entre ambas.
 */
import { crearAnalisis, ApiError } from "./api.js";
import {
  construirEquipos,
  activarTogglePico,
  leerFormulario,
  mostrarResultado,
  mostrarError,
  limpiarError,
  setCargando,
  onAnalizar,
} from "./ui.js";

// --- Inicialización cuando el DOM está listo ---
function init() {
  construirEquipos();
  activarTogglePico();
  onAnalizar(analizar);
}

// --- Handler del botón "Analizar" ---
async function analizar() {
  limpiarError();

  // 1. Leer y validar el formulario.
  let datos;
  try {
    datos = leerFormulario();
  } catch (err) {
    mostrarError(err.message);
    return;
  }

  // 2. Llamar al backend.
  setCargando(true);
  try {
    const resultado = await crearAnalisis(datos);
    mostrarResultado(resultado);
  } catch (err) {
    if (err instanceof ApiError) {
      // Mostrar el mensaje amigable; el detalle técnico va a la consola.
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

// Arrancar cuando el documento esté listo.
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
