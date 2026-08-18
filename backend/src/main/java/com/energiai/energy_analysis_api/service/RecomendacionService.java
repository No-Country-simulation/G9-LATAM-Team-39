package com.energiai.energy_analysis_api.service;

import com.energiai.energy_analysis_api.entity.AnalisisEnergetico;
import com.energiai.energy_analysis_api.entity.Recomendacion;
import org.springframework.stereotype.Service;

import java.util.Locale;

@Service
public class RecomendacionService {

    public void generarRecomendaciones(AnalisisEnergetico analisis) {

        if (analisis == null) {
            throw new IllegalArgumentException(
                    "El análisis energético no puede ser nulo"
            );
        }

        if (analisis.getCategoria() == null
                || analisis.getCategoria().isBlank()) {

            throw new IllegalArgumentException(
                    "La categoría del análisis no puede estar vacía"
            );
        }

        String categoria = analisis.getCategoria()
                .trim()
                .toUpperCase(Locale.ROOT);

        switch (categoria) {

            case "EFICIENTE":
                generarEficiente(analisis);
                break;

            case "MODERADO":
                generarModerado(analisis);
                break;

            case "INEFICIENTE":
                generarIneficiente(analisis);
                break;

            default:
                agregar(
                        analisis,
                        "Continúa monitoreando tu consumo energético para identificar oportunidades de ahorro.",
                        "MEDIA",
                        1
                );
                break;
        }
    }

    private void generarEficiente(AnalisisEnergetico analisis) {

        agregar(
                analisis,
                "Mantén tus hábitos actuales de consumo energético.",
                "BAJA",
                1
        );

        agregar(
                analisis,
                "Continúa monitoreando periódicamente tu consumo de energía.",
                "BAJA",
                2
        );

        agregar(
                analisis,
                "Aprovecha la iluminación y ventilación natural siempre que sea posible.",
                "BAJA",
                3
        );
    }

    private void generarModerado(AnalisisEnergetico analisis) {

        agregar(
                analisis,
                "Reduce el uso de equipos eléctricos durante los horarios de mayor consumo.",
                "MEDIA",
                1
        );

        agregar(
                analisis,
                "Desconecta los dispositivos que no estén siendo utilizados.",
                "MEDIA",
                2
        );

        agregar(
                analisis,
                "Revisa las horas de uso de los equipos con mayor consumo energético.",
                "MEDIA",
                3
        );

        agregar(
                analisis,
                "Considera sustituir equipos antiguos por alternativas de mayor eficiencia energética.",
                "MEDIA",
                4
        );
    }

    private void generarIneficiente(AnalisisEnergetico analisis) {

        agregar(
                analisis,
                "Reduce las horas de funcionamiento de los equipos de alto consumo.",
                "ALTA",
                1
        );

        agregar(
                analisis,
                "Evita utilizar varios equipos de alto consumo al mismo tiempo.",
                "ALTA",
                2
        );

        agregar(
                analisis,
                "Identifica los aparatos que generan el mayor consumo energético en la vivienda.",
                "ALTA",
                3
        );

        agregar(
                analisis,
                "Prioriza el uso de equipos con mayor eficiencia energética.",
                "ALTA",
                4
        );

        agregar(
                analisis,
                "Realiza un seguimiento frecuente de tu consumo para comprobar si las medidas de ahorro están funcionando.",
                "MEDIA",
                5
        );
    }

    private void agregar(
            AnalisisEnergetico analisis,
            String descripcion,
            String prioridad,
            int orden
    ) {

        Recomendacion recomendacion =
                Recomendacion.builder()
                        .descripcion(descripcion)
                        .prioridad(prioridad)
                        .orden(orden)
                        .build();

        analisis.agregarRecomendacion(recomendacion);
    }
}