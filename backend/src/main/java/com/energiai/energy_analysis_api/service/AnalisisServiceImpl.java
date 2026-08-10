package com.energiai.energy_analysis_api.service;

import com.energiai.energy_analysis_api.dto.request.AnalisisRequest;
import com.energiai.energy_analysis_api.dto.response.AnalisisResponse;
import com.energiai.energy_analysis_api.entity.AnalisisEnergetico;
import com.energiai.energy_analysis_api.repository.AnalisisEnergeticoRepository;

import org.springframework.stereotype.Service;
import com.energiai.energy_analysis_api.exception.AnalisisNotFoundException;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;


@Service
public class AnalisisServiceImpl implements AnalisisService {

    private final AnalisisEnergeticoRepository analisisEnergeticoRepository;


    /**
     * Constructor utilizado para inyectar AnalisisEnergeticoRepository.
     */
    public AnalisisServiceImpl(
            AnalisisEnergeticoRepository analisisEnergeticoRepository) {

        this.analisisEnergeticoRepository = analisisEnergeticoRepository;
    }


    @Override
    public AnalisisResponse registrarAnalisis(AnalisisRequest request) {

        /*
         * Creamos la entidad que será utilizada por JPA
         * para almacenar la información.
         */
        AnalisisEnergetico analisis = new AnalisisEnergetico();

        /*
         * Copiamos los datos que existen tanto en
         * AnalisisRequest como en AnalisisEnergetico.
         *
         * AnalisisRequest actualmente contiene:
         * - consumoKwh
         * - usoHorarioPico
         * - cantidadEquipos
         * - tipoInmueble
         * - horasAltoConsumo
         */
        analisis.setConsumoKwh(request.getConsumoKwh());
        analisis.setUsoHorarioPico(request.getUsoHorarioPico());
        analisis.setCantidadEquipos(request.getCantidadEquipos());
        analisis.setTipoInmueble(request.getTipoInmueble());

        /*
         * AnalisisRequest tiene horasAltoConsumo como Integer,
         * mientras que la entidad AnalisisEnergetico lo tiene
         * como BigDecimal.
         * Por eso debemos realizar la conversión.
         */
        if (request.getHorasAltoConsumo() != null) {

            analisis.setHorasAltoConsumo(
                    java.math.BigDecimal.valueOf(
                            request.getHorasAltoConsumo()
                    )
            );
        }

        /*
         * Guardamos la entidad utilizando el repositorio.
         *
         * El servicio es quien utiliza el repositorio.
         * El Controller NO accede directamente a él.
         */
        AnalisisEnergetico analisisGuardado =
                analisisEnergeticoRepository.save(analisis);

        /*
         * Después de guardar, convertimos la entidad
         * a AnalisisResponse.
         *
         * El controlador recibirá el DTO y no la entidad.
         */
        return convertirAResponse(analisisGuardado);
    }


    @Override
    public List<AnalisisResponse> obtenerTodosLosAnalisis() {

        /*
         * findAll() devuelve:
         *
         * List<AnalisisEnergetico>
         *
         * Nosotros necesitamos devolver:
         *
         * List<AnalisisResponse>
         *
         * Por eso convertimos cada entidad mediante
         * convertirAResponse().
         */
        return analisisEnergeticoRepository.findAll()
                .stream()
                .map(this::convertirAResponse)
                .toList();
    }


    /**
     * Obtiene un análisis por su ID.
     **/
    @Override

    public AnalisisResponse obtenerAnalisisPorId(UUID id) {

        /*
         * Buscamos el análisis utilizando el Repository.
         *
         * findById() devuelve Optional porque el registro
         * podría no existir.
         */
        AnalisisEnergetico analisis =
                analisisEnergeticoRepository.findById(id)
                        .orElseThrow(() ->
                                new AnalisisNotFoundException(
                                        "No se encontró el análisis con ID: " + id
                                )
                        );


        /*
         * Si existe, convertimos la entidad a DTO
         * antes de devolverla.
         */
        return convertirAResponse(analisis);
    }


    /**
     * Convierte una entidad AnalisisEnergetico
     * en un AnalisisResponse.
     *
     * Este método es privado porque solamente lo necesita
     * esta clase.
     *
     * De esta forma evitamos repetir la misma conversión
     * en registrarAnalisis(), obtenerTodosLosAnalisis()
     * y obtenerAnalisisPorId().
     */
    private AnalisisResponse convertirAResponse(
            AnalisisEnergetico analisis) {

        /*
         * Creamos el DTO que será devuelto al Controller.
         */
        AnalisisResponse response = new AnalisisResponse();

        /*
         * Copiamos los campos que AnalisisResponse
         * actualmente tiene definidos.
         */
        response.setId(analisis.getId());
        response.setCategoria(analisis.getCategoria());
        response.setProbabilidad(analisis.getProbabilidad());
        response.setCostoEstimadoMensual(
                analisis.getCostoEstimadoMensual()
        );
        response.setMoneda(analisis.getMoneda());
        response.setFechaAnalisis(analisis.getFechaAnalisis());

        /*
         * AnalisisResponse tiene:
         *
         * List<String> recomendaciones
         *
         * mientras que la entidad tiene:
         *
         * List<Recomendacion>
         *
         * Como tu requerimiento solamente pide utilizar
         * AnalisisRequest y AnalisisResponse, no agregamos
         * aquí lógica adicional para construir recomendaciones.
         *
         * Para mantener el servicio enfocado únicamente
         * en los requerimientos indicados, dejamos este
         * campo como null.
         */
        response.setRecomendaciones(null);

        return response;
    }
}