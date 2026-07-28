package com.energiai.energy_analysis_api.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "recomendacion")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Recomendacion {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 500)
    private String descripcion;

    @Column(nullable = false, length = 10)
    private String prioridad;

    @Column(name = "orden_recomendacion", nullable = false)
    private Integer orden;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "analisis_id", nullable = false)
    private AnalisisEnergetico analisis;
}
