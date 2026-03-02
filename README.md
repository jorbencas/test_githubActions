# 🛰️ test_githubActions

![Build Status](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/scraper_workflow.yml?branch=master&style=flat-square&label=Estado&logo=github)
![GitHub last commit](https://img.shields.io/github/last-commit/jorbencas/test_githubActions?style=flat-square&logo=git&label=Último%20cambio)
![Surge Status](https://img.shields.io/badge/Surge-Live-blue?style=flat-square&logo=vercel)

![Logo de Tecnología](./public/optimizado/Image.png)

Este es un ecosistema automatizado de noticias tech. El sistema no solo recopila información, sino que la procesa mediante **Inteligencia Artificial** para ofrecerte lo más relevante de forma digerida y multicanal.

🚀 **[Ver Dashboard de Noticias](http://jorbencasdownloaderdocument.surge.sh)**

---

## 🛠️ Super-Funcionalidades

* **🤖 Análisis con IA (Gemini Pro):** Genera resúmenes profesionales de las noticias recolectadas para que no tengas que leerlas todas.
* **🌍 Traducción Inteligente:** Todas las fuentes (incluso vídeos en inglés) se traducen automáticamente al castellano usando `mtranslate`.
* **📺 Multimedia Dashboard:** Genera una web estática en Surge con una galería visual de los últimos vídeos de YouTube y una lista de artículos.
* **📩 Notificaciones Multicanal:**
    * **Telegram:** Reportes estructurados con iconos, nombres de canal y fechas de publicación.
    * **Email:** Resumen IA enviado a través de Mailgun, optimizado con técnicas anti-spam para Gmail.
* **🚀 Auto-Publicación:** Crea automáticamente archivos Markdown (`.md`) limpios para tu blog en **Astro/Vercel**.
* **🔗 Checker de Enlaces:** Verifica la salud de los links en [blog-jorbencas.vercel.app](https://blog-jorbencas.vercel.app/).

## ⚙️ Configuración (Secrets de GitHub)

Para que el proyecto funcione en GitHub Actions, debes configurar los siguientes `Secrets` en tu repositorio:

| Secret | Descripción |
| :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | El token de tu bot de @BotFather |
| `TELEGRAM_CHAT_ID` | El ID del chat o grupo (ej: `-100...`) |
| `GEMINI_API_KEY` | Tu API Key de Google AI Studio |
| `MAILGUN_API_KEY` | Tu API Key de Mailgun |
| `MAILGUN_DOMAIN` | Tu dominio configurado en Mailgun |
| `EMAIL_USER` | Tu dirección de correo de destino |

---

## 🚀 Instalación y Uso Local

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/jorbencas/test_githubActions.git
    ```
2.  **Instalar dependencias:**
    ```bash
    pip install requests beautifulsoup4 google-generativeai mtranslate
    ```
3.  **Ejecutar el script:**
    ```bash
    python downloadFile.py
    ```

---

## 🤖 Flujo de Automatización

El proyecto utiliza **GitHub Actions** para ejecutarse de forma autónoma:
1.  **Cron Job:** Se dispara según el horario configurado en `.github/workflows/scraper_workflow.yml`.
2.  **Verificación de Cambios:** El flujo incluye una protección de Git que evita errores de "commit vacío". Si no hay noticias nuevas, el sistema termina la tarea sin realizar cambios en el repositorio.
3.  **Despliegue:** Al detectar novedades, actualiza el `index.html` en Surge y genera el nuevo post para Vercel.

---
*Mantenido por **[Jorge (@jorbencas)](https://github.com/jorbencas)***