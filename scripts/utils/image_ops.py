"""
image_ops.py — Utilidades compartidas de imagen (SSIM, metadata, escala).
Centraliza el algoritmo SSIM (Structural Similarity Index) y helpers de
pillow usados por scripts/tools/optimize.py y scripts/tools/fix_images.py.

Import desde un módulo en scripts/*, después de `sys.path.insert` hacia la
raíz de scripts:
    from utils.image_ops import (
        compute_ssim, find_optimal_quality, strip_metadata, constrain_size,
        MAX_WIDTH, SSIM_THRESHOLD, QUALITY_START, QUALITY_MIN, QUALITY_STEP,
    )
"""

from typing import Callable, List, Optional, Tuple

from PIL import Image

# ==============================================================================
# CONSTANTES ALGORÍTMICAS DE COMPRESIÓN SSIM
# ==============================================================================
MAX_WIDTH: int = 1920               # Ancho máximo (constrain_size)
SSIM_THRESHOLD: float = 0.98        # Identidad perceptiva humana
QUALITY_START: int = 85
QUALITY_MIN: int = 50
QUALITY_STEP: int = 5
WEBP_METHOD: int = 6                # Máxima compresión WebP

# Tamaño de cálculo de SSIM (reducción fija para comparación estable)
SSIM_T_SIZE: Tuple[int, int] = (160, 160)


# ==============================================================================
# ALGORITMO SSIM (Pillow-only, sin numpy)
# ==============================================================================
def _channel_stats(
    pixels_a: List[int], pixels_b: List[int], width: int, height: int
) -> Tuple[float, float, float, float, float]:
    """Estadísticas de canal para SSIM: media, varianza y covarianza."""
    n: int = width * height
    if n == 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0
    sum_a: float = 0.0
    sum_b: float = 0.0
    sum_aa: float = 0.0
    sum_bb: float = 0.0
    sum_ab: float = 0.0
    for i in range(n):
        a: int = pixels_a[i]
        b: int = pixels_b[i]
        sum_a += a
        sum_b += b
        sum_aa += a * a
        sum_bb += b * b
        sum_ab += a * b
    m_a: float = sum_a / n
    m_b: float = sum_b / n
    var_a: float = max((sum_aa / n) - (m_a ** 2), 0.0)
    var_b: float = max((sum_bb / n) - (m_b ** 2), 0.0)
    cov_ab: float = (sum_ab / n) - (m_a * m_b)
    return m_a, m_b, var_a, var_b, cov_ab


def compute_ssim(img1: Image.Image, img2: Image.Image) -> float:
    """SSIM en escala de grises entre dos imágenes (0.0-1.0)."""
    C1: float = (0.01 * 255) ** 2
    C2: float = (0.03 * 255) ** 2
    ssim_w: int = SSIM_T_SIZE[0]
    ssim_h: int = SSIM_T_SIZE[1]
    a: Image.Image = img1.convert("L").resize(SSIM_T_SIZE, Image.LANCZOS)
    b: Image.Image = img2.convert("L").resize(SSIM_T_SIZE, Image.LANCZOS)
    px_a: List[int] = list(a.tobytes())
    px_b: List[int] = list(b.tobytes())
    m_a, m_b, v_a, v_b, c_ab = _channel_stats(px_a, px_b, ssim_w, ssim_h)
    num: float = (2 * m_a * m_b + C1) * (2 * c_ab + C2)
    den: float = (m_a ** 2 + m_b ** 2 + C1) * (v_a + v_b + C2)
    return num / den if den != 0.0 else 1.0


# ==============================================================================
# IMAGE PROCESSING (STRIP & CONSTRAIN)
# ==============================================================================
def strip_metadata(img: Image.Image) -> Image.Image:
    """Elimina metadatos creando una imagen nueva del mismo modo/tamaño."""
    clean: Image.Image = Image.new(img.mode, img.size)
    clean.paste(img)
    return clean


def constrain_size(img: Image.Image, max_width: int = MAX_WIDTH) -> Image.Image:
    """Redimensiona si el ancho excede max_width, conservando proporción."""
    if img.width > max_width:
        ratio: float = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    return img


def find_optimal_quality(
    original: Image.Image,
    save_func: Callable[[int], Image.Image],
    start: int = QUALITY_START,
    min_q: int = QUALITY_MIN,
) -> int:
    """Busca la calidad máxima perceptualmente idéntica (descendente)."""
    best_q: int = start
    for q in range(start, min_q - 1, -QUALITY_STEP):
        compressed: Image.Image = save_func(q)
        if compute_ssim(original, compressed) >= SSIM_THRESHOLD:
            best_q = q
        else:
            break
    return best_q
