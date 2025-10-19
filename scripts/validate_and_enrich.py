#!/usr/bin/env python3
"""Validate supplier links, scrape missing data and split catalog into clean vs pending buckets.

Usage:
    export GOOGLE_SHEETS_ID=...
    export GOOGLE_SERVICE_ACCOUNT_FILE=config/google-service-account.json
    python3 scripts/validate_and_enrich.py

Outputs:
    output_catalogo/catalogo_clean_ready.csv
    output_catalogo/catalogo_pending.csv
    (optionally updates Google Sheet tabs "Clean & Ready" e "Pendentes" se credenciais estiverem configuradas)
"""
from __future__ import annotations

import csv
import datetime as dt
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:  # gspread might not be installed in some environments
    gspread = None
    Credentials = None

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
)
REQUEST_TIMEOUT = 20
BASE_DIR = Path(__file__).resolve().parents[1]
CATALOG_MASTER_PATH = BASE_DIR / "output_catalogo" / "catalogo_master_with_price.csv"
CLEAN_OUTPUT = BASE_DIR / "output_catalogo" / "catalogo_clean_ready.csv"
PENDING_OUTPUT = BASE_DIR / "output_catalogo" / "catalogo_pending.csv"
SCRAPE_RAW_DIR = BASE_DIR / "output_catalogo" / "scrape_raw"
SCRAPE_RAW_DIR.mkdir(exist_ok=True)

GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "config/google-service-account.json")
TAB_CLEAN = "Clean & Ready"
TAB_PENDING = "Pendentes"


@dataclass
class ScrapeResult:
    status: str
    description: str = ""
    composition: str = ""
    raw_excerpt: str = ""
    warnings: List[str] = field(default_factory=list)

    def to_observation(self) -> str:
        parts = [self.status]
        parts.extend(self.warnings)
        return "; ".join([p for p in parts if p])


def load_catalog(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Catálogo master não encontrado: {path}")
    df = pd.read_csv(path)
    required = {"source", "category", "sku", "name", "price", "normalized_url", "primary_url"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas em falta no catálogo master: {missing}")
    return df


def fetch_html(url: str) -> Tuple[Optional[str], Optional[str]]:
    if not url:
        return None, "missing_url"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT})
    except Exception as exc:  # network errors
        return None, f"request_error: {exc}"  # type: ignore[arg-type]

    if response.status_code != 200:
        return None, f"http_status_{response.status_code}"

    return response.text, None


def _extract_section(soup: BeautifulSoup, keywords: List[str]) -> str:
    upper_keywords = [k.upper() for k in keywords]
    # Search for elements containing keywords
    for element in soup.find_all(text=True):
        text = element.strip()
        if not text:
            continue
        upper_text = text.upper()
        if any(keyword in upper_text for keyword in upper_keywords):
            parent_text = " ".join(element.parent.stripped_strings) if element.parent else text
            return parent_text
    return ""


def extract_description_and_composition(html: str) -> ScrapeResult:
    soup = BeautifulSoup(html, "html.parser")

    # Attempt meta description first
    desc_candidates = []
    for attr in ["description", "og:description", "twitter:description"]:
        meta_tag = soup.find("meta", attrs={"name": attr}) or soup.find("meta", attrs={"property": attr})
        if meta_tag and meta_tag.get("content"):
            desc_candidates.append(meta_tag.get("content").strip())

    # Fallback: product summary paragraphs
    if not desc_candidates:
        summary = soup.find(class_="summary")
        if summary:
            desc_candidates.append(" ".join(summary.stripped_strings))
    if not desc_candidates:
        first_paragraph = soup.find("p")
        if first_paragraph:
            desc_candidates.append(first_paragraph.get_text(strip=True))

    description = next((c for c in desc_candidates if len(c) >= 40), "")

    composition = _extract_section(soup, ["COMPOSIÇÃO", "COMPOSITION"])
    if not composition:
        composition = _extract_section(soup, ["MATERIAL", "FABRIC", "TISSU"])

    raw_excerpt = " ".join(soup.get_text(separator=" ").split())[:500]
    warnings: List[str] = []
    status = "OK"
    if not description:
        warnings.append("descrição não encontrada")
        status = "INCOMPLETO"
    if not composition:
        warnings.append("composição não encontrada")
        status = "INCOMPLETO"

    return ScrapeResult(status=status, description=description, composition=composition, raw_excerpt=raw_excerpt, warnings=warnings)


