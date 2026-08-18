/**
 * Capa de API — toda la comunicación con el backend vive aquí.
 *
 * El resto del frontend NO usa fetch directamente: llama a estas funciones.
 * Así, si cambia la forma de comunicarse con el backend (headers, auth,
 * manejo de errores), se cambia en un solo lugar.
 */
import { CONFIG } from "./config.js";

/**
 * Error de API con información útil para la UI.
 */
export class ApiError extends Error {
  constructor(message, status = null, detalle = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detalle = detalle;
  }
}

/**
 * Envía un análisis energético al backend y devuelve el resultado.
 *
 * @param {Object} datos - cuerpo que espera el backend (AnalisisRequest):
 *   { consumoKwh, usoHorarioPico, cantidadEquipos, tipoInmueble, equiposAltoConsumo }
 *   NOTA: horasAltoConsumo NO se envía; lo calcula el backend.
 * @returns {Promise<Object>} el AnalisisResponse del backend.
 * @throws {ApiError} si la petición falla o el backend responde con error.
 */
export async function crearAnalisis(datos) {
  const url = CONFIG.BASE_URL + CONFIG.ENDPOINTS.analisis;

  let respuesta;
  try {
    respuesta = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });
  } catch (err) {
    // Falla de red: backend apagado, CORS, sin conexión.
    throw new ApiError(
      `No se pudo conectar con el backend (${url}). ` +
      `Verifica que esté corriendo y que CORS esté habilitado.`,
      null,
      err.message
    );
  }

  if (!respuesta.ok) {
    // El backend respondió, pero con un código de error (4xx / 5xx).
    let detalle = null;
    try { detalle = await respuesta.text(); } catch (_) {}
    throw new ApiError(
      `El servidor respondió con estado ${respuesta.status}.`,
      respuesta.status,
      detalle
    );
  }

  return respuesta.json();
}

/**
 * Recupera un análisis previo por su ID (GET /api/analisis/{id}).
 * Disponible para una futura pantalla de historial.
 *
 * @param {string} id - UUID del análisis.
 * @returns {Promise<Object>} el AnalisisResponse.
 */
export async function obtenerAnalisis(id) {
  const url = `${CONFIG.BASE_URL}${CONFIG.ENDPOINTS.analisis}/${id}`;

  let respuesta;
  try {
    respuesta = await fetch(url);
  } catch (err) {
    throw new ApiError(`No se pudo conectar con el backend (${url}).`, null, err.message);
  }

  if (!respuesta.ok) {
    throw new ApiError(`El servidor respondió con estado ${respuesta.status}.`, respuesta.status);
  }
  return respuesta.json();
}
