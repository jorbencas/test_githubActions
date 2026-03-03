import os, json, requests, asyncio
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

# --- 1. CONFIGURACIÓN ---
CONFIG = {
    "FOLDER": "files"
}

def limpiar_enlaces_rotos(historial):
    print(f"🧹 Iniciando limpieza de enlaces rotos ({len(historial)} items)...")
    ahora = datetime.now()
    limite_antiguedad = ahora - timedelta(days=90) # 3 meses
    revisar_reciente = ahora - timedelta(days=30)  # No re-revisar si se miró hace poco

    items_a_validar = []
    items_intactos = []

    for item in historial:
        # 1. Convertimos la fecha en que se añadió el link
        # (Asumo que guardas 'fecha_adicion' en formato ISO: YYYY-MM-DD)
        fecha_adicion = datetime.fromisoformat(item.get('ts', ahora.isoformat()))
        ultima_verif = item.get('ultima_verificacion')
        
        # REGLA: ¿Es un link antiguo (> 3 meses)?
        es_antiguo = fecha_adicion < limite_antiguedad
        
        # REGLA DE CACHÉ: ¿Se revisó hace menos de 30 días?
        revisado_hace_poco = False
        if ultima_verif:
            fecha_v = datetime.fromisoformat(ultima_verif)
            if ahora - fecha_v < (ahora - revisar_reciente):
                revisado_hace_poco = True

        # Solo validamos si es antiguo Y no se ha verificado recientemente
        if es_antiguo and not revisado_hace_poco:
            items_a_validar.append(item)
        else:
            items_intactos.append(item)

    print(f"⏩ Omitiendo {len(items_intactos)} enlaces (son recientes o ya verificados).")
    print(f"🔍 Validando {len(items_a_validar)} enlaces de más de 2 meses...")

    if not items_a_validar:
        return historial

    # --- Ejecución rápida con hilos ---
    def chequear(item):
        try:
            r = requests.head(item['enlace'], timeout=8, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=True)
            if r.status_code < 400:
                item['ultima_verificacion'] = ahora.isoformat()
                return item
            else:
                print(f"❌ Roto [{r.status_code}]: {item['titulo']}")
                return None # Eliminado por roto
        except:
            return item 

    with ThreadPoolExecutor(max_workers=20) as executor:
        resultados = list(executor.map(chequear, items_a_validar))
    print(f"✨ Limpieza completada. {enlaces_borrados} enlaces eliminados.")

    return items_intactos + [r for r in resultados if r is not None]


def main():
    archivo_h = os.path.join(CONFIG["FOLDER"], "all_news.json")
    historial = json.load(open(archivo_h)) if os.path.exists(archivo_h) else []
    total = limpiar_enlaces_rotos(historial)
    with open(archivo_h, 'w') as f: json.dump(total[:600], f, indent=4)


if __name__ == "__main__":
    asyncio.run(main())