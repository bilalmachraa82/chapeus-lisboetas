#!/usr/bin/env python3
"""Full-fidelity extractor for Chapéus Lisboeta catalog."""
from __future__ import annotations

import csv
import json
import re
import sqlite3
import unicodedata
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from PIL import Image
from bs4 import BeautifulSoup
from openpyxl import load_workbook

BASE_DIR = Path(__file__).resolve().parents[1]
WORKBOOK_PATH = BASE_DIR / "WEBSITE Produtos Catálogo.xlsx"
OUTPUT_DIR = BASE_DIR / "output_catalogo"
IMAGES_DIR = OUTPUT_DIR / "images"
DATA_JSON = OUTPUT_DIR / "catalogo.json"
DATA_CSV = OUTPUT_DIR / "catalogo.csv"
DB_PATH = OUTPUT_DIR / "catalogo.db"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}

SPEC_KEYS = [
    "COR",
    "TAMANHO",
    "VENDIDO POR",
    "COMPOSIÇÃO",
    "COULEUR",
    "TAILLE",
    "VENDU PAR",
    "COMPOSITION",
]

MIN_WIDTH = 800
MIN_HEIGHT = 800

session = requests.Session()
session.headers.update(HEADERS)


def slugify(value: str, allow_empty: bool = False) -> str:
    """Generate filesystem/api safe slug."""
    value = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9-]+", "-", value.lower())
    value = re.sub(r"-+", "-", value).strip("-")
    if not value and not allow_empty:
        value = "produto"
    return value


def ensure_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def extract_links(text: Optional[str]) -> List[str]:
    if not text:
        return []
    return re.findall(r"https?://[^\s]+", text.replace("\n", " "))


def parse_specs_block(text: Optional[str]) -> Dict[str, str]:
    if not text:
        return {}
    block = text.replace("\n", " ")
    pattern = re.compile(
        r"(" + "|".join(SPEC_KEYS) + r")\s+(.+?)(?=" + "|".join(SPEC_KEYS) + r"|$)",
        re.IGNORECASE | re.DOTALL,
    )
    specs: Dict[str, str] = {}
    for key, value in pattern.findall(block):
        norm_key = key.strip().upper()
        value = re.sub(r"\s+", " ", value.strip())
        specs[norm_key] = value
    return specs


def split_tags(text: Optional[str]) -> List[str]:
    if not text:
        return []
    cleaned = re.sub(r"(?i)^tags?:", "", text)
    return [tag.strip() for tag in cleaned.replace(";", ",").split(",") if tag.strip()]


def scrape_product_page(url: str) -> Dict:
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        return {"error": str(exc), "url": url, "images": []}

    soup = BeautifulSoup(resp.text, "lxml")
    data: Dict[str, Optional[str]] = {
        "url": url,
        "name": None,
        "description": None,
        "price": None,
        "currency": None,
        "images": [],  # List[Dict]
        "raw_jsonld": None,
    }

    # JSON-LD payloads
    jsonld_payloads = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            payload = json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(payload, list):
            jsonld_payloads.extend(payload)
        else:
            jsonld_payloads.append(payload)

    product_entry = None
    for entry in jsonld_payloads:
        if not isinstance(entry, dict):
            continue
        entry_type = entry.get("@type")
        if isinstance(entry_type, list) and "Product" in entry_type:
            product_entry = entry
            break
        if entry_type == "Product":
            product_entry = entry
            break

    if product_entry:
        data["raw_jsonld"] = product_entry
        data["name"] = product_entry.get("name")
        data["description"] = product_entry.get("description")
        images = product_entry.get("image")
        if isinstance(images, str):
            images = [images]
        elif not isinstance(images, list):
            images = []
        offer = product_entry.get("offers")
        if isinstance(offer, dict):
            data["price"] = offer.get("price")
            data["currency"] = offer.get("priceCurrency")
        for pos, img_url in enumerate(images or [], start=1):
            data["images"].append(
                {
                    "url": img_url,
                    "alt": None,
                    "origin": "jsonld",
                    "position": pos,
                }
            )

    if not data.get("name"):
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            data["name"] = og_title["content"]
    if not data.get("description"):
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            data["description"] = og_desc["content"]

    og_img = soup.find("meta", property="og:image")
    if og_img and og_img.get("content"):
        data["images"].append(
            {
                "url": og_img["content"],
                "alt": None,
                "origin": "og:image",
                "position": len(data["images"]) + 1,
            }
        )

    gallery_imgs = soup.select(".woocommerce-product-gallery__image img, img.wp-post-image")
    start_pos = len(data["images"]) + 1
    for index, img in enumerate(gallery_imgs, start=start_pos):
        src = img.get("data-large_image") or img.get("data-src") or img.get("src")
        if not src:
            continue
        image_meta = {
            "url": src,
            "alt": img.get("data-alt") or img.get("alt") or None,
            "origin": "gallery",
            "position": index,
        }
        width = img.get("data-large_image_width") or img.get("width")
        height = img.get("data-large_image_height") or img.get("height")
        for key, value in ("width_hint", width), ("height_hint", height):
            if value:
                try:
                    image_meta[key] = int(value)
                except ValueError:
                    pass
        data["images"].append(image_meta)

    normalized: List[Dict] = []
    seen = OrderedDict()
    for image in data["images"]:
        img_url = image.get("url")
        if not img_url:
            continue
        absolute = urljoin(url, img_url)
        if any(token in absolute for token in ("-100x100", "-150x150", "-300x300")):
            continue
        base = absolute.split("?")[0]
        if base in seen:
            continue
        seen[base] = {**image, "url": absolute}
    normalized.extend(seen.values())
    data["images"] = normalized
    return data


