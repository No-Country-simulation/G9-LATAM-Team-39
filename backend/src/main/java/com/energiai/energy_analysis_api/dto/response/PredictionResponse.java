package com.energiai.energy_analysis_api.dto.response;

import java.math.BigDecimal;

public class PredictionResponse {

    private String categoria;
    private BigDecimal probabilidad;

    public PredictionResponse() {
    }

    public PredictionResponse(String categoria, BigDecimal probabilidad) {
        this.categoria = categoria;
        this.probabilidad = probabilidad;
    }

    public String getCategoria() {
        return categoria;
    }

    public void setCategoria(String categoria) {
        this.categoria = categoria;
    }

    public BigDecimal getProbabilidad() {
        return probabilidad;
    }

    public void setProbabilidad(BigDecimal probabilidad) {
        this.probabilidad = probabilidad;
    }
}