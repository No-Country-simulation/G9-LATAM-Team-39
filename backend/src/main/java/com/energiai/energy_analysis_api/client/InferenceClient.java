package com.energiai.energy_analysis_api.client;

import com.energiai.energy_analysis_api.dto.request.PredictionRequest;
import com.energiai.energy_analysis_api.dto.response.PredictionResponse;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestClientResponseException;

@Component
public class InferenceClient {

    private final RestClient restClient;

    public InferenceClient(
            @Value("${inference-service.url:http://localhost:8000}")
            String inferenceServiceUrl
    ) {

        SimpleClientHttpRequestFactory requestFactory =
                new SimpleClientHttpRequestFactory();

        requestFactory.setConnectTimeout(5000);
        requestFactory.setReadTimeout(10000);

        this.restClient = RestClient.builder()
                .requestFactory(requestFactory)
                .baseUrl(inferenceServiceUrl)
                .build();
    }

    public PredictionResponse predecir(PredictionRequest request) {

        if (request == null) {
            throw new IllegalArgumentException(
                    "La solicitud de predicción no puede ser nula"
            );
        }

        try {

            PredictionResponse response =
                    restClient.post()
                            .uri("/predict")
                            .contentType(MediaType.APPLICATION_JSON)
                            .accept(MediaType.APPLICATION_JSON)
                            .body(request)
                            .retrieve()
                            .body(PredictionResponse.class);

            if (response == null) {
                throw new IllegalStateException(
                        "El servicio de inferencia devolvió una respuesta vacía"
                );
            }

            return response;

        } catch (RestClientResponseException e) {

            System.err.println(
                    "Error del servicio de inferencia. HTTP: "
                            + e.getStatusCode()
            );

            System.err.println(
                    "Respuesta FastAPI: "
                            + e.getResponseBodyAsString()
            );

            throw new IllegalStateException(
                    "El servicio de inferencia rechazó la solicitud: "
                            + e.getResponseBodyAsString(),
                    e
            );

        } catch (RestClientException e) {

            throw new IllegalStateException(
                    "No fue posible comunicarse con el servicio de inferencia",
                    e
            );
        }
    }
}