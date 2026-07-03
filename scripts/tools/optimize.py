"""
optimize.py — Advanced Image & Animation Optimization
======================================================
1. Formats: WebP, AVIF, Progressive JPEG, Quantized PNG, SVG.
2. Animation: Converts GIFs to optimized MP4 and WebM (video format).
3. Quality: SSIM-guided adaptive compression.
4. UX: Auto-resize, metadata stripping.

Uses Pillow (+ pillow-avif-plugin) and FFmpeg.
"""

import hashlib
import json
import math
import os
import shutil
import subprocess
from pathlib import Path
from PIL import Image

try:
    import pillow_avif
except ImportError:
    pillow_avif = None

from scripts.utils.constants_downloadfile import CONFIG

# ───────────────────────── Configuration ─────────────────────────
INPUT_DIR = CONFIG.get("IMAGES_FOLDER", "images")
OUTPUT_DIR = CONFIG.get("IMAGES_PATH_PREFIX", "public/optimizado")
CACHE_FILE = "optimized_cache.json"

MAX_WIDTH = 1920
SSIM_THRESHOLD = 0.98      # Perceptually identical
QUALITY_START = 85
QUALITY_MIN = 50
QUALITY_STEP = 5
WEBP_METHOD = 6            # Best compression

SUPPORTED_RASTER = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
SUPPORTED_GIF = (".gif",)
SUPPORTED_SVG = (".svg",)
ALL_SUPPORTED = SUPPORTED_RASTER + SUPPORTED_GIF + SUPPORTED_SVG


# ───────────────────────── SSIM (Pillow-only) ─────────────────────────
def _channel_stats(pixels_a, pixels_b, width, height):
    n = width * height
    if n == 0: return 0, 0, 0, 0, 0
    sum_a = sum_b = sum_aa = sum_bb = sum_ab = 0
    for i in range(n):
        a, b = pixels_a[i], pixels_b[i]
        sum_a += a; sum_b += b
        sum_aa += a*a; sum_bb += b*b
        sum_ab += a*b
    m_a, m_b = sum_a/n, sum_b/n
    var_a = max((sum_aa/n) - (m_a**2), 0)
    var_b = max((sum_bb/n) - (m_b**2), 0)
    cov_ab = (sum_ab/n) - (m_a*m_b)
    return m_a, m_b, var_a, var_b, cov_ab

def compute_ssim(img1, img2):
    C1, C2 = (0.01*255)**2, (0.03*255)**2
    t_size = (160, 160)
    a = img1.convert("L").resize(t_size, Image.LANCZOS)
    b = img2.convert("L").resize(t_size, Image.LANCZOS)
    px_a, px_b = list(a.tobytes()), list(b.tobytes())
    m_a, m_b, v_a, v_b, c_ab = _channel_stats(px_a, px_b, 160, 160)
    num = (2*m_a*m_b + C1) * (2*c_ab + C2)
    den = (m_a**2 + m_b**2 + C1) * (v_a + v_b + C2)
    return num/den if den != 0 else 1.0


# ───────────────────────── Image Processing ─────────────────────────
def strip_metadata(img):
    clean = Image.new(img.mode, img.size)
    clean.paste(img)
    return clean

def constrain_size(img, max_width=MAX_WIDTH):
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    return img

def find_optimal_quality(original, save_func, start=QUALITY_START, min_q=QUALITY_MIN):
    best_q = start
    for q in range(start, min_q - 1, -QUALITY_STEP):
        compressed = save_func(q)
        if compute_ssim(original, compressed) >= SSIM_THRESHOLD:
            best_q = q
        else:
            break
    return best_q


def optimize_raster(input_path, out_dir, filename):
    img = Image.open(input_path)
    orig_size = os.path.getsize(input_path)
    results = {}
    
    img = constrain_size(img)
    img = strip_metadata(img)
    
    ext = filename.lower().rsplit(".", 1)[-1]
    base = filename.rsplit(".", 1)[0]

    # 1. Optimized Original
    out_path = os.path.join(out_dir, filename)
    if ext in ("jpg", "jpeg"):
        img_rgb = img.convert("RGB")
        def save_jpeg(q):
            img_rgb.save(out_path, format="JPEG", optimize=True, progressive=True, quality=q)
            return Image.open(out_path)
        opt_q = find_optimal_quality(img_rgb, save_jpeg)
        img_rgb.save(out_path, format="JPEG", optimize=True, progressive=True, quality=opt_q)
        results["jpeg"] = {"file": filename, "size": os.path.getsize(out_path), "q": opt_q}
    elif ext == "png":
        has_alpha = img.mode in ("RGBA", "LA", "PA")
        img_save = img.convert("RGBA") if has_alpha else img.convert("RGB")
        colors = img_save.getcolors(maxcolors=256)
        if colors and not has_alpha:
            img_save.quantize(colors=len(colors), method=Image.Quantize.MEDIANCUT).save(out_path, optimize=True)
        else:
            img_save.save(out_path, optimize=True)
        results["png"] = {"file": filename, "size": os.path.getsize(out_path)}

    # 2. WebP
    webp_name = f"{base}.webp"
    webp_path = os.path.join(out_dir, webp_name)
    img_webp = img.convert("RGBA") if img.mode in ("RGBA", "LA", "P") else img.convert("RGB")
    def save_webp(q):
        img_webp.save(webp_path, format="WEBP", quality=q, method=WEBP_METHOD)
        return Image.open(webp_path)
    opt_w = find_optimal_quality(img_webp, save_webp)
    img_webp.save(webp_path, format="WEBP", quality=opt_w, method=WEBP_METHOD)
    results["webp"] = {"file": webp_name, "size": os.path.getsize(webp_path), "q": opt_w}

    # 3. AVIF (if plugin available)
    if pillow_avif:
        avif_name = f"{base}.avif"
        avif_path = os.path.join(out_dir, avif_name)
        def save_avif(q):
            img_webp.save(avif_path, format="AVIF", quality=q, speed=6)
            return Image.open(avif_path)
        opt_a = find_optimal_quality(img_webp, save_avif)
        img_webp.save(avif_path, format="AVIF", quality=opt_a, speed=6)
        results["avif"] = {"file": avif_name, "size": os.path.getsize(avif_path), "q": opt_a}

    print(f"  ✅ {filename}: {orig_size:,}B → WebP={results['webp']['size']:,}B ", end="")
    if "avif" in results: print(f"AVIF={results['avif']['size']:,}B", end="")
    print(f" (ahorro max {(orig_size - min(r['size'] for r in results.values()))/orig_size*100:.1f}%)")
    return results


