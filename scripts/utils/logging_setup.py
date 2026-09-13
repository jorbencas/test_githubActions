"""
logging_setup.py — Configuración de logging compartida (DRY/SRP).
Sustituye el bloque duplicado `makedirs + basicConfig` (fichero rotatorio de
5 MB + consola) presente en múltiples módulos de `scripts/`.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
MAX_BYTES = 1024 * 1024 * 5


def setup_logging(log_name: str, log_file: str, logs_dir: str, backup_count: int = 5,
                  level: int = logging.INFO) -> logging.Logger:
    """Configura el logging raíz con un fichero rotatorio y salida a consola.

    Mismo comportamiento que el bloque histórico duplicado en cada módulo:
    `os.makedirs(logs_dir, exist_ok=True)` + `basicConfig` con
    `RotatingFileHandler(maxBytes=5MB, backupCount=N)` y `StreamHandler()`.
    Devuelve el logger nombrado.
    """
    os.makedirs(logs_dir, exist_ok=True)
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[
            RotatingFileHandler(
                os.path.join(logs_dir, log_file),
                maxBytes=MAX_BYTES,
                backupCount=backup_count,
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(log_name)