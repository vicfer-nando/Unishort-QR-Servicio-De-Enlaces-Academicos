# Comprobar QR

Arranque e instalación: [README](../../README.md), secciones 3–6.

1. Abrir `http://localhost:5500` con la API en 8000.
2. Crear un enlace a `http://localhost:5500/?demo=qr`.
3. Comprobar la imagen y pulsar Descargar PNG.
4. Escanear: debe contener `http://localhost:8000/s/{code}`.
5. Consultar métricas con clave admin: obtener QR no suma clics; abrir el
   enlace sí suma uno.

Prueba automática aislada desde raíz: `python scripts/verify_runtime.py`.
Un teléfono necesita una URL pública o IP LAN accesible configurada en
`UNISHORT_BASE_URL`; `localhost` en el teléfono apunta al propio teléfono.
La lectura de contenido del QR también se verifica localmente con OpenCV.
