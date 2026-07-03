#!/usr/bin/env python3
"""
downloadFile.py — Delegation wrapper for backward compatibility.

Replaced the monolithic scraper. Now delegates to the modular scripts:
  - scrape_news.py      → noticias_historico.json
  - scrape_tools.py     → herramientas.json
  - generate_weekly.py  → dashboard HTML + weekly recap MD
  - send_email.py       → Mailgun newsletter
  - send_telegram.py    → Telegram notification

Usage:
  python downloadFile.py               # run full pipeline
  python downloadFile.py --news-only   # scrape news only
"""

import sys
import logging
import subprocess
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("downloadFile")

SCRIPTS = {
    "news": "scrape_news.py",
    "tools": "scrape_tools.py",
    "weekly": "generate_weekly.py",
    "email": "send_email.py",
    "telegram": "send_telegram.py",
}

def run_script(name, script):
    logger.info(f"🚀 Delegando a {script}...")
    result = subprocess.run(
        [sys.executable, script],
        capture_output=False,
    )
    if result.returncode != 0:
        logger.error(f"❌ {script} falló con código {result.returncode}")
        return False
    logger.info(f"✅ {script} completado")
    return True

def main():
    args = set(sys.argv[1:])
    news_only = "--news-only" in args

    if news_only:
        scripts_to_run = ["news"]
    else:
        scripts_to_run = ["news", "tools", "weekly", "email", "telegram"]

    for key in scripts_to_run:
        if key not in SCRIPTS:
            continue
        script = SCRIPTS[key]
        script_path = os.path.join(os.path.dirname(__file__), script)
        if not os.path.exists(script_path):
            logger.warning(f"⚠️  {script} no encontrado, saltando")
            continue
        if not run_script(key, script_path):
            logger.warning(f"⚠️  Pipeline continuando tras fallo en {script}")

    logger.info("🎯 downloadFile.py — pipeline delegado completado")

if __name__ == "__main__":
    main()
