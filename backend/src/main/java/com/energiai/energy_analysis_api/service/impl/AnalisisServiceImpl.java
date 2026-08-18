package com.energiai.energy_analysis_api.service.impl;

import com.energiai.energy_analysis_api.client.InferenceClient;
import com.energiai.energy_analysis_api.dto.request.AnalisisRequest;
import com.energiai.energy_analysis_api.dto.request.PredictionRequest;
import com.energiai.energy_analysis_api.dto.response.AnalisisResponse;
import com.energiai.energy_analysis_api.dto.response.PredictionResponse;
import com.energiai.energy_analysis_api.entity.AnalisisEnergetico;
import com.energiai.energy_analysis_api.exception.AnalisisNoEncontradoException;
import com.energiai.energy_analysis_api.mapper.AnalisisMapper;
import com.energiai.energy_analysis_api.repository.AnalisisEnergeticoRepository;
import com.energiai.energy_analysis_api.service.AnalisisService;
import com.energiai.energy_analysis_api.service.CalculadoraAltoConsumoService;
import com.energiai.energy_analysis_api.service.CalculadoraCostoService;
import com.energiai.energy_analysis_api.service.RecomendacionService;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

@Service
@Transactional
public class AnalisisServiceImpl implements AnalisisService {

    private final AnalisisEnergeticoRepository repository;
    private final AnalisisMapper mapper;
    private final CalculadoraAltoConsumoService calculadoraAltoConsumoService;
    private final InferenceClient inferenceClient;
    private final CalculadoraCostoService calculadoraCostoService;
    private final RecomendacionService recomendacionService;

    public AnalisisServiceImpl(
            AnalisisEnergeticoRepository repository,
            AnalisisMapper mapper,
            CalculadoraAltoConsumoService calculadoraAltoConsumoService,
            InferenceClient inferenceClient,
            CalculadoraCostoService calculadoraCostoService,
            RecomendacionService recomendacionService
    ) {
        this.repository = repository;
        this.mapper = mapper;
        this.calculadoraAltoConsumoService =
                calculadoraAltoConsumoService;
        this.inferenceClient = inferenceClient;
        this.calculadoraCostoService =
                calculadoraCostoService;
        this.recomendacionService =
                recomendacionService;
    }

    @Override
    public AnalisisResponse crearAnalisis(
            AnalisisRequest request
    ) {

        /*
         * 1. Calculamos automáticamente las horas
         * equivalentes de alto consumo.
         */
        calcularHorasAltoConsumo(request);

        /*
         * 2. Convertimos los datos recibidos
         * a una entidad JPA.
         */
        AnalisisEnergetico analisis =
                mapper.toEntity(request);

        /*
         * 3. Solicitamos al servicio Python
         * la clasificación del modelo.
         */
        PredictionResponse prediction =
                obtenerPrediccion(request);

        /*
         * 4. Guardamos categoría y probabilidad.
         */
        analisis.setCategoria(
                prediction.getCategoria()
        );

        analisis.setProbabilidad(
                prediction.getProbabilidad()
        );

        /*
         * 5. Calculamos el costo mensual estimado.
         */
        BigDecimal costoEstimado =
                calculadoraCostoService
                        .calcularCostoMensual(
                                request.getConsumoKwh()
                        );

        analisis.setCostoEstimadoMensual(
                costoEstimado
        );

        /*
         * Guardamos también la tarifa utilizada
         * para que el análisis pueda ser auditado
         * posteriormente.
         */
        analisis.setTarifaReferenciaKwh(
                calculadoraCostoService
                        .obtenerTarifaReferenciaKwh()
        );

        analisis.setMoneda(
                calculadoraCostoService.obtenerMoneda()
        );

        /*
         * 6. Generamos recomendaciones según
         * la categoría obtenida por el modelo.
         */
        recomendacionService
                .generarRecomendaciones(analisis);

        /*
         * 7. Guardamos el análisis.
         *
         * Como AnalisisEnergetico tiene CascadeType.ALL,
         * las recomendaciones también se almacenarán.
         */
        AnalisisEnergetico analisisGuardado =
                repository.save(analisis);

        /*
         * 8. Convertimos todo a AnalisisResponse.
         */
        return mapper.toResponse(
                analisisGuardado
        );
    }

