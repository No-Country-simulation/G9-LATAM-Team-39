package com.energiai.energy_analysis_api.service;

import com.energiai.energy_analysis_api.dto.request.AnalisisRequest;
import com.energiai.energy_analysis_api.dto.response.AnalisisResponse;
import com.energiai.energy_analysis_api.entity.AnalisisEnergetico;
import com.energiai.energy_analysis_api.exception.AnalisisNotFoundException;
import com.energiai.energy_analysis_api.repository.AnalisisEnergeticoRepository;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AnalisisServiceImplTest {

    @Mock
    private AnalisisEnergeticoRepository repository;

    @InjectMocks
    private AnalisisServiceImpl service;

    private AnalisisEnergetico analisis;
    private AnalisisRequest request;

    @BeforeEach
    void setUp() {

        request = new AnalisisRequest();
        request.setConsumoKwh(BigDecimal.valueOf(250));
        request.setCantidadEquipos(6);
        request.setUsoHorarioPico(true);
        request.setTipoInmueble("Casa");
        request.setHorasAltoConsumo(5);

        analisis = new AnalisisEnergetico();
        analisis.setId(UUID.randomUUID());
        analisis.setConsumoKwh(BigDecimal.valueOf(250));
        analisis.setCantidadEquipos(6);
        analisis.setUsoHorarioPico(true);
        analisis.setTipoInmueble("Casa");
        analisis.setHorasAltoConsumo(BigDecimal.valueOf(5));

        analisis.setCategoria("MEDIO");
        analisis.setProbabilidad(BigDecimal.valueOf(0.85));
        analisis.setCostoEstimadoMensual(BigDecimal.valueOf(120));
        analisis.setMoneda("PEN");
        analisis.setFechaAnalisis(LocalDateTime.now());

    }

    @Test
    void debeRegistrarAnalisis() {

        when(repository.save(any(AnalisisEnergetico.class)))
                .thenReturn(analisis);

        AnalisisResponse response =
                service.registrarAnalisis(request);

        assertNotNull(response);
        assertEquals("MEDIO", response.getCategoria());

        verify(repository, times(1))
                .save(any(AnalisisEnergetico.class));

    }

    @Test
    void debeObtenerTodosLosAnalisis() {

        when(repository.findAll())
                .thenReturn(List.of(analisis));

        List<AnalisisResponse> lista =
                service.obtenerTodosLosAnalisis();

        assertEquals(1, lista.size());

        verify(repository).findAll();

    }

    @Test
    void debeObtenerAnalisisPorId() {

        when(repository.findById(analisis.getId()))
                .thenReturn(Optional.of(analisis));

        AnalisisResponse response =
                service.obtenerAnalisisPorId(analisis.getId());

        assertNotNull(response);
        assertEquals(analisis.getId(), response.getId());

    }

    @Test
    void debeLanzarExcepcionSiNoExisteElAnalisis() {

        UUID id = UUID.randomUUID();

        when(repository.findById(id))
                .thenReturn(Optional.empty());

        assertThrows(
                AnalisisNotFoundException.class,
                () -> service.obtenerAnalisisPorId(id)
        );

    }

}