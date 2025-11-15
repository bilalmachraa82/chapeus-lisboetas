#!/usr/bin/env python3
"""Upload local product images to Shopify using Admin API."""

from __future__ import annotations

import argparse
import base64
import csv
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import requests
except ModuleNotFoundError as exc:  # pragma: no cover - guidance for missing deps
    raise SystemExit(
        "Missing dependency 'requests'. Install it with 'pip install requests'."
    ) from exc


CSV_IMAGE_SEPARATOR = "|"


def _normalize_sku(value: str) -> str:
    return value.strip().lower()


@dataclass
class ShopifyConfig:
    store_domain: str
    api_version: str
    access_token: str
    rate_limit_seconds: float = 0.5


class ShopifyUploader:
    def __init__(self, config: ShopifyConfig) -> None:
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": config.access_token,
            }
        )

    # ------------------------------------------------------------------
    # Product lookup helpers
    # ------------------------------------------------------------------
    def _products_endpoint(self) -> str:
        return (
            f"https://{self.config.store_domain}/admin/api/"
            f"{self.config.api_version}/products.json"
        )

    def _product_images_endpoint(self, product_id: int) -> str:
        return (
            f"https://{self.config.store_domain}/admin/api/"
            f"{self.config.api_version}/products/{product_id}/images.json"
        )

    def find_product_id_by_sku(self, sku: str) -> Optional[int]:
        """Iterate through products until we find a variant with the SKU."""

        normalized_sku = _normalize_sku(sku)
        since_id: Optional[int] = None

        while True:
            params: Dict[str, str] = {"limit": "250", "fields": "id,title,variants"}
            if since_id:
                params["since_id"] = str(since_id)

            response = self.session.get(
                self._products_endpoint(), params=params, timeout=30
            )
            if response.status_code != 200:
                raise RuntimeError(
                    f"Failed to fetch products (status {response.status_code}): {response.text}"
                )

            products = response.json().get("products", [])
            if not products:
                return None

            for product in products:
                for variant in product.get("variants", []):
                    variant_sku = variant.get("sku") or ""
                    if _normalize_sku(variant_sku) == normalized_sku:
                        return int(product["id"])

            since_id = int(products[-1]["id"])
            time.sleep(self.config.rate_limit_seconds)

    # ------------------------------------------------------------------
    # Image upload helpers
    # ------------------------------------------------------------------
    def upload_image(
        self,
        product_id: int,
        image_path: Path,
        alt_text: str,
        position: Optional[int] = None,
    ) -> Tuple[bool, str]:
        """Upload a single image file to Shopify and return status + message."""

        if not image_path.exists():
            return False, f"Imagem não encontrada: {image_path}"

        with image_path.open("rb") as handle:
            encoded = base64.b64encode(handle.read()).decode("utf-8")

        payload: Dict[str, object] = {"image": {"attachment": encoded, "alt": alt_text}}
        if position is not None:
            payload["image"]["position"] = position

        response = self.session.post(
            self._product_images_endpoint(product_id),
            json=payload,
            timeout=60,
        )

        if response.status_code in (200, 201):
            return True, "Upload concluído"

        return False, f"Erro {response.status_code}: {response.text}"


def parse_image_paths(raw_value: str) -> List[str]:
    if not raw_value:
        return []
    parts = [segment.strip() for segment in raw_value.split(CSV_IMAGE_SEPARATOR)]
    return [segment for segment in parts if segment]


def process_csv(
    csv_path: Path,
    images_base: Path,
    uploader: ShopifyUploader,
    only_skus: Optional[Sequence[str]] = None,
    start_from_sku: Optional[str] = None,
) -> None:
    only_normalized = {_normalize_sku(sku) for sku in only_skus} if only_skus else None
    start_normalized = _normalize_sku(start_from_sku) if start_from_sku else None
    skip_mode = start_normalized is not None

    with csv_path.open("r", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            sku = row.get("sku", "").strip()
            product_name = row.get("name", "").strip() or sku or "Produto sem nome"

            if not sku:
                print("⚠️  Linha ignorada: SKU em branco")
                continue

            normalized_sku = _normalize_sku(sku)
            if only_normalized and normalized_sku not in only_normalized:
                continue

            if skip_mode:
                if normalized_sku == start_normalized:
                    skip_mode = False
                else:
                    continue

            image_paths = parse_image_paths(row.get("image_paths", ""))
            if not image_paths:
                print(f"⚠️  {sku}: sem imagens no CSV")
                continue

            print(f"➡️  {sku} — {product_name}")
            product_id = uploader.find_product_id_by_sku(sku)
            if not product_id:
                print(f"   ❌ Produto não encontrado no Shopify (SKU: {sku})")
                continue

            print(f"   ✅ Produto Shopify ID {product_id}")

            for index, relative_path in enumerate(image_paths, start=1):
                resolved = images_base / relative_path
                success, message = uploader.upload_image(
                    product_id=product_id,
                    image_path=resolved,
                    alt_text=product_name,
                    position=index,
                )
                label = resolved.name
                if success:
                    print(f"      ✅ {label}: {message}")
                else:
                    print(f"      ❌ {label}: {message}")

                time.sleep(uploader.config.rate_limit_seconds)

            # Pequena pausa entre produtos
            time.sleep(1.0)


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload automático de imagens para Shopify"
    )
    parser.add_argument(
        "--csv",
        default="output_catalogo/lovable_import.csv",
        type=Path,
        help="Caminho para o CSV com SKUs e image_paths",
    )
    parser.add_argument(
        "--images-base",
        default=Path("output_catalogo"),
        type=Path,
        help="Diretório base onde a pasta images/ está localizada",
    )
    parser.add_argument(
        "--store",
        default="lovable-project-rswvt.myshopify.com",
        help="Domínio do Shopify (sem https)",
    )
    parser.add_argument(
        "--api-version",
        default="2025-01",
        help="Versão da API Admin",
    )
    parser.add_argument(
        "--access-token",
        default=None,
        help="Token Admin API (sobrepõe variável de ambiente SHOPIFY_ADMIN_API_KEY)",
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=0.5,
        help="Espera em segundos entre requisições",
    )
    parser.add_argument(
        "--only-skus",
        nargs="*",
        help="Processa apenas os SKUs indicados",
    )
    parser.add_argument(
        "--start-from",
        help="Ignora linhas até encontrar este SKU",
    )
    return parser.parse_args(args)


def main(cli_args: Optional[Sequence[str]] = None) -> None:
    args = parse_args(cli_args)

    access_token = args.access_token or os.environ.get("SHOPIFY_ADMIN_API_KEY")
    if not access_token:
        raise SystemExit(
            "Defina SHOPIFY_ADMIN_API_KEY ou use --access-token com a chave do Admin API"
        )

    config = ShopifyConfig(
        store_domain=args.store,
        api_version=args.api_version,
        access_token=access_token,
        rate_limit_seconds=max(args.rate_limit, 0.2),
    )

    uploader = ShopifyUploader(config)
    process_csv(
        csv_path=args.csv.resolve(),
        images_base=args.images_base.resolve(),
        uploader=uploader,
        only_skus=args.only_skus,
        start_from_sku=args.start_from,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrompido pelo utilizador", file=sys.stderr)
        sys.exit(130)
