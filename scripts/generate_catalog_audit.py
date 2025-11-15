#!/usr/bin/env python3
"""Generate a reconciliation report between Google Sheet, catalogo.json and WooCommerce CSV."""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parents[1]
SHEET_CSV = BASE_DIR / "output_catalogo" / "catalogo_google_sheet.csv"
CATALOGO_JSON = BASE_DIR / "output_catalogo" / "catalogo.json"
WC_CSV = BASE_DIR / "output_catalogo" / "woocommerce_import_localhost.csv"
OUTPUT_DIR = BASE_DIR / "relatorios"
OUTPUT_DIR.mkdir(exist_ok=True)

SPEC_NORMALIZED_KEYS = {
    "COR": "Cor",
    "TAMANHO": "Tamanho",
    "COMPOSIÇÃO": "Composição",
    "VENDIDO POR": "Pack",
}

ISSUE_PRIORITY = [
    "missing_in_catalog",
    "image_none",
    "image_partial",
    "image_filtered",
    "short_missing_site",
    "long_missing_site",
    "tags_diff",
    "specs_missing",
    "price_diff",
    "sheet_no_price",
    "missing_in_wc",
]

SUGGESTION_MAP = {
    "image_none": "Incluir ao menos uma imagem antes do próximo import ou usar fotos do fornecedor.",
    "image_partial": "Rever validate_and_enrich.py para aceitar fallback (<800px) ou subir manualmente no WP.",
    "image_filtered": "Reduzir limites MIN_WIDTH/MIN_HEIGHT ou buscar imagens em maior resolução.",
    "short_missing_site": "Propagar a 'Descrição curta' do Sheet para o campo info_short do catalogo.json.",
    "long_missing_site": "Propagar a descrição longa do Sheet/scrape para o catalogo.json antes do import.",
    "tags_diff": "Atualizar tags no catalogo.json/CSV para refletir o que foi aprovado no Sheet.",
    "specs_missing": "Completar especificações (Cor/Tamanho/Composição/Pack) antes do próximo import.",
    "price_diff": "Sincronizar preços entre Sheet e catalogo.json antes de gerar o CSV do WooCommerce.",
    "missing_in_catalog": "Executar sync_google_sheet.py para criar/atualizar o produto no catalogo.json.",
    "missing_in_wc": "Regerar woocommerce_import_localhost.csv para incluir este produto.",
    "sheet_no_price": "Cliente precisa informar preço no Sheet (regra solicitada: não importar sem preço).",
}


