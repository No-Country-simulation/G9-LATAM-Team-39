/**
 * Navegación entre las tres vistas: landing (inicio), app (formulario)
 * y consulta (buscar análisis por código).
 * No hay recarga de página: se muestra/oculta cada vista.
 */

const landing  = () => document.getElementById("landing");
const app      = () => document.getElementById("app");
const consulta = () => document.getElementById("consulta");

/** Oculta todas las vistas. */
function ocultarTodo() {
  landing().hidden = true;
  app().hidden = true;
  consulta().hidden = true;
}

/** Muestra una vista y sube al inicio. */
function mostrar(vista) {
  ocultarTodo();
  vista().hidden = false;
  window.scrollTo({ top: 0, behavior: "auto" });
}

export function mostrarFormulario() { mostrar(app); }
export function mostrarLanding()    { mostrar(landing); }
export function mostrarConsulta()   { mostrar(consulta); }

/** Engancha todos los botones que navegan entre vistas. */
export function activarNavegacion() {
  document.querySelectorAll("[data-goto-form]").forEach((b) =>
    b.addEventListener("click", mostrarFormulario)
  );
  document.querySelectorAll("[data-goto-landing]").forEach((b) =>
    b.addEventListener("click", mostrarLanding)
  );
  document.querySelectorAll("[data-goto-consulta]").forEach((b) =>
    b.addEventListener("click", mostrarConsulta)
  );
}
