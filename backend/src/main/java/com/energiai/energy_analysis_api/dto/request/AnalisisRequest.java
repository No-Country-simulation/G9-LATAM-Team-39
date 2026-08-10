package com.energiai.energy_analysis_api.dto.request;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AnalisisRequest {

    @NotNull(message = "El consumo en kWh es obligatorio")
    @Positive(message = "El consumo debe ser mayor a cero")
    private Double consumoKwh;

    @NotNull(message = "Debe indicar si utiliza horario pico")
    private Boolean usoHorarioPico;

    @NotNull(message = "La cantidad de equipos es obligatoria")
    @Positive(message = "La cantidad de equipos debe ser mayor que cero")
    private Integer cantidadEquipos;

    @NotBlank(message = "El tipo de inmueble es obligatorio")
    private String tipoInmueble;

    @NotNull(message = "Las horas de alto consumo son obligatorias")
    @Min(value = 0, message = "Las horas no pueden ser negativas")
    @Max(value = 24, message = "Las horas no pueden ser mayores a 24")
    private Integer horasAltoConsumo;
}