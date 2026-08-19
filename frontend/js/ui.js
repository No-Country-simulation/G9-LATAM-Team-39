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
  error:    () => document.getElementById("error"),
  btn:      () => document.getElementById("analizar"),
  resultado:() => document.getElementById("resultado"),
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
 * Lee el formulario y devuelve el cuerpo listo para el backend (AnalisisRequest).
 * Lanza Error con mensaje claro si algún dato es inválido.
 */
export function leerFormulario() {
  const consumo = parseFloat(el.consumo().value);
  const cantidad = parseInt(el.cantidad().value, 10);
  const tipo = el.tipo().value;

  if (!consumo || consumo <= 0) throw new Error("Ingresa un consumo válido (mayor que cero).");
  if (consumo > 2000) throw new Error("El consumo mensual parece demasiado alto. Verifica el valor (un hogar típico usa entre 100 y 500 kWh; el máximo aceptado es 2000).");
  if (!cantidad || cantidad < 1) throw new Error("La cantidad de equipos debe ser al menos 1.");

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
 * Pinta el resultado (AnalisisResponse) en la tarjeta de resultado.
 */
export function mostrarResultado(data) {
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

  const res = el.resultado();
  res.classList.add("show");
  res.scrollIntoView({ behavior: "smooth", block: "start" });
}

// --- Estado del botón y errores ---
export function mostrarError(msg) {
  const box = el.error();
  box.textContent = msg;
  box.classList.add("show");
}
export function limpiarError() {
  el.error().classList.remove("show");
}
export function setCargando(cargando) {
  const b = el.btn();
  b.disabled = cargando;
  b.textContent = cargando ? "Analizando…" : "Analizar mi consumo";
}

// Exponer el botón para que main.js le enganche el evento.
export function onAnalizar(handler) {
  el.btn().addEventListener("click", handler);
}
