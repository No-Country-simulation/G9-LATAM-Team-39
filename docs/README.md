# Documentación

Documentación técnica y funcional del proyecto. Esta carpeta es la **única versión válida** de todo lo compartido: contrato, arquitectura, plan y decisiones. Los README de cada módulo **enlazan aquí en lugar de duplicar**.


## Regla de versión única

- Lo **compartido** (contrato de la API, arquitectura, plan por sprints, reglas de etiquetado, decisiones) vive **aquí y en un solo lugar**.
- Los README de módulo (`backend/`, `inference-service/`, `data-science/`, `frontend/`) son **solo operativos** (cómo correr esa pieza). No repiten el contrato ni la arquitectura; enlazan a `docs/`.
- Si el contrato cambia, se cambia **aquí** y se avisa al equipo. Nunca se edita en dos sitios.

## Documentos

| Documento | Contenido |
|---|---|
| `documentacion.md` | Documento principal: resumen, arquitectura, plan por sprints, riesgos |
| `contrato-api.md` | Contrato de la API: `POST /analisis-energetico` y `GET /resultados/{id}` |
| `guia-oci.md` | Paso a paso reproducible de OCI Object Storage (bucket, credenciales, subida/descarga del modelo) |
| `reglas-etiquetado.md` | Definición y justificación de EFICIENTE / MODERADO / INEFICIENTE |
| `consumo-por-aparato.md` | Consumo promedio por electrodoméstico (ENCEVI) para las recomendaciones |
| `flujo-proyecto.md` | Recorrido completo: de ENCEVI al usuario final, con responsables |
| `decisiones.md` | Registro de decisiones (ADR): qué se decidió y por qué |
| `casos-prueba.md` | Los 3 ejemplos obligatorios de uso |

## Checklist de entregables del hackathon

- [ ] API documentada (Swagger)
- [ ] Modelo entrenado, evaluado y serializado
- [ ] Al menos un servicio de OCI integrado
- [ ] 3 ejemplos reales o simulados de uso
- [ ] Video demostrativo
- [ ] Enlaces (repo, app, Swagger, notebook)

## Estado

La documentación se completará conforme avance el desarrollo. El contrato, la arquitectura y las reglas de etiquetado deben cerrarse en el Sprint 1.
