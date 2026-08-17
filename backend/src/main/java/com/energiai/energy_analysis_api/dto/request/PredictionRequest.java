package com.energiai.energy_analysis_api.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.math.BigDecimal;

public class PredictionRequest {

    @JsonProperty("consumo_kwh")
    private BigDecimal consumoKwh;

    @JsonProperty("uso_horario_pico")
    private Boolean usoHorarioPico;

    @JsonProperty("cantidad_equipos")
    private Integer cantidadEquipos;

    @JsonProperty("tipo_inmueble")
    private String tipoInmueble;

    @JsonProperty("horas_alto_consumo")
    private BigDecimal horasAltoConsumo;

    public PredictionRequest() {
    }

    public PredictionRequest(
            BigDecimal consumoKwh,
            Boolean usoHorarioPico,
            Integer cantidadEquipos,
            String tipoInmueble,
            BigDecimal horasAltoConsumo
    ) {
        this.consumoKwh = consumoKwh;
        this.usoHorarioPico = usoHorarioPico;
        this.cantidadEquipos = cantidadEquipos;
        this.tipoInmueble = tipoInmueble;
        this.horasAltoConsumo = horasAltoConsumo;
    }

    public BigDecimal getConsumoKwh() {
        return consumoKwh;
    }

    public void setConsumoKwh(BigDecimal consumoKwh) {
        this.consumoKwh = consumoKwh;
    }

    public Boolean getUsoHorarioPico() {
        return usoHorarioPico;
    }

    public void setUsoHorarioPico(Boolean usoHorarioPico) {
        this.usoHorarioPico = usoHorarioPico;
    }

    public Integer getCantidadEquipos() {
        return cantidadEquipos;
    }

    public void setCantidadEquipos(Integer cantidadEquipos) {
        this.cantidadEquipos = cantidadEquipos;
    }

    public String getTipoInmueble() {
        return tipoInmueble;
    }

    public void setTipoInmueble(String tipoInmueble) {
        this.tipoInmueble = tipoInmueble;
    }

    public BigDecimal getHorasAltoConsumo() {
        return horasAltoConsumo;
    }

    public void setHorasAltoConsumo(BigDecimal horasAltoConsumo) {
        this.horasAltoConsumo = horasAltoConsumo;
    }
}