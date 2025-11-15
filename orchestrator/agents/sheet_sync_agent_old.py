#!/usr/bin/env python3
"""
SHEETSYNC-AGENT - Google Sheets → WordPress Sync
Phase 1: Data Foundation

Synchronizes 17 worksheets from Google Sheets to WordPress products
- Pulls all product data (SKU, Nome, Preço, Descrição, etc.)
- Creates/updates WooCommerce products
- Respects NO PRICE = NO PUBLISH rule
- Handles product categories mapping
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from base_agent import BaseAgent
import gspread
from google.oauth2.service_account import Credentials
import re
from typing import Dict, List, Optional, Tuple

# Google Sheets configuration
GOOGLE_SHEETS_ID = "1m5ObJBG3CXetWNN9BoXwE69EVA5RH-xMqozhY3d7ptw"
SERVICE_ACCOUNT_FILE = Path(__file__).resolve().parent.parent.parent / 'config' / 'google-service-account.json'

# Worksheet names (17 categories)
WORKSHEETS = [
    "BOINAS INVERNO",
    "BOINAS VERÃO",
    "PANAMÁ",
    "ARTIGOS EM PELE",
    "GORROS",
    "CHAPÉUS LÃ",
    "DIVERSOS",
    "FEMININO",
    "CERIMÓNIA",
    "PALHA",
    "À PROVA D'ÁGUA",
    "PROTEÇÃO SOLAR",
    "CHAPÉUS EM TECIDO",
    "VISEIRAS",
    "BONÉS",
    "COWBOY",
    "CORTIÇA"
]

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
    """Sync Google Sheets → WordPress products"""

    def __init__(self):
        super().__init__(
            name="SheetSync-Agent",
            description="Sync Google Sheets → WordPress (17 worksheets)"
        )
        self.sheets_client = None
        self.spreadsheet = None

    def connect_sheets(self):
        """Connect to Google Sheets API"""
        try:
            if not SERVICE_ACCOUNT_FILE.exists():
                self.add_error(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")
                return False

            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            creds = Credentials.from_service_account_file(
                str(SERVICE_ACCOUNT_FILE),
                scopes=scopes
            )

            self.sheets_client = gspread.authorize(creds)
            self.spreadsheet = self.sheets_client.open_by_key(GOOGLE_SHEETS_ID)

            self.logger.info(f"✓ Connected to Google Sheets: {self.spreadsheet.title}")
            return True

        except Exception as e:
            self.add_error(f"Failed to connect to Google Sheets: {e}")
            return False

    def parse_product_row(self, row: List[str], worksheet_name: str) -> Optional[Dict]:
        """
        Parse a product row from Google Sheets
        Expected columns: SKU, Nome, Preço, Descrição curta, Descrição longa, etc.
        """
        if len(row) < 3:  # Minimum: SKU, Nome, Preço
            return None

        # Extract fields (adjust indices based on actual sheet structure)
        product = {
            'sku': row[0].strip() if len(row) > 0 else "",
            'name': row[1].strip() if len(row) > 1 else "",
            'price': row[2].strip() if len(row) > 2 else "",
            'short_description': row[3].strip() if len(row) > 3 else "",
            'long_description': row[4].strip() if len(row) > 4 else "",
            'category': worksheet_name,
            'tags': row[5].strip() if len(row) > 5 else "",
            'color': row[6].strip() if len(row) > 6 else "",
            'size': row[7].strip() if len(row) > 7 else "",
            'composition': row[8].strip() if len(row) > 8 else "",
            'supplier_url': row[10].strip() if len(row) > 10 else "",
        }

        # Validate required fields
        if not product['sku']:
            return None

        if not product['name']:
            return None

        # NO PRICE = NO PUBLISH rule
        if not product['price'] or not self._is_valid_price(product['price']):
            self.add_warning(f"SKU {product['sku']} has no valid price - will be set as draft")
            product['status'] = 'draft'
        else:
            product['status'] = 'publish'

        return product

    def _is_valid_price(self, price_str: str) -> bool:
        """Validate price string"""
        try:
            price_str = price_str.replace('€', '').replace(',', '.').strip()
            price = float(price_str)
            return price > 0
        except (ValueError, AttributeError):
            return False

    def get_or_create_category(self, category_path: List[str]) -> Optional[int]:
        """
        Get or create WooCommerce product category
        category_path example: ["Chapéus", "Boinas", "Inverno"]
        Returns: term_id of the leaf category
        """
        cursor = self.db.cursor()
        parent_id = 0

        for category_name in category_path:
            # Check if category exists
            cursor.execute("""
                SELECT t.term_id
                FROM lx_terms t
                INNER JOIN lx_term_taxonomy tt ON t.term_id = tt.term_id
                WHERE tt.taxonomy = 'product_cat'
                AND t.name = %s
                AND tt.parent = %s
                LIMIT 1
            """, (category_name, parent_id))

            result = cursor.fetchone()

            if result:
                # Category exists
                parent_id = result[0]
            else:
                # Create category
                slug = category_name.lower().replace(' ', '-')
                slug = re.sub(r'[^a-z0-9\-]', '', slug)

                # Insert into lx_terms
                cursor.execute("""
                    INSERT INTO lx_terms (name, slug, term_group)
                    VALUES (%s, %s, 0)
                """, (category_name, slug))
                term_id = cursor.lastrowid

                # Insert into lx_term_taxonomy
                cursor.execute("""
                    INSERT INTO lx_term_taxonomy (term_id, taxonomy, description, parent, count)
                    VALUES (%s, 'product_cat', '', %s, 0)
                """, (term_id, parent_id))

                self.db.commit()
                parent_id = term_id
                self.logger.info(f"Created category: {category_name} (ID: {term_id})")

        cursor.close()
        return parent_id

    def find_product_by_sku(self, sku: str) -> Optional[int]:
        """Find WordPress product by SKU"""
        cursor = self.db.cursor()

        cursor.execute("""
            SELECT post_id FROM lx_postmeta
            WHERE meta_key = '_sku'
            AND UPPER(meta_value) = %s
            LIMIT 1
        """, (sku.upper(),))

        result = cursor.fetchone()
        cursor.close()

        return result[0] if result else None

    def create_or_update_product(self, product: Dict) -> bool:
        """Create or update WooCommerce product"""
        try:
            cursor = self.db.cursor()

            # Check if product exists
            product_id = self.find_product_by_sku(product['sku'])

            from datetime import datetime
            now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            if product_id:
                # Update existing product
                cursor.execute("""
                    UPDATE lx_posts
                    SET post_title = %s,
                        post_content = %s,
                        post_excerpt = %s,
                        post_status = %s,
                        post_modified = %s,
                        post_modified_gmt = %s
                    WHERE ID = %s
                """, (
                    product['name'],
                    product['long_description'],
                    product['short_description'],
                    product['status'],
                    now, now,
                    product_id
                ))

                self.logger.info(f"Updated product: {product['sku']} - {product['name']}")

            else:
                # Create new product
                post_name = product['name'].lower().replace(' ', '-')
                post_name = re.sub(r'[^a-z0-9\-]', '', post_name)

                cursor.execute("""
                    INSERT INTO lx_posts (
                        post_author, post_date, post_date_gmt, post_content,
                        post_title, post_excerpt, post_status, post_name,
                        post_modified, post_modified_gmt, post_type,
                        to_ping, pinged, post_content_filtered
                    ) VALUES (
                        1, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, 'product', '', '', ''
                    )
                """, (
                    now, now,
                    product['long_description'],
                    product['name'],
                    product['short_description'],
                    product['status'],
                    post_name,
                    now, now
                ))

                product_id = cursor.lastrowid
                self.logger.info(f"Created product: {product['sku']} - {product['name']} (ID: {product_id})")

            # Update product meta
            meta_updates = [
                ('_sku', product['sku']),
                ('_regular_price', product['price']),
                ('_price', product['price']),
                ('_stock_status', 'instock'),
                ('_manage_stock', 'no'),
                ('_visibility', 'visible'),
                ('_tax_status', 'taxable'),
                ('_tax_class', ''),
            ]

            for meta_key, meta_value in meta_updates:
                # Check if meta exists
                cursor.execute("""
                    SELECT meta_id FROM lx_postmeta
                    WHERE post_id = %s AND meta_key = %s
                """, (product_id, meta_key))

                if cursor.fetchone():
                    # Update
                    cursor.execute("""
                        UPDATE lx_postmeta
                        SET meta_value = %s
                        WHERE post_id = %s AND meta_key = %s
                    """, (meta_value, product_id, meta_key))
                else:
                    # Insert
                    cursor.execute("""
                        INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
                        VALUES (%s, %s, %s)
                    """, (product_id, meta_key, meta_value))

            # Assign category
            if product['category'] in CATEGORY_MAPPING:
                category_path = CATEGORY_MAPPING[product['category']]
                category_id = self.get_or_create_category(category_path)

                if category_id:
                    # Check if relationship exists
                    cursor.execute("""
                        SELECT object_id FROM lx_term_relationships
                        WHERE object_id = %s AND term_taxonomy_id = %s
                    """, (product_id, category_id))

                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO lx_term_relationships (object_id, term_taxonomy_id, term_order)
                            VALUES (%s, %s, 0)
                        """, (product_id, category_id))

            self.db.commit()
            cursor.close()

            self.record_success()
            return True

        except Exception as e:
            self.add_error(f"Failed to create/update product {product['sku']}: {e}")
            self.record_failure()
            return False

    def sync_worksheet(self, worksheet_name: str) -> int:
        """Sync a single worksheet"""
        try:
            worksheet = self.spreadsheet.worksheet(worksheet_name)
            all_values = worksheet.get_all_values()

            if not all_values:
                self.add_warning(f"Worksheet {worksheet_name} is empty")
                return 0

            # Skip header row
            data_rows = all_values[1:] if len(all_values) > 1 else []

            products_synced = 0

            for row in data_rows:
                product = self.parse_product_row(row, worksheet_name)

                if product:
                    if self.create_or_update_product(product):
                        products_synced += 1

            self.logger.info(f"✓ Synced {products_synced} products from {worksheet_name}")
            return products_synced

        except gspread.exceptions.WorksheetNotFound:
            self.add_warning(f"Worksheet not found: {worksheet_name}")
            return 0
        except Exception as e:
            self.add_error(f"Failed to sync worksheet {worksheet_name}: {e}")
            return 0

    def run(self) -> int:
        """Main execution"""
        # Connect to Google Sheets
        if not self.connect_sheets():
            return 1

        # Count total worksheets
        self.metrics.items_total = len(WORKSHEETS)

        # Create backup before making changes
        backup_file = self.create_backup("sheetsync_pre")

        # Sync each worksheet
        total_products_synced = 0

        for worksheet_name in WORKSHEETS:
            self.log_progress(
                f"Syncing {worksheet_name}...",
                (WORKSHEETS.index(worksheet_name) + 1) / len(WORKSHEETS) * 100
            )

            products_synced = self.sync_worksheet(worksheet_name)
            total_products_synced += products_synced

        self.logger.info(f"\n✓ Total products synced: {total_products_synced}")

        # Success if we synced at least 50% of worksheets
        success_threshold = 0.5
        if self.metrics.success_rate >= success_threshold:
            return 0
        else:
            self.logger.error(f"Success rate {self.metrics.success_rate:.1%} below threshold {success_threshold:.0%}")
            return 1


if __name__ == '__main__':
    agent = SheetSyncAgent()
    sys.exit(agent.execute())
