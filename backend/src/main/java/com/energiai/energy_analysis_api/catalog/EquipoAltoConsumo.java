package com.energiai.energy_analysis_api.catalog;

import java.math.BigDecimal;

public enum EquipoAltoConsumo {

    AIRE_ACONDICIONADO(
            "Aire acondicionado",
            new BigDecimal("1.50")
    ),

    CALENTADOR_ELECTRICO(
            "Calentador eléctrico",
            new BigDecimal("1.50")
    ),

    HORNO_ELECTRICO(
            "Horno eléctrico",
            new BigDecimal("2.00")
    ),

    SECADORA_ROPA(
            "Secadora de ropa",
            new BigDecimal("3.00")
    ),

    PARRILLA_ELECTRICA(
            "Parrilla eléctrica",
            new BigDecimal("1.50")
    ),

    LAVAVAJILLAS(
            "Lavavajillas",
            new BigDecimal("1.20")
    ),

    BOMBA_AGUA(
            "Bomba de agua",
            new BigDecimal("0.75")
    ),

    CALEFACTOR_ELECTRICO(
            "Calefactor eléctrico",
            new BigDecimal("1.50")
    );

    private final String nombre;
    private final BigDecimal potenciaKw;

    EquipoAltoConsumo(
            String nombre,
            BigDecimal potenciaKw
    ) {
        this.nombre = nombre;
        this.potenciaKw = potenciaKw;
    }

    public String getNombre() {
        return nombre;
    }

    public BigDecimal getPotenciaKw() {
        return potenciaKw;
    }

    /**
     * Busca un equipo utilizando el código recibido
     * desde el frontend.
     *
     * Ejemplo:
     * "AIRE_ACONDICIONADO"
     */
    public static EquipoAltoConsumo buscarPorCodigo(String codigo) {

        if (codigo == null || codigo.isBlank()) {
            throw new IllegalArgumentException(
                    "El código del equipo no puede estar vacío"
            );
        }

        try {
            return EquipoAltoConsumo.valueOf(
                    codigo.trim().toUpperCase()
            );
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException(
                    "Equipo de alto consumo no válido: " + codigo
            );
        }
    }
}