def normalize_key(value: str) -> str:
    if not value:
        return ""
    text = unicodedata.normalize("NFKD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("“", "").replace("”", "")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def normalize_text(value: str) -> str:
    if not value:
        return ""
    text = unicodedata.normalize("NFKD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", "", text.lower())
    return text


def parse_price(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.replace("€", "").replace("EUR", "").replace(" ", "")
    # Support formats "24,90" and "24.90"
    if text.count(",") == 1 and text.count(".") == 0:
        text = text.replace(",", ".")
    elif text.count(",") == 1 and text.count(".") == 1 and text.find(",") > text.find("."):
        # format like 1.234,56 → remove thousand dot then replace comma
        text = text.replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def split_list(value: Optional[str]) -> List[str]:
    if not value:
        return []
    tokens = re.split(r"[\n;,]", value)
    return [token.strip() for token in tokens if token.strip()]


def shorten(value: Optional[str], limit: int = 220) -> str:
    if not value:
        return ""
    text = re.sub(r"\s+", " ", value.strip())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


@dataclass
class SheetRow:
    key: str
    sku: str
    nome: str
    categoria: str
    price: Optional[float]
    short_desc: str
    long_desc: str
    tags: List[str]
    images: List[str]
    specs: Dict[str, str]
    supplier_url: str
    raw: Dict[str, str] = field(default_factory=dict)


@dataclass
class SiteEntry:
    key: str
    data: Dict

    @property
    def price(self) -> Optional[float]:
        value = self.data.get("price")
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @property
    def images(self) -> List[Dict]:
        return self.data.get("downloaded_images", [])

    @property
    def filtered_images(self) -> List[Dict]:
        return self.data.get("filtered_images", [])


@dataclass
class WooEntry:
    key: str
    row: Dict[str, str]
    images: List[str]


@dataclass
class ReportRow:
    sku: str
    nome: str
    categoria: str
    preco_sheet: str
    preco_site: str
    status: str
    pendencias: str
    sugestao: str
    sheet_img_count: int
    site_img_count: int
    wc_img_count: int
    fotos_sheet: str
    fotos_site: str
    fotos_wc: str
    fotos_filtradas: str
    desc_curta_sheet: str
    desc_curta_site: str
    desc_longa_sheet: str
    desc_longa_site: str
    tags_sheet: str
    tags_site: str
    specs_sheet: str
    specs_site: str
    url_fornecedor: str
    slug_site: str

    def to_csv_row(self) -> Dict[str, str]:
        return {
            "SKU": self.sku,
            "Nome": self.nome,
            "Categoria Sheet": self.categoria,
            "Preço Sheet": self.preco_sheet,
            "Preço Site": self.preco_site,
            "Status importação": self.status,
            "Pendências detectadas": self.pendencias,
            "Sugestão": self.sugestao,
            "Sheet fotos (count)": str(self.sheet_img_count),
            "Site fotos (count)": str(self.site_img_count),
            "WooCommerce fotos (count)": str(self.wc_img_count),
            "Fotos Sheet": self.fotos_sheet,
            "Fotos Site": self.fotos_site,
            "Fotos WooCommerce": self.fotos_wc,
            "Fotos filtradas (motivo)": self.fotos_filtradas,
            "Descrição curta Sheet": self.desc_curta_sheet,
            "Descrição curta Site": self.desc_curta_site,
            "Descrição longa Sheet (preview)": self.desc_longa_sheet,
            "Descrição longa Site (preview)": self.desc_longa_site,
            "Tags Sheet": self.tags_sheet,
            "Tags Site": self.tags_site,
            "Especificações Sheet": self.specs_sheet,
            "Especificações Site": self.specs_site,
            "URL fornecedor": self.url_fornecedor,
            "Slug / produto site": self.slug_site,
        }


@dataclass
class Summary:
    sheet_total: int = 0
    sheet_with_price: int = 0
    sheet_without_price: int = 0
    site_total: int = 0
    wc_total: int = 0
    status_counts: Dict[str, int] = field(default_factory=dict)
    issue_counts: Dict[str, int] = field(default_factory=dict)
    sheet_missing_in_site: List[str] = field(default_factory=list)
    site_only: List[str] = field(default_factory=list)

    def add_status(self, status: str) -> None:
        self.status_counts[status] = self.status_counts.get(status, 0) + 1

    def add_issue(self, code: str) -> None:
        self.issue_counts[code] = self.issue_counts.get(code, 0) + 1

    def to_dict(self) -> Dict:
        return {
            "sheet_total": self.sheet_total,
            "sheet_with_price": self.sheet_with_price,
            "sheet_without_price": self.sheet_without_price,
            "site_total": self.site_total,
            "wc_total": self.wc_total,
            "status_counts": self.status_counts,
            "issue_counts": self.issue_counts,
            "sheet_missing_in_site": self.sheet_missing_in_site,
            "site_only": self.site_only,
        }


def load_sheet_rows() -> List[SheetRow]:
    rows: List[SheetRow] = []
    with SHEET_CSV.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            sku = " ".join((raw.get("SKU") or "").split())
            key = normalize_key(sku or raw.get("Nome") or raw.get("URL fornecedor"))
            specs = {
                "Cor": (raw.get("Cor") or "").strip(),
                "Tamanho": (raw.get("Tamanho") or "").strip(),
                "Composição": (raw.get("Composição") or "").strip(),
                "Pack": (raw.get("Pack") or "").strip(),
            }
            rows.append(
                SheetRow(
                    key=key,
                    sku=sku,
                    nome=(raw.get("Nome") or "").strip(),
                    categoria=(raw.get("Sheet") or "").strip(),
                    price=parse_price(raw.get("Preço")),
                    short_desc=(raw.get("Descrição curta") or "").strip(),
                    long_desc=(raw.get("Descrição longa") or "").strip(),
                    tags=split_list(raw.get("Tags")),
                    images=split_list(raw.get("Imagens")),
                    specs=specs,
                    supplier_url=(raw.get("URL fornecedor") or "").strip(),
                    raw=raw,
                )
            )
    return rows


def load_site_map() -> Dict[str, SiteEntry]:
    data = json.loads(CATALOGO_JSON.read_text(encoding="utf-8"))
    site_entries: Dict[str, SiteEntry] = {}
    for entry in data:
        key = normalize_key(entry.get("supplier_code") or entry.get("slug"))
        if not key:
            continue
        site_entries[key] = SiteEntry(key=key, data=entry)
    return site_entries


def load_wc_map() -> Dict[str, WooEntry]:
    wc_entries: Dict[str, WooEntry] = {}
    with WC_CSV.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            sku = " ".join((row.get("SKU") or "").split())
            key = normalize_key(sku or row.get("Name"))
            if not key:
                continue
            wc_entries[key] = WooEntry(key=key, row=row, images=split_list(row.get("Images")))
    return wc_entries


def format_specs(specs: Dict[str, str]) -> str:
    cleaned = {k: v for k, v in specs.items() if v}
    return json.dumps(cleaned, ensure_ascii=False) if cleaned else "{}"


def filtered_info(entries: List[Dict]) -> str:
    if not entries:
        return ""
    return "; ".join(
        f"{item.get('reason')} ({item.get('width')}x{item.get('height')})" for item in entries
    )


def build_report() -> None:
    sheet_rows = load_sheet_rows()
    site_map = load_site_map()
    wc_map = load_wc_map()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = OUTPUT_DIR / f"catalog_audit_{timestamp}.csv"
    summary_path = OUTPUT_DIR / f"catalog_audit_summary_{timestamp}.json"

    summary = Summary(
        sheet_total=len(sheet_rows),
        site_total=len(site_map),
        wc_total=len(wc_map),
    )

    report_rows: List[ReportRow] = []

    for row in sheet_rows:
        key = row.key or normalize_key(row.supplier_url)
        site = site_map.get(key)
        wc = wc_map.get(key)

        sheet_has_price = row.price is not None and row.price > 0
        if sheet_has_price:
            summary.sheet_with_price += 1
        else:
            summary.sheet_without_price += 1

        issues: List[str] = []
        status = "Completo"

        if not sheet_has_price:
            issues.append("sheet_no_price")
            status = "Ignorar (sem preço)"
        elif not site:
            issues.append("missing_in_catalog")
            status = "Fora do site"
            summary.sheet_missing_in_site.append(row.sku)
        else:
            if row.price is not None and site.price is not None:
                if abs(row.price - site.price) > 0.01:
                    issues.append("price_diff")
            elif row.price is not None and site.price is None:
                issues.append("price_diff")

            sheet_img_count = len(row.images)
            site_img_count = len(site.images)
            if sheet_img_count == 0 and site_img_count == 0:
                issues.append("image_none")
            elif sheet_img_count > 0 and site_img_count == 0:
                issues.append("image_none")
            elif sheet_img_count > site_img_count:
                issues.append("image_partial")
            if site.filtered_images:
                issues.append("image_filtered")

            if row.short_desc and not (site.data.get("info_short") or "").strip():
                issues.append("short_missing_site")
            if row.long_desc and not (site.data.get("long_description") or "").strip():
                issues.append("long_missing_site")

            sheet_tags = {normalize_text(tag) for tag in row.tags if tag}
            site_tags = {normalize_text(tag) for tag in site.data.get("tags", [])}
            if sheet_tags and sheet_tags - site_tags:
                issues.append("tags_diff")

            site_specs_normalized: Dict[str, str] = {}
            for spec_key, label in SPEC_NORMALIZED_KEYS.items():
                if spec_key in site.data.get("specs", {}):
                    value = site.data["specs"].get(spec_key)
                    if value is None:
                        site_specs_normalized[label] = ""
                    else:
                        site_specs_normalized[label] = str(value).strip()
            spec_diff = []
            for label, sheet_value in row.specs.items():
                sheet_clean = sheet_value.strip()
                site_clean = (site_specs_normalized.get(label) or "").strip()
                if sheet_clean and not site_clean:
                    spec_diff.append(label)
                elif sheet_clean and site_clean and normalize_text(sheet_clean) != normalize_text(site_clean):
                    spec_diff.append(label)
            if spec_diff:
                issues.append("specs_missing")

            if sheet_has_price and not wc:
                issues.append("missing_in_wc")

        if issues and status == "Completo":
            status = "Parcial"

        ordered_issues = [code for code in ISSUE_PRIORITY if code in issues]
        pendencias: List[str] = []
        for code in ordered_issues:
            if code == "image_none":
                pendencias.append("Sem imagens no site")
            elif code == "image_partial":
                pendencias.append("Fotos incompletas vs Sheet")
            elif code == "image_filtered":
                pendencias.append("Imagens filtradas por baixa resolução")
            elif code == "short_missing_site":
                pendencias.append("Descrição curta ausente no site")
            elif code == "long_missing_site":
                pendencias.append("Descrição longa ausente no site")
            elif code == "tags_diff":
                pendencias.append("Tags divergentes")
            elif code == "specs_missing":
                pendencias.append("Especificações divergentes")
            elif code == "price_diff":
                pendencias.append("Preço divergente")
            elif code == "missing_in_catalog":
                pendencias.append("Produto não sincronizado no catalogo.json")
            elif code == "missing_in_wc":
                pendencias.append("Produto não saiu no CSV WooCommerce")
            elif code == "sheet_no_price":
                pendencias.append("Sem preço no Sheet (não importar)")

        suggestions = [SUGGESTION_MAP[code] for code in ordered_issues if code in SUGGESTION_MAP]

        summary.add_status(status)
        for code in ordered_issues:
            summary.add_issue(code)

        report_rows.append(
            ReportRow(
                sku=row.sku,
                nome=row.nome,
                categoria=row.categoria,
                preco_sheet=f"{row.price:.2f}" if row.price is not None else "",
                preco_site=f"{site.price:.2f}" if site and site.price is not None else "",
                status=status,
                pendencias="; ".join(pendencias),
                sugestao=" ".join(dict.fromkeys(suggestions)),
                sheet_img_count=len(row.images),
                site_img_count=len(site.images) if site else 0,
                wc_img_count=len(wc.images) if wc else 0,
                fotos_sheet=", ".join(row.images),
                fotos_site=", ".join(img.get("path", "") for img in (site.images if site else []) if img.get("path")),
                fotos_wc=", ".join(wc.images) if wc else "",
                fotos_filtradas=filtered_info(site.filtered_images if site else []),
                desc_curta_sheet=row.short_desc,
                desc_curta_site=(site.data.get("info_short") or "") if site else "",
                desc_longa_sheet=shorten(row.long_desc),
                desc_longa_site=shorten(site.data.get("long_description") or "") if site else "",
                tags_sheet=", ".join(row.tags),
                tags_site=", ".join(site.data.get("tags", [])) if site else "",
                specs_sheet=format_specs(row.specs),
                specs_site=format_specs(site.data.get("specs", {})) if site else "{}",
                url_fornecedor=row.supplier_url,
                slug_site=site.data.get("slug", "") if site else "",
            )
        )

    for key, entry in site_map.items():
        if key in {row.key for row in sheet_rows}:
            continue
        summary.site_only.append(entry.data.get("supplier_code"))
        report_rows.append(
            ReportRow(
                sku=entry.data.get("supplier_code", ""),
                nome=entry.data.get("name", ""),
                categoria=entry.data.get("sheet", ""),
                preco_sheet="",
                preco_site=f"{entry.price:.2f}" if entry.price is not None else "",
                status="Só no site (não consta no Sheet)",
                pendencias="Rever origem - produto não está no Sheet",
                sugestao="Adicionar ao Sheet antes do próximo sync para manter paridade.",
                sheet_img_count=0,
                site_img_count=len(entry.images),
                wc_img_count=0,
                fotos_sheet="",
                fotos_site=", ".join(img.get("path", "") for img in entry.images if img.get("path")),
                fotos_wc="",
                fotos_filtradas="",
                desc_curta_sheet="",
                desc_curta_site=entry.data.get("info_short", ""),
                desc_longa_sheet="",
                desc_longa_site=shorten(entry.data.get("long_description") or ""),
                tags_sheet="",
                tags_site=", ".join(entry.data.get("tags", [])),
                specs_sheet="{}",
                specs_site=format_specs(entry.data.get("specs", {})),
                url_fornecedor=entry.data.get("supplier_url", ""),
                slug_site=entry.data.get("slug", ""),
            )
        )

    report_rows.sort(key=lambda item: (item.status, item.categoria, item.sku))

    headers = list(ReportRow.__dataclass_fields__.keys())

    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "SKU",
                "Nome",
                "Categoria Sheet",
                "Preço Sheet",
                "Preço Site",
                "Status importação",
                "Pendências detectadas",
                "Sugestão",
                "Sheet fotos (count)",
                "Site fotos (count)",
                "WooCommerce fotos (count)",
                "Fotos Sheet",
                "Fotos Site",
                "Fotos WooCommerce",
                "Fotos filtradas (motivo)",
                "Descrição curta Sheet",
                "Descrição curta Site",
                "Descrição longa Sheet (preview)",
                "Descrição longa Site (preview)",
                "Tags Sheet",
                "Tags Site",
                "Especificações Sheet",
                "Especificações Site",
                "URL fornecedor",
                "Slug / produto site",
            ],
        )
        writer.writeheader()
        for row in report_rows:
            writer.writerow(row.to_csv_row())

    summary_path.write_text(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ Relatório gerado: {csv_path}")
    print(f"✅ Sumário: {summary_path}")


if __name__ == "__main__":
    build_report()
