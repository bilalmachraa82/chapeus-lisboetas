#!/usr/bin/env python3
"""Quick QA validator for output_catalogo datasets."""
from __future__ import annotations

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_JSON = BASE_DIR / "output_catalogo" / "catalogo.json"

REQUIRED_FIELDS = ["sheet", "brand", "name", "price", "supplier_url"]


def main() -> None:
    if not DATA_JSON.exists():
        raise SystemExit("catalogo.json não encontrado. Execute o scraper primeiro.")

    data = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    if not data:
        raise SystemExit("Dataset vazio.")

    missing_price = []
    missing_images = []
    fallback_used = []

    for entry in data:
        for field in REQUIRED_FIELDS:
            if field not in entry:
                raise SystemExit(f"Campo obrigatório '{field}' ausente em {entry.get('slug')}")
        if entry.get("price") in (None, "", 0):
            missing_price.append(entry.get("slug"))
        images = entry.get("downloaded_images", [])
        if not images:
            missing_images.append(entry.get("slug"))
        for filtered in entry.get("filtered_images", []):
            if filtered.get("reason") == "fallback_used_low_resolution":
                fallback_used.append(entry.get("slug"))

    if missing_price:
        print("⚠️ Produtos sem preço:", ", ".join(missing_price))
    if missing_images:
        print("⚠️ Produtos sem imagens HD (verificar manualmente):", ", ".join(missing_images))

    total = len(data)
    print(f"✅ QA concluído: {total} produtos com imagens HD.")
    if fallback_used:
        print(
            "ℹ️ Produtos com fallback de baixa resolução:",
            ", ".join(sorted(set(fallback_used))),
        )


if __name__ == "__main__":
    main()
