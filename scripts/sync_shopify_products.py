#!/usr/bin/env python3
"""Sincroniza produtos completos (dados + imagens) diretamente com a Shopify Admin API."""
from __future__ import annotations

import argparse
import base64
import csv
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

import requests

DEFAULT_CSV_PATHS = [
    Path("output_catalogo/lovable_import_clean.csv"),
    Path("output_catalogo/lovable_import.csv"),
]


@dataclass
class ShopifyConfig:
    domain: str
    token: str
    rate_delay: float = 0.8

    @property
    def base_url(self) -> str:
        return f"https://{self.domain}/admin/api/2025-01"

    def headers(self) -> dict:
        return {
            "X-Shopify-Access-Token": self.token,
            "Content-Type": "application/json",
        }


def slugify(text: str) -> str:
    import re
    import unicodedata

    text = " ".join(text.replace("\n", " ").split()) or "produto"
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text or "produto"


def load_csv(path: Path) -> List[dict]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("CSV vazio")
    return rows


def find_csv(custom_path: Optional[str]) -> Path:
    if custom_path:
        return Path(custom_path).resolve()
    for candidate in DEFAULT_CSV_PATHS:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Nenhum CSV encontrado nas localizações padrão")


def fetch_all_products(cfg: ShopifyConfig) -> List[int]:
    ids: List[int] = []
    since_id = 0
    while True:
        params = {"limit": 250}
        if since_id:
            params["since_id"] = since_id
        res = requests.get(f"{cfg.base_url}/products.json", headers=cfg.headers(), params=params, timeout=30)
        res.raise_for_status()
        products = res.json().get("products", [])
        if not products:
            break
        ids.extend(p["id"] for p in products)
        since_id = products[-1]["id"]
        time.sleep(cfg.rate_delay)
    return ids


def delete_products(cfg: ShopifyConfig, product_ids: Iterable[int]) -> None:
    for pid in product_ids:
        url = f"{cfg.base_url}/products/{pid}.json"
        res = requests.delete(url, headers=cfg.headers(), timeout=30)
        if res.status_code not in (200, 204):
            print(f"⚠️  Falha ao apagar {pid}: {res.text}")
        else:
            print(f"🗑️  Produto {pid} removido")
        time.sleep(cfg.rate_delay)


def build_images(row: dict, images_base: Path) -> List[dict]:
    paths = [p.strip() for p in (row.get("image_paths") or "").split("|") if p.strip()]
    payload: List[dict] = []
    for position, rel_path in enumerate(paths, start=1):
        file_path = images_base / rel_path
        if not file_path.exists():
            print(f"   ⚠️  Imagem não encontrada: {file_path}")
            continue
        with file_path.open("rb") as img:
            b64 = base64.b64encode(img.read()).decode("utf-8")
        payload.append({
            "attachment": b64,
            "filename": file_path.name,
            "position": position,
            "alt": row.get("name") or row.get("sku") or file_path.stem,
        })
    return payload


def parse_price(value: str) -> str:
    value = value or "0"
    cleaned = value.replace("€", "").replace(",", ".")
    import re

    cleaned = re.sub(r"[^0-9.]", "", cleaned)
    if cleaned.count(".") > 1:
        first = cleaned.find(".")
        cleaned = cleaned[: first + 1] + cleaned[first + 1 :].replace(".", "")
    try:
        return f"{float(cleaned):.2f}"
    except ValueError:
        return "0.00"


def create_product(cfg: ShopifyConfig, row: dict, images_base: Path) -> bool:
    title = (row.get("name") or "").strip()
    price = parse_price(row.get("regular_price", ""))
    if not title or price == "0.00":
        print(f"⚠️  Ignorado sem título/preço: {row.get('sku')}")
        return False

    sku = (row.get("sku") or slugify(title))[:40]
    description = row.get("description_html", "").strip()
    categories = row.get("categories", "")
    product_type = categories.split(">").pop().strip() if categories else "Catalogo"
    tags = ", ".join([t.strip() for t in (row.get("tags") or "").split(",") if t.strip()])

    variant = {
        "sku": sku,
        "price": price,
        "compare_at_price": parse_price(row.get("sale_price", "")) if row.get("sale_price") else None,
        "inventory_management": "shopify",
        "inventory_policy": "deny",
        "inventory_quantity": int(float(row.get("stock") or 0)),
        "requires_shipping": True,
        "taxable": True,
        "option1": "Default Title",
    }

    payload = {
        "product": {
            "title": title,
            "body_html": description,
            "vendor": "Chapeus Lisboetas",
            "product_type": product_type,
            "tags": tags,
            "handle": slugify(title),
            "status": "active",
            "options": [{"name": "Title"}],
            "variants": [variant],
            "images": build_images(row, images_base),
        }
    }

    res = requests.post(
        f"{cfg.base_url}/products.json",
        headers=cfg.headers(),
        json=payload,
        timeout=120,
    )
    if res.status_code not in (200, 201):
        print(f"❌ Falhou {sku}: {res.text}")
        return False
    print(f"✅ Criado {title} ({sku})")
    time.sleep(cfg.rate_delay)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Publica produtos e imagens diretamente no Shopify")
    parser.add_argument("--csv", help="Caminho para o CSV limpo")
    parser.add_argument("--images-base", default="output_catalogo", help="Diretório base das imagens")
    parser.add_argument("--no-delete", action="store_true", help="Não apagar produtos existentes antes")
    args = parser.parse_args()

    domain = os.environ.get("SHOPIFY_STORE_DOMAIN") or os.environ.get("SHOPIFY_DOMAIN")
    token = os.environ.get("SHOPIFY_ADMIN_API_TOKEN") or os.environ.get("shopify_admin_api_token")
    if not domain or not token:
        raise SystemExit("Defina SHOPIFY_STORE_DOMAIN e SHOPIFY_ADMIN_API_TOKEN no ambiente")

    cfg = ShopifyConfig(domain=domain, token=token)
    csv_path = find_csv(args.csv)
    images_base = Path(args.images_base).resolve()

    rows = load_csv(csv_path)
    print(f"📄 CSV carregado: {csv_path} ({len(rows)} linhas)")

    if not args.no_delete:
        product_ids = fetch_all_products(cfg)
        if product_ids:
            print(f"🗑️  Apagando {len(product_ids)} produtos existentes...")
            delete_products(cfg, product_ids)
        else:
            print("ℹ️  Nenhum produto anterior encontrado")

    created = 0
    for row in rows:
        if create_product(cfg, row, images_base):
            created += 1

    print(f"\n🎯 Publicação concluída: {created}/{len(rows)} produtos criados")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrompido pelo utilizador", file=sys.stderr)
        sys.exit(130)
