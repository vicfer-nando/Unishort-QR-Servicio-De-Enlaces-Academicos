# Datos del QR

No hay entidad persistida de QR. Se reutiliza el enlace existente en
`short_urls`: código, URL original, fecha de creación, estado, expiración y
contador agregado. Su descripción vigente está en `backend/app/models.py`.

Entrada: código. Salida: bytes PNG derivados de `UNISHORT_BASE_URL` y código.
Antes de generar se comprueban existencia, actividad y vencimiento. Consultar
QR no modifica `click_count`. Nunca se codifica la URL de destino en el PNG.
