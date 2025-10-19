#!/usr/bin/env python3
"""Export catalogo.json to a Google-Sheets friendly CSV master file."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parents[1]
CATALOGO_JSON = BASE_DIR / "output_catalogo" / "catalogo.json"
MASTER_CSV = BASE_DIR / "output_catalogo" / "catalogo_master.csv"

FIELDNAMES = [
    "Sheet",
    "SKU",
    "Nome",
    "Preço",
    "Descrição curta",
    "Descrição longa",
    "Tags",
    "Cor",
    "Tamanho",
    "Composição",
    "Pack",
    "URL fornecedor",
    "URLs extra",
    "Imagens",
    "Prioridade",
    "Destaque homepage?",
    "Notas internas",
]

SPEC_KEYS = {
    "COR": "Cor",
    "TAMANHO": "Tamanho",
    "COMPOSIÇÃO": "Composição",
    "VENDIDO POR": "Pack",
}


def normalise_specs(specs: Dict[str, str]) -> Dict[str, str]:
    result = {label: "" for label in SPEC_KEYS.values()}
    for key, label in SPEC_KEYS.items():
        value = specs.get(key)
        if value:
            result[label] = value
    return result


def main() -> None:
    if not CATALOGO_JSON.exists():
        raise SystemExit("catalogo.json não encontrado. Execute o scraper primeiro.")

    data: List[Dict] = json.loads(CATALOGO_JSON.read_text(encoding="utf-8"))
    MASTER_CSV.parent.mkdir(parents=True, exist_ok=True)

    with MASTER_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, FIELDNAMES)
        writer.writeheader()
        for record in data:
            specs = normalise_specs(record.get("specs", {}))
            row = {
                "Sheet": record.get("sheet", ""),
                "SKU": record.get("supplier_code") or record.get("slug"),
                "Nome": record.get("name", ""),
                "Preço": record.get("price", ""),
                "Descrição curta": record.get("info_short", ""),
                "Descrição longa": record.get("scraped", [{}])[0].get("description", "")
                if record.get("scraped")
                else "",
                "Tags": ", ".join(record.get("tags", [])),
                "URL fornecedor": record.get("supplier_url", ""),
                "URLs extra": "\n".join(record.get("extra_urls", [])),
                "Imagens": ", ".join(
                    img.get("path")
                    for img in record.get("downloaded_images", [])
                    if img.get("path")
                ),
                "Prioridade": record.get("priority", ""),
                "Destaque homepage?": record.get("featured", ""),
                "Notas internas": record.get("notes", ""),
            }
            row.update(specs)
            writer.writerow(row)

    print(f"Master CSV gerado em {MASTER_CSV}")


if __name__ == "__main__":
    main()
