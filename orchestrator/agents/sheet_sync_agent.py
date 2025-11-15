#!/usr/bin/env python3
"""
SHEETSYNC-AGENT v2 - Catalogo.json → WordPress Sync
Phase 1: Data Foundation

ADAPTED: Reads from catalogo.json instead of Google Sheets directly
- Loads enriched product data (scraped from supplier URLs)
- Creates/updates WooCommerce products
- Respects NO PRICE = NO PUBLISH rule
- Links downloaded images
- Maps categories correctly
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

sys.path.append(str(Path(__file__).resolve().parent.parent))
from base_agent import BaseAgent

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CATALOGO_JSON = BASE_DIR / 'output_catalogo' / 'catalogo.json'

# WooCommerce category mapping
CATEGORY_MAPPING = {
    "BOINAS INVERNO": ["Chapéus", "Boinas", "Inverno"],
    "BOINAS VERÃO": ["Chapéus", "Boinas", "Verão"],
    "PANAMÁ": ["Chapéus", "Panamá"],
    "ARTIGOS EM PELE": ["Acessórios", "Pele"],
    "GORROS": ["Chapéus", "Gorros"],
    "CHAPÉUS LÃ": ["Chapéus", "Lã"],
    "DIVERSOS": ["Chapéus", "Diversos"],
    "FEMININO": ["Chapéus", "Feminino"],
    "CERIMÓNIA": ["Chapéus", "Cerimónia"],
    "PALHA": ["Chapéus", "Palha"],
    "À PROVA D'ÁGUA": ["Chapéus", "Impermeável"],
    "PROTEÇÃO SOLAR": ["Chapéus", "Proteção Solar"],
    "CHAPÉUS EM TECIDO": ["Chapéus", "Tecido"],
    "VISEIRAS": ["Chapéus", "Viseiras"],
    "BONÉS": ["Chapéus", "Bonés"],
    "COWBOY": ["Chapéus", "Cowboy"],
    "CORTIÇA": ["Acessórios", "Cortiça"]
}


class SheetSyncAgent(BaseAgent):
    """Sync catalogo.json → WordPress products"""

    def __init__(self):
        super().__init__(
            name="SheetSync-Agent-v2",
            description="Sync catalogo.json → WordPress (62 enriched products)"
        )

    def extract_sku(self, product: Dict) -> str:
        """Extract or generate SKU from product data"""
        # Priority 1: supplier_code (e.g., "Boné – 22182")
        if product.get('supplier_code'):
            # Extract numbers from supplier_code
            match = re.search(r'(\d{4,6})', product['supplier_code'])
            if match:
                return match.group(1)

        # Priority 2: Extract from name (last resort)
        if product.get('name'):
            match = re.search(r'(\d{4,6})', product['name'])
            if match:
                return match.group(1)

        # Priority 3: Generate from sheet + row
        sheet_prefix = product.get('sheet', 'UNKNOWN')[:3].upper()
        row = product.get('sheet_row', 0)
        return f"{sheet_prefix}{row:04d}"

    def find_product_by_sku(self, sku: str) -> Optional[int]:
        """Find WordPress product ID by SKU"""
        cursor = self.db.cursor()

        # Try exact match first
        cursor.execute("""
            SELECT post_id FROM lx_postmeta
            WHERE meta_key = '_sku'
            AND UPPER(meta_value) = %s
            LIMIT 1
        """, (sku.upper(),))

        result = cursor.fetchone()
        if result:
            return result[0]

        # Try partial match
        cursor.execute("""
            SELECT post_id FROM lx_postmeta
            WHERE meta_key = '_sku'
            AND UPPER(meta_value) LIKE %s
            LIMIT 1
        """, (f"{sku.upper()}%",))

        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    def get_or_create_category(self, category_path: List[str]) -> int:
        """Get or create WooCommerce category hierarchy"""
        cursor = self.db.cursor()
        parent_id = 0

        for cat_name in category_path:
            # Check if category exists
            cursor.execute("""
                SELECT t.term_id
                FROM lx_terms t
                INNER JOIN lx_term_taxonomy tt ON t.term_id = tt.term_id
                WHERE tt.taxonomy = 'product_cat'
                AND t.name = %s
                AND tt.parent = %s
                LIMIT 1
            """, (cat_name, parent_id))

            result = cursor.fetchone()

            if result:
                parent_id = result[0]
            else:
                # Create category
                slug = cat_name.lower().replace(' ', '-').replace('ã', 'a').replace('é', 'e').replace('ó', 'o')

                cursor.execute("INSERT INTO lx_terms (name, slug) VALUES (%s, %s)", (cat_name, slug))
                term_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO lx_term_taxonomy (term_id, taxonomy, description, parent, count)
                    VALUES (%s, 'product_cat', '', %s, 0)
                """, (term_id, parent_id))

                self.logger.info(f"Created category: {cat_name}")
                parent_id = term_id

        cursor.close()
        return parent_id

    def assign_product_category(self, product_id: int, category_id: int):
        """Assign category to product"""
        cursor = self.db.cursor()

        # Remove existing categories
        cursor.execute("""
            DELETE FROM lx_term_relationships
            WHERE object_id = %s
            AND term_taxonomy_id IN (
                SELECT term_taxonomy_id FROM lx_term_taxonomy WHERE taxonomy = 'product_cat'
            )
        """, (product_id,))

        # Add new category
        cursor.execute("""
            INSERT INTO lx_term_relationships (object_id, term_taxonomy_id)
            VALUES (%s, (SELECT term_taxonomy_id FROM lx_term_taxonomy WHERE term_id = %s AND taxonomy = 'product_cat'))
        """, (product_id, category_id))

        # Update category count
        cursor.execute("""
            UPDATE lx_term_taxonomy
            SET count = (
                SELECT COUNT(*) FROM lx_term_relationships WHERE term_taxonomy_id = lx_term_taxonomy.term_taxonomy_id
            )
            WHERE term_id = %s
        """, (category_id,))

        cursor.close()

    def create_or_update_product(self, product_data: Dict) -> bool:
        """Create or update WordPress product"""
        try:
            cursor = self.db.cursor()

            sku = self.extract_sku(product_data)
            product_id = self.find_product_by_sku(sku)

            # Determine status (NO PRICE = NO PUBLISH)
            price_raw = product_data.get('price', 0)
            try:
                price = float(price_raw) if price_raw else 0
            except (ValueError, TypeError):
                price = 0
            status = 'publish' if price and price > 0 else 'draft'

            # Product title
            title = product_data.get('name', 'Produto sem nome')

            # Short description (handle None)
            short_desc = product_data.get('info_short') or ''

            # Long description (build from specs)
            specs = product_data.get('specs', {})
            long_desc = (short_desc or '') + "\n\n"
            if specs:
                long_desc += "**Especificações:**\n"
                for key, value in specs.items():
                    long_desc += f"- {key}: {value}\n"

            if product_id:
                # UPDATE existing product
                cursor.execute("""
                    UPDATE lx_posts
                    SET post_title = %s,
                        post_content = %s,
                        post_excerpt = %s,
                        post_status = %s,
                        post_modified = NOW(),
                        post_modified_gmt = NOW()
                    WHERE ID = %s
                """, (title, long_desc, short_desc, status, product_id))

                self.logger.info(f"Updated product: {sku} - {title}")

            else:
                # INSERT new product
                cursor.execute("""
                    INSERT INTO lx_posts (
                        post_author, post_date, post_date_gmt, post_content, post_title,
                        post_excerpt, post_status, comment_status, ping_status,
                        post_name, post_modified, post_modified_gmt, post_parent,
                        guid, menu_order, post_type, post_mime_type, comment_count,
                        to_ping, pinged, post_content_filtered
                    ) VALUES (
                        1, NOW(), NOW(), %s, %s,
                        %s, %s, 'open', 'closed',
                        %s, NOW(), NOW(), 0,
                        '', 0, 'product', '', 0,
                        '', '', ''
                    )
                """, (long_desc, title, short_desc, status, sku.lower()))

                product_id = cursor.lastrowid
                self.logger.info(f"Created product: {sku} - {title}")

            # Update meta fields
            meta_fields = {
                '_sku': sku,
                '_price': str(price),
                '_regular_price': str(price),
                '_sale_price': '',
                '_stock_status': 'instock',
                '_manage_stock': 'no',
                '_virtual': 'no',
                '_downloadable': 'no',
                '_visibility': 'visible',
                '_featured': 'no',
                '_product_attributes': '',
            }

            # Add specs as attributes
            if specs:
                meta_fields['_product_specs'] = json.dumps(specs)

            for meta_key, meta_value in meta_fields.items():
                cursor.execute("""
                    DELETE FROM lx_postmeta WHERE post_id = %s AND meta_key = %s
                """, (product_id, meta_key))

                cursor.execute("""
                    INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
                    VALUES (%s, %s, %s)
                """, (product_id, meta_key, meta_value))

            # Assign category
            sheet_name = product_data.get('sheet', '')
            if sheet_name in CATEGORY_MAPPING:
                category_path = CATEGORY_MAPPING[sheet_name]
                category_id = self.get_or_create_category(category_path)
                self.assign_product_category(product_id, category_id)

            self.db.commit()
            cursor.close()
            return True

        except Exception as e:
            self.add_error(f"Failed to create/update product {sku}: {e}")
            self.db.rollback()
            return False

    def run(self) -> int:
        """Main execution"""

        # 1. Load catalogo.json
        if not CATALOGO_JSON.exists():
            self.add_error(f"Catalogo.json not found: {CATALOGO_JSON}")
            return 1

        with open(CATALOGO_JSON, 'r', encoding='utf-8') as f:
            products = json.load(f)

        self.logger.info(f"Loaded {len(products)} products from catalogo.json")
        self.metrics.items_total = len(products)

        # 2. Process each product
        for product in products:
            sku = self.extract_sku(product)
            price_raw = product.get('price', 0)

            # Convert price to float (handle strings)
            try:
                price = float(price_raw) if price_raw else 0
            except (ValueError, TypeError):
                price = 0

            # NO PRICE = NO PUBLISH
            if not price or price <= 0:
                self.add_warning(f"Skip {product.get('name')} - NO PRICE")
                self.record_skip()
                continue

            # Create/update
            success = self.create_or_update_product(product)

            if success:
                self.record_success()
            else:
                self.record_failure()

        # 3. Report
        self.logger.info(f"\nSync Summary:")
        self.logger.info(f"  Total: {self.metrics.items_total}")
        self.logger.info(f"  Succeeded: {self.metrics.items_succeeded}")
        self.logger.info(f"  Failed: {self.metrics.items_failed}")
        self.logger.info(f"  Skipped (no price): {self.metrics.items_skipped}")

        return 0 if self.metrics.success_rate >= 0.8 else 1


if __name__ == '__main__':
    agent = SheetSyncAgent()
    sys.exit(agent.execute())