def download_images(image_entries: List[Dict], dest_dir: Path) -> Tuple[List[Dict], List[Dict]]:
    ensure_dirs(dest_dir)
    stored: List[Dict] = []
    filtered: List[Dict] = []
    fallback_candidates: List[Tuple[Path, Dict, Optional[int], Optional[int], float]] = []
    for idx, image in enumerate(image_entries, start=1):
        img_url = image.get("url")
        if not img_url:
            continue
        parsed = urlparse(img_url)
        ext = Path(parsed.path).suffix or ".jpg"
        filename = f"img_{idx:02d}{ext.lower()}"
        filepath = dest_dir / filename
        try:
            resp = session.get(img_url, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as exc:
            filtered.append({"url": img_url, "reason": "download_error", "detail": str(exc)})
            continue
        filepath.write_bytes(resp.content)
        width = height = None
        try:
            with Image.open(filepath) as img:
                width, height = img.size
        except Exception as exc:  # pragma: no cover - corrupted file
            filtered.append({"url": img_url, "reason": "unreadable_image", "detail": str(exc)})
            filepath.unlink(missing_ok=True)
            continue
        if width < MIN_WIDTH or height < MIN_HEIGHT:
            fallback_candidates.append((filepath, image, width, height, (width or 0) * (height or 0)))
            filtered.append(
                {
                    "url": img_url,
                    "reason": "low_resolution",
                    "width": width,
                    "height": height,
                }
            )
            continue
        stored.append(
            {
                "path": str(filepath.relative_to(OUTPUT_DIR)),
                "url": img_url,
                "alt": image.get("alt"),
                "origin": image.get("origin"),
                "position": image.get("position"),
                "width": width,
                "height": height,
            }
        )
    if not stored and fallback_candidates:
        # choose best resolution fallback and include it despite low-res warning
        best_path, best_image, best_width, best_height, _ = max(
            fallback_candidates, key=lambda item: item[4]
        )
        stored.append(
            {
                "path": str(best_path.relative_to(OUTPUT_DIR)),
                "url": best_image.get("url"),
                "alt": best_image.get("alt"),
                "origin": best_image.get("origin"),
                "position": best_image.get("position"),
                "width": best_width,
                "height": best_height,
            }
        )
        # mark corresponding filtered entry as fallback_used
        for entry in filtered:
            if entry.get("url") == best_image.get("url"):
                entry["reason"] = "fallback_used_low_resolution"
                break
    return stored, filtered


def build_dataset(limit: Optional[int] = None) -> List[Dict]:
    wb = load_workbook(WORKBOOK_PATH, data_only=True)
    dataset: List[Dict] = []
    for sheet in wb.worksheets:
        category = sheet.title.strip()
        row = 2
        while row <= sheet.max_row:
            top = sheet[row]
            detail = sheet[row + 1] if row + 1 <= sheet.max_row else None
            if detail and not any((cell.value not in (None, "")) for cell in detail):
                detail = None
            brand = top[1].value if len(top) > 1 else None
            name = top[2].value if len(top) > 2 else None
            if not (brand or name):
                row += 2
                continue
            info_short = top[3].value if len(top) > 3 else None
            cell = top[4] if len(top) > 4 else None
            supplier_url = None
            if cell is not None:
                supplier_url = cell.hyperlink.target if cell.hyperlink else cell.value
            def cell_value(cells, idx):
                if cells and len(cells) > idx:
                    value = cells[idx].value
                    if value not in (None, ""):
                        return value
                return None

            price = cell_value(detail, 0) or cell_value(top, 0)
            supplier_code = cell_value(detail, 1) or cell_value(top, 1)
            tags_raw = cell_value(detail, 2) or cell_value(top, 2)
            specs_block = cell_value(detail, 3) or cell_value(top, 3)
            variations_raw = cell_value(detail, 4) or cell_value(top, 4)

            extra_links = []
            extra_links.extend(extract_links(variations_raw))
            extra_links.extend(extract_links(specs_block))
            extra_links.extend(extract_links(tags_raw))
            extra_links = [link for link in extra_links if link != supplier_url]

            record = OrderedDict(
                sheet=category,
                sheet_row=row,
                brand=brand,
                name=name,
                info_short=info_short,
                supplier_url=supplier_url,
                extra_urls=list(OrderedDict.fromkeys(extra_links)),
                price=price,
                supplier_code=supplier_code,
                tags=split_tags(tags_raw),
                specs=parse_specs_block(specs_block),
                variations=variations_raw,
            )
            dataset.append(record)
            if limit and len(dataset) >= limit:
                return dataset
            row += 2
    return dataset


def save_csv(records: List[Dict]) -> None:
    ensure_dirs(OUTPUT_DIR)
    fieldnames = list(records[0].keys()) + ["slug", "downloaded_images", "filtered_images", "scraped"]
    with DATA_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = dict(record)
            for key, value in list(row.items()):
                if isinstance(value, (list, dict)):
                    row[key] = json.dumps(value, ensure_ascii=False)
            row["slug"] = record.get("slug")
            row["downloaded_images"] = json.dumps(record.get("downloaded_images", []), ensure_ascii=False)
            row["filtered_images"] = json.dumps(record.get("filtered_images", []), ensure_ascii=False)
            row["scraped"] = json.dumps(record.get("scraped", []), ensure_ascii=False)
            writer.writerow(row)


def save_json(records: List[Dict]) -> None:
    ensure_dirs(OUTPUT_DIR)
    with DATA_JSON.open("w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2)


def save_sqlite(records: List[Dict]) -> None:
    ensure_dirs(OUTPUT_DIR)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS products")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sheet TEXT,
            sheet_row INTEGER,
            brand TEXT,
            name TEXT,
            info_short TEXT,
            supplier_url TEXT,
            price REAL,
            supplier_code TEXT,
            tags TEXT,
            specs TEXT,
            variations TEXT,
            slug TEXT,
            scraped TEXT,
            downloaded_images TEXT,
            filtered_images TEXT
        )
        """
    )
    cur.execute("DELETE FROM products")
    for record in records:
        cur.execute(
            """
            INSERT INTO products
            (sheet, sheet_row, brand, name, info_short, supplier_url, price,
             supplier_code, tags, specs, variations, slug, scraped,
             downloaded_images, filtered_images)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.get("sheet"),
                record.get("sheet_row"),
                record.get("brand"),
                record.get("name"),
                record.get("info_short"),
                record.get("supplier_url"),
                record.get("price"),
                record.get("supplier_code"),
                json.dumps(record.get("tags"), ensure_ascii=False),
                json.dumps(record.get("specs"), ensure_ascii=False),
                record.get("variations"),
                record.get("slug"),
                json.dumps(record.get("scraped"), ensure_ascii=False),
                json.dumps(record.get("downloaded_images"), ensure_ascii=False),
                json.dumps(record.get("filtered_images"), ensure_ascii=False),
            ),
        )
    conn.commit()
    conn.close()


