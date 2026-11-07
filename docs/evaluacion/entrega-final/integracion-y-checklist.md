# Integración segura y cierre humano

Estos comandos **no se ejecutaron**. Corresponden al propietario después de revisar
el trabajo. La rama actual es feature/panel-administrativo; no cambiar de rama para
guardar los avances. No reescribir historia, forzar push ni borrar bases.

## Revisar y guardar

Desde la raíz, PowerShell:

```powershell
git status --short --branch
git diff --stat
git diff --check
git ls-files '*.db' '*.sqlite' '*.sqlite3' '*.env' '*.pem' '*.key'
```

La última consulta debe quedar vacía para los archivos actuales; `.env.example`
es público y no contiene una clave. Revisar también los archivos nuevos, que no
aparecen en git diff hasta añadirlos. No mostrar una .env real por pantalla.

Tras revisión del equipo, añadir rutas explícitas que incluyen panel, auditoría
y documentación final; los derivados/temporales están ignorados:

```powershell
git add -- .env.example .gitignore README.md CHANGELOG.md .github/workflows backend frontend docker docs quarto scripts specs tests tools/documentation
git add -- "Asignación_Y_Rubrica_Evaluación_Sumativa_1.pdf"
git diff --cached --check
git diff --cached --name-only
git diff --cached --stat
```

Comprobar que no figuren bases, `.env`, `.verification`, node_modules ni HTML
generado. Revisar el diff preparado y los resultados; solo entonces:

```powershell
git commit -m "feat: integrar panel administrativo y preparar entrega sumativa 1"
git push -u origin feature/panel-administrativo
```

El mensaje abarca los cambios funcionales previos y el cierre; el equipo puede
dividirlos en commits coherentes si puede hacerlo sin perder dependencias. No
atribuir el conjunto a integrantes que no lo validaron ni alterar autores.

## PR, CI y Pages

1. Abrir un PR real desde feature/panel-administrativo a main, con resumen y
   resultados efectivos. Pedir revisión humana según la gobernanza del equipo.
2. Comprobar los workflows quality y documentation del **SHA de ese PR**; resolver
   cualquier fallo. CI antiguo de 543701c no satisface esta verificación final.
3. Fusionar por la interfaz cuando se cumplan revisión y checks. El asistente no
   ha hecho merge ni autorizado en nombre del equipo.
4. Configurar/publicar Pages siguiendo [la guía](publicacion-quarto.md); construir
   primero sin publicar, revisar el artefacto y luego ejecutar con publicar=true.
5. Abrir la URL real sin sesión, registrarla y completar el texto EVA. No confundir
   el artefacto de Actions con un portal público permanente.

## Lista final del estudiante

- [ ] Todos los cambios necesarios figuran en main y se anotó el SHA final.
- [ ] Quality y documentation aprobaron ese contenido; se guardaron enlaces reales.
- [ ] Portal abre sin sesión; ocho diagramas visibles; PDF, OpenAPI y dossier accesibles.
- [x] Lista de cinco integrantes y responsabilidades confirmada por el equipo.
- [ ] Se aportaron materiales académicos pendientes y cada persona validó su ficha/reflexión.
- [ ] Se verificó uso de OpenCode/modelo y se revisó la declaración IA.
- [ ] Se obtuvieron capturas auténticas sin claves ni datos sensibles.
- [ ] Se practicó la demo sobre base aislada; Docker se marca probado solo si se ejecutó.
- [ ] Texto EVA contiene enlaces reales y se envió efectivamente por la persona responsable.

Las casillas no se marcan automáticamente por haber redactado este procedimiento.
