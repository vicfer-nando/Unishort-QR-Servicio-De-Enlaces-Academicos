# ADR 0007: Eliminación de claves del limitador durante inactividad

- Estado: corrección implementada; revisión de privacidad por dos personas pendiente.
- Fecha: 2026-11-05.

## Contexto

El limitador reiniciaba la ventana de un cliente cuando volvía a solicitar,
pero no eliminaba entradas de clientes que no regresaban. Incumplía el TTL
efímero y podía aumentar indefinidamente la memoria.

## Decisión

Cada ventana tiene un temporizador daemon que elimina su entrada aunque no
haya tráfico. Un temporizador anterior no puede eliminar una ventana nueva.
Reset cancela los temporizadores y los tests controlan reloj y callbacks para
verificar expiración sin esperas. `/shorten` comparte el límite de v1 para
evitar elusión por la ruta heredada.

## Alternativas y consecuencias

Limpiar solo al recibir tráfico conserva claves durante la inactividad.
Redis añade infraestructura innecesaria para la demostración local. Un
temporizador por ventana añade un hilo por cliente activo; no se acredita
capacidad para tráfico masivo. En despliegue institucional se debe aplicar el
límite en un proxy y revisar los límites por trabajador. No hay persistencia,
eventos individuales ni asociación de la clave efímera con enlaces.
