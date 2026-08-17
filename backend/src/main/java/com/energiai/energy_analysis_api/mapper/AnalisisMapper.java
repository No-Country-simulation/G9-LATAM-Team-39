package com.energiai.energy_analysis_api.mapper;

import com.energiai.energy_analysis_api.dto.request.AnalisisRequest;
import com.energiai.energy_analysis_api.dto.response.AnalisisResponse;
import com.energiai.energy_analysis_api.entity.AnalisisEnergetico;
import com.energiai.energy_analysis_api.entity.Recomendacion;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.List;

@Component
public class AnalisisMapper {

    /**
     * Convierte los datos recibidos desde el frontend
     * en una entidad lista para ser guardada.
     */
    public AnalisisEnergetico toEntity(AnalisisRequest request) {
        if (request == null) {
            throw new IllegalArgumentException(
                    "La solicitud de análisis no puede ser nula"
            );
        }

        return AnalisisEnergetico.builder()
                .consumoKwh(request.getConsumoKwh())
                .usoHorarioPico(request.getUsoHorarioPico())
                .cantidadEquipos(request.getCantidadEquipos())
                .tipoInmueble(request.getTipoInmueble())
                .horasAltoConsumo(request.getHorasAltoConsumo())
                .categoria("PENDIENTE")
                .probabilidad(BigDecimal.ZERO)
                .costoEstimadoMensual(BigDecimal.ZERO)
                .tarifaReferenciaKwh(BigDecimal.ZERO)
                .moneda("MXN")
                .versionModelo(null)
                .build();
    }

    /**
     * Convierte una entidad almacenada en PostgreSQL
     * en el DTO que será enviado al frontend.
     */
    public AnalisisResponse toResponse(AnalisisEnergetico entity) {
        if (entity == null) {
            throw new IllegalArgumentException(
                    "El análisis energético no puede ser nulo"
            );
        }

        List<String> recomendaciones = entity.getRecomendaciones() == null
                ? List.of()
                : entity.getRecomendaciones()
                  .stream()
                  .map(this::obtenerTextoRecomendacion)
                  .toList();

        return new AnalisisResponse(
                entity.getId(),
                entity.getCategoria(),
                entity.getProbabilidad(),
                entity.getCostoEstimadoMensual(),
                entity.getMoneda(),
                entity.getFechaAnalisis(),
                recomendaciones
        );
    }

    /**
     * Actualiza únicamente los datos que provienen
     * de AnalisisRequest.
     */
    public void updateEntity(
            AnalisisEnergetico entity,
            AnalisisRequest request
    ) {
        if (entity == null) {
            throw new IllegalArgumentException(
                    "El análisis energético no puede ser nulo"
            );
        }

        if (request == null) {
            throw new IllegalArgumentException(
                    "La solicitud de análisis no puede ser nula"
            );
        }

        entity.setConsumoKwh(request.getConsumoKwh());
        entity.setUsoHorarioPico(request.getUsoHorarioPico());
        entity.setCantidadEquipos(request.getCantidadEquipos());
        entity.setTipoInmueble(request.getTipoInmueble());
        entity.setHorasAltoConsumo(request.getHorasAltoConsumo());
    }

    private String obtenerTextoRecomendacion(
            Recomendacion recomendacion
    ) {
        if (recomendacion == null) {
            return "";
        }

        return recomendacion.getDescripcion();
    }
}