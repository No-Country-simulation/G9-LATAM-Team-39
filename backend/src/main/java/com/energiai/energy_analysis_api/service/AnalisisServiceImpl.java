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
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;


@Service
public class AnalisisServiceImpl implements AnalisisService {

    private final AnalisisEnergeticoRepository analisisEnergeticoRepository;
    private final InferenceClient inferenceClient;


    public AnalisisServiceImpl(
            AnalisisEnergeticoRepository analisisEnergeticoRepository,
            InferenceClient inferenceClient) {

        this.analisisEnergeticoRepository =
                analisisEnergeticoRepository;

        this.inferenceClient =
                inferenceClient;
    }


    @Override
    public AnalisisResponse registrarAnalisis(
            AnalisisRequest request) {

        /*
         * Creamos la entidad que posteriormente
         * se guardará en PostgreSQL.
         */
        AnalisisEnergetico analisis =
                new AnalisisEnergetico();


        /*
         * Copiamos los datos recibidos.
         */
        analisis.setConsumoKwh(
                request.getConsumoKwh()
        );

        analisis.setUsoHorarioPico(
                request.getUsoHorarioPico()
        );

        analisis.setCantidadEquipos(
                request.getCantidadEquipos()
        );

        analisis.setTipoInmueble(
                request.getTipoInmueble()
        );


        if (request.getHorasAltoConsumo() != null) {

            analisis.setHorasAltoConsumo(
                    BigDecimal.valueOf(
                            request.getHorasAltoConsumo()
                    )
            );
        }


        /*
         * Java llama al servicio Python.
         *
         * Python ejecuta el modelo ML y devuelve:
         *
         * categoria
         * probabilidad
         */
        PredictionResponse prediction =
                inferenceClient.predecir(request);


        /*
         * Guardamos los resultados generados
         * por el modelo.
         */
        analisis.setCategoria(
                prediction.getCategoria()
        );

        analisis.setProbabilidad(
                prediction.getProbabilidad()
        );


        /*
         * Tarifa de referencia:
         * R$ 0.75 por kWh.
         */
        BigDecimal tarifa =
                new BigDecimal("0.75");

        analisis.setTarifaReferenciaKwh(
                tarifa
        );


        /*
         * Costo mensual:
         *
         * consumo × tarifa
         */
        BigDecimal costo =
                request.getConsumoKwh()
                        .multiply(tarifa)
                        .setScale(
                                2,
                                RoundingMode.HALF_UP
                        );

        analisis.setCostoEstimadoMensual(
                costo
        );


        /*
         * Moneda utilizada.
         */
        analisis.setMoneda(
                "BRL"
        );


        /*
         * Versión inicial del modelo.
         */
        analisis.setVersionModelo(
                "1.0.0"
        );


        /*
         * Guardamos todo el análisis
         * en PostgreSQL.
         */
        AnalisisEnergetico analisisGuardado =
                analisisEnergeticoRepository.save(
                        analisis
                );


        /*
         * Convertimos a DTO de respuesta.
         */
        return convertirAResponse(
                analisisGuardado
        );
    }


    @Override
    public List<AnalisisResponse>
    obtenerTodosLosAnalisis() {

        return analisisEnergeticoRepository
                .findAll()
                .stream()
                .map(this::convertirAResponse)
                .toList();
    }


    @Override
    public AnalisisResponse obtenerAnalisisPorId(
            UUID id) {

        AnalisisEnergetico analisis =
                analisisEnergeticoRepository
                        .findById(id)
                        .orElseThrow(() ->
                                new AnalisisNotFoundException(
                                        "No se encontró el análisis con ID: "
                                                + id
                                )
                        );

        return convertirAResponse(
                analisis
        );
    }


    /*
     * Genera recomendaciones utilizando
     * reglas simples sobre los datos
     * del consumo energético.
     */
    private List<String> generarRecomendaciones(
            AnalisisEnergetico analisis) {

        List<String> recomendaciones =
                new ArrayList<>();


        /*
         * REGLA 1:
         * Uso durante horario pico.
         */
        if (Boolean.TRUE.equals(
                analisis.getUsoHorarioPico())) {

            recomendaciones.add(
                    "Reducir el uso de equipos durante horarios pico"
            );
        }


        /*
         * REGLA 2:
         * Cantidad elevada de equipos.
         */
        if (analisis.getCantidadEquipos() != null
                && analisis.getCantidadEquipos() >= 10) {

            recomendaciones.add(
                    "Evaluar aparatos con alto consumo energético"
            );
        }


        /*
         * REGLA 3:
         * Muchas horas de alto consumo.
         */
        if (analisis.getHorasAltoConsumo() != null
                && analisis.getHorasAltoConsumo()
                .compareTo(
                        BigDecimal.valueOf(8)
                ) >= 0) {

            recomendaciones.add(
                    "Distribuir actividades de mayor consumo a lo largo del día"
            );
        }


        /*
         * Si el perfil no activa ninguna regla,
         * enviamos una recomendación general.
         */
        if (recomendaciones.isEmpty()) {

            recomendaciones.add(
                    "Mantener hábitos de consumo eficientes y monitorear periódicamente el uso de energía"
            );
        }


        return recomendaciones;
    }


    /*
     * Convierte la entidad de PostgreSQL
     * a la respuesta JSON de nuestra API.
     */
    private AnalisisResponse convertirAResponse(
            AnalisisEnergetico analisis) {

        AnalisisResponse response =
                new AnalisisResponse();


        response.setId(
                analisis.getId()
        );

        response.setCategoria(
                analisis.getCategoria()
        );

        response.setProbabilidad(
                analisis.getProbabilidad()
        );

        response.setCostoEstimadoMensual(
                analisis.getCostoEstimadoMensual()
        );

        response.setMoneda(
                analisis.getMoneda()
        );

        response.setFechaAnalisis(
                analisis.getFechaAnalisis()
        );


        /*
         * Aquí ya no devolvemos null.
         */
        response.setRecomendaciones(
                generarRecomendaciones(analisis)
        );


        return response;
    }
}