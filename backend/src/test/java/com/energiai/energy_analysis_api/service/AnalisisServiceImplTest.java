package com.energiai.energy_analysis_api.service;

import com.energiai.energy_analysis_api.dto.request.AnalisisRequest;
import com.energiai.energy_analysis_api.dto.response.AnalisisResponse;
import com.energiai.energy_analysis_api.entity.AnalisisEnergetico;
import com.energiai.energy_analysis_api.exception.AnalisisNoEncontradoException;
import com.energiai.energy_analysis_api.mapper.AnalisisMapper;
import com.energiai.energy_analysis_api.repository.AnalisisEnergeticoRepository;
import com.energiai.energy_analysis_api.service.impl.AnalisisServiceImpl;

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

    @Mock
    private AnalisisMapper mapper;

    @Mock
    private CalculadoraAltoConsumoService calculadoraAltoConsumoService;

    @InjectMocks
    private AnalisisServiceImpl service;

    private AnalisisEnergetico analisis;
    private AnalisisRequest request;
    private AnalisisResponse response;

    @BeforeEach
    void setUp() {

        UUID id = UUID.randomUUID();
        LocalDateTime fecha = LocalDateTime.now();

        request = new AnalisisRequest();
        request.setConsumoKwh(BigDecimal.valueOf(250));
        request.setCantidadEquipos(6);
        request.setUsoHorarioPico(true);
        request.setTipoInmueble("Casa");
        request.setEquiposAltoConsumo(List.of());

        analisis = new AnalisisEnergetico();
        analisis.setId(id);
        analisis.setConsumoKwh(BigDecimal.valueOf(250));
        analisis.setCantidadEquipos(6);
        analisis.setUsoHorarioPico(true);
        analisis.setTipoInmueble("Casa");
        analisis.setHorasAltoConsumo(BigDecimal.ZERO);
        analisis.setCategoria("MEDIO");
        analisis.setProbabilidad(BigDecimal.valueOf(0.85));
        analisis.setCostoEstimadoMensual(BigDecimal.valueOf(120));
        analisis.setMoneda("MXN");
        analisis.setFechaAnalisis(fecha);

        response = new AnalisisResponse(
                id,
                "MEDIO",
                BigDecimal.valueOf(0.85),
                BigDecimal.valueOf(120),
                "MXN",
                fecha,
                List.of()
        );
    }

    @Test
    void debeCrearAnalisis() {

        when(calculadoraAltoConsumoService
                .calcularHorasAltoConsumo(request.getEquiposAltoConsumo()))
                .thenReturn(BigDecimal.ZERO);

        when(mapper.toEntity(request))
                .thenReturn(analisis);

        when(repository.save(analisis))
                .thenReturn(analisis);

        when(mapper.toResponse(analisis))
                .thenReturn(response);

        AnalisisResponse resultado =
                service.crearAnalisis(request);

        assertNotNull(resultado);
        assertEquals("MEDIO", resultado.getCategoria());
        assertEquals(BigDecimal.ZERO, request.getHorasAltoConsumo());

        verify(calculadoraAltoConsumoService, times(1))
                .calcularHorasAltoConsumo(
                        request.getEquiposAltoConsumo()
                );

        verify(mapper, times(1))
                .toEntity(request);

        verify(repository, times(1))
                .save(analisis);

        verify(mapper, times(1))
                .toResponse(analisis);
    }

    @Test
    void debeObtenerTodosLosAnalisis() {

        when(repository.findAll())
                .thenReturn(List.of(analisis));

        when(mapper.toResponse(analisis))
                .thenReturn(response);

        List<AnalisisResponse> lista =
                service.obtenerTodos();

        assertNotNull(lista);
        assertEquals(1, lista.size());
        assertEquals("MEDIO", lista.get(0).getCategoria());

        verify(repository, times(1))
                .findAll();

        verify(mapper, times(1))
                .toResponse(analisis);
    }

    @Test
    void debeObtenerAnalisisPorId() {

        when(repository.findById(analisis.getId()))
                .thenReturn(Optional.of(analisis));

        when(mapper.toResponse(analisis))
                .thenReturn(response);

        AnalisisResponse resultado =
                service.obtenerPorId(analisis.getId());

        assertNotNull(resultado);
        assertEquals(
                analisis.getId(),
                resultado.getId()
        );

        verify(repository, times(1))
                .findById(analisis.getId());

        verify(mapper, times(1))
                .toResponse(analisis);
    }

    @Test
    void debeLanzarExcepcionSiNoExisteElAnalisis() {

        UUID id = UUID.randomUUID();

        when(repository.findById(id))
                .thenReturn(Optional.empty());

        assertThrows(
                AnalisisNoEncontradoException.class,
                () -> service.obtenerPorId(id)
        );

        verify(repository, times(1))
                .findById(id);
    }

    @Test
    void debeActualizarAnalisis() {

        when(repository.findById(analisis.getId()))
                .thenReturn(Optional.of(analisis));

        when(calculadoraAltoConsumoService
                .calcularHorasAltoConsumo(request.getEquiposAltoConsumo()))
                .thenReturn(BigDecimal.ZERO);

        when(repository.save(analisis))
                .thenReturn(analisis);

        when(mapper.toResponse(analisis))
                .thenReturn(response);

        AnalisisResponse resultado =
                service.actualizar(
                        analisis.getId(),
                        request
                );

        assertNotNull(resultado);
        assertEquals(BigDecimal.ZERO, request.getHorasAltoConsumo());

        verify(repository, times(1))
                .findById(analisis.getId());

        verify(calculadoraAltoConsumoService, times(1))
                .calcularHorasAltoConsumo(
                        request.getEquiposAltoConsumo()
                );

        verify(mapper, times(1))
                .updateEntity(analisis, request);

        verify(repository, times(1))
                .save(analisis);

        verify(mapper, times(1))
                .toResponse(analisis);
    }

    @Test
    void debeEliminarAnalisis() {

        when(repository.findById(analisis.getId()))
                .thenReturn(Optional.of(analisis));

        service.eliminar(analisis.getId());

        verify(repository, times(1))
                .findById(analisis.getId());

        verify(repository, times(1))
                .delete(analisis);
    }
}