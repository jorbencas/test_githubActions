"""Estampa `updatedDate` en el frontmatter de los posts del blog según el
último commit que tocó cada fichero (ignorando los commits del bot).

Regla:
- Si el fichero tiene un último commit humano con fecha > pubDate, se escribe
  (o actualiza) `updatedDate` con esa fecha, respetando el formato de pubDate.
- Si `updatedDate` existe pero no hay ninguna fecha de actualización válida,
  se elimina la línea para que el badge "ACTUALIZADO" no muestre datos falsos.

Uso:
    python -m scripts.tools.bump_updated_dates --blog-path ./blog [--dry-run]
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

POSTS_REL = "src/content/posts"
BOT_AUTHORS = {"github-actions[bot]", "GitHub Actions"}
DATE_RE = re.compile(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})")


def git(cwd, *args):
    res = subprocess.run(list(args), cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  [git] error: {res.stderr.strip()}", file=sys.stderr)
    return res


def last_human_commit(cwd, rel_file):
    # Sin --follow (lento): log -1 por ruta, si el último es del bot, subimos
    # por el primer padre hasta encontrar un commit humano.
    res = git(cwd, "git", "log", "-1", "--format=%H|%an|%ai", "--", rel_file)
    if not res.stdout.strip():
        return None
    hash_, author, iso = res.stdout.strip().split("|", 2)
    if author.strip() not in BOT_AUTHORS:
        return iso[:10]
    for _ in range(5):
        res = git(cwd, "git", "log", "-1", f"{hash_}^", "--format=%H|%an|%ai", "--", rel_file)
        if not res.stdout.strip():
            return None
        hash_, author, iso = res.stdout.strip().split("|", 2)
        if author.strip() not in BOT_AUTHORS:
            return iso[:10]
    return None


def parse_date(value):
    m = DATE_RE.search(value)
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def fmt_date(pub_date, sep):
    y, m, d = pub_date
    return f"{y:04d}{sep}{m:02d}{sep}{d:02d}"


def frontmatter_block(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[3:end]


def process(file, blog_root, dry_run):
    text = file.read_text(encoding="utf-8")
    fm = frontmatter_block(text)
    if fm is None:
        print(f"  riesgo: frontmatter inválido en {file.name} (omitido)")
        return False

    pub_m = re.search(r"^pubDate:\s*(.+?)\s*$", fm, re.M)
    upd_m = re.search(r"^updatedDate:\s*(.+?)\s*$", fm, re.M)
    if not pub_m:
        return False

    pub = parse_date(pub_m.group(1))
    if pub is None:
        print(f"  riesgo: pubDate ilegible en {file.name} (omitido)")
        return False

    last_date = last_human_commit(str(blog_root), f"{POSTS_REL}/{file.name}")
    last = parse_date(last_date) if last_date else None

    sep = "/" if "/" in pub_m.group(1) else "-"
    new_line = None
    has_update = upd_m is not None

    if last is not None and last > pub:
        new_line = f"updatedDate: \"{fmt_date(last, sep)}\""
    if new_line is None and not has_update:
        return False

    changed = False
    if new_line is not None:
        if has_update:
            new_fm = fm[: upd_m.start()] + new_line + fm[upd_m.end():]
            changed = new_fm != fm
            fm = new_fm
        else:
            insert_at = pub_m.end()
            new_fm = fm[:insert_at] + "\n" + new_line + fm[insert_at:]
            changed = new_fm != fm
            fm = new_fm
    else:
        new_fm = fm[: upd_m.start()] + fm[upd_m.end():]
        new_fm = re.sub(r"\n{3,}", "\n\n", new_fm)
        changed = new_fm != fm
        fm = new_fm

    if not changed:
        return False

    if dry_run:
        print(f"  [{file.name}] -> {new_line or 'updatedDate eliminada'}")
        return True

    begin = 3
    end = text.find("\n---", begin)
    file.write_text(text[:begin] + fm + text[end:], encoding="utf-8")
    print(f"  [{file.name}] -> {new_line or 'updatedDate eliminada'}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--blog-path", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    posts_dir = Path(args.blog_path) / POSTS_REL
    if not posts_dir.is_dir():
        print(f"No existe {posts_dir}", file=sys.stderr)
        return 1

    blog_root = Path(args.blog_path)
    print("Estampando updatedDate según historial de git…")
    for mdx in sorted(posts_dir.glob("*.mdx")):
        process(mdx, blog_root, args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())