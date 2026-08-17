package com.energiai.energy_analysis_api.service;

import com.energiai.energy_analysis_api.client.InferenceClient;
import com.energiai.energy_analysis_api.dto.request.AnalisisRequest;
import com.energiai.energy_analysis_api.dto.request.PredictionRequest;
import com.energiai.energy_analysis_api.dto.response.AnalisisResponse;
import com.energiai.energy_analysis_api.dto.response.PredictionResponse;
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
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AnalisisServiceImplTest {

    @Mock
    private AnalisisEnergeticoRepository repository;

    @Mock
    private AnalisisMapper mapper;

    @Mock
    private CalculadoraAltoConsumoService calculadoraAltoConsumoService;

    @Mock
    private InferenceClient inferenceClient;

    @Mock
    private CalculadoraCostoService calculadoraCostoService;

    @Mock
    private RecomendacionService recomendacionService;

    @InjectMocks
    private AnalisisServiceImpl service;

    private AnalisisEnergetico analisis;
    private AnalisisRequest request;
    private AnalisisResponse response;
    private PredictionResponse predictionResponse;

    @BeforeEach
    void setUp() {

        UUID id = UUID.randomUUID();
        LocalDateTime fecha = LocalDateTime.now();

        request = new AnalisisRequest();
        request.setConsumoKwh(BigDecimal.valueOf(350));
        request.setCantidadEquipos(8);
        request.setUsoHorarioPico(true);
        request.setTipoInmueble("Casa");
        request.setEquiposAltoConsumo(List.of());

        analisis = new AnalisisEnergetico();
        analisis.setId(id);
        analisis.setConsumoKwh(BigDecimal.valueOf(350));
        analisis.setCantidadEquipos(8);
        analisis.setUsoHorarioPico(true);
        analisis.setTipoInmueble("Casa");
        analisis.setHorasAltoConsumo(BigDecimal.ZERO);
        analisis.setCategoria("PENDIENTE");
        analisis.setProbabilidad(BigDecimal.ZERO);
        analisis.setCostoEstimadoMensual(BigDecimal.ZERO);
        analisis.setTarifaReferenciaKwh(BigDecimal.ZERO);
        analisis.setMoneda("MXN");
        analisis.setFechaAnalisis(fecha);

        predictionResponse =
                new PredictionResponse(
                        "INEFICIENTE",
                        new BigDecimal("0.9999")
                );

        response = new AnalisisResponse(
                id,
                "INEFICIENTE",
                new BigDecimal("0.9999"),
                new BigDecimal("350.00"),
                "MXN",
                fecha,
                List.of(
                        "Reduce las horas de funcionamiento de los equipos de alto consumo."
                )
        );
    }

    @Test
    void debeCrearAnalisis() {

        when(calculadoraAltoConsumoService
                .calcularHorasAltoConsumo(
                        request.getEquiposAltoConsumo()
                ))
                .thenReturn(BigDecimal.ZERO);

        when(mapper.toEntity(request))
                .thenReturn(analisis);

        when(inferenceClient.predecir(
                any(PredictionRequest.class)
        ))
                .thenReturn(predictionResponse);

        when(calculadoraCostoService
                .calcularCostoMensual(
                        request.getConsumoKwh()
                ))
                .thenReturn(
                        new BigDecimal("350.00")
                );

        when(calculadoraCostoService
                .obtenerTarifaReferenciaKwh())
                .thenReturn(
                        new BigDecimal("1.00")
                );

        when(repository.save(analisis))
                .thenReturn(analisis);

        when(mapper.toResponse(analisis))
                .thenReturn(response);

        AnalisisResponse resultado =
                service.crearAnalisis(request);

        assertNotNull(resultado);

        assertEquals(
                "INEFICIENTE",
                analisis.getCategoria()
        );

        assertEquals(
                new BigDecimal("0.9999"),
                analisis.getProbabilidad()
        );

        assertEquals(
                new BigDecimal("350.00"),
                analisis.getCostoEstimadoMensual()
        );

        assertEquals(
                new BigDecimal("1.00"),
                analisis.getTarifaReferenciaKwh()
        );

        verify(recomendacionService, times(1))
                .generarRecomendaciones(analisis);

        verify(repository, times(1))
                .save(analisis);
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

        verify(repository, times(1))
                .findAll();
    }

    @Test
    void debeObtenerAnalisisPorId() {

        when(repository.findById(
                analisis.getId()
        ))
                .thenReturn(
                        Optional.of(analisis)
                );

        when(mapper.toResponse(analisis))
                .thenReturn(response);

        AnalisisResponse resultado =
                service.obtenerPorId(
                        analisis.getId()
                );

        assertNotNull(resultado);

        assertEquals(
                analisis.getId(),
                resultado.getId()
        );
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
    }

    @Test
    void debeActualizarAnalisis() {

        when(repository.findById(
                analisis.getId()
        ))
                .thenReturn(
                        Optional.of(analisis)
                );

        when(calculadoraAltoConsumoService
                .calcularHorasAltoConsumo(
                        request.getEquiposAltoConsumo()
                ))
                .thenReturn(BigDecimal.ZERO);

        when(inferenceClient.predecir(
                any(PredictionRequest.class)
        ))
                .thenReturn(predictionResponse);

        when(calculadoraCostoService
                .calcularCostoMensual(
                        request.getConsumoKwh()
                ))
                .thenReturn(
                        new BigDecimal("350.00")
                );

        when(calculadoraCostoService
                .obtenerTarifaReferenciaKwh())
                .thenReturn(
                        new BigDecimal("1.00")
                );

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

        assertEquals(
                "INEFICIENTE",
                analisis.getCategoria()
        );

        assertEquals(
                new BigDecimal("350.00"),
                analisis.getCostoEstimadoMensual()
        );

        verify(recomendacionService, times(1))
                .generarRecomendaciones(analisis);

        verify(repository, times(1))
                .save(analisis);
    }

    @Test
    void debeEliminarAnalisis() {

        when(repository.findById(
                analisis.getId()
        ))
                .thenReturn(
                        Optional.of(analisis)
                );

        service.eliminar(
                analisis.getId()
        );

        verify(repository, times(1))
                .delete(analisis);
    }
}