import sys
import subprocess
import os

def ensure_venv():
    """Asegura que el script se ejecute dentro del entorno virtual .venv."""
    venv_dir = os.path.join(os.path.dirname(__file__), ".venv")
    venv_python = os.path.join(venv_dir, "bin", "python3")
    
    # Si ya estamos en un venv o no existe el .venv, no hacemos nada
    if sys.prefix != sys.base_prefix or not os.path.exists(venv_python):
        return

    print(f"[*] Reiniciando script usando el entorno virtual: {venv_python}")
    try:
        # Re-ejecutamos el script actual usando el python del venv
        os.execv(venv_python, [venv_python] + sys.argv)
    except Exception as e:
        print(f"[!] Error al intentar usar el venv: {e}")
        sys.exit(1)

# --- RE-EJECUCIÓN EN VENV SI ES NECESARIO ---
ensure_venv()

import http.server
import socketserver
import webbrowser
import threading
import time

def instalar_dependencias():
    """Instala las dependencias desde requirements.txt si es necesario."""
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_file):
        print(f"[*] Verificando e instalando dependencias desde {req_file}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        except Exception as e:
            print(f"[!] Error crítico instalando dependencias: {e}")
            sys.exit(1)
    else:
        print("[!] No se encontró requirements.txt. Saltando instalación.")

# --- INICIO: INSTALAR DEPENDENCIAS ---
instalar_dependencias()

def run_scraper():
    from dotenv import load_dotenv
    # Cargamos las variables del .env
    load_dotenv()
    
    # Para evitar que toque 'auto-news', le decimos al script 
    # que no envíe correos ni genere posts (simulando que no hay 'nuevos')
    # O simplemente ejecutamos el script principal. 
    print("🚀 Ejecutando scraper...")
    import downloadFile 
    # Al importar y ejecutar main(), se generará el index.html
    import asyncio
    asyncio.run(downloadFile.main())

if __name__ == "__main__":
    # Ejecutar el proceso de descarga/generación de index.html
    run_scraper()
