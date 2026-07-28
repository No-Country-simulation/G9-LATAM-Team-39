package com.energiai.energy_analysis_api.entity;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "analisis_energetico")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AnalisisEnergetico {

    @Id
    private UUID id;

    @Column(name = "consumo_kwh", nullable = false, precision = 10, scale = 2)
    private BigDecimal consumoKwh;

    @Column(name = "uso_horario_pico", nullable = false)
    private Boolean usoHorarioPico;

    @Column(name = "cantidad_equipos", nullable = false)
    private Integer cantidadEquipos;

    @Column(name = "tipo_inmueble", nullable = false, length = 30)
    private String tipoInmueble;

    @Column(name = "horas_alto_consumo", nullable = false, precision = 4, scale = 2)
    private BigDecimal horasAltoConsumo;

    @Column(nullable = false, length = 20)
    private String categoria;

    @Column(nullable = false, precision = 5, scale = 4)
    private BigDecimal probabilidad;

    @Column(name = "costo_estimado_mensual", nullable = false, precision = 12, scale = 2)
    private BigDecimal costoEstimadoMensual;

    @Column(name = "tarifa_referencia_kwh", nullable = false, precision = 10, scale = 4)
    private BigDecimal tarifaReferenciaKwh;

    @Column(nullable = false, length = 3)
    private String moneda;

    @Column(name = "version_modelo", length = 30)
    private String versionModelo;

    @Column(name = "fecha_analisis", nullable = false)
    private LocalDateTime fechaAnalisis;

    @OneToMany(
            mappedBy = "analisis",
            cascade = CascadeType.ALL,
            orphanRemoval = true,
            fetch = FetchType.LAZY
    )
    @Builder.Default
    private List<Recomendacion> recomendaciones = new ArrayList<>();

    @PrePersist
    public void prePersist() {
        if (id == null) {
            id = UUID.randomUUID();
        }

        if (fechaAnalisis == null) {
            fechaAnalisis = LocalDateTime.now();
        }
    }

    public void agregarRecomendacion(Recomendacion recomendacion) {
        recomendaciones.add(recomendacion);
        recomendacion.setAnalisis(this);
    }
}