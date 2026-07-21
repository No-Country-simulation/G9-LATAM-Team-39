# Analizador Inteligente de Consumo Energético

Proyecto desarrollado para el Hackathon ONE – Proyectos G9 de Alura + Oracle con NoCountry.

## Objetivo

Desarrollar una solución que analice información relacionada con el consumo energético de viviendas y clasifique su perfil como:

- Eficiente
- Moderado
- Ineficiente

La aplicación devolverá la categoría estimada, la probabilidad del modelo, el costo mensual de referencia y recomendaciones para optimizar el consumo energético.

## Datos de entrada

El MVP utilizará inicialmente los siguientes campos:

- `consumo_kwh`: consumo mensual de energía.
- `uso_horario_pico`: indica si existe uso de equipos durante el horario considerado de mayor demanda.
- `cantidad_equipos`: número total de equipos eléctricos considerados.
- `tipo_inmueble`: tipo de vivienda o inmueble.
- `horas_alto_consumo`: tiempo estimado de uso de equipos de alto consumo.

## Resultado esperado

La solución podrá devolver:

- Categoría energética.
- Probabilidad o nivel de confianza del modelo.
- Costo mensual estimado.
- Tarifa de referencia.
- Recomendaciones de optimización.

## Arquitectura propuesta

- `backend/`: API REST principal desarrollada con Java y Spring Boot.
- `frontend/`: interfaz para captura de datos y visualización de resultados.
- `data-science/`: procesamiento de datos, análisis exploratorio, entrenamiento y evaluación del modelo.
- `inference-service/`: servicio Python encargado de cargar y ejecutar el modelo de Machine Learning.
- `docs/`: documentación técnica, funcional y de despliegue.

## Flujo general

1. El usuario captura los datos en el frontend.
2. El frontend envía la solicitud al backend.
3. El backend valida la información.
4. El backend solicita una predicción al servicio de inferencia.
5. El servicio de inferencia ejecuta el modelo entrenado.
6. El backend completa el resultado con costo y recomendaciones.
7. El frontend presenta el análisis al usuario.

## Tecnologías previstas

### Backend

- Java
- Spring Boot
- Maven
- API REST
- OpenAPI/Swagger

### Data Science e inferencia

- Python
- Pandas
- Scikit-learn
- Joblib
- FastAPI
- Random Forest

### Infraestructura

- GitHub
- Oracle Cloud Infrastructure

## Estado

Proyecto en etapa inicial de desarrollo.

La arquitectura y las tecnologías podrán ajustarse durante el hackathon según las decisiones del equipo.