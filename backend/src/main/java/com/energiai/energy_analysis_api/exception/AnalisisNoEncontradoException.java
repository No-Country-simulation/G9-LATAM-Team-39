package com.energiai.energy_analysis_api.exception;

public class AnalisisNoEncontradoException extends RuntimeException {

    public AnalisisNoEncontradoException(String mensaje) {
        super(mensaje);
    }
}