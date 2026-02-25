import hashlib
import json
import os
from PIL import Image

# Configuración
directory = "images"  # Carpeta de entrada
output_dir = "optimizado" # Carpeta de salida
cache_file = "optimized_cache.json"

# Crear carpetas si no existen
os.makedirs(output_dir, exist_ok=True)

# Cargar caché
try:
    with open(cache_file, "r") as f:
        cache = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    cache = {}

new_cache = {}

for filename in os.listdir(directory):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        path = os.path.join(directory, filename)
        output_path = os.path.join(output_dir, filename)
        
        # Calcular hash del archivo original
        with open(path, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        # Si el archivo no ha cambiado, mantenemos el registro y saltamos
        if cache.get(filename) == file_hash and os.path.exists(output_path):
            new_cache[filename] = file_hash
            continue

        print(f"Optimizando: {filename}...")
        try:
            img = Image.open(path)
            # Convertir a RGB si es necesario (evita errores con RGBA en JPEG)
            if img.mode in ("RGBA", "P") and filename.lower().endswith(".jpg"):
                img = img.convert("RGB")
            
            img.save(output_path, optimize=True, quality=85)
            new_cache[filename] = file_hash # Guardamos el hash del original
        except Exception as e:
            print(f"Error procesando {filename}: {e}")

# Guardar el nuevo registro de caché
with open(cache_file, "w") as f:
    json.dump(new_cache, f, indent=4)