def optimize_gif(input_path, out_dir, filename):
    orig_size = os.path.getsize(input_path)
    base = filename.rsplit(".", 1)[0]
    out_path_mp4 = os.path.join(out_dir, f"{base}.mp4")
    out_path_webm = os.path.join(out_dir, f"{base}.webm")
    
    # 1. MP4 (H.264)
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-movflags", "faststart", "-pix_fmt", "yuv420p",
        "-vf", "scale='trunc(iw/2)*2:trunc(ih/2)*2'",
        "-c:v", "libx264", "-crf", "23", "-an", out_path_mp4
    ], capture_output=True)
    
    # 2. WebM (VP9)
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0", "-an", out_path_webm
    ], capture_output=True)
    
    # 3. Optimized original GIF as fallback
    shutil.copy2(input_path, os.path.join(out_dir, filename))
    
    results = {
        "mp4": {"file": f"{base}.mp4", "size": os.path.getsize(out_path_mp4)},
        "webm": {"file": f"{base}.webm", "size": os.path.getsize(out_path_webm)},
        "gif": {"file": filename, "size": orig_size}
    }
    
    savings = (orig_size - results["mp4"]["size"]) / orig_size * 100
    print(f"  🎬 {filename} (GIF→Video): {orig_size:,}B → MP4={results['mp4']['size']:,}B (ahorra {savings:.1f}%)")
    return results

def optimize_svg(path, out_dir, filename):
    orig_size = os.path.getsize(path)
    out_path = os.path.join(out_dir, filename)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    import re
    content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
    content = re.sub(r"\s+", " ", content).strip()
    with open(out_path, "w", encoding="utf-8") as f: f.write(content)
    new_size = os.path.getsize(out_path)
    print(f"  ✅ {filename} (SVG): {orig_size:,}B → {new_size:,}B")
    return {"svg": {"file": filename, "size": new_size}}


def main():
    print("="*60 + "\n🖼️  Advanced Optimization Pipeline (Phase 2)\n" + "="*60)
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    try:
        with open(CACHE_FILE, "r") as f: cache = json.load(f)
    except FileNotFoundError: cache = {}
    
    new_cache = {}
    stats = {"orig": 0, "opt": 0, "proc": 0, "skip": 0}

    for filename in sorted(os.listdir(INPUT_DIR)):
        if not filename.lower().endswith(ALL_SUPPORTED): continue
        path = os.path.join(INPUT_DIR, filename)
        if not os.path.isfile(path): continue
        
        with open(path, "rb") as f: f_hash = hashlib.md5(f.read()).hexdigest()
        cached = cache.get(filename)
        if isinstance(cached, dict) and cached.get("hash") == f_hash:
            if all(os.path.exists(os.path.join(OUTPUT_DIR, i["file"])) for i in cached["outputs"].values()):
                new_cache[filename] = cached
                stats["skip"] += 1
                stats["orig"] += cached["original_size"]
                stats["opt"] += min(i["size"] for i in cached["outputs"].values())
                continue

        print(f"\n🔄 Optimizando: {filename}...")
        try:
            ext = filename.lower().rsplit(".", 1)[-1]
            if f".{ext}" in SUPPORTED_GIF: res = optimize_gif(path, OUTPUT_DIR, filename)
            elif f".{ext}" in SUPPORTED_SVG: res = optimize_svg(path, OUTPUT_DIR, filename)
            else: res = optimize_raster(path, OUTPUT_DIR, filename)
            
            new_cache[filename] = {"hash": f_hash, "original_size": os.path.getsize(path), "outputs": res}
            stats["proc"] += 1
            stats["orig"] += new_cache[filename]["original_size"]
            stats["opt"] += min(r["size"] for r in res.values())
        except Exception as e:
            print(f"  ❌ Error: {e}")
            shutil.copy2(path, os.path.join(OUTPUT_DIR, filename))

    with open(CACHE_FILE, "w") as f: json.dump(new_cache, f, indent=4)
    print("\n" + "="*60 + "\n📊 Resumen final")
    print(f"  Procesados: {stats['proc']} | Cache: {stats['skip']}")
    if stats["orig"] > 0:
        print(f"  Ahorro total: {(stats['orig'] - stats['opt'])/stats['orig']*100:.1f}%")
    print("="*60)

if __name__ == "__main__": main()