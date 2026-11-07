# Datos

Sin tablas, columnas, migraciones ni cambios en registros existentes.
ShortURL conserva código, destino, created_at, expires_at, is_active y click_count.
El resumen se deriva de COUNT/SUM/CASE; no se persiste ni cuenta eventos individuales.
Estados excluyentes: inactive si is_active=false; expired si habilitado y vencido;
active en cualquier otro caso habilitado. La fecha igual a ahora ya está vencida.
total_visits suma todos los contadores, incluidos los de enlaces no utilizables.
La clave permanece en el entorno del servidor y en memoria de la página activa.
No se crea una entidad usuario, sesión persistida, cookie ni registro de claves.
