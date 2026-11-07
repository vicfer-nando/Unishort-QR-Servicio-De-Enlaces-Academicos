# Contribución y evidencia observable

## Estado observado el 2026-11-06

- Rama local: feature/panel-administrativo, HEAD 543701c.
- El panel y el cierre técnico contienen cambios locales aún no confirmados.
- El historial recibido muestra el merge 105e39c de PR #2, feature/martina, y el
  commit 8df95a3 de actualización del backend/dependencias de Martina Alejandra
  Maldonado Machuca. Prueba incorporación de una contribución, no revisión aprobada.
- git shortlog identifica cuatro commits con el nombre Victor Fernando Roa Carrion,
  uno con Victor Fernando Roa Carrión y uno con Martina. Las dos variantes de Victor
  usan el mismo correo en Git; no se presentan como personas distintas.
- CODEOWNERS designa a @vicfer-nando. Esto no prueba una revisión ni aprobación.
- No hay evidencia suficiente para asignar porcentajes de trabajo, horas, asistencia
  o atribuir tareas específicas del panel a una persona mediante nuevos commits.

Estos hechos provienen del historial local. No se reescribe ni fabrica colaboración.

Consulta remota autorizada el 2026-11-06: el
[PR #2](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos/pull/2)
de MartinaMaldonado está fusionado y registra revisión APPROVED de vicfer-nando
del 2026-11-05 a las 13:59:35 UTC (08:59:35 de Ecuador). Esto verifica revisión
de ese PR, no del panel o auditoría sin commit. Para HEAD 543701c el conector
devolvió workflow_runs=[] (solo ejecuciones disparadas por PR, primera página)
y statuses=[] (estados combinados). No cubre todos los check-runs ni prueba
ausencia global de Actions. La consulta pública completa posterior sí verificó
[run 42091635246](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos/actions/runs/42091635246),
evento push, completed/success para 543701c; su trabajo quality aprobó instalación,
pruebas y herramientas. No incluye los cambios locales del panel/auditoría.

## Estrategia equivalente a GitFlow

La inspección ampliada de `git log --all` para el dossier también identifica a
MariaCVR y su commit 0cb3c2d de especificación, en origin/maria-del-cisne y en una
rama archivada, no en main recibido. La consulta remota verifica PR #1 abierto,
no fusionado y con conflictos; sus cambios históricos de seguridad no representan
el contrato actual. Véanse las [fichas individuales](evaluacion/entrega-final/contribuciones-individuales.md)
para evidencias y campos personales pendientes. El recuento anterior se refería
al historial de integración recibido, no a toda contribución en todas las ramas.

Se adopta para este repositorio académico una estrategia de ramas de funcionalidad
y PR a main, con main como integración estable, sin rama develop permanente.
Es una simplificación apropiada para un único incremento sin líneas de versión
concurrentes. El PDF p. 6 admite GitFlow o equivalente justificado. PR #2 y la rama
feature/panel-administrativo constituyen evidencia parcial; documentar la estrategia
ahora no demuestra que todas las ramas o cambios anteriores la hayan seguido.

Las ramas archivo/main-reemplazado y chore/codeowners se conservan; no se eliminan
ni se reordena historia para aparentar un flujo distinto. El panel sigue pendiente
de revisión, commit y PR autorizados por el propietario.

## Flujo propuesto de entrega, todavía no ejecutado

1. Revisar git status y diff conservando la rama actual y las bases ignoradas.
2. Ejecutar pruebas/lint/tipos, preparar Quarto y revisar la matriz de auditoría.
3. Obtener revisión humana de cambios funcionales, seguridad y documentación.
4. Solo con autorización del propietario, hacer commits descriptivos y push de
   la rama; abrir o actualizar PR con evidencia del resultado real.
5. Verificar la ejecución de Actions sobre el SHA que incorpora los cambios.
6. Fusionar siguiendo la revisión acordada. No confundir workflow configurado,
   PR abierto o un commit ajeno con CI aprobada sobre el código de entrega.

La constitución solicita revisiones/ratificación; siguen pendientes cuando no hay
evidencia. Este documento no las concede ni modifica esa gobernanza.
