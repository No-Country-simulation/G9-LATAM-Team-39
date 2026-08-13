package com.energiai.energy_analysis_api.service;

import com.energiai.energy_analysis_api.client.InferenceClient;
import com.energiai.energy_analysis_api.dto.request.AnalisisRequest;
import com.energiai.energy_analysis_api.dto.response.AnalisisResponse;
import com.energiai.energy_analysis_api.dto.response.PredictionResponse;
import com.energiai.energy_analysis_api.entity.AnalisisEnergetico;
import com.energiai.energy_analysis_api.exception.AnalisisNotFoundException;
import com.energiai.energy_analysis_api.repository.AnalisisEnergeticoRepository;

import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;
import java.util.UUID;

@Service
public class AnalisisServiceImpl implements AnalisisService {

    private final AnalisisEnergeticoRepository analisisEnergeticoRepository;
    private final InferenceClient inferenceClient;

    public AnalisisServiceImpl(
            AnalisisEnergeticoRepository analisisEnergeticoRepository,
            InferenceClient inferenceClient) {

        this.analisisEnergeticoRepository = analisisEnergeticoRepository;
        this.inferenceClient = inferenceClient;
    }

    @Override
    public AnalisisResponse registrarAnalisis(AnalisisRequest request) {

        /*
         * 1. Creamos la entidad que se guardará en PostgreSQL.
         */
        AnalisisEnergetico analisis = new AnalisisEnergetico();

        /*
         * 2. Copiamos las variables recibidas.
         */
        analisis.setConsumoKwh(request.getConsumoKwh());
        analisis.setUsoHorarioPico(request.getUsoHorarioPico());
        analisis.setCantidadEquipos(request.getCantidadEquipos());
        analisis.setTipoInmueble(request.getTipoInmueble());

        if (request.getHorasAltoConsumo() != null) {
            analisis.setHorasAltoConsumo(
                    BigDecimal.valueOf(request.getHorasAltoConsumo())
            );
        }

        /*
         * 3. Llamamos al servicio Python.
         *
         * Python ejecuta el modelo de Machine Learning
         * y devuelve categoría + probabilidad.
         */
        PredictionResponse prediction =
                inferenceClient.predecir(request);

        /*
         * 4. Guardamos el resultado del modelo.
         */
        analisis.setCategoria(prediction.getCategoria());
        analisis.setProbabilidad(prediction.getProbabilidad());

        /*
         * 5. Tarifa de referencia del proyecto.
         */
        BigDecimal tarifa = new BigDecimal("0.75");

        analisis.setTarifaReferenciaKwh(tarifa);

        /*
         * 6. Calculamos el costo mensual:
         *
         * consumo kWh × tarifa
         */
        BigDecimal costo =
                request.getConsumoKwh()
                        .multiply(tarifa)
                        .setScale(2, RoundingMode.HALF_UP);

        analisis.setCostoEstimadoMensual(costo);

        /*
         * 7. Moneda del proyecto.
         */
        analisis.setMoneda("BRL");

        /*
         * 8. Versión inicial del modelo.
         */
        analisis.setVersionModelo("1.0.0");

        /*
         * 9. Guardamos el análisis completo.
         */
        AnalisisEnergetico analisisGuardado =
                analisisEnergeticoRepository.save(analisis);

        /*
         * 10. Convertimos a DTO de respuesta.
         */
        return convertirAResponse(analisisGuardado);
    }

    @Override
    public List<AnalisisResponse> obtenerTodosLosAnalisis() {

        return analisisEnergeticoRepository.findAll()
                .stream()
                .map(this::convertirAResponse)
                .toList();
    }

    @Override
    public AnalisisResponse obtenerAnalisisPorId(UUID id) {

        AnalisisEnergetico analisis =
                analisisEnergeticoRepository.findById(id)
                        .orElseThrow(() ->
                                new AnalisisNotFoundException(
                                        "No se encontró el análisis con ID: " + id
                                )
                        );

        return convertirAResponse(analisis);
    }

    private AnalisisResponse convertirAResponse(
            AnalisisEnergetico analisis) {

        AnalisisResponse response = new AnalisisResponse();

        response.setId(analisis.getId());
        response.setCategoria(analisis.getCategoria());
        response.setProbabilidad(analisis.getProbabilidad());
        response.setCostoEstimadoMensual(
                analisis.getCostoEstimadoMensual()
        );
        response.setMoneda(analisis.getMoneda());
        response.setFechaAnalisis(analisis.getFechaAnalisis());

        /*
         * Las recomendaciones las implementaremos después.
         */
        response.setRecomendaciones(null);

        return response;
    }
}