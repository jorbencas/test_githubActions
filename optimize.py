import hashlib json os Image

# Cargar registro de imágenes ya optimizadas
cache_file = "optimized_cache.json"
try:
    with open(cache_file, "r") as f:
        cache = json.load(f)
except FileNotFoundError:
    cache = {}

for filename in os.listdir(directory):
    if filename.endswith((".jpg", ".png")):
        path = os.path.join(directory, filename)
        
        # Calcular el hash (DNI) del archivo actual
        with open(path, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        if cache.get(filename) == file_hash:
            continue # Si el hash es igual, no hacemos nada

        # Optimizar...
        img = Image.open(path)
        img.save(path, optimize=True, quality=85)
        
        # Actualizar el hash después de optimizar
        with open(path, "rb") as f:
            cache[filename] = hashlib.md5(f.read()).hexdigest()

# Guardar el nuevo registro
with open(cache_file, "w") as f:
    json.dump(cache, f)