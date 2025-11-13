#!/usr/bin/env python3
"""
Sync WooCommerce product categories using the CSV catalog.

Steps:
1. Parse output_catalogo/woocommerce_import_localhost.csv
2. For each product, ensure category hierarchy exists (e.g., "Chapéus > Boinas > Inverno")
3. Assign the leaf category (and optionally the full path) to the product via WP-CLI

Usage:
    python3 scripts/apply_categories_from_csv.py
    python3 scripts/apply_categories_from_csv.py --limit 10
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path

CSV_FILE = Path("output_catalogo/woocommerce_import_localhost.csv")
CONTAINER = "chapeus_wordpress"
WP_USER = "codex-admin"


def run_wp_cli(args: list[str]) -> subprocess.CompletedProcess:
    cmd = ["docker", "exec", CONTAINER, "wp", *args, f"--user={WP_USER}", "--allow-root"]
    return subprocess.run(cmd, capture_output=True, text=True)


def get_product_id_by_sku(sku: str) -> int | None:
    res = run_wp_cli([
        "post", "list",
        "--post_type=product",
        f"--meta_key=_sku",
        f"--meta_value={sku}",
        "--field=ID",
        "--format=csv",
    ])
    if res.returncode == 0 and res.stdout.strip():
        return int(res.stdout.strip())
    return None


class CategoryManager:
    def __init__(self) -> None:
        self.term_cache: list[dict] = []

    def _ensure_cache(self) -> None:
        if self.term_cache:
            return
        res = run_wp_cli(["term", "list", "product_cat", "--format=json"])
        if res.returncode == 0 and res.stdout.strip():
            self.term_cache = json.loads(res.stdout)

    def _find_term(self, name: str, parent_id: int) -> int | None:
        self._ensure_cache()
        for term in self.term_cache:
            if term.get("name") == name and int(term.get("parent", 0)) == parent_id:
                return int(term["term_id"])
        return None

    def _add_to_cache(self, term_id: int, name: str, parent_id: int) -> None:
        self.term_cache.append({
            "term_id": term_id,
            "name": name,
            "parent": parent_id,
        })

    def ensure_path(self, path: str) -> list[int]:
        """Ensure category hierarchy exists, returning list of term IDs for each level."""
        ids: list[int] = []
        parent_id = 0
        for part in [p.strip() for p in path.split(">") if p.strip()]:
            term_id = self._find_term(part, parent_id)
            if term_id is None:
                res = run_wp_cli([
                    "term", "create", "product_cat", part,
                    f"--parent={parent_id}",
                    "--porcelain",
                ])
                if res.returncode != 0 or not res.stdout.strip():
                    raise RuntimeError(
                        f"Failed to create category '{part}' (parent {parent_id}): {res.stderr}"
                    )
                term_id = int(res.stdout.strip())
                self._add_to_cache(term_id, part, parent_id)
            ids.append(term_id)
            parent_id = term_id
        return ids


def apply_categories(limit: int | None = None) -> None:
    rows = []
    with CSV_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            if limit and len(rows) >= limit:
                break

    manager = CategoryManager()
    updated = 0
    missing_products = 0

    for row in rows:
        sku = (row.get("SKU") or "").splitlines()[0].strip()
        if not sku:
            continue
        product_id = get_product_id_by_sku(sku)
        if not product_id:
            missing_products += 1
            continue

        categories = (row.get("Categories") or "").strip()
        if not categories:
            continue

        try:
            term_ids = manager.ensure_path(categories)
        except RuntimeError as exc:
            print(f"⚠️  {sku}: {exc}")
            continue

        terms_php = ", ".join(str(tid) for tid in term_ids)
        php_code = f"wp_set_object_terms({product_id}, array({terms_php}), 'product_cat');"
        res = run_wp_cli(["eval", php_code])

        if res.returncode == 0:
            updated += 1
        else:
            print(f"⚠️  Failed to assign category for {sku}: {res.stderr.strip()}")

    print(f"✅ Categorias aplicadas: {updated}")
    if missing_products:
        print(f"⚠️  Produtos não encontrados por SKU: {missing_products}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply categories from CSV to WooCommerce products.")
    parser.add_argument("--limit", type=int, help="Process only N products (debug).")
    args = parser.parse_args()

    if not CSV_FILE.exists():
        raise SystemExit(f"CSV não encontrado: {CSV_FILE}")

    apply_categories(args.limit)


if __name__ == "__main__":
    main()
