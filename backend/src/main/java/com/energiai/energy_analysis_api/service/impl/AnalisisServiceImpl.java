package com.energiai.energy_analysis_api.service.impl;

import com.energiai.energy_analysis_api.dto.request.AnalisisRequest;
import com.energiai.energy_analysis_api.dto.response.AnalisisResponse;
import com.energiai.energy_analysis_api.entity.AnalisisEnergetico;
import com.energiai.energy_analysis_api.exception.AnalisisNoEncontradoException;
import com.energiai.energy_analysis_api.mapper.AnalisisMapper;
import com.energiai.energy_analysis_api.repository.AnalisisEnergeticoRepository;
import com.energiai.energy_analysis_api.service.AnalisisService;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
@Transactional
public class AnalisisServiceImpl implements AnalisisService {

    private final AnalisisEnergeticoRepository repository;
    private final AnalisisMapper mapper;

    public AnalisisServiceImpl(
            AnalisisEnergeticoRepository repository,
            AnalisisMapper mapper
    ) {
        this.repository = repository;
        this.mapper = mapper;
    }

    @Override
    public AnalisisResponse crearAnalisis(AnalisisRequest request) {

        AnalisisEnergetico analisis =
                mapper.toEntity(request);

        AnalisisEnergetico analisisGuardado =
                repository.save(analisis);

        return mapper.toResponse(analisisGuardado);
    }

    @Override
    @Transactional(readOnly = true)
    public List<AnalisisResponse> obtenerTodos() {

        return repository.findAll()
                .stream()
                .map(mapper::toResponse)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public AnalisisResponse obtenerPorId(UUID id) {

        AnalisisEnergetico analisis =
                buscarEntidadPorId(id);

        return mapper.toResponse(analisis);
    }

    @Override
    public AnalisisResponse actualizar(
            UUID id,
            AnalisisRequest request
    ) {

        AnalisisEnergetico analisisExistente =
                buscarEntidadPorId(id);

        mapper.updateEntity(
                analisisExistente,
                request
        );

        AnalisisEnergetico analisisActualizado =
                repository.save(analisisExistente);

        return mapper.toResponse(analisisActualizado);
    }

    @Override
    public void eliminar(UUID id) {

        AnalisisEnergetico analisis =
                buscarEntidadPorId(id);

        repository.delete(analisis);
    }

    private AnalisisEnergetico buscarEntidadPorId(UUID id) {

        if (id == null) {
            throw new IllegalArgumentException(
                    "El identificador del análisis no puede ser nulo"
            );
        }

        return repository.findById(id)
                .orElseThrow(() ->
                        new AnalisisNoEncontradoException(
                                "No se encontró el análisis energético con ID: "
                                        + id
                        )
                );
    }
}