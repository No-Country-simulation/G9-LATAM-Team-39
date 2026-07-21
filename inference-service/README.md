# Inference Service

Este módulo contendrá un servicio independiente en Python encargado de cargar y ejecutar el modelo de Machine Learning.

## Propósito

El modelo será entrenado con herramientas de Python y Scikit-learn. Como la API principal estará desarrollada con Java y Spring Boot, este servicio funcionará como puente entre el backend y el modelo serializado.

## Responsabilidades previstas

- Cargar el modelo entrenado.
- Validar los datos recibidos desde el backend.
- Aplicar las mismas transformaciones utilizadas durante el entrenamiento.
- Realizar la predicción.
- Obtener la probabilidad mediante `predict_proba`, cuando el modelo lo soporte.
- Devolver la categoría y la probabilidad.
- Gestionar errores de carga o predicción.

## Flujo previsto

1. Spring Boot recibe la solicitud del frontend.
2. Spring Boot valida los datos.
3. Spring Boot envía los datos al servicio de inferencia.
4. El servicio carga o utiliza el modelo previamente cargado.
5. El modelo genera la predicción.
6. El servicio devuelve la categoría y la probabilidad.
7. Spring Boot completa la respuesta para el frontend.

## Tecnologías previstas

- Python
- FastAPI
- Uvicorn
- Scikit-learn
- Pandas
- Joblib

## Estado

El servicio FastAPI todavía no ha sido inicializado.