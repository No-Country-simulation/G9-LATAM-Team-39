/**
 * Configuración central del frontend.
 *
 * Cambiar BASE_URL según el entorno:
 *   - Local:      http://localhost:8080
 *   - Producción: la URL del backend en Render
 *
 * Mantener la config en un solo lugar evita tener URLs regadas por el código.
 */
export const CONFIG = {
  // URL base del backend Java. NO incluye la ruta del endpoint.
  BASE_URL: "http://localhost:8080",

  // Rutas de la API (relativas a BASE_URL).
  // Nota: el requisito oficial usa "/analise-energetica" (portugués); el equipo
  // decidió mantenerlo en español por coherencia con el resto del proyecto.
  ENDPOINTS: {
    analisis: "/analisis-energetico",
  },
};

/**
 * Catálogo de equipos de alto consumo.
 * Los códigos deben coincidir EXACTAMENTE con el enum EquipoAltoConsumo
 * del backend (catalog/EquipoAltoConsumo.java). Si el backend agrega o
 * cambia un equipo, actualizar aquí.
 */
export const CATALOGO_EQUIPOS = [
  { codigo: "AIRE_ACONDICIONADO",   nombre: "Aire acondicionado" },
  { codigo: "CALENTADOR_ELECTRICO", nombre: "Calentador eléctrico" },
  { codigo: "HORNO_ELECTRICO",      nombre: "Horno eléctrico" },
  { codigo: "SECADORA_ROPA",        nombre: "Secadora de ropa" },
  { codigo: "PARRILLA_ELECTRICA",   nombre: "Parrilla eléctrica" },
  { codigo: "LAVAVAJILLAS",         nombre: "Lavavajillas" },
  { codigo: "BOMBA_AGUA",           nombre: "Bomba de agua" },
  { codigo: "CALEFACTOR_ELECTRICO", nombre: "Calefactor eléctrico" },
];
