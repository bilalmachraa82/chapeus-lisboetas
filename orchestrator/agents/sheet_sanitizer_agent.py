#!/usr/bin/env python3
"""
SHEETSANITIZER-AGENT - Data Validation
Phase 1: Data Foundation

Validates all product data:
- Price format validation (>0, numeric)
- SKU format validation
- Required fields check
- Duplicate SKU detection
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from base_agent import BaseAgent
import re

class SheetSanitizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SheetSanitizer-Agent",
            description="Validação dados (preço>0, formato SKU)"
        )

    def validate_sku(self, sku: str) -> bool:
        """Validate SKU format"""
        if not sku:
            return False
        # SKU should be 4-6 digits optionally with letters
        return bool(re.match(r'^\d{4,6}[A-Z]{0,2}(-[A-Z])?$', sku.upper()))

    def validate_price(self, price_str: str) -> tuple[bool, float]:
        """Validate price"""
        try:
            price_str = price_str.replace('€', '').replace(',', '.').strip()
            price = float(price_str)
            return price > 0, price
        except (ValueError, AttributeError):
            return False, 0.0

    def run(self) -> int:
        cursor = self.db.cursor()

        # Get all products with SKU and price
        cursor.execute("""
            SELECT p.ID, p.post_title,
                   sku.meta_value as sku,
                   price.meta_value as price
            FROM lx_posts p
            LEFT JOIN lx_postmeta sku ON p.ID = sku.post_id AND sku.meta_key = '_sku'
            LEFT JOIN lx_postmeta price ON p.ID = price.post_id AND price.meta_key = '_price'
            WHERE p.post_type = 'product'
        """)

        products = cursor.fetchall()
        self.metrics.items_total = len(products)

        invalid_skus = []
        invalid_prices = []
        duplicates = {}

        for product_id, title, sku, price in products:
            # Validate SKU
            if not self.validate_sku(sku or ''):
                invalid_skus.append((product_id, title, sku))
                self.add_warning(f"Invalid SKU: {sku} for {title}")

            # Check duplicates
            if sku:
                if sku not in duplicates:
                    duplicates[sku] = []
                duplicates[sku].append((product_id, title))

            # Validate price
            is_valid_price, price_value = self.validate_price(price or '')
            if not is_valid_price:
                invalid_prices.append((product_id, title, price))
                self.add_warning(f"Invalid price: {price} for {title}")

            # Overall validation
            if self.validate_sku(sku or '') and is_valid_price:
                self.record_success()
            else:
                self.record_failure()

        # Report duplicates
        for sku, products_list in duplicates.items():
            if len(products_list) > 1:
                self.add_warning(f"Duplicate SKU {sku}: {len(products_list)} products")

        self.logger.info(f"\nValidation Summary:")
        self.logger.info(f"  Invalid SKUs: {len(invalid_skus)}")
        self.logger.info(f"  Invalid prices: {len(invalid_prices)}")
        self.logger.info(f"  Duplicate SKUs: {sum(1 for v in duplicates.values() if len(v) > 1)}")

        cursor.close()
        return 0 if self.metrics.success_rate >= 0.8 else 1

if __name__ == '__main__':
    agent = SheetSanitizerAgent()
    sys.exit(agent.execute())
