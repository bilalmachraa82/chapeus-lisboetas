#!/usr/bin/env python3
"""Synchronise Google Sheets catalog with local catalogo.json."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "output_catalogo"
CATALOGO_JSON = OUTPUT_DIR / "catalogo.json"
BACKUP_JSON = OUTPUT_DIR / "catalogo_backup.json"

SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "config/google-service-account.json")
WORKSHEET_NAME = os.getenv("GOOGLE_SHEETS_TAB", "Catalogo")

COLUMN_MAP = {
    "Sheet": "sheet",
    "SKU": "sku",
    "Nome": "name",
    "Preço": "price",
    "Descrição curta": "info_short",
    "Descrição longa": "long_description",
    "Tags": "tags",
    "Cor": ("specs", "COR"),
    "Tamanho": ("specs", "TAMANHO"),
    "Composição": ("specs", "COMPOSIÇÃO"),
    "Pack": ("specs", "VENDIDO POR"),
    "URL fornecedor": "supplier_url",
    "URLs extra": "extra_urls",
    "Imagens": "image_paths",
    "Prioridade": "priority",
    "Destaque homepage?": "featured",
    "Notas internas": "notes",
}

REQUIRED_COLUMNS = ["SKU", "Nome", "Preço"]


def load_sheet_rows():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise SystemExit(
            "Dependências gspread/google-auth não instaladas. Execute: \n"
            "pip install gspread google-auth"
        ) from exc

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    if not Path(SERVICE_ACCOUNT_FILE).exists():
        raise SystemExit(
            f"Ficheiro de credenciais não encontrado: {SERVICE_ACCOUNT_FILE}."
        )

    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    client = gspread.authorize(credentials)

    if not SHEET_ID:
        raise SystemExit("Defina a variável de ambiente GOOGLE_SHEETS_ID com o ID do documento.")

    sheet = client.open_by_key(SHEET_ID)
    worksheet = sheet.worksheet(WORKSHEET_NAME) if WORKSHEET_NAME else sheet.sheet1
    rows = worksheet.get_all_records()
    headers = worksheet.row_values(1)

    missing = [col for col in REQUIRED_COLUMNS if col not in headers]
    if missing:
        raise SystemExit(f"Colunas obrigatórias em falta no Sheet: {', '.join(missing)}")

    return rows


def load_catalogo() -> List[Dict]:
    if not CATALOGO_JSON.exists():
        raise SystemExit("catalogo.json não encontrado. Execute o scraper antes de sincronizar.")
    return json.loads(CATALOGO_JSON.read_text(encoding="utf-8"))


def record_key(record: Dict) -> str:
    return str(record.get("supplier_code") or record.get("slug") or "").strip()


def merge_sheet(rows: List[Dict], catalog: List[Dict]) -> List[Dict]:
    catalog_by_sku = {record_key(r): r for r in catalog}
    updated = []
    seen = set()

    for row in rows:
        sku = str(row.get("SKU", "")).strip()
        if not sku:
            continue
        seen.add(sku)
        base = catalog_by_sku.get(sku, {
            "slug": sku.lower().replace(" ", "-"),
            "supplier_code": sku,
            "specs": {},
            "tags": [],
            "downloaded_images": [],
            "filtered_images": [],
            "extra_urls": [],
            "scraped": [],
        })

        for column, target in COLUMN_MAP.items():
            value = row.get(column)
            if isinstance(value, str):
                value = value.strip()
            if value in (None, ""):
                continue

            if target == "sku":
                continue
            elif target == "tags":
                tags = [t.strip() for t in value.replace(";", ",").split(",") if t.strip()]
                base["tags"] = tags
            elif target == "extra_urls":
                urls = [u.strip() for u in value.splitlines() if u.strip()]
                base["extra_urls"] = urls
            elif target == "image_paths":
                paths = [p.strip() for p in value.split(",") if p.strip()]
                base["downloaded_images"] = [
                    {"path": p, "url": "", "origin": "sheet", "position": idx + 1}
                    for idx, p in enumerate(paths)
                ]
            elif target == "long_description":
                if base.get("scraped"):
                    base["scraped"][0]["description"] = value
                else:
                    base["scraped"] = [{"description": value}]
            elif isinstance(target, tuple) and target[0] == "specs":
                base.setdefault("specs", {})[target[1]] = value
            else:
                base[target] = value

        # ensure sheet column
        if row.get("Sheet"):
            base["sheet"] = row["Sheet"].strip()
        base["supplier_code"] = sku
        base.setdefault("price", row.get("Preço") or base.get("price"))
        try:
            base["price"] = float(str(base["price"]).replace(",", "."))
        except (TypeError, ValueError):
            pass
        updated.append(base)
        catalog_by_sku[sku] = base

    # include untouched records (not present in sheet)
    for sku, record in catalog_by_sku.items():
        if sku not in seen:
            updated.append(record)

    return updated


def main() -> None:
    rows = load_sheet_rows()
    catalog = load_catalogo()

    BACKUP_JSON.write_text(CATALOGO_JSON.read_text(encoding="utf-8"), encoding="utf-8")
    merged = merge_sheet(rows, catalog)
    CATALOGO_JSON.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Sincronização concluída. Registos totais: {len(merged)}")
    print(f"Backup criado em {BACKUP_JSON}")


if __name__ == "__main__":
    main()
