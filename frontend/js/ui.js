/**
 * Capa de UI — construye el formulario, lee sus valores y pinta resultados.
 *
 * No sabe nada de fetch ni del backend: solo del DOM. Recibe y devuelve datos
 * planos. La orquestación (llamar a la API) la hace main.js.
 */
import { CATALOGO_EQUIPOS } from "./config.js";

// --- Referencias al DOM, en un solo lugar ---
const el = {
  consumo:  () => document.getElementById("consumo"),
  cantidad: () => document.getElementById("cantidad"),
  tipo:     () => document.getElementById("tipo"),
  equipos:  () => document.getElementById("equipos"),
  pico:     () => document.querySelectorAll("#pico .opt"),
  btn:      () => document.getElementById("analizar"),
  // Modal y sus vistas
  modal:       () => document.getElementById("modal"),
  viewLoading: () => document.getElementById("viewLoading"),
  viewResult:  () => document.getElementById("viewResult"),
  viewError:   () => document.getElementById("viewError"),
};

let usoPico = true; // estado del toggle de horario pico

/**
 * Construye el multiselector de equipos a partir del catálogo.
 * Cada equipo tiene un checkbox; al marcarlo, se muestran sus campos
 * de horas/día y días/mes.
 */
export function construirEquipos() {
  const cont = el.equipos();
  CATALOGO_EQUIPOS.forEach((eq) => {
    const div = document.createElement("div");
    div.className = "equipo";
    div.innerHTML = `
      <label class="equipo-head">
        <input type="checkbox" data-codigo="${eq.codigo}">
        <span>${eq.nombre}</span>
      </label>
      <div class="equipo-detalle">
        <div>
          <label>Horas/día</label>
          <input type="number" class="horas" min="0.5" max="24" step="0.5" value="4">
        </div>
        <div>
          <label>Días/mes</label>
          <input type="number" class="dias" min="1" max="31" step="1" value="20">
        </div>
      </div>`;
    const chk = div.querySelector("input[type=checkbox]");
    const det = div.querySelector(".equipo-detalle");
    chk.addEventListener("change", () => det.classList.toggle("show", chk.checked));
    cont.appendChild(div);
  });
}

/**
 * Activa el toggle de horario pico (Sí / No).
 */
export function activarTogglePico() {
  el.pico().forEach((opt) => {
    opt.addEventListener("click", () => {
      el.pico().forEach((o) => o.classList.remove("active"));
      opt.classList.add("active");
      usoPico = opt.dataset.val === "true";
    });
  });
}

/**
 * Impide teclear punto o coma en el campo de cantidad de equipos,
 * para que solo se puedan ingresar números enteros.
 */
export function bloquearDecimalesCantidad() {
  const input = el.cantidad();
  input.addEventListener("keydown", (e) => {
    if (e.key === "." || e.key === ",") {
      e.preventDefault();
    }
  });
}

/**
 * Lee el formulario y devuelve el cuerpo listo para el backend (AnalisisRequest).
 * Lanza Error con mensaje claro si algún dato es inválido.
 */
export function leerFormulario() {
  const consumo = parseFloat(el.consumo().value);
  const cantidadRaw = el.cantidad().value;       // valor crudo, para detectar decimales
  const cantidad = parseInt(cantidadRaw, 10);
  const tipo = el.tipo().value;

  if (!consumo || consumo <= 0) throw new Error("Ingresa un consumo válido (mayor que cero).");
  if (consumo > 2000) throw new Error("El consumo mensual parece demasiado alto. Verifica el valor (un hogar típico usa entre 100 y 500 kWh; el máximo aceptado es 2000).");
  if (!cantidad || cantidad < 1) throw new Error("La cantidad de equipos debe ser al menos 1.");
  if (cantidad > 50) throw new Error("La cantidad de equipos no puede superar 50.");
  if (cantidadRaw.includes(".") || cantidadRaw.includes(",")) throw new Error("La cantidad de equipos debe ser un número entero (sin decimales).");

  const equiposAltoConsumo = [];
  document.querySelectorAll(".equipo").forEach((div) => {
    const chk = div.querySelector("input[type=checkbox]");
    if (chk.checked) {
      equiposAltoConsumo.push({
        codigoEquipo: chk.dataset.codigo,
        horasUsoDia: parseFloat(div.querySelector(".horas").value),
        diasUsoMes: parseInt(div.querySelector(".dias").value, 10),
      });
    }
  });

  // horasAltoConsumo NO se incluye: el backend lo calcula desde los equipos.
  return {
    consumoKwh: consumo,
    usoHorarioPico: usoPico,
    cantidadEquipos: cantidad,
    tipoInmueble: tipo,
    equiposAltoConsumo,
  };
}

/**
 * Muestra solo una de las tres vistas dentro del modal.
 */
function mostrarVista(cual) {
  el.viewLoading().hidden = cual !== "loading";
  el.viewResult().hidden  = cual !== "result";
  el.viewError().hidden   = cual !== "error";
}