def process_records(records: List[Dict]) -> None:
    for record in records:
        urls = [record.get("supplier_url")] + record.get("extra_urls", [])
        urls = [url for url in urls if url]
        images_collected: List[Dict] = []
        scraped_payloads: List[Dict] = []
        for url in urls:
            scraped = scrape_product_page(url)
            scraped_payloads.append(scraped)
            images_collected.extend(scraped.get("images", []))

        unique_images = OrderedDict()
        for image in images_collected:
            img_url = image.get("url")
            if not img_url:
                continue
            base = img_url.split("?")[0]
            if base in unique_images:
                continue
            unique_images[base] = image

        sku_source = record.get("supplier_code") or record.get("name")
        slug = slugify(sku_source)
        dest_dir = IMAGES_DIR / record.get("sheet", "misc").lower() / slug
        local_images, filtered_images = download_images(list(unique_images.values()), dest_dir)

        record["downloaded_images"] = local_images
        record["filtered_images"] = filtered_images
        record["scraped"] = scraped_payloads
        record["slug"] = slug


def main(limit: Optional[int] = None) -> None:
    ensure_dirs(OUTPUT_DIR, IMAGES_DIR)
    records = build_dataset(limit=limit)
    if not records:
        print("Nenhum registo encontrado no Excel.")
        return
    process_records(records)
    save_json(records)
    save_csv(records)
    save_sqlite(records)
    print(f"Processados {len(records)} produtos.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extrair catálogo e ativos do Chapéus Lisboeta")
    parser.add_argument("--limit", type=int, help="Processar apenas os primeiros N produtos")
    args = parser.parse_args()
    main(limit=args.limit)
