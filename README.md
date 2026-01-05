# test_githubActions

![Logo de Tecnología](https://img.icons8.com/color/96/000000/technology-items.png)

Este proyecto realiza múltiples tareas útiles: scraping de noticias de tecnología en España, verificación de enlaces rotos en tu sitio, y generación de sitemap.

[The link of the page](http://jorbencasdownloaderdocument.surge.sh)

## Funcionalidades
- **Scraping de noticias**: Extrae títulos y enlaces de Xataka, Genbeta, ComputerHoy y El Español Tech.
- **Checker de enlaces rotos**: Verifica enlaces en https://jorbencas.github.io/blog/ (ajusta BASE_URL si es otro).
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