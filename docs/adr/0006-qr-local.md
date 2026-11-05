# ADR 0006: Generación de QR local y descarga mediante Blob

- Estado: decisión existente documentada; revisión del equipo pendiente.
- Fecha: 2026-11-05.

## Contexto

El PNG debe codificar la URL corta sin consultar destinos ni servicios de QR.
La API y la interfaz funcionan en puertos distintos durante la demostración.

## Decisión

Conservar qrcode y Pillow para generar PNG en memoria; OpenCV verifica la
decodificación en desarrollo. Usar fetch y una URL Blob para la descarga del
frontend. Mantener el endpoint con disposición inline para visualizar imagen.

## Alternativas y consecuencias

Un generador externo añade tráfico y exposición innecesaria. Guardar cada PNG
duplica datos derivados. Cambiar siempre a attachment afecta el uso como imagen.
La solución local no añade dependencias, no almacena QR y permite descargar
entre puertos con CORS. La aceptación visual queda pendiente de ejecución.
