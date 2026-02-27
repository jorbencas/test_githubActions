import os
import http.server
import socketserver
import webbrowser
import threading
import time
from dotenv import load_dotenv

def run_scraper():
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

def serve_local():
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    # Permitir reutilizar el puerto si cerramos y abrimos rápido
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌍 Servidor local activo en: http://localhost:{PORT}")
        print("💡 Presiona CTRL+C para detener el servidor.")
        
        # Abrir el navegador tras un segundo para dar tiempo al server
        threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido.")
            httpd.server_close()

if __name__ == "__main__":
    # 1. Ejecutar el proceso de descarga/generación de index.html
    run_scraper()
    
    # 2. Servir el resultado
    serve_local()