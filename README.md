# test_githubActions

![Logo de Tecnología](./image.png)

Este proyecto realiza múltiples tareas útiles: scraping de noticias de tecnología en España, verificación de enlaces rotos en tu sitio, y generación de sitemap.

<a href="http://jorbencasdownloaderdocument.surge.sh" target="_blank">The link of the page</a>

## Funcionalidades
- **Scraping de noticias**: Extrae títulos y enlaces de Xataka, Genbeta, ComputerHoy y El Español Tech.
- **Checker de enlaces rotos**: Verifica enlaces en https://blog-jorbencas.vercel.app/ (ajusta BASE_URL si es otro).
- **Generador de sitemap**: Crea sitemap.xml con enlaces encontrados.

## Instalación
- Clona el repo.
- Ejecuta `pip install requests beautifulsoup4`.
- Corre el script: `python downloadFile.py`.

## Fuentes scrapeadas
- Xataka
- Genbeta
- ComputerHoy
- El Español Tech