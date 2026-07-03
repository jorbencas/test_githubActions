#!/usr/bin/env python3
"""
make_cover_collage.py — Genera portadas compuestas para proyectos/herramientas del blog.

Modos de uso:

  # CI: escanea content/ y genera portadas faltantes
  python scripts/make_cover_collage.py --ci

  # Proyecto externo (Tech Pulse)
  python scripts/make_cover_collage.py --url URL --output public/img/proyecto_cover

  # Tool del blog (diagramas desde frontmatter MDX)
  python scripts/make_cover_collage.py --mdx RUTA.mdx --output public/img/tool_cover

  # Screenshots locales con dev server + ruta
  python scripts/make_cover_collage.py --route /tools/extractor --dev-server --output public/img/tool_cover

  # Desde imágenes existentes
  python scripts/make_cover_collage.py --images a.png b.png c.png --output public/img/proyecto_cover
"""
import argparse, json, re, sys, subprocess, time, asyncio, textwrap
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from io import BytesIO
from random import uniform

from PIL import Image, ImageDraw, ImageFont

import argparse
_argv_blog_path = None
for i, a in enumerate(list(__import__("sys").argv)):
    if a == "--blog-path" and i + 1 < len(__import__("sys").argv):
        _argv_blog_path = __import__("sys").argv[i + 1]
        break
ROOT = Path(_argv_blog_path).resolve() if _argv_blog_path else Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from fix_images import compress_and_save_adaptive, IMG_DIR, SIZES, slugify

