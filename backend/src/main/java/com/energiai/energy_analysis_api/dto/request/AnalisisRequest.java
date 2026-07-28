package com.energiai.energy_analysis_api.dto.request;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;

public class AnalisisRequest {

    @NotNull(message = "El consumo en kWh es obligatorio")
    @DecimalMin(
            value = "0.0",
            inclusive = false,
            message = "El consumo debe ser mayor que cero"
    )
    private BigDecimal consumoKwh;

    @NotNull(message = "El uso en horario pico es obligatorio")
    private Boolean usoHorarioPico;

    @NotNull(message = "La cantidad de equipos es obligatoria")
    @Min(
            value = 1,
            message = "La cantidad de equipos debe ser mayor o igual a 1"
    )
    private Integer cantidadEquipos;

    @NotBlank(message = "El tipo de inmueble es obligatorio")
    @Size(
            max = 50,
            message = "El tipo de inmueble no puede superar los 50 caracteres"
    )
    private String tipoInmueble;

    @NotNull(message = "Las horas de alto consumo son obligatorias")
    @Min(
            value = 0,
            message = "Las horas de alto consumo no pueden ser negativas"
    )
    @Max(
            value = 24,
            message = "Las horas de alto consumo no pueden superar 24"
    )
    private Integer horasAltoConsumo;

    public AnalisisRequest() {
    }

    public AnalisisRequest(
            BigDecimal consumoKwh,
            Boolean usoHorarioPico,
            Integer cantidadEquipos,
            String tipoInmueble,
            Integer horasAltoConsumo
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

    public Integer getHorasAltoConsumo() {
        return horasAltoConsumo;
    }

    public void setHorasAltoConsumo(Integer horasAltoConsumo) {
        this.horasAltoConsumo = horasAltoConsumo;
    }
}