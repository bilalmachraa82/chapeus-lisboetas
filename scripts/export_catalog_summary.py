#!/usr/bin/env python3
"""Generate summary tables (counts por coleção e por tipo)."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
CATALOGO_JSON = BASE_DIR / "output_catalogo" / "catalogo.json"
SUMMARY_CATEGORIA = BASE_DIR / "output_catalogo" / "catalogo_summary_sheet.csv"
SUMMARY_CATEGORIA_TIPO = BASE_DIR / "output_catalogo" / "catalogo_summary_sheet_tipo.csv"


def main() -> None:
    if not CATALOGO_JSON.exists():
        raise SystemExit("catalogo.json não encontrado. Execute o scraper antes de gerar o resumo.")

    data = json.loads(CATALOGO_JSON.read_text(encoding="utf-8"))
    counter_sheet = Counter()
    counter_sheet_type = Counter()

    for record in data:
        sheet = (record.get("sheet") or "").strip() or "Sem categoria"
        name = (record.get("name") or record.get("slug") or "").strip() or "Sem nome"
        counter_sheet[sheet] += 1
        counter_sheet_type[(sheet, name)] += 1

    SUMMARY_CATEGORIA.parent.mkdir(parents=True, exist_ok=True)

    with SUMMARY_CATEGORIA.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Coleção", "Total" ])
        for sheet, total in sorted(counter_sheet.items()):
            writer.writerow([sheet, total])

    with SUMMARY_CATEGORIA_TIPO.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Coleção", "Tipo", "Total"])
        for (sheet, name), total in sorted(counter_sheet_type.items()):
            writer.writerow([sheet, name, total])

    print(f"Resumo por coleção: {SUMMARY_CATEGORIA}")
    print(f"Resumo por coleção/tipo: {SUMMARY_CATEGORIA_TIPO}")


if __name__ == "__main__":
    main()
