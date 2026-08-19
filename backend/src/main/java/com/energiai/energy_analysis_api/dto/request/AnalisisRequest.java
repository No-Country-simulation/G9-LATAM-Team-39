package com.energiai.energy_analysis_api.dto.request;

import jakarta.validation.Valid;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;
import java.util.List;

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

    /*
     * Esta lista será enviada por el frontend.
     * El usuario seleccionará los equipos de alto consumo
     * e indicará cuánto los utiliza.
     */
    @Valid
    private List<EquipoAltoConsumoRequest> equiposAltoConsumo;

    /*
     * Este valor será calculado por el backend.
     *
     * horasAltoConsumo =
     * kWh de equipos de alto consumo / 1.5
     *
     * No queremos que el usuario tenga que calcularlo manualmente.
     */
    @DecimalMin(
            value = "0.0",
            inclusive = true,
            message = "Las horas equivalentes de alto consumo no pueden ser negativas"
    )

    @DecimalMax(
            value = "10000.0",
            inclusive = true,
            message = "El consumo mensual supera el máximo permitido"
    )

    private BigDecimal horasAltoConsumo;

    public AnalisisRequest() {
    }

    public AnalisisRequest(
            BigDecimal consumoKwh,
            Boolean usoHorarioPico,
            Integer cantidadEquipos,
            String tipoInmueble,
            List<EquipoAltoConsumoRequest> equiposAltoConsumo,
            BigDecimal horasAltoConsumo
    ) {
        this.consumoKwh = consumoKwh;
        this.usoHorarioPico = usoHorarioPico;
        this.cantidadEquipos = cantidadEquipos;
        this.tipoInmueble = tipoInmueble;
        this.equiposAltoConsumo = equiposAltoConsumo;
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

    public List<EquipoAltoConsumoRequest> getEquiposAltoConsumo() {
        return equiposAltoConsumo;
    }

    public void setEquiposAltoConsumo(
            List<EquipoAltoConsumoRequest> equiposAltoConsumo
    ) {
        this.equiposAltoConsumo = equiposAltoConsumo;
    }

    public BigDecimal getHorasAltoConsumo() {
        return horasAltoConsumo;
    }

    public void setHorasAltoConsumo(BigDecimal horasAltoConsumo) {
        this.horasAltoConsumo = horasAltoConsumo;
    }
}