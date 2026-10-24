# Ejemplo: publicar un cambio con pull request (0.1.0 -> 0.2.0)

**Estado: NO EJECUTADO todavía.** La rama `mejora/consulta-5s` existe solo en esta laptop. Cada paso de abajo cambia GitHub o Vercel y se hace solo con autorización.

El cambio: el dashboard consulta cada 5 s (antes 2 s) y se pausa con la pestaña oculta. Motivo: el ESP32 publica cada 5 s y la cuota de Vercel se gasta en peticiones sin datos nuevos. Es una mejora compatible, por eso sube MINOR (0.1.0 -> 0.2.0).

Los commits de la rama usan Conventional Commits: `feat:` y `chore:`. Revísalos con `git log --oneline main..mejora/consulta-5s`.

## Pasos

1. **NO EJECUTADO todavía.** Subir la rama:
   `git push -u origin mejora/consulta-5s`
2. **NO EJECUTADO todavía.** Abrir el pull request:
   `gh pr create --base main --head mejora/consulta-5s --title "feat: consultar cada 5 s y pausar con la pestaña oculta" --body-file CHANGELOG.md`
3. **NO EJECUTADO todavía.** Mirar las pruebas: pestaña Actions en GitHub, o `gh pr checks`. Debe quedar en verde.
4. **NO EJECUTADO todavía.** Mirar el despliegue de prueba: Vercel comenta en el PR con una URL de preview. Ábrela, comprueba el pie `v0.2.0` y que `/api/version` devuelva 0.2.0.
5. **NO EJECUTADO todavía.** Fusionar (Vercel despliega main solo):
   `gh pr merge --squash --delete-branch`
6. **NO EJECUTADO todavía.** Actualizar main local y crear el tag:
   `git checkout main && git pull`
   `git tag -a v0.2.0 -m "Versión 0.2.0"`
   `git push origin v0.2.0`
7. **NO EJECUTADO todavía.** Crear el release con sus notas:
   `gh release create v0.2.0 --title "v0.2.0" --notes "Consulta cada 5 s y pausa con la pestaña oculta. Ver CHANGELOG.md."`

## Pendiente de ajustar en el PR
El README aún dice "consulta cada 2 s" (líneas de cuota y de latencia). Corrígelo con un commit `docs:` antes del merge.
