import os, json, requests, asyncio
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

# --- 1. CONFIGURACIÓN ---
CONFIG = {
    "FOLDER": "files"
}
def limpiar_y_validar_historial(historial):
    if not historial: return []
    
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
    limite_cache = ahora - timedelta(days=30) # No re-revisar si se miró hace poco

    items_a_validar = []
    items_intactos = []

    for item in solo_noticias:
        try:
            fecha_adicion = datetime.fromisoformat(item.get('ts', ahora.isoformat()))
        except:
            fecha_adicion = ahora

        ultima_verif_str = item.get('ultima_verificacion')
        revisado_recientemente = False
        
        if ultima_verif_str:
            try:
                fecha_v = datetime.fromisoformat(ultima_verif_str)
                if fecha_v > limite_cache:
                    revisado_recientemente = True
            except: pass

        if fecha_adicion < limite_antiguedad and not revisado_recientemente:
            items_a_validar.append(item)
        else:
            items_intactos.append(item)

    if not items_a_validar:
        return items_intactos

    print(f"🔍 Validando integridad de {len(items_a_validar)} enlaces antiguos...")

    def chequear(item):
        try:
            # HEAD es más rápido porque no descarga el contenido, solo la respuesta del servidor
            r = requests.head(item['enlace'], timeout=8, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=True)
            if 400 <= r.status_code < 600:
                print(f"❌ Roto [{r.status_code}]: {item['titulo'][:30]}...")
                return None
            item['ultima_verificacion'] = ahora.isoformat()
            return item
        except:
            return item # Si falla la conexión, lo mantenemos por si es algo temporal

    with ThreadPoolExecutor(max_workers=20) as executor:
        resultados = list(executor.map(chequear, items_a_validar))

    final = items_intactos + [r for r in resultados if r is not None]
    print(f"✨ Historial saneado. Total actual: {len(final)} noticias.")
    return final

def main():
    archivo_h = os.path.join(CONFIG["FOLDER"], "all_news.json")
    historial = json.load(open(archivo_h)) if os.path.exists(archivo_h) else []
    total = limpiar_y_validar_historial(historial)
    with open(archivo_h, 'w') as f: json.dump(total[:600], f, indent=4)


if __name__ == "__main__":
    asyncio.run(main())