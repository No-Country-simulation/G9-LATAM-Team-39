package com.energiai.energy_analysis_api.controller;

import com.energiai.energy_analysis_api.dto.request.AnalisisRequest;
import com.energiai.energy_analysis_api.dto.response.AnalisisResponse;
import com.energiai.energy_analysis_api.service.AnalisisService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@CrossOrigin(origins = "https://proyecto-self-five.vercel.app")
@CrossOrigin(origins = "*")
@RestController
@RequestMapping("/api/analisis")
@Tag(
        name = "Análisis Energético",
        description = "Endpoints para registrar, consultar, actualizar y eliminar análisis energéticos"
)
public class AnalisisController {

    private final AnalisisService analisisService;

    public AnalisisController(AnalisisService analisisService) {
        this.analisisService = analisisService;
    }

    @Operation(
            summary = "Registrar análisis",
            description = "Registra un nuevo análisis energético."
    )
    @PostMapping
    public ResponseEntity<AnalisisResponse> crearAnalisis(
            @Valid @RequestBody AnalisisRequest request
    ) {
        AnalisisResponse response =
                analisisService.crearAnalisis(request);

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(response);
    }

    @Operation(
            summary = "Obtener todos los análisis",
            description = "Devuelve la lista completa de análisis energéticos registrados."
    )
    @GetMapping
    public ResponseEntity<List<AnalisisResponse>> obtenerTodos() {
        return ResponseEntity.ok(
                analisisService.obtenerTodos()
        );
    }

    @Operation(
            summary = "Buscar análisis por ID",
            description = "Obtiene un análisis energético utilizando su identificador UUID."
    )
    @GetMapping("/{id}")
    public ResponseEntity<AnalisisResponse> obtenerPorId(
            @PathVariable UUID id
    ) {
        return ResponseEntity.ok(
                analisisService.obtenerPorId(id)
        );
    }

    @Operation(
            summary = "Actualizar análisis",
            description = "Actualiza los datos de un análisis energético existente."
    )
    @PutMapping("/{id}")
    public ResponseEntity<AnalisisResponse> actualizar(
            @PathVariable UUID id,
            @Valid @RequestBody AnalisisRequest request
    ) {
        return ResponseEntity.ok(
                analisisService.actualizar(id, request)
        );
    }

    @Operation(
            summary = "Eliminar análisis",
            description = "Elimina un análisis energético utilizando su identificador UUID."
    )
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> eliminar(
            @PathVariable UUID id
    ) {
        analisisService.eliminar(id);

        return ResponseEntity.noContent().build();
    }
}