def ensure_gspread_client() -> Optional[gspread.Client]:
    if not GOOGLE_SHEETS_ID or not SERVICE_ACCOUNT_FILE:
        return None
    if gspread is None or Credentials is None:
        print("[INFO] gspread não disponível; ignorando atualização do Google Sheets.")
        return None
    if not Path(SERVICE_ACCOUNT_FILE).exists():
        print(f"[INFO] ficheiro de credenciais não encontrado: {SERVICE_ACCOUNT_FILE}; sem update do Sheets.")
        return None
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"],
    )
    return gspread.authorize(creds)


def update_sheet_tab(client: gspread.Client, tab_name: str, headers: List[str], rows: List[List[str]]) -> None:
    try:
        ws = client.open_by_key(GOOGLE_SHEETS_ID).worksheet(tab_name)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = client.open_by_key(GOOGLE_SHEETS_ID).add_worksheet(title=tab_name, rows=1000, cols=len(headers))
    if rows:
        ws.update([headers] + rows, value_input_option="USER_ENTERED")
    else:
        ws.update("A1", [headers])



def main() -> None:
    df = load_catalog(CATALOG_MASTER_PATH)
    clean_records: List[Dict[str, str]] = []
    pending_records: List[Dict[str, str]] = []

    timestamp = dt.datetime.utcnow().isoformat()

    for _, row in df.iterrows():
        sku = row.get("sku", "")
        url = row.get("primary_url", "")
        source = row.get("source", "")
        category = row.get("category", "")
        name = row.get("name", "")
        price = row.get("price", "")

        html, error = fetch_html(url)
        if error or not html:
            pending_records.append(
                {
                    "SKU": sku,
                    "Fonte": source,
                    "Categoria": category,
                    "Nome": name,
                    "Preço": str(price),
                    "URL fornecedor": url,
                    "Descrição obtida": "",
                    "Composição obtida": "",
                    "Observações": error or "sem_html",
                    "Scrape timestamp": timestamp,
                }
            )
            continue

        # Guardar raw html (opcional para debug)
        raw_path = SCRAPE_RAW_DIR / f"{sku.replace('/', '_')}.html"
        raw_path.write_text(html, encoding="utf-8", errors="ignore")

        scrape = extract_description_and_composition(html)
        record = {
            "SKU": sku,
            "Fonte": source,
            "Categoria": category,
            "Nome": name,
            "Preço": str(price),
            "URL fornecedor": url,
            "Descrição obtida": scrape.description,
            "Composição obtida": scrape.composition,
            "Observações": scrape.to_observation(),
            "Scrape timestamp": timestamp,
        }
        if scrape.status == "OK":
            clean_records.append(record)
        else:
            pending_records.append(record)

    CLEAN_OUTPUT.parent.mkdir(exist_ok=True)
    pd.DataFrame(clean_records).to_csv(CLEAN_OUTPUT, index=False)
    pd.DataFrame(pending_records).to_csv(PENDING_OUTPUT, index=False)

    print(f"[INFO] Produtos prontos: {len(clean_records)} → {CLEAN_OUTPUT}")
    print(f"[INFO] Produtos pendentes: {len(pending_records)} → {PENDING_OUTPUT}")

    client = ensure_gspread_client()
    if client:
        update_sheet_tab(
            client,
            TAB_CLEAN,
            ["SKU", "Fonte", "Categoria", "Nome", "Preço", "URL fornecedor", "Descrição obtida", "Composição obtida", "Observações", "Scrape timestamp"],
            [[str(record[h]) for h in ["SKU", "Fonte", "Categoria", "Nome", "Preço", "URL fornecedor", "Descrição obtida", "Composição obtida", "Observações", "Scrape timestamp"]] for record in clean_records],
        )
        update_sheet_tab(
            client,
            TAB_PENDING,
            ["SKU", "Fonte", "Categoria", "Nome", "Preço", "URL fornecedor", "Descrição obtida", "Composição obtida", "Observações", "Scrape timestamp"],
            [[str(record[h]) for h in ["SKU", "Fonte", "Categoria", "Nome", "Preço", "URL fornecedor", "Descrição obtida", "Composição obtida", "Observações", "Scrape timestamp"]] for record in pending_records],
        )
        print(f"[INFO] Google Sheet atualizado ({TAB_CLEAN}, {TAB_PENDING}).")
    else:
        print("[INFO] Google Sheet não foi atualizado (credenciais ausentes ou gspread indisponível).")


if __name__ == "__main__":
    main()
