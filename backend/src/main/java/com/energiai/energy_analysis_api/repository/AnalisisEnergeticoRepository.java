package com.energiai.energy_analysis_api.repository;

import com.energiai.energy_analysis_api.entity.AnalisisEnergetico;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.UUID;

@Repository
public interface AnalisisEnergeticoRepository extends JpaRepository<AnalisisEnergetico, UUID> {

}