/** Abre el modal. */
function abrirModal() {
  el.modal().hidden = false;
  document.body.style.overflow = "hidden"; // evita scroll de fondo
}

/** Cierra el modal. */
export function cerrarModal() {
  el.modal().hidden = true;
  document.body.style.overflow = "";
}

/**
 * Pinta el resultado (AnalisisResponse) dentro del modal.
 */
export function mostrarResultado(data, titulo = "Tu resultado", mostrarCodigo = true) {
  const tagEl = document.getElementById("resultTag");
  if (tagEl) tagEl.textContent = titulo;

  const cat = (data.categoria || "").toString();
  const catEl = document.getElementById("r-cat");
  catEl.textContent = cat || "—";
  catEl.className = "cat " + cat.toLowerCase();

  const prob = data.probabilidad != null ? Math.round(parseFloat(data.probabilidad) * 100) : null;
  document.getElementById("r-prob").textContent = prob != null ? `${prob}% de confianza` : "";

  const costo = data.costoEstimadoMensual;
  const moneda = data.moneda || "BRL";
  document.getElementById("r-costo").textContent =
    costo != null ? `${parseFloat(costo).toFixed(2)} ${moneda}` : "—";

  let fecha = "—";
  if (data.fechaAnalisis) {
    try {
      fecha = new Date(data.fechaAnalisis).toLocaleDateString("es-MX",
        { day: "2-digit", month: "short", year: "numeric" });
    } catch (_) {}
  }
  document.getElementById("r-fecha").textContent = fecha;

  const ul = document.getElementById("r-recos");
  ul.innerHTML = "";
  (data.recomendaciones || []).forEach((r) => {
    const li = document.createElement("li");
    li.textContent = r;
    ul.appendChild(li);
  });

  // El código (id) solo se muestra al ANALIZAR (para guardarlo).
  // Al CONSULTAR, el usuario ya tiene el código, así que se oculta.
  const idBox = document.getElementById("idBox");
  if (idBox) idBox.hidden = !mostrarCodigo;
  if (mostrarCodigo) {
    const idEl = document.getElementById("r-id");
    if (idEl) idEl.textContent = data.id || "—";
  }

  mostrarVista("result");
}

/**
 * Muestra un mensaje de error dentro del modal.
 */
export function mostrarError(msg) {
  document.getElementById("errorMsg").textContent = msg;
  abrirModal();
  mostrarVista("error");
}

/**
 * Controla el estado de carga: abre el modal con el spinner.
 * @param {boolean} cargando
 * @param {Object} [opciones] - textos personalizados del spinner:
 *   { titulo, subtitulo }. Si no se pasan, usa los de "analizar".
 */
export function setCargando(cargando, opciones = {}) {
  if (cargando) {
    const titulo = opciones.titulo || "Analizando tu consumo…";
    const subtitulo = opciones.subtitulo || "Nuestro modelo está evaluando tu perfil energético.";
    const tEl = document.getElementById("loadingText");
    const sEl = document.getElementById("loadingSub");
    if (tEl) tEl.textContent = titulo;
    if (sEl) sEl.textContent = subtitulo;
    abrirModal();
    mostrarVista("loading");
  }
}

/**
 * Conecta los botones de cierre del modal (X, "Entendido", "Cerrar",
 * y clic en el fondo oscuro).
 */
export function activarModal() {
  document.getElementById("modalClose").addEventListener("click", cerrarModal);
  document.getElementById("modalDone").addEventListener("click", cerrarModal);
  document.getElementById("errorClose").addEventListener("click", cerrarModal);
  // Clic en el fondo oscuro (fuera del recuadro) cierra el modal.
  el.modal().addEventListener("click", (e) => {
    if (e.target === el.modal()) cerrarModal();
  });
  // Tecla Escape cierra el modal.
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !el.modal().hidden) cerrarModal();
  });

  // Botón "Copiar" el código del análisis.
  const btnCopiar = document.getElementById("copiarId");
  if (btnCopiar) {
    btnCopiar.addEventListener("click", async () => {
      const id = document.getElementById("r-id").textContent.trim();
      if (!id || id === "—") return;
      try {
        await navigator.clipboard.writeText(id);
      } catch (_) {
        // Respaldo si el navegador bloquea el portapapeles.
        const tmp = document.createElement("textarea");
        tmp.value = id;
        document.body.appendChild(tmp);
        tmp.select();
        document.execCommand("copy");
        document.body.removeChild(tmp);
      }
      btnCopiar.textContent = "Copiado ✓";
      btnCopiar.classList.add("copiado");
      setTimeout(() => {
        btnCopiar.textContent = "Copiar";
        btnCopiar.classList.remove("copiado");
      }, 1800);
    });
  }
}

// Exponer el botón para que main.js le enganche el evento.
export function onAnalizar(handler) {
  el.btn().addEventListener("click", handler);
}
