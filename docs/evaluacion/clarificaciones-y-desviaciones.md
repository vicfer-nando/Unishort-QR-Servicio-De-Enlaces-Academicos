# Clarificaciones y límites de la entrega — 2026-11-06

Registro retrospectivo de preguntas técnicas de auditoría, con respuestas basadas
en solicitud, código y pruebas. No acredita ejecución de /speckit.clarify ni
entrevista, votación, firma, aprobación institucional o revisión independiente.

| Pregunta | Respuesta verificable / decisión | Fuente y estado |
|---|---|---|
| ¿Cuál es el problema? | Compartir recursos académicos con URL breves y QR verificables, conservando el destino. | Especificaciones 001/002; necesidad declarada, no estudio institucional certificado. |
| ¿Quién usa el incremento? | Usuario académico crea/descarga; visitante abre; administrador técnico consulta/modifica; docente verifica. | Frontend, rutas y especificaciones. DTI es un actor propuesto, no una integración real. |
| ¿Puede sustituirse FastAPI por Django? | Se conserva FastAPI: continuidad, validación y OpenAPI, con ADR 0001. | El PDF pp. 3–4 presenta stack de referencia y exige justificar tecnologías adicionales; no consta aprobación docente específica. |
| ¿Se repiten enlaces iguales? | v1 crea uno nuevo cada vez; /shorten conserva deduplicación heredada. | Contratos y tests/test_shorten.py. |
| ¿El QR se genera al crear? | Crear devuelve qr_url; el PNG se genera en otra petición GET y no incrementa visitas. | api/v1.py y tests/integration/test_qr.py. |
| ¿Qué significa activo? | is_active=true y sin caducidad o con fecha futura. Inactivo prevalece sobre caducado en lista/resumen. | services.link_to_data y pruebas admin. |
| ¿Reactivar renueva caducidad? | No; un vencido sigue rechazándose hasta quitar/ampliar fecha. | test_reactivation_does_not_bypass_expiration. |
| ¿errors debe ser null? | Se conserva [] en éxito y lista de errores en fallo para no romper clientes. No se atribuye equivalencia aprobada por el docente. | Contrato v1, ADR 0005 y prueba de envelope. |
| ¿Todas las rutas devuelven JSON universal? | v1 y /health sí. PNG y 307 son excepciones por representación HTTP. Rutas heredadas mantienen JSON anterior y errores mixtos documentados. | Contratos. La compatibilidad heredada es una desviación explícita, no una excepción de protocolo. |
| ¿La clave sustituye usuarios/roles? | No; autorización real con clave compartida, solo memoria en la página. No identifica a una persona ni revoca globalmente al hacer logout. | ADR 0004, tests/security, admin.test.mjs. |
| ¿Hay cero datos personales? | No se recopila metadato de visitantes. La URL original ingresada podría contener datos sensibles; el servicio la conserva y el administrador puede verla. | models.py/domain.py. No se garantiza que toda URL arbitraria carezca de PII. |
| ¿Se completaron todas las puertas de la constitución? | No: revisión/ratificación/firma no acreditadas; 410 frente al 404 textual constitucional y frontend JS se conservan por compatibilidad y alcance. | Constitución y contratos. Requiere reconciliación humana, no se enmienda ni simula aprobación. |
| ¿Se cumplieron SC-004 y SC-007 visuales? | No acreditados; medir HTTP loopback no mide presentación visual ni prueba con persona no técnica. | Informes históricos y comprobaciones actuales. |
| ¿Se leyó el PDF oficial? | Sí, texto completo de 11 páginas mediante pypdf; salida UTF-8. | Fuente incorporada en esta continuación del 2026-11-06. Sin render visual Poppler, no disponible. |
| ¿Se declaró el uso de IA? | Se documenta el apoyo de Codex y las verificaciones realizadas; cada estudiante debe explicar y responsabilizarse de su aporte. | docs/evaluacion/uso-ia-y-contribucion.md; PDF pp. 8/10. Reflexiones individuales pendientes. |

Alcance de este cierre: reconciliar documentación/modelos y verificar el incremento
existente; no añadir identidad institucional, servicios externos ni cambios incompatibles.
