package com.energiai.energy_analysis_api.config;

import io.swagger.v3.oas.models.ExternalDocumentation;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI energyApi() {

        return new OpenAPI()
                .info(new Info()
                        .title("Energy Analysis API")
                        .description("API REST para análisis y clasificación del consumo energético")
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("Equipo EnergyAI")
                                .email("equipo@energiai.com"))
                        .license(new License()
                                .name("MIT")))
                .externalDocs(new ExternalDocumentation()
                        .description("Repositorio del proyecto"));
    }
}