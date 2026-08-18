package com.energiai.energy_analysis_api.service;

import com.energiai.energy_analysis_api.dto.request.EquipoAltoConsumoRequest;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class CalculadoraAltoConsumoServiceTest {

    private CalculadoraAltoConsumoService service;

    @BeforeEach
    void setUp() {
        service = new CalculadoraAltoConsumoService();
    }

    @Test
    void debeCalcularHorasEquivalentesCorrectamente() {

        EquipoAltoConsumoRequest aire =
                new EquipoAltoConsumoRequest(
                        "AIRE_ACONDICIONADO",
                        new BigDecimal("4"),
                        20
                );

        BigDecimal resultado =
                service.calcularHorasAltoConsumo(
                        List.of(aire)
                );

        /*
         * Aire acondicionado = 1.50 kW
         *
         * 1.50 × 4 horas × 20 días = 120 kWh
         *
         * 120 / 1.5 = 80 horas equivalentes
         */
        assertEquals(
                new BigDecimal("80.00"),
                resultado
        );
    }

    @Test
    void debeDevolverCeroCuandoNoHayEquipos() {

        BigDecimal resultado =
                service.calcularHorasAltoConsumo(
                        List.of()
                );

        assertEquals(
                BigDecimal.ZERO,
                resultado
        );
    }

    @Test
    void debeDevolverCeroCuandoListaEsNula() {

        BigDecimal resultado =
                service.calcularHorasAltoConsumo(
                        null
                );

        assertEquals(
                BigDecimal.ZERO,
                resultado
        );
    }

    @Test
    void debeLanzarExcepcionCuandoEquipoNoExiste() {

        EquipoAltoConsumoRequest equipo =
                new EquipoAltoConsumoRequest(
                        "EQUIPO_INVENTADO",
                        new BigDecimal("2"),
                        10
                );

        assertThrows(
                IllegalArgumentException.class,
                () -> service.calcularHorasAltoConsumo(
                        List.of(equipo)
                )
        );
    }

    @Test
    void debeLanzarExcepcionSiSuperaLimite200() {

        EquipoAltoConsumoRequest secadora =
                new EquipoAltoConsumoRequest(
                        "SECADORA_ROPA",
                        new BigDecimal("10"),
                        31
                );

        assertThrows(
                IllegalArgumentException.class,
                () -> service.calcularHorasAltoConsumo(
                        List.of(secadora)
                )
        );
    }
}