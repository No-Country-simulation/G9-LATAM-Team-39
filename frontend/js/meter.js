/**
 * Anima el medidor del hero para simular un modelo analizando en vivo.
 * Es puramente decorativo: no toca la API ni la lógica del formulario.
 *
 * Comportamiento:
 *  - Los dígitos "corren" como una lectura de consumo en tiempo real.
 *  - El indicador recorre EFICIENTE → MODERADO → INEFICIENTE evaluando,
 *    y se "asienta" en una categoría antes de reiniciar el ciclo.
 */

const CATEGORIAS = [
  { seg: 0, kwh: [40, 150] },    // EFICIENTE  → consumo bajo
  { seg: 1, kwh: [150, 350] },   // MODERADO   → consumo medio
  { seg: 2, kwh: [350, 800] },   // INEFICIENTE→ consumo alto
];

let intervalDigitos = null;
let timeoutCiclo = null;

export function iniciarMedidor() {
  const meter = document.getElementById("meter");
  if (!meter) return;

  // Respetar "reduce motion": dejar un estado fijo, sin animar.
  const prefiereQuieto = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const dial = document.getElementById("meterDial");
  const status = document.getElementById("meterStatus");
  const segmentos = [...meter.querySelectorAll(".meter-seg")];

  if (prefiereQuieto) {
    segmentos[0].classList.add("on");
    if (dial) dial.textContent = "092";
    if (status) status.innerHTML = "Ejemplo";
    return;
  }

  let idx = 0;

  function correrDigitos(min, max, duracionMs) {
    clearInterval(intervalDigitos);
    const fin = Date.now() + duracionMs;
    intervalDigitos = setInterval(() => {
      if (!dial) return;
      if (Date.now() >= fin) {
        // Asentar en un valor final coherente con la categoría.
        const val = Math.round(min + Math.random() * (max - min));
        dial.textContent = String(val).padStart(3, "0");
        clearInterval(intervalDigitos);
      } else {
        const val = Math.round(min + Math.random() * (max - min));
        dial.textContent = String(val).padStart(3, "0");
      }
    }, 70);
  }

  function ciclo() {
    const cat = CATEGORIAS[idx];

    // Marcar el segmento activo.
    segmentos.forEach((s) => s.classList.remove("on"));
    segmentos[cat.seg].classList.add("on");

    // Correr los dígitos hacia el rango de esa categoría.
    correrDigitos(cat.kwh[0], cat.kwh[1], 1400);

    // Pasar a la siguiente categoría tras una pausa.
    idx = (idx + 1) % CATEGORIAS.length;
    timeoutCiclo = setTimeout(ciclo, 2600);
  }

  ciclo();
}

/** Detiene la animación (por si se navega fuera del hero). */
export function detenerMedidor() {
  clearInterval(intervalDigitos);
  clearTimeout(timeoutCiclo);
}
