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


@Tag(
        name = "Análisis Energético",
        description = "Endpoints para registrar y consultar análisis energéticos"
)
@RestController
@RequestMapping("/api/analisis")
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
    public ResponseEntity<AnalisisResponse> registrarAnalisis(
            @Valid @RequestBody AnalisisRequest request) {

        /*
         * El Controller delega el trabajo al Service.
         */
        AnalisisResponse response =
                analisisService.registrarAnalisis(request);

        /*
         * 201 CREATED indica que el recurso fue creado
         * correctamente.
         */
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(response);
    }

    @Operation(
            summary = "Obtener todos los análisis",
            description = "Devuelve la lista completa de análisis registrados."
    )
    @GetMapping
    public ResponseEntity<List<AnalisisResponse>> obtenerTodosLosAnalisis() {

        /*
         * Delegamos la consulta al Service.
         */
        List<AnalisisResponse> analisis =
                analisisService.obtenerTodosLosAnalisis();

        /*
         * ResponseEntity.ok() devuelve HTTP 200 OK
         * junto con la lista de resultados.
         */
        return ResponseEntity.ok(analisis);
    }


    /**
     * GET /api/analisis/{id}
     * Obtiene un análisis específico utilizando su ID.
     * Como la entidad utiliza UUID como identificador,
     * usamos UUID también en el Controller.
     * @PathVariable obtiene el valor {id} de la URL.
     */
    @Operation(
            summary = "Buscar análisis por ID",
            description = "Obtiene un análisis utilizando su identificador UUID."
    )
    @GetMapping("/{id}")
    public ResponseEntity<AnalisisResponse> obtenerAnalisisPorId(
            @PathVariable UUID id) {

        /*
         * Delegamos la búsqueda al Service.
         */
        AnalisisResponse response =
                analisisService.obtenerAnalisisPorId(id);

        /*
         * Si el análisis existe, devolvemos HTTP 200 OK.
         */
        return ResponseEntity.ok(response);
    }
}
