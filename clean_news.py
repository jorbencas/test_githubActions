"""clean_news.py — Quarterly maintenance: filter videos, validate links."""
import os
import json
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from constants_downloadfile import TIPO_KEY, ENLACE_KEY, TITULO_KEY, TS_KEY, ULTIMA_VERIF_KEY

CONFIG = {
    "FOLDER": "files"
}


def limpiar_y_validar_historial(historial):
    if not historial:
        return []

    print(f"🧹 Iniciando limpieza y validación ({len(historial)} items)...")
    ahora = datetime.now()

    solo_noticias = [x for x in historial if x.get(TIPO_KEY) in ('noticia', None)]
    vids_eliminados = len(historial) - len(solo_noticias)
    if vids_eliminados > 0:
        print(f"🗑️ Eliminados {vids_eliminados} vídeos/shorts (tipo != noticia).")

    limite_antiguedad = ahora - timedelta(days=90)
    limite_cache = ahora - timedelta(days=30)

    items_a_validar = []
    items_intactos = []

    for item in solo_noticias:
        ts_str = item.get(TS_KEY, ahora.isoformat()).replace('Z', '')
        try:
            fecha_adicion = datetime.fromisoformat(ts_str)
        except (ValueError, TypeError):
            fecha_adicion = ahora

        ultima_verif_str = item.get(ULTIMA_VERIF_KEY)
        revisado_recientemente = False

        if ultima_verif_str:
            try:
                fecha_v = datetime.fromisoformat(ultima_verif_str.replace('Z', ''))
                if fecha_v > limite_cache:
                    revisado_recientemente = True
            except (ValueError, TypeError):
                pass

        if fecha_adicion < limite_antiguedad and not revisado_recientemente:
            items_a_validar.append(item)
        else:
            items_intactos.append(item)

    if not items_a_validar:
        print("✅ No hay enlaces antiguos que requieran validación.")
        return items_intactos

    print(f"🔍 Validando {len(items_a_validar)} enlaces antiguos...")

    def chequear(item):
        enlace = item.get(ENLACE_KEY)
        titulo = item.get(TITULO_KEY, 'Sin título')[:30]
        if not enlace:
            return None
        try:
            r = requests.get(enlace, timeout=10,
                             headers={'User-Agent': 'Mozilla/5.0'},
                             allow_redirects=True, stream=True)
            r.close()
            if 400 <= r.status_code < 600:
                print(f"❌ Roto [{r.status_code}]: {titulo}...")
                return None
            item[ULTIMA_VERIF_KEY] = ahora.isoformat()
            return item
        except requests.RequestException:
            return item

    resultados = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futuros = {executor.submit(chequear, i): i for i in items_a_validar}
        for f in as_completed(futuros):
            r = f.result()
            if r is not None:
                resultados.append(r)

    final = items_intactos + resultados
    print(f"✨ Historial saneado. Total actual: {len(final)} noticias.")
    return final


def main():
    os.makedirs(CONFIG["FOLDER"], exist_ok=True)

    ruta = os.path.join(CONFIG["FOLDER"], "noticias_historico.json")

    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            historial = json.load(f)
    else:
        historial = []

    total = limpiar_y_validar_historial(historial)

    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(total[:600], f, indent=4, ensure_ascii=False)

    print(f"💾 Guardados {min(len(total), 600)} items en {ruta}")


if __name__ == "__main__":
    main()
