import os
import json
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

# --- 1. CONFIGURACIÓN ---
CONFIG = {
    "FOLDER": "files"
}

def limpiar_y_validar_historial(historial):
    if not historial: 
        return []
    
    print(f"🧹 Iniciando limpieza y validación ({len(historial)} items)...")
    ahora = datetime.now() 
    
    # --- PASO 1: Eliminar Vídeos y Shorts ---
    # Solo nos quedamos con los que NO tienen 'id_video'
    solo_noticias = [x for x in historial if x.get('id_video') is None]
    vids_eliminados = len(historial) - len(solo_noticias)
    if vids_eliminados > 0:
        print(f"🗑️ Se han eliminado {vids_eliminados} vídeos/shorts del historial.")

    # --- PASO 2: Link Checker (Solo para noticias antiguas) ---
    limite_antiguedad = ahora - timedelta(days=90) # Revisar si tienen > 3 meses
    limite_cache = ahora - timedelta(days=30)      # No re-revisar si se miró hace menos de 1 mes

    items_a_validar = []
    items_intactos = []

    for item in solo_noticias:
        # Reemplazamos la 'Z' por nada si viene de formatos ISO UTC para evitar conflictos de zona horaria naive/aware
        ts_str = item.get('ts', ahora.isoformat()).replace('Z', '')
        try:
            fecha_adicion = datetime.fromisoformat(ts_str)
        except:
            fecha_adicion = ahora

        ultima_verif_str = item.get('ultima_verificacion')
        revisado_recientemente = False
        
        if ultima_verif_str:
            try:
                fecha_v = datetime.fromisoformat(ultima_verif_str.replace('Z', ''))
                if fecha_v > limite_cache:
                    revisado_recientemente = True
            except: 
                pass

        if fecha_adicion < limite_antiguedad and not revisado_recientemente:
            items_a_validar.append(item)
        else:
            items_intactos.append(item)

    if not items_a_validar:
        print("✅ No hay enlaces antiguos que requieran validación.")
        return items_intactos

    print(f"🔍 Validando integridad de {len(items_a_validar)} enlaces antiguos...")

    def chequear(item):
        enlace = item.get('enlace')
        titulo = item.get('titulo', 'Sin título')[:30]
        
        if not enlace:
            return None # Si el elemento no tiene enlace, lo consideramos corrupto y lo eliminamos
            
        try:
            # HEAD es más rápido porque no descarga el contenido, solo la respuesta del servidor
            r = requests.head(enlace, timeout=8, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=True)
            if 400 <= r.status_code < 600:
                print(f"❌ Roto [{r.status_code}]: {titulo}...")
                return None
            
            # Guardamos la fecha de verificación en formato ISO string
            item['ultima_verificacion'] = ahora.isoformat()
            return item
        except requests.RequestException:
            # Si falla la conexión (Timeout, error de DNS, etc.), lo mantenemos por si es algo temporal
            return item 

    # Ejecución en paralelo con un máximo de 20 hilos trabajadores
    with ThreadPoolExecutor(max_workers=20) as executor:
        resultados = list(executor.map(chequear, items_a_validar))

    # Combinamos los que no hacía falta validar junto con los resultados válidos (eliminando los None)
    final = items_intactos + [r for r in resultados if r is not None]
    print(f"✨ Historial saneado. Total actual: {len(final)} noticias.")
    return final

def main():
    # Asegurar que la carpeta contenedora existe antes de operar para evitar errores de escritura
    if not os.path.exists(CONFIG["FOLDER"]):
        os.makedirs(CONFIG["FOLDER"])
        
    archivo_h = os.path.join(CONFIG["FOLDER"], "all_news.json")
    if os.path.exists(archivo_h):
        with open(archivo_h, 'r', encoding='utf-8') as f:
            historial = json.load(f)
    else:
        historial = []
        
    total = limpiar_y_validar_historial(historial)
    
    with open(archivo_h, 'w', encoding='utf-8') as f: 
        # Guardamos acotando a un máximo de 600 elementos como tenías configurado originalmente
        json.dump(total[:600], f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    # Corregido: Llamada directa a main() eliminando la envoltura asíncrona incompatible
    main()
