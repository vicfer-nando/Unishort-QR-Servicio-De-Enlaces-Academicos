# Decisiones de QR

La biblioteca existente `qrcode` genera el símbolo y Pillow serializa el PNG.
La zona de silencio y el tamaño se validan en Settings. OpenCV se usa solo en
pruebas para verificar que el contenido se decodifica como `short_url`.

Un enlace `download` dirigido al puerto de la API puede ignorarse por distinto
origen. Se obtiene el PNG mediante CORS y se descarga una URL Blob del origen
del frontend. La URL efímera se revoca después del clic. No se persiste imagen
ni se solicita a un servicio externo. Ver ADR 0006 y contrato `qr.md`.
