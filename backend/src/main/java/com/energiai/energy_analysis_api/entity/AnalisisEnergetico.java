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

    /*
     * Identificador único del análisis.
     * Se genera automáticamente antes de guardar el registro
     * si todavía no tiene un UUID asignado.
     */
    @Id
    @Column(nullable = false, updatable = false)
    private UUID id;


    /*
     * Consumo mensual de energía en kWh.
     * Ejemplo: 420.50
     */
    @Column(
            name = "consumo_kwh",
            nullable = false,
            precision = 10,
            scale = 2
    )
    private BigDecimal consumoKwh;


    /*
     * Indica si el usuario utiliza energía durante
     * horarios considerados de mayor demanda.
     */
    @Column(
            name = "uso_horario_pico",
            nullable = false
    )
    private Boolean usoHorarioPico;


    /*
     * Cantidad total de equipos eléctricos considerados
     * para el análisis.
     */
    @Column(
            name = "cantidad_equipos",
            nullable = false
    )
    private Integer cantidadEquipos;


    /*
     * Tipo de inmueble.
     * Valores esperados por el modelo:
     * Casa
     * Departamento
     * Otro
     */
    @Column(
            name = "tipo_inmueble",
            nullable = false,
            length = 30
    )
    private String tipoInmueble;


    /*
     * Horas equivalentes de alto consumo energético.
     */
    @Column(
            name = "horas_alto_consumo",
            nullable = false,
            precision = 6,
            scale = 2
    )
    private BigDecimal horasAltoConsumo;


    /*
     * Resultado devuelto por el modelo de Machine Learning.
     *
     * Ejemplos:
     * EFICIENTE
     * MODERADO
     * INEFICIENTE
     */
    @Column(
            name = "categoria",
            nullable = false,
            length = 20
    )
    private String categoria;


    /*
     * Probabilidad/confianza asociada a la predicción.
     *
     * Ejemplo:
     * 0.8123
     */
    @Column(
            name = "probabilidad",
            nullable = false,
            precision = 5,
            scale = 4
    )
    private BigDecimal probabilidad;


    /*
     * Costo mensual estimado.
     *
     * Se calcula en el backend:
     *
     * consumoKwh × tarifaReferenciaKwh
     */
    @Column(
            name = "costo_estimado_mensual",
            nullable = false,
            precision = 12,
            scale = 2
    )
    private BigDecimal costoEstimadoMensual;


    /*
     * Tarifa de referencia utilizada para calcular
     * el costo energético.
     *
     * Para el proyecto:
     * 0.75 por kWh
     */
    @Column(
            name = "tarifa_referencia_kwh",
            nullable = false,
            precision = 10,
            scale = 4
    )
    private BigDecimal tarifaReferenciaKwh;


    /*
     * Moneda utilizada para representar el costo.
     *
     * En el contrato actual:
     * BRL
     */
    @Column(
            name = "moneda",
            nullable = false,
            length = 3
    )
    private String moneda;


    /*
     * Permite registrar qué versión del modelo
     * realizó la predicción.
     *
     * Este campo puede ser null.
     */
    @Column(
            name = "version_modelo",
            length = 30
    )
    private String versionModelo;


    /*
     * Fecha y hora en la que se realizó el análisis.
     * Se genera automáticamente antes de persistir.
     */
    @Column(
            name = "fecha_analisis",
            nullable = false,
            updatable = false
    )
    private LocalDateTime fechaAnalisis;


    /*
     * Un análisis energético puede tener varias recomendaciones.
     *
     * Ejemplo:
     *
     * Análisis
     * ├── Reducir uso en horario pico
     * ├── Revisar equipos de alto consumo
     * └── Distribuir actividades durante el día
     */
    @OneToMany(
            mappedBy = "analisis",
            cascade = CascadeType.ALL,
            orphanRemoval = true,
            fetch = FetchType.LAZY
    )
    @Builder.Default
    private List<Recomendacion> recomendaciones = new ArrayList<>();


    /*
     * Se ejecuta automáticamente justo antes de insertar
     * el registro en PostgreSQL.
     */
    @PrePersist
    public void prePersist() {

        if (id == null) {
            id = UUID.randomUUID();
        }

        if (fechaAnalisis == null) {
            fechaAnalisis = LocalDateTime.now();
        }
    }


    /*
     * Método auxiliar para agregar una recomendación
     * manteniendo correctamente la relación bidireccional.
     */
    public void agregarRecomendacion(Recomendacion recomendacion) {

        if (recomendacion == null) {
            return;
        }

        recomendaciones.add(recomendacion);
        recomendacion.setAnalisis(this);
    }


    /*
     * Método auxiliar para eliminar una recomendación
     * manteniendo correctamente la relación bidireccional.
     */
    public void eliminarRecomendacion(Recomendacion recomendacion) {

        if (recomendacion == null) {
            return;
        }

        recomendaciones.remove(recomendacion);
        recomendacion.setAnalisis(null);
    }
}