    @Override
    @Transactional(readOnly = true)
    public List<AnalisisResponse> obtenerTodos() {

        return repository.findAll()
                .stream()
                .map(mapper::toResponse)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public AnalisisResponse obtenerPorId(UUID id) {

        AnalisisEnergetico analisis =
                buscarEntidadPorId(id);

        return mapper.toResponse(analisis);
    }

    @Override
    public AnalisisResponse actualizar(
            UUID id,
            AnalisisRequest request
    ) {

        /*
         * 1. Buscamos el registro existente.
         */
        AnalisisEnergetico analisisExistente =
                buscarEntidadPorId(id);

        /*
         * 2. Recalculamos horas de alto consumo.
         */
        calcularHorasAltoConsumo(request);

        /*
         * 3. Actualizamos las variables base.
         */
        mapper.updateEntity(
                analisisExistente,
                request
        );

        /*
         * 4. Volvemos a consultar el modelo.
         */
        PredictionResponse prediction =
                obtenerPrediccion(request);

        analisisExistente.setCategoria(
                prediction.getCategoria()
        );

        analisisExistente.setProbabilidad(
                prediction.getProbabilidad()
        );

        /*
         * 5. Recalculamos costo mensual.
         */
        BigDecimal costoEstimado =
                calculadoraCostoService
                        .calcularCostoMensual(
                                request.getConsumoKwh()
                        );

        analisisExistente.setCostoEstimadoMensual(
                costoEstimado
        );

        analisisExistente.setTarifaReferenciaKwh(
                calculadoraCostoService
                        .obtenerTarifaReferenciaKwh()
        );

        analisisExistente.setMoneda(
                calculadoraCostoService.obtenerMoneda()
        );

        /*
         * 6. Eliminamos las recomendaciones anteriores.
         *
         * La entidad utiliza orphanRemoval = true,
         * por lo que Hibernate eliminará las anteriores
         * de la base de datos.
         */
        analisisExistente
                .getRecomendaciones()
                .clear();

        /*
         * 7. Generamos las recomendaciones nuevas
         * para la clasificación actual.
         */
        recomendacionService
                .generarRecomendaciones(
                        analisisExistente
                );

        /*
         * 8. Guardamos el análisis actualizado.
         */
        AnalisisEnergetico analisisActualizado =
                repository.save(
                        analisisExistente
                );

        return mapper.toResponse(
                analisisActualizado
        );
    }

    @Override
    public void eliminar(UUID id) {

        AnalisisEnergetico analisis =
                buscarEntidadPorId(id);

        repository.delete(analisis);
    }

    /**
     * Calcula las horas equivalentes de alto consumo
     * utilizando los equipos enviados por el frontend.
     */
    private void calcularHorasAltoConsumo(
            AnalisisRequest request
    ) {

        if (request == null) {
            throw new IllegalArgumentException(
                    "La solicitud de análisis no puede ser nula"
            );
        }

        BigDecimal horasCalculadas =
                calculadoraAltoConsumoService
                        .calcularHorasAltoConsumo(
                                request.getEquiposAltoConsumo()
                        );

        request.setHorasAltoConsumo(
                horasCalculadas
        );
    }

    /**
     * Construye las cinco variables requeridas
     * por FastAPI y solicita una predicción.
     */
    private PredictionResponse obtenerPrediccion(
            AnalisisRequest request
    ) {

        PredictionRequest predictionRequest =
                new PredictionRequest(
                        request.getConsumoKwh(),
                        request.getUsoHorarioPico(),
                        request.getCantidadEquipos(),
                        request.getTipoInmueble(),
                        request.getHorasAltoConsumo()
                );

        PredictionResponse prediction =
                inferenceClient.predecir(
                        predictionRequest
                );

        if (prediction == null) {
            throw new IllegalStateException(
                    "El servicio de inferencia no devolvió una predicción"
            );
        }

        if (prediction.getCategoria() == null
                || prediction.getCategoria().isBlank()) {

            throw new IllegalStateException(
                    "El servicio de inferencia no devolvió una categoría válida"
            );
        }

        if (prediction.getProbabilidad() == null) {

            throw new IllegalStateException(
                    "El servicio de inferencia no devolvió una probabilidad válida"
            );
        }

        return prediction;
    }

    private AnalisisEnergetico buscarEntidadPorId(
            UUID id
    ) {

        if (id == null) {
            throw new IllegalArgumentException(
                    "El identificador del análisis no puede ser nulo"
            );
        }

        return repository.findById(id)
                .orElseThrow(() ->
                        new AnalisisNoEncontradoException(
                                "No se encontró el análisis energético con ID: "
                                        + id
                        )
                );
    }
}