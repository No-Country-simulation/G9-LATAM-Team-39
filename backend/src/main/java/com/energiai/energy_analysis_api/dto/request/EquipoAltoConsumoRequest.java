package com.energiai.energy_analysis_api.dto.request;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;

public class EquipoAltoConsumoRequest {

    @NotBlank(message = "El código del equipo es obligatorio")
    private String codigoEquipo;

    @NotNull(message = "Las horas de uso diario son obligatorias")
    @DecimalMin(
            value = "0.0",
            inclusive = false,
            message = "Las horas de uso diario deben ser mayores que cero"
    )
    @DecimalMax(
            value = "24.0",
            inclusive = true,
            message = "Las horas de uso diario no pueden superar 24"
    )
    private BigDecimal horasUsoDia;

    @NotNull(message = "Los días de uso al mes son obligatorios")
    @Min(
            value = 1,
            message = "Los días de uso al mes deben ser al menos 1"
    )
    @Max(
            value = 31,
            message = "Los días de uso al mes no pueden superar 31"
    )
    private Integer diasUsoMes;

    public EquipoAltoConsumoRequest() {
    }

    public EquipoAltoConsumoRequest(
            String codigoEquipo,
            BigDecimal horasUsoDia,
            Integer diasUsoMes
    ) {
        this.codigoEquipo = codigoEquipo;
        this.horasUsoDia = horasUsoDia;
        this.diasUsoMes = diasUsoMes;
    }

    public String getCodigoEquipo() {
        return codigoEquipo;
    }

    public void setCodigoEquipo(String codigoEquipo) {
        this.codigoEquipo = codigoEquipo;
    }

    public BigDecimal getHorasUsoDia() {
        return horasUsoDia;
    }

    public void setHorasUsoDia(BigDecimal horasUsoDia) {
        this.horasUsoDia = horasUsoDia;
    }

    public Integer getDiasUsoMes() {
        return diasUsoMes;
    }

    public void setDiasUsoMes(Integer diasUsoMes) {
        this.diasUsoMes = diasUsoMes;
    }
}