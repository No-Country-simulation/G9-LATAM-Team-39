package com.energiai.energy_analysis_api.dto.response;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

public class AnalisisResponse {

    private UUID id;
    private String categoria;
    private BigDecimal probabilidad;
    private BigDecimal costoEstimadoMensual;
    private String moneda;
    private LocalDateTime fechaAnalisis;
    private List<String> recomendaciones;

    public AnalisisResponse() {
    }

    public AnalisisResponse(
            UUID id,
            String categoria,
            BigDecimal probabilidad,
            BigDecimal costoEstimadoMensual,
            String moneda,
            LocalDateTime fechaAnalisis,
            List<String> recomendaciones
    ) {
        this.id = id;
        this.categoria = categoria;
        this.probabilidad = probabilidad;
        this.costoEstimadoMensual = costoEstimadoMensual;
        this.moneda = moneda;
        this.fechaAnalisis = fechaAnalisis;
        this.recomendaciones = recomendaciones;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
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

    public BigDecimal getCostoEstimadoMensual() {
        return costoEstimadoMensual;
    }

    public void setCostoEstimadoMensual(BigDecimal costoEstimadoMensual) {
        this.costoEstimadoMensual = costoEstimadoMensual;
    }

    public String getMoneda() {
        return moneda;
    }

    public void setMoneda(String moneda) {
        this.moneda = moneda;
    }

    public LocalDateTime getFechaAnalisis() {
        return fechaAnalisis;
    }

    public void setFechaAnalisis(LocalDateTime fechaAnalisis) {
        this.fechaAnalisis = fechaAnalisis;
    }

    public List<String> getRecomendaciones() {
        return recomendaciones;
    }

    public void setRecomendaciones(List<String> recomendaciones) {
        this.recomendaciones = recomendaciones;
    }
}