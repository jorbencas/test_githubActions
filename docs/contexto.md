# Contexto — test_githubActions (Jul 2026)

## Cambios recientes

### Dashboard (public/) — 01/07/2026
- Unificados filtros RSS: eliminado "RSS" de FILTRO_BADGE (quedan solo Todas/Tech)
- RSS se maneja exclusivamente como tipo de fuente (FILTRO_TIPO_FUENTE) y filtro específico (news-rss-filters)
- Separados filtros en divs: `.news-section` + `.multimedia-section` (cada uno con sus propios filtros)
- Añadida fecha dinámica en header (`#header-date`)
- Eliminado `badgeNoticias` de las dependencias de `aplicarFiltrosVideos` (era redundante)
- Rendering de YouTube mejorado: se muestran items con `id_video` correctamente

### Scripts nuevos
- `manage_resources.py`: Gestión automática de resources.mdx del blog
  - Añade herramientas nuevas de `herramientas.json` a la sección "Nuevas Herramientas"
  - Paginación automática: cuando resources.mdx > 500 tarjetas, crea resources2.mdx, etc.
  - Usa depth-based HTML parser para manejar divs anidados correctamente
  - Cada archivo mantiene su propio frontmatter y secciones

### Workflows nuevos
- `.github/workflows/daily_resources.yml`: Se ejecuta cada día a las 06:00 UTC
  - Scrapea tools (GitHub Trending + Product Hunt)
  - Ejecuta manage_resources.py contra el blog
  - Crea PR directo al blog (jorbencas/blog)
  
### Fix fix_images.py — 03/07/2026
- Corregido bug donde `fix_images.py` eliminaba `import ResponsiveImage` de posts del blog
- **Causa**: el script borraba el import siempre y solo lo re-agregaba si encontraba `<ResponsiveImage` en el contenido
- **Solución**: nueva lógica condicional:
  - Si componente existe + import falta → agregar import después del frontmatter
  - Si componente NO existe + import existe → eliminar import
  - Si ambos existen → no hacer nada (mantener)
- Commit: `[fix] fix_images.py: preserve ResponsiveImage import when component is used`

## Notas
- El dashboard se despliega en Surge.sh solo los sábados (scraper_workflow.yml)
- Los recursos NO aparecen en el dashboard — van directo al blog vía PR
- manage_resources.py usa el blog checkout en `./blog` (misma estructura que scraper_workflow.yml)
- Límite: 500 tarjetas por archivo resources.mdx (configurable con --max-cards)
