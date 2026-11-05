# ADR 002: Estrategia de Autenticación, Autorización y Protección de Datos

* **Estado:** Aprobado
* **Fecha:** 2026-11-05
* **Autores:** MariaCVR, vicfer-nando

## Contexto
La Práctica 004 requiere asegurar los endpoints del servicio Unishort frente a accesos no autorizados, datos malformados y fuga de secretos.

## Decisión
1. **Autenticación:** Implementar validación mediante API Key en la cabecera HTTP `X-API-Key` para operaciones administrativas (`POST /shorten`).
2. **Autorización:** El acceso anónimo se limita exclusivamente a la redirección (`GET /s/{short_code}`).
3. **Validación de Datos:** Uso de schemas Pydantic (`HttpUrl`) para validación sintáctica y reglas de negocio para impedir URLs duplicadas.
4. **Protección de Secretos:** Configuración mediante variables de entorno (`.env`) excluidas de Git.

## Consecuencias
* **Positivas:** Control de acceso liviano sin sobrecarga de base de datos, aislamiento de claves privadas y respuestas estandarizadas.
* **Restricciones:** En producción se migrará a tokens JWT expirables.