package com.energiai.energy_analysis_api.service;

import com.energiai.energy_analysis_api.catalog.EquipoAltoConsumo;
import com.energiai.energy_analysis_api.dto.request.EquipoAltoConsumoRequest;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;

@Service
public class CalculadoraAltoConsumoService {

    private static final BigDecimal CARGA_REFERENCIA_KW =
            new BigDecimal("1.5");

    private static final BigDecimal LIMITE_HORAS_ALTO_CONSUMO =
            new BigDecimal("200.0");

    /**
     * Calcula las horas equivalentes de alto consumo:
     *
     * horasAltoConsumo =
     * kWh acumulados de equipos de alto consumo / 1.5
     */
    public BigDecimal calcularHorasAltoConsumo(
            List<EquipoAltoConsumoRequest> equipos
    ) {

        if (equipos == null || equipos.isEmpty()) {
            return BigDecimal.ZERO;
        }

        BigDecimal totalKwh = BigDecimal.ZERO;

        for (EquipoAltoConsumoRequest equipoRequest : equipos) {

            if (equipoRequest == null) {
                continue;
            }

            EquipoAltoConsumo equipo =
                    EquipoAltoConsumo.buscarPorCodigo(
                            equipoRequest.getCodigoEquipo()
                    );

            BigDecimal potenciaKw =
                    equipo.getPotenciaKw();

            BigDecimal horasUsoDia =
                    equipoRequest.getHorasUsoDia();

            BigDecimal diasUsoMes =
                    BigDecimal.valueOf(
                            equipoRequest.getDiasUsoMes()
                    );

            /*
             * kWh del equipo =
             * potencia(kW) × horas/día × días/mes
             */
            BigDecimal consumoEquipoKwh =
                    potenciaKw
                            .multiply(horasUsoDia)
                            .multiply(diasUsoMes);

            totalKwh =
                    totalKwh.add(consumoEquipoKwh);
        }

        /*
         * horasAltoConsumo =
         * total kWh alto consumo / 1.5 kW
         */
        BigDecimal horasAltoConsumo =
                totalKwh.divide(
                        CARGA_REFERENCIA_KW,
                        2,
                        RoundingMode.HALF_UP
                );

        /*
         * El contrato actual del modelo acepta [0, 200].
         */
        if (horasAltoConsumo.compareTo(
                LIMITE_HORAS_ALTO_CONSUMO
        ) > 0) {

            throw new IllegalArgumentException(
                    "Las horas equivalentes de alto consumo "
                            + "superan el límite permitido de 200"
            );
        }

        return horasAltoConsumo;
    }
}