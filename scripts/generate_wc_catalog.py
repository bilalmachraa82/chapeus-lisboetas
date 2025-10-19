#!/usr/bin/env python3
"""Generate WooCommerce import CSV from output_catalogo/catalogo.json."""
from __future__ import annotations

import csv
import html
import json
import re
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_JSON = BASE_DIR / "output_catalogo" / "catalogo.json"
OUTPUT_CSV = BASE_DIR / "output_catalogo" / "woocommerce_import.csv"
IMAGES_PREFIX = "catalogo2025"  # relative to wp-content/uploads

# map sheet names to category breadcrumbs
CATEGORY_OVERRIDES: Dict[str, str] = {
    "BOINAS INVERNO": "Chapéus > Boinas > Inverno",
    "BOINAS VERÃO": "Chapéus > Boinas > Verão",
    "FEMININO": "Chapéus > Feminino",
    "GORROS": "Chapéus > Gorros",
    "CERIMÓNIA": "Chapéus > Cerimónia",
    "PALHA": "Chapéus > Palha",
    "PANAMÁ": "Chapéus > Panamá",
    "ARTIGOS EM PELE": "Acessórios > Artigos em Pele",
    "CORTIÇA": "Chapéus > Cortiça",
    "DIVERSOS": "Chapéus > Diversos",
    "CHAPÉUS LÃ": "Chapéus > Lã",
    "À PROVA D´ÁGUA": "Chapéus > À prova d'Água",
    "CHAPÉUS EM TECIDO": "Chapéus > Tecido",
    "VISEIRAS": "Chapéus > Viseiras",
    "BONÉS": "Bonés",
    "COWBOY": "Chapéus > Cowboy",
    "PROTEÇÃO SOLAR": "Chapéus > Proteção Solar",
}

ATTRIBUTE_NAMES = [
    ("COR", "Cor"),
    ("TAMANHO", "Tamanho"),
    ("COMPOSIÇÃO", "Composição"),
    ("VENDIDO POR", "Pack"),
]

CSV_HEADERS = [
    "ID",
    "Type",
    "SKU",
    "Name",
    "Published",
    "Is featured?",
    "Visibility in catalog",
    "Short description",
    "Description",
    "Date sale price starts",
    "Date sale price ends",
    "Tax status",
    "Tax class",
    "In stock?",
    "Stock",
    "Low stock amount",
    "Backorders allowed?",
    "Sold individually?",
    "Weight (kg)",
    "Length (cm)",
    "Width (cm)",
    "Height (cm)",
    "Allow customer reviews?",
    "Purchase note",
    "Sale price",
    "Regular price",
    "Categories",
    "Tags",
    "Shipping class",
    "Images",
    "Download limit",
    "Download expiry days",
    "Parent",
    "Grouped products",
    "Upsells",
    "Cross-sells",
    "External URL",
    "Button text",
    "Position",
]
# attribute columns appended later


def render_description(info_short: str, specs: Dict[str, str], scraped: List[Dict]) -> str:
    parts = []
    if info_short:
        parts.append(f"<p>{html.escape(info_short)}</p>")
    # combine description from scraped if exists
    for payload in scraped:
        descr = payload.get("description")
        if descr:
            parts.append(f"<p>{html.escape(descr)}</p>")
            break
    if specs:
        spec_lines = "".join(
            f"<li><strong>{html.escape(str(key).title())}</strong>: {html.escape(str(value))}</li>"
            for key, value in specs.items()
        )
        parts.append(f"<ul>{spec_lines}</ul>")
    return "".join(parts)


def render_short_description(info_short: str, specs: Dict[str, str]) -> str:
    if info_short:
        return html.escape(str(info_short))
    if specs:
        # pick first key
        key, value = next(iter(specs.items()))
        return html.escape(f"{str(key).title()}: {value}")
    return ""


def category_for_sheet(sheet: str) -> str:
    sheet = sheet.strip()
    if sheet in CATEGORY_OVERRIDES:
        return CATEGORY_OVERRIDES[sheet]
    return f"Chapéus > {sheet.title()}"


def build_images_list(record: Dict) -> str:
    images = record.get("downloaded_images", [])
    if not images:
        return ""
    paths = []
    for image in images:
        rel = image.get("path")
        if not rel:
            continue
        rel_path = Path(rel)
        # remove leading "images" folder and prepend uploads dir
        try:
            parts = list(rel_path.parts)
            if parts[0] == "images":
                parts = parts[1:]
            final_path = Path(IMAGES_PREFIX).joinpath(*parts)
        except IndexError:
            final_path = Path(IMAGES_PREFIX) / rel_path
        paths.append(str(final_path).replace(" ", "%20"))
    return ", ".join(paths)


def build_attribute_columns(specs: Dict[str, str]) -> Dict[str, str]:
    columns = {}
    for idx, (spec_key, label) in enumerate(ATTRIBUTE_NAMES, start=1):
        value = specs.get(spec_key)
        if not value:
            continue
        value = str(value)
        columns[f"Attribute {idx} name"] = label
        normalized = value
        normalized = normalized.replace("\n", " | ")
        normalized = normalized.replace("/", " | ")
        normalized = normalized.replace(";", " | ")
        normalized = normalized.replace("•", " | ")
        normalized = re.sub(r",\s+", " | ", normalized)
        parts = [item.strip() for item in normalized.split("|") if item.strip()]
        columns[f"Attribute {idx} value(s)"] = " | ".join(parts) if parts else value
        columns[f"Attribute {idx} visible"] = "1"
        columns[f"Attribute {idx} global"] = "1"
    # fill empty columns to keep CSV headers consistent
    for idx in range(1, len(ATTRIBUTE_NAMES) + 1):
        columns.setdefault(f"Attribute {idx} name", "")
        columns.setdefault(f"Attribute {idx} value(s)", "")
        columns.setdefault(f"Attribute {idx} visible", "0")
        columns.setdefault(f"Attribute {idx} global", "0")
    return columns


def main() -> None:
    if not INPUT_JSON.exists():
        raise SystemExit("catalogo.json não encontrado")

    data = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    rows = []
    stats = {"total": 0, "skipped_price": 0, "skipped_images": 0}
    for record in data:
        stats["total"] += 1
        price = record.get("price")
        if not price:
            stats["skipped_price"] += 1
            continue
        images_field = build_images_list(record)
        if not images_field:
            stats["skipped_images"] += 1
            continue

        specs = record.get("specs", {})
        short_desc = render_short_description(record.get("info_short", ""), specs)
        long_desc = render_description(record.get("info_short", ""), specs, record.get("scraped", []))
        tags = record.get("tags", [])

        row = {
            "ID": "",
            "Type": "simple",
            "SKU": record.get("supplier_code") or record.get("slug"),
            "Name": record.get("name") or record.get("slug"),
            "Published": "1",
            "Is featured?": "0",
            "Visibility in catalog": "visible",
            "Short description": short_desc,
            "Description": long_desc,
            "Date sale price starts": "",
            "Date sale price ends": "",
            "Tax status": "taxable",
            "Tax class": "",
            "In stock?": "1",
            "Stock": "10",
            "Low stock amount": "2",
            "Backorders allowed?": "0",
            "Sold individually?": "0",
            "Weight (kg)": "0.2",
            "Length (cm)": "",
            "Width (cm)": "",
            "Height (cm)": "",
            "Allow customer reviews?": "1",
            "Purchase note": "",
            "Sale price": "",
            "Regular price": str(price),
            "Categories": category_for_sheet(record.get("sheet", "")),
            "Tags": ", ".join(tags),
            "Shipping class": "",
            "Images": images_field,
            "Download limit": "",
            "Download expiry days": "",
            "Parent": "",
            "Grouped products": "",
            "Upsells": "",
            "Cross-sells": "",
            "External URL": record.get("supplier_url") or "",
            "Button text": "",
            "Position": "0",
        }
        attr_cols = build_attribute_columns(specs)
        row.update(attr_cols)
        rows.append(row)

    if not rows:
        raise SystemExit("Nenhum produto válido para exportação.")

    # ensure headers include attribute columns
    headers = CSV_HEADERS + [
        "Attribute 1 name", "Attribute 1 value(s)", "Attribute 1 visible", "Attribute 1 global",
        "Attribute 2 name", "Attribute 2 value(s)", "Attribute 2 visible", "Attribute 2 global",
        "Attribute 3 name", "Attribute 3 value(s)", "Attribute 3 visible", "Attribute 3 global",
        "Attribute 4 name", "Attribute 4 value(s)", "Attribute 4 visible", "Attribute 4 global",
    ]

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Produtos totais: {stats['total']}")
    print(f"Sem preço: {stats['skipped_price']}")
    print(f"Sem imagens: {stats['skipped_images']}")
    print(f"Exportados: {len(rows)} → {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