CANVAS_W = 1400
CANVAS_H = 900
GAP = 10
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = FONT_PATHS if bold else [FONT_PATHS[1]] if len(FONT_PATHS) > 1 else FONT_PATHS
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _parse_mdx_frontmatter(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        content = f.read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not m:
        return {"title": Path(path).stem, "description": "", "tags": []}
    fm = m.group(1)
    def get(key: str) -> str:
        p = re.search(rf"^{key}:\s*['\"]?(.+?)['\"]?\s*$", fm, re.MULTILINE)
        return p.group(1).strip() if p else ""
    tags_raw = re.search(r"tags:\s*\[(.*?)\]", fm, re.DOTALL)
    tags = [t.strip().strip("\"'") for t in tags_raw.group(1).split(",")] if tags_raw else []
    body = content[m.end():].strip()
    return {
        "title": get("title"),
        "description": get("description"),
        "tags": tags,
        "body": body[:500],
        "url": get("url"),
        "component": get("component"),
        "image": get("image"),
    }


# =====================================================================
# SOURCE PROVIDERS
# =====================================================================

class SourceProvider(ABC):
    @abstractmethod
    def get_images(self) -> list[Image.Image]: ...


class PlaywrightProvider(SourceProvider):
    """Captura 3 screenshots de una URL usando Playwright vía Node.js helper."""

    _script_dir = Path(__file__).resolve().parent
    HELPER = _script_dir / "screenshot_helper.mjs"

    def __init__(self, url: str, actions_json: Optional[str] = None):
        self.url = url
        self.actions = json.loads(actions_json) if actions_json else []

    def get_images(self) -> list[Image.Image]:
        tmp_dir = Path("/tmp/opencode")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        out1 = str(tmp_dir / "collage_1.png")
        out2 = str(tmp_dir / "collage_2.png")
        out3 = str(tmp_dir / "collage_3.png")

        try:
            subprocess.run(
                ["node", str(self.HELPER), self.url, out1, out2, out3],
                check=True, timeout=60, cwd=ROOT,
            )
        except Exception as e:
            raise RuntimeError(f"Error al capturar {self.url}: {e}")

        images = [Image.open(p).convert("RGB") for p in [out1, out2, out3]]
        return images


class FileProvider(SourceProvider):
    def __init__(self, paths: list[str]):
        self.paths = paths

    def get_images(self) -> list[Image.Image]:
        return [Image.open(p).convert("RGB") for p in self.paths]


class PillowDiagramProvider(SourceProvider):
    """Genera 3 diagramas visuales desde un MDX usando solo Pillow."""

    BG = "#0f141c"
    ACCENT = "#00f2fe"
    CARD_BG = "#1e293b"
    TEXT_COLOR = "#f1f5f9"
    SUB_COLOR = "#94a3b8"
    W = 1400
    H = 900

    def __init__(self, mdx_path: str):
        self.data = _parse_mdx_frontmatter(mdx_path)
        self.title = self.data["title"]
        self.desc = self.data["description"]
        self.tags = self.data["tags"]

    def _draw_card(self, draw, x, y, w, h, fill=CARD_BG, border=None):
        draw.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=fill,
                               outline=border or self.ACCENT, width=1 if border else 0)

    def _diagram_architecture(self) -> Image.Image:
        """Title + description + large central box with stack tags."""
        img = Image.new("RGB", (self.W, self.H), self.BG)
        draw = ImageDraw.Draw(img)
        f_title = _load_font(42, bold=True)
        f_sub = _load_font(22)
        f_body = _load_font(18)
        f_tag = _load_font(16, bold=True)

        # Title
        draw.text((60, 50), self.title, font=f_title, fill=self.TEXT_COLOR)
        # Accent line
        draw.rectangle([60, 115, 400, 123], fill=self.ACCENT)

        # Description
        y_desc = 155
        for line in textwrap.wrap(self.desc[:200], width=55):
            draw.text((60, y_desc), line, font=f_body, fill=self.SUB_COLOR)
            y_desc += 30

        # Central architecture box
        box_x, box_y, box_w, box_h = 100, 280, self.W - 200, 400
        self._draw_card(draw, box_x, box_y, box_w, box_h, fill="#1a2332")
        draw.text((box_x + 40, box_y + 30), "ARQUITECTURA", font=f_sub, fill=self.ACCENT)
        draw.text((box_x + 40, box_y + 80),
                  textwrap.fill(self.desc[:300], width=60),
                  font=f_body, fill=self.SUB_COLOR)

        # Tags as badges at bottom of box
        y_tags = box_y + box_h - 80
        x_tags = box_x + 40
        for tag in self.tags[:6]:
            tw = draw.textbbox((0, 0), tag.upper(), font=f_tag)[2] + 30
            if x_tags + tw > box_x + box_w - 40:
                x_tags = box_x + 40
                y_tags += 45
            draw.rounded_rectangle([x_tags, y_tags, x_tags + tw, y_tags + 36],
                                   radius=6, fill="#0f141c", outline=self.ACCENT, width=1)
            draw.text((x_tags + 15, y_tags + 6), tag.upper(), font=f_tag, fill=self.ACCENT)
            x_tags += tw + 12

        return img

    def _diagram_flow(self) -> Image.Image:
        """Flow/process diagram with 3-5 steps."""
        img = Image.new("RGB", (self.W, self.H), self.BG)
        draw = ImageDraw.Draw(img)
        f_sub = _load_font(24, bold=True)
        f_body = _load_font(18)

        steps = [
            ("ENTRADA", "Datos / Petición", self.ACCENT),
            ("PROCESO", "Lógica principal", "#38bdf8"),
            ("IA / API", "Gemini / externa", "#a78bfa"),
            ("SALIDA", "Resultado formateado", "#34d399"),
        ]

        box_w = 280
        box_h = 200
        total_w = len(steps) * box_w + (len(steps) - 1) * 60
        start_x = (self.W - total_w) // 2
        y_center = (self.H - box_h) // 2

        for i, (step_title, step_desc, color) in enumerate(steps):
            x = start_x + i * (box_w + 60)
            self._draw_card(draw, x, y_center, box_w, box_h, fill="#1a2332", border=color)
            draw.text((x + 20, y_center + 20), step_title, font=f_sub, fill=color)
            draw.text((x + 20, y_center + 70), step_desc, font=f_body, fill=self.SUB_COLOR)
            draw.text((x + 20, y_center + 110), textwrap.fill(self.desc[:100], width=25),
                      font=_load_font(14), fill="#475569")

            # Arrow between boxes
            if i < len(steps) - 1:
                ax = x + box_w
                ay = y_center + box_h // 2
                arrow_length = 40
                draw.line([(ax + 10, ay), (ax + arrow_length, ay)], fill="#475569", width=3)
                draw.polygon([(ax + arrow_length + 5, ay),
                              (ax + arrow_length - 5, ay - 6),
                              (ax + arrow_length - 5, ay + 6)], fill="#475569")

        return img

    def _diagram_stack(self) -> Image.Image:
        """Tech stack badges with section title."""
        img = Image.new("RGB", (self.W, self.H), self.BG)
        draw = ImageDraw.Draw(img)
        f_title = _load_font(36, bold=True)
        f_tag = _load_font(20, bold=True)

        draw.text((60, 50), "STACK TECNOLÓGICO", font=f_title, fill=self.TEXT_COLOR)
        draw.rectangle([60, 110, 450, 118], fill=self.ACCENT)

        colors = [self.ACCENT, "#38bdf8", "#a78bfa", "#f472b6", "#34d399", "#fbbf24"]
        rows = [self.tags[i:i + 4] for i in range(0, len(self.tags), 4)]
        y_start = 180
        for ri, row in enumerate(rows):
            x = 80
            y = y_start + ri * 80
            for ci, tag in enumerate(row):
                c = colors[(ri * 4 + ci) % len(colors)]
                tw = draw.textbbox((0, 0), tag.upper(), font=f_tag)[2] + 40
                th = 50
                self._draw_card(draw, x, y, tw, th, fill="#1a2332", border=c)
                # Glow effect: smaller filled rect
                draw.rounded_rectangle([x + 4, y + 4, x + tw - 4, y + th - 4],
                                       radius=8, fill="#1e293b")
                draw.text((x + tw // 2 - draw.textbbox((0, 0), tag.upper(), font=f_tag)[2] // 2,
                          y + th // 2 - 12), tag.upper(), font=f_tag, fill=c)
                x += tw + 20

        # Bottom: project info card
        if self.desc:
            f_body = _load_font(18)
            y_info = y_start + len(rows) * 80 + 60
            self._draw_card(draw, 60, y_info, self.W - 120, 160, fill="#1a2332")
            draw.text((100, y_info + 20), "DESCRIPCIÓN", font=_load_font(20, bold=True), fill=self.ACCENT)
            for i, line in enumerate(textwrap.wrap(self.desc[:300], width=70)):
                draw.text((100, y_info + 60 + i * 30), line, font=f_body, fill=self.SUB_COLOR)

        return img

    def get_images(self) -> list[Image.Image]:
        return [self._diagram_architecture(), self._diagram_flow(), self._diagram_stack()]


class DevServerRouteProvider(SourceProvider):
    """Arranca npm run dev y captura screenshots de una ruta local."""

    def __init__(self, route: str):
        self.route = route

    def get_images(self) -> list[Image.Image]:
        proc = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            # Wait for server to be ready
            import socket
            for _ in range(60):
                time.sleep(1)
                try:
                    s = socket.socket()
                    s.connect(("localhost", 4321))
                    s.close()
                    break
                except ConnectionRefusedError:
                    continue
            else:
                raise RuntimeError("Dev server did not start in 60s")

            provider = PlaywrightProvider(f"http://localhost:4321{self.route}")
            return provider.get_images()
        finally:
            proc.terminate()
            proc.wait(timeout=5)


# =====================================================================
# LAYOUT STRATEGIES
# =====================================================================

class LayoutStrategy(ABC):
    @abstractmethod
    def compose(self, images: list[Image.Image]) -> Image.Image: ...


class LeftBigRightStackedLayout(LayoutStrategy):
    """1 imagen grande izquierda + 2 apiladas derecha. Canvas 1400×900.
    
    Si mecano_style=True, las imágenes se rotan ligeramente y se reducen
    de tamaño para imitar la estética del collage de Mecano.
    """

    def __init__(self, mecano_style: bool = False):
        self.mecano = mecano_style

    def _paste_rotated(self, canvas: Image.Image, img: Image.Image,
                       cx: int, cy: int, tw: int, th: int,
                       angle: float, crop_top: int = 0) -> Image.Image:
        """Redimensiona, rota y pega una imagen centrada en (cx, cy)."""
        bg_color = "#0f141c"
        img = img.convert("RGB")
        src_h = img.height - crop_top
        if src_h <= 0:
            crop_top = 0
            src_h = img.height
        r = max(tw / img.width, th / src_h)
        nw = int(img.width * r)
        nh = int(src_h * r)
        img = img.resize((nw, nh), Image.LANCZOS)
        left = (nw - tw) // 2
        top = (nh - th) // 2
        img = img.crop((left, top, left + tw, top + th))

        # Shadow as RGBA
        shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle(
            [6, 6, tw - 6, th - 6], radius=6, fill=(0, 0, 0, 90)
        )

        # Rotate
        shadow_rot = shadow.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0))
        img_rot = img.rotate(angle, expand=True, fillcolor=bg_color)

        # Paste position (centered)
        sw, sh = img_rot.size
        px = cx - sw // 2
        py = cy - sh // 2

        # Work in RGBA for proper shadow compositing
        canvas_rgba = canvas.convert("RGBA")
        canvas_rgba.alpha_composite(shadow_rot, (px + 3, py + 5))
        canvas_rgba.paste(img_rot, (px, py))
        return canvas_rgba.convert("RGB")

    def compose(self, images: list[Image.Image]) -> Image.Image:
        if len(images) < 3:
            raise ValueError(f"Se necesitan 3 imágenes, se recibieron {len(images)}")

        canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), "#0f141c")

        if self.mecano:
            # Mecano style: smaller panels with slight rotation
            # Left/main panel — slightly tilted left
            left_angle = uniform(-3.0, 0.0)
            left_cx, left_cy = 420, 430
            left_tw, left_th = 700, 660
            canvas = self._paste_rotated(canvas, images[0],
                                         left_cx, left_cy, left_tw, left_th,
                                         angle=left_angle, crop_top=80)

            # Right-top panel — tilted right
            rt_angle = uniform(1.5, 4.5)
            rt_cx, rt_cy = 1120, 200
            rt_tw, rt_th = 500, 340
            canvas = self._paste_rotated(canvas, images[1],
                                         rt_cx, rt_cy, rt_tw, rt_th,
                                         angle=rt_angle)

            # Right-bottom panel — tilted left
            rb_angle = uniform(-3.5, 0.0)
            rb_cx, rb_cy = 1090, 670
            rb_tw, rb_th = 480, 370
            canvas = self._paste_rotated(canvas, images[2],
                                         rb_cx, rb_cy, rb_tw, rb_th,
                                         angle=rb_angle)

            return canvas

        # Original (non-rotated) layout
        gap = GAP
        left_w = 910
        right_w = CANVAS_W - left_w - gap
        right_h = (CANVAS_H - gap * 2) // 2
        left_h = CANVAS_H - gap * 2

        def fit(img: Image.Image, tw: int, th: int, crop_top: int = 0) -> Image.Image:
            img = img.convert("RGB")
            src_h = img.height - crop_top
            if src_h <= 0:
                crop_top = 0
                src_h = img.height
            r = max(tw / img.width, th / src_h)
            nw = int(img.width * r)
            nh = int(src_h * r)
            img = img.resize((nw, nh), Image.LANCZOS)
            left = (nw - tw) // 2
            top = (nh - th) // 2
            return img.crop((left, top, left + tw, top + th))

        draw = ImageDraw.Draw(canvas)
        left_img = fit(images[0], left_w, left_h, crop_top=80)
        canvas.paste(left_img, (gap, gap))
        draw.rectangle([gap, gap, left_w + gap, left_h + gap], outline="#1e293b", width=1)

        rt_img = fit(images[1], right_w, right_h)
        canvas.paste(rt_img, (left_w + gap * 2, gap))
        draw.rectangle([left_w + gap * 2, gap, left_w + gap * 2 + right_w, gap + right_h],
                       outline="#1e293b", width=1)

        rb_img = fit(images[2], right_w, right_h)
        canvas.paste(rb_img, (left_w + gap * 2, gap + right_h + gap))
        draw.rectangle([left_w + gap * 2, gap + right_h + gap,
                        left_w + gap * 2 + right_w, CANVAS_H - gap],
                       outline="#1e293b", width=1)

        return canvas


