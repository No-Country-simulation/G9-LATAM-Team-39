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
    AnalisisResponse crearAnalisis(AnalisisRequest request);

    /**
     * Obtiene todos los análisis energéticos registrados.
     *
     * @return lista de análisis
     */
    List<AnalisisResponse> obtenerTodos();

    /**
     * Obtiene un análisis energético por su identificador UUID.
     *
     * @param id identificador UUID del análisis
     * @return análisis encontrado
     */
    AnalisisResponse obtenerPorId(UUID id);

    /**
     * Actualiza los datos de entrada de un análisis existente.
     *
     * @param id identificador UUID del análisis
     * @param request nuevos datos del análisis
     * @return análisis actualizado
     */
    AnalisisResponse actualizar(UUID id, AnalisisRequest request);

    /**
     * Elimina un análisis energético.
     *
     * @param id identificador UUID del análisis
     */
    void eliminar(UUID id);
}