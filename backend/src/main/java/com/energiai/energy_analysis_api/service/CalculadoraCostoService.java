package com.energiai.energy_analysis_api.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;

@Service
public class CalculadoraCostoService {

    private final BigDecimal tarifaReferenciaKwh;
    private final String moneda;

    public CalculadoraCostoService(
            @Value("${energiai.tarifa-referencia-kwh:0.75}")
            BigDecimal tarifaReferenciaKwh,

            @Value("${energiai.moneda:BRL}")
            String moneda
    ) {
        this.tarifaReferenciaKwh = tarifaReferenciaKwh;
        this.moneda = moneda;
    }

    public BigDecimal calcularCostoMensual(
            BigDecimal consumoKwh
    ) {

        if (consumoKwh == null) {
            throw new IllegalArgumentException(
                    "El consumo en kWh no puede ser nulo"
            );
        }

        if (consumoKwh.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException(
                    "El consumo en kWh no puede ser negativo"
            );
        }

        return consumoKwh
                .multiply(tarifaReferenciaKwh)
                .setScale(
                        2,
                        RoundingMode.HALF_UP
                );
    }

    public BigDecimal obtenerTarifaReferenciaKwh() {
        return tarifaReferenciaKwh;
    }

    public String obtenerMoneda() {
        return moneda;
    }
}