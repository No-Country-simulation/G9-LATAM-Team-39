package com.energiai.energy_analysis_api.client;

import com.energiai.energy_analysis_api.dto.request.AnalisisRequest;
import com.energiai.energy_analysis_api.dto.response.PredictionResponse;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.LinkedHashMap;
import java.util.Map;

@Component
public class InferenceClient {

    private final RestClient restClient;

    public InferenceClient(
            @Value("${inference.service.url}") String inferenceServiceUrl) {

        this.restClient = RestClient.builder()
                .baseUrl(inferenceServiceUrl)
                .build();
    }

    public PredictionResponse predecir(AnalisisRequest request) {

        /*
         * Python espera nombres snake_case:
         *
         * consumo_kwh
         * uso_horario_pico
         * cantidad_equipos
         * tipo_inmueble
         * horas_alto_consumo
         *
         * Java usa camelCase, por eso construimos
         * explícitamente el JSON que espera FastAPI.
         */
        Map<String, Object> body = new LinkedHashMap<>();

        body.put(
                "consumo_kwh",
                request.getConsumoKwh()
        );

        body.put(
                "uso_horario_pico",
                request.getUsoHorarioPico()
        );

        body.put(
                "cantidad_equipos",
                request.getCantidadEquipos()
        );

        body.put(
                "tipo_inmueble",
                request.getTipoInmueble()
        );

        body.put(
                "horas_alto_consumo",
                request.getHorasAltoConsumo()
        );

        PredictionResponse response = restClient
                .post()
                .uri("/predict")
                .contentType(MediaType.APPLICATION_JSON)
                .body(body)
                .retrieve()
                .body(PredictionResponse.class);

        if (response == null) {
            throw new IllegalStateException(
                    "El inference-service no devolvió una predicción."
            );
        }

        return response;
    }
}
