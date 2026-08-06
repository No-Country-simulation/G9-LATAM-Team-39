package com.energiai.energy_analysis_api.service;

import com.energiai.energy_analysis_api.dto.request.AnalisisRequest;
import com.energiai.energy_analysis_api.dto.response.AnalisisResponse;

import java.util.List;
import java.util.UUID;

/**
 * Define las operaciones disponibles para administrar
 * los análisis energéticos.
 *
 * Esta interfaz permite desacoplar al controlador de la
 * implementación concreta del servicio.
 */
public interface AnalisisService {

    /**
     * Registra un nuevo análisis energético.
     *
     * @param request datos recibidos para crear el análisis
     * @return información del análisis registrado
     */
    AnalisisResponse registrarAnalisis(AnalisisRequest request);

    /**
     * Obtiene todos los análisis energéticos registrados.
     *
     * @return lista de análisis convertidos a DTOs
     */
    List<AnalisisResponse> obtenerTodosLosAnalisis();

    /**
     * Busca un análisis energético por su identificador.
     *
     * En este proyecto el ID de AnalisisEnergetico es UUID,
     * por eso el parámetro debe ser UUID y no Long.
     *
     * @param id identificador del análisis
     * @return análisis encontrado convertido a DTO
     */
    AnalisisResponse obtenerAnalisisPorId(UUID id);
}