#!/usr/bin/env python3
"""
Import AI-generated product images and attach them to WooCommerce products.

Steps per product:
1. Detect local *_pro.* images inside wp-content/uploads/products/**/<slug>/
2. Import (or reuse) each AI image as a WordPress attachment (skip copy).
3. Update the WooCommerce featured image and gallery so AI shots appear primeiro,
   mantendo as imagens originais a seguir.

Usage:
    python3 scripts/import_ai_photos.py              # Processa todos com default 4 fotos/sku
    python3 scripts/import_ai_photos.py --limit 10   # Apenas 10 produtos (debug)
    python3 scripts/import_ai_photos.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

CONTAINER = "chapeus_wordpress"
WP_USER = "codex-admin"
UPLOADS_ROOT = Path("wordpress/wp-content/uploads")
PRODUCTS_DIR = UPLOADS_ROOT / "products"
CATALOG_PATH = Path("output_catalogo/catalogo.json")
CONTAINER_UPLOADS = Path("/var/www/html/wp-content/uploads")


def run_wp_cli(args: List[str], *, capture_stdout: bool = True) -> subprocess.CompletedProcess:
    """Execute a WP-CLI command inside the Docker container."""
    cmd = ["docker", "exec", CONTAINER, "wp", *args, f"--user={WP_USER}", "--allow-root"]
    return subprocess.run(
        cmd,
        check=False,
        capture_output=capture_stdout,
        text=True,
    )


def load_slug_map() -> Dict[str, str]:
    """Return mapping slug -> primary SKU (matches WooCommerce _sku)."""
    with CATALOG_PATH.open() as f:
        catalog = json.load(f)

    slug_map: Dict[str, str] = {}
    for entry in catalog:
        slug = entry.get("slug")
        supplier_code = entry.get("supplier_code") or entry.get("supplier_code_clean")
        if not slug or not supplier_code:
            continue
        primary = supplier_code.splitlines()[0].split(",")[0].strip()
        if primary:
            slug_map[slug] = primary
    return slug_map


def find_attachment_id(relative_path: str) -> Optional[int]:
    """Check if an attachment already exists for the given uploads-relative path."""
    res = run_wp_cli(
        [
            "post",
            "list",
            "--post_type=attachment",
            "--meta_key=_wp_attached_file",
            f"--meta_value={relative_path}",
            "--field=ID",
            "--format=ids",
        ]
    )
    if res.returncode == 0 and res.stdout.strip():
        return int(res.stdout.strip().splitlines()[0])
    return None


def import_media(relative_path: str) -> Optional[int]:
    """Register existing file as attachment via custom PHP helper."""
    abs_path = CONTAINER_UPLOADS / relative_path
    helper_script = Path("/var/www/html/register_ai_attachment.php")
    res = run_wp_cli(
        [
            "eval-file",
            str(helper_script),
            str(abs_path),
            relative_path,
        ]
    )
    if res.returncode != 0:
        sys.stderr.write(f"    ❌ Falha ao registar {relative_path}: {res.stderr.strip()}\n")
        return None
    output = res.stdout.strip()
    return int(output.splitlines()[-1]) if output else None


def get_product_id_by_sku(sku: str) -> Optional[int]:
    res = run_wp_cli(
        [
            "post",
            "list",
            "--post_type=product",
            "--meta_key=_sku",
            f"--meta_value={sku}",
            "--field=ID",
            "--format=ids",
        ]
    )
    if res.returncode == 0 and res.stdout.strip():
        return int(res.stdout.strip().splitlines()[0])
    return None


def get_post_meta(post_id: int, key: str) -> str:
    res = run_wp_cli(["post", "meta", "get", str(post_id), key])
    if res.returncode != 0:
        return ""
    return res.stdout.strip()


def update_post_meta(post_id: int, key: str, value: str) -> bool:
    res = run_wp_cli(["post", "meta", "update", str(post_id), key, value])
    return res.returncode == 0


def unique(seq: List[int]) -> List[int]:
    seen = set()
    out: List[int] = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Importar fotos AI e ligar a produtos.")
    parser.add_argument("--max-ai", type=int, default=4, help="Máximo de fotos AI por produto.")
    parser.add_argument("--limit", type=int, help="Processar apenas N produtos (debug).")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    slug_map = load_slug_map()
    if not slug_map:
        sys.stderr.write("❌ Não consegui construir o mapa slug->SKU.\n")
        return 1

    processed = 0
    imported_attachments = 0
    reused_attachments = 0
    updated_products = 0

    for dirpath in sorted(PRODUCTS_DIR.rglob("*")):
        if args.limit and processed >= args.limit:
            break
        if not dirpath.is_dir():
            continue

        slug = dirpath.name
        if slug not in slug_map:
            continue

        ai_files = sorted(dirpath.glob("*_pro.*"))
        if not ai_files:
            continue

        processed += 1
        sku = slug_map[slug]
        product_id = get_product_id_by_sku(sku)
        if not product_id:
            sys.stderr.write(f"⚠️  Produto com SKU '{sku}' não encontrado no WordPress.\n")
            continue

        selected_files = ai_files[: args.max_ai]
        attachment_ids: List[int] = []

        for file_path in selected_files:
            relative_path = file_path.relative_to(UPLOADS_ROOT).as_posix()
            existing_id = find_attachment_id(relative_path)
            if existing_id:
                attachment_ids.append(existing_id)
                reused_attachments += 1
                continue

            if args.dry_run:
                attachment_ids.append(-1)
                continue

            attachment_id = import_media(relative_path)
            if attachment_id:
                attachment_ids.append(attachment_id)
                imported_attachments += 1

        attachment_ids = [aid for aid in attachment_ids if aid > 0]
        if not attachment_ids:
            sys.stderr.write(f"⚠️  Nenhuma attachment válida para {slug}.\n")
            continue

        if args.dry_run:
            print(f"[DRY RUN] {slug} → {len([aid for aid in attachment_ids if aid > 0])} imagens")
            continue

        featured = attachment_ids[0]
        gallery_ai = attachment_ids[1:]

        existing_gallery_raw = get_post_meta(product_id, "_product_image_gallery")
        existing_gallery_ids = (
            [int(i) for i in existing_gallery_raw.split(",") if i.strip().isdigit()]
            if existing_gallery_raw
            else []
        )

        merged_gallery = unique(gallery_ai + [gid for gid in existing_gallery_ids if gid != featured])

        if not update_post_meta(product_id, "_thumbnail_id", str(featured)):
            sys.stderr.write(f"❌ Falha ao definir thumbnail para product {product_id} ({slug}).\n")
            continue

        gallery_value = ",".join(str(gid) for gid in merged_gallery)
        if not update_post_meta(product_id, "_product_image_gallery", gallery_value):
            sys.stderr.write(f"⚠️  Falha ao atualizar gallery para product {product_id} ({slug}).\n")

        updated_products += 1
        print(f"✅ {slug}: {len(attachment_ids)} fotos AI ligadas ao produto #{product_id}")

    print("\nResumo:")
    print(f" - Diretórios com AI visitados: {processed}")
    print(f" - Produtos atualizados: {updated_products}")
    print(f" - Attachments importados: {imported_attachments}")
    print(f" - Attachments reutilizados: {reused_attachments}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