class ThreeInRowLayout(LayoutStrategy):
    """3 imágenes del mismo tamaño en fila horizontal."""

    def compose(self, images: list[Image.Image]) -> Image.Image:
        if len(images) < 3:
            raise ValueError(f"Se necesitan 3 imágenes, se recibieron {len(images)}")

        canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), "#0f141c")
        gap = GAP
        w = (CANVAS_W - gap * 4) // 3
        h = CANVAS_H - gap * 2

        for i, img in enumerate(images[:3]):
            img = img.convert("RGB")
            r = max(w / img.width, h / img.height)
            img = img.resize((int(img.width * r), int(img.height * r)), Image.LANCZOS)
            left = (img.width - w) // 2
            top = (img.height - h) // 2
            cropped = img.crop((left, top, left + w, top + h))
            x = gap + i * (w + gap)
            canvas.paste(cropped, (x, gap))

        return canvas


LAYOUTS = {
    "left-big-right-stacked": LeftBigRightStackedLayout,
    "three-in-row": ThreeInRowLayout,
}


# =====================================================================
# IMAGE EXPORTER
# =====================================================================

class ImageExporter:
    """Exporta el collage como PNG + variantes WebP/AVIF vía fix_images."""

    def __init__(self, output_base: str, dry_run: bool = False):
        self.output_path = Path(output_base)
        self.folder = self.output_path.parent
        self.base_name = self.output_path.name
        self.dry_run = dry_run

    def export(self, canvas: Image.Image) -> str:
        # Save master PNG
        master_path = self.folder / f"{self.base_name}.png"
        if not self.dry_run:
            self.folder.mkdir(parents=True, exist_ok=True)
            canvas.save(master_path, "PNG")
            print(f"  ✓ Master PNG: {master_path}")

            # Remove existing variants to avoid stale files
            for f in list(self.folder.iterdir()):
                if f.stem.startswith(self.base_name) and f.suffix in (".webp", ".avif"):
                    f.unlink()

            # Generate compressed variants via fix_images pipeline
            avif, webp, blur = compress_and_save_adaptive(canvas, self.base_name, self.folder)
            for name, size in webp:
                print(f"  ✓ {name} ({size}w)")
            for name, size in avif:
                print(f"  ✓ {name} ({size}w)")
            print(f"  ✓ Blur placeholder generated")
        else:
            print(f"  [dry-run] Master PNG: {master_path}")
            for s in SIZES:
                print(f"  [dry-run] {self.base_name}-{s}.webp + .avif")

        return str(master_path)


# =====================================================================
# CI MODE (scans content, generates missing covers)
# =====================================================================

def _update_image_field(mdx_path: Path, new_image: str) -> bool:
    """Reemplaza la línea `image:` en frontmatter con la nueva ruta."""
    with open(mdx_path, encoding="utf-8") as f:
        content = f.read()

    # Check if the image line already has the correct value
    m_img = re.search(r'^image:\s*["\'](.+?)["\']\s*$', content, re.MULTILINE)
    if m_img and m_img.group(1) == new_image:
        return False  # Already up to date

    new_content = re.sub(
        r'^(image:\s*)["\'].*?["\']\s*$',
        rf'\1"{new_image}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if new_content == content:
        # No existing image line — add it after the title/description block
        m = re.match(r"^(---.*?\n)(.*?)(\n---)", content, re.DOTALL)
        if m:
            # Insert image after the tags line or at the end of frontmatter
            inserted = False
            lines = m.group(2).split("\n")
            for i, line in enumerate(lines):
                if line.strip().startswith("tags:"):
                    lines.insert(i + 1, f'image: "{new_image}"')
                    inserted = True
                    break
            if not inserted:
                lines.append(f'image: "{new_image}"')
            new_front = "\n".join(lines)
            new_content = m.group(1) + new_front + m.group(3) + content[m.end():]
        else:
            return False

    with open(mdx_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def ci_mode(force: bool = False, dry_run: bool = False) -> int:
    """
    Recorre src/content/myprojects/ y src/content/tools/.
    Para cada MDX sin portada real, genera collage/diagrama
    y actualiza el frontmatter.
    Retorna el número de archivos procesados.
    """
    processed = 0
    content_dir = ROOT / "src" / "content"

    # Helper: comprueba si una portada ya existe
    def cover_exists(base_name: str) -> bool:
        return (IMG_DIR / f"{base_name}-1200.webp").exists()

    # 1. Projects with live URL → Playwright
    projects_dir = content_dir / "myprojects"
    if projects_dir.exists():
        for mdx in sorted(projects_dir.rglob("*.mdx")):
            data = _parse_mdx_frontmatter(str(mdx))
            url = data.get("url")
            if not url:
                continue
            base_name = slugify(mdx.stem) + "_cover"
            if cover_exists(base_name) and not force:
                continue

            if dry_run:
                print(f"  [dry-run] {data['title']} → collage desde {url}")
                processed += 1
                continue

            print(f"\n📸 {data['title']}")
            print(f"   URL: {url}")
            try:
                provider = PlaywrightProvider(url)
                images = provider.get_images()
                layout = LeftBigRightStackedLayout(mecano_style=True)
                canvas = layout.compose(images)
                exporter = ImageExporter(str(IMG_DIR / base_name))
                exporter.export(canvas)
                # Update frontmatter
                _update_image_field(mdx, f"img/{base_name}-1200.webp")
                print(f"   ✓ Frontmatter actualizado en {mdx.name}")
                processed += 1
            except Exception as e:
                print(f"   ✗ Error: {e}")

    # 2. Tools → Pillow diagrams
    tools_dir = content_dir / "tools"
    if tools_dir.exists():
        for mdx in sorted(tools_dir.rglob("*.mdx")):
            data = _parse_mdx_frontmatter(str(mdx))
            base_name = slugify(mdx.stem) + "_cover"
            if cover_exists(base_name) and not force:
                continue

            if dry_run:
                print(f"  [dry-run] {data['title']} → diagramas")
                processed += 1
                continue

            print(f"\n📐 {data['title']}")
            try:
                provider = PillowDiagramProvider(str(mdx))
                images = provider.get_images()
                layout = LeftBigRightStackedLayout()
                canvas = layout.compose(images)
                exporter = ImageExporter(str(IMG_DIR / base_name))
                exporter.export(canvas)
                _update_image_field(mdx, f"img/{base_name}-1200.webp")
                print(f"   ✓ Frontmatter actualizado en {mdx.name}")
                processed += 1
            except Exception as e:
                print(f"   ✗ Error: {e}")

    return processed


# =====================================================================
# CLI
# =====================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Genera portadas compuestas para proyectos/herramientas del blog"
    )
    parser.add_argument("--blog-path", help="Ruta al blog (ya procesado por script)")
    parser.add_argument("--ci", action="store_true",
                        help="Modo CI: escanea content/ y genera portadas faltantes")
    parser.add_argument("--url", help="URL externa para capturar screenshots")
    parser.add_argument("--route", help="Ruta local (con --dev-server) para capturar")
    parser.add_argument("--mdx", help="Archivo MDX del cual generar diagramas")
    parser.add_argument("--images", nargs="+", help="3 imágenes ya existentes")
    parser.add_argument("--output", "-o",
                        help="Base path de salida (ej: public/img/proyecto_cover)")
    parser.add_argument("--layout", default="left-big-right-stacked",
                        choices=list(LAYOUTS.keys()),
                        help="Layout del collage (default: left-big-right-stacked)")
    parser.add_argument("--mecano", action="store_true",
                        help="Estilo Mecano: paneles más pequeños, rotados ligeramente y con sombra")
    parser.add_argument("--dev-server", action="store_true",
                        help="Arranca npm run dev automáticamente (para --route)")
    parser.add_argument("--actions", help="JSON con acciones para Playwright")
    parser.add_argument("--dry-run", action="store_true",
                        help="Solo muestra lo que haría sin ejecutar")
    parser.add_argument("--force", action="store_true",
                        help="Regenera portadas aunque ya existan")
    args = parser.parse_args()

    # CI mode
    if args.ci:
        n = ci_mode(force=args.force, dry_run=args.dry_run)
        print(f"\n✅ CI mode: {n} portadas generadas/actualizadas")
        return

    # Manual mode — require --output
    if not args.output:
        parser.error("Modo manual requiere --output")

    # Build source provider
    provider: SourceProvider
    if args.url:
        provider = PlaywrightProvider(args.url, args.actions)
    elif args.route:
        if args.dev_server:
            provider = DevServerRouteProvider(args.route)
        else:
            provider = PlaywrightProvider(f"http://localhost:4321{args.route}", args.actions)
    elif args.mdx:
        provider = PillowDiagramProvider(args.mdx)
    elif args.images:
        provider = FileProvider(args.images)
    else:
        parser.error("Especifica --url, --route, --mdx, --images o --ci")

    # Get images
    print("📸 Obteniendo imágenes...")
    images = provider.get_images()
    print(f"   → {len(images)} imágenes obtenidas")

    # Compose
    print("🎨 Componiendo collage...")
    layout_cls = LAYOUTS[args.layout]
    if args.mecano:
        if not issubclass(layout_cls, LeftBigRightStackedLayout):
            parser.error("--mecano solo disponible con layout left-big-right-stacked")
        layout = layout_cls(mecano_style=True)
    else:
        layout = layout_cls()
    canvas = layout.compose(images)
    print(f"   → Collage {canvas.width}×{canvas.height}")

    # Export
    print("💾 Exportando...")
    exporter = ImageExporter(args.output, dry_run=args.dry_run)
    master_path = exporter.export(canvas)

    print(f"\n✅ Listo! Master: {master_path}")
    if not args.dry_run:
        print(f"   image: \"img/{Path(master_path).stem}-1200.webp\"")


if __name__ == "__main__":
    main()
