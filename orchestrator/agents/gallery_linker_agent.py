#!/usr/bin/env python3
"""
GALLERYLINKER-AGENT - Link Images to Products
Phase 2: Product Enrichment

Links AI photos to WooCommerce products:
- Sets featured images (_thumbnail_id)
- Populates product galleries (_product_image_gallery)
- Handles orphan attachments
- Validates image associations
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from base_agent import BaseAgent
import json
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class GalleryLinkerAgent(BaseAgent):
    """Link AI photos to WooCommerce products"""

    def __init__(self):
        super().__init__(
            name="GalleryLinker-Agent",
            description="Associa imagens aos produtos (featured + gallery)"
        )
        self.image_inventory = None

    def load_image_inventory(self) -> bool:
        """Load image inventory from ImageInventory-Agent"""
        inventory_path = BASE_DIR / 'relatorios' / 'orchestrator' / 'image_inventory.json'

        if not inventory_path.exists():
            self.add_error(f"Image inventory not found: {inventory_path}")
            self.add_error("Run ImageInventory-Agent first")
            return False

        try:
            self.image_inventory = json.loads(inventory_path.read_text())
            self.logger.info(f"Loaded inventory: {len(self.image_inventory)} products")
            return True
        except Exception as e:
            self.add_error(f"Failed to load inventory: {e}")
            return False

    def find_product_by_sku(self, sku: str) -> Optional[int]:
        """Find WordPress product by SKU"""
        cursor = self.db.cursor()

        # Try exact match
        cursor.execute("""
            SELECT post_id FROM lx_postmeta
            WHERE meta_key = '_sku'
            AND UPPER(meta_value) = %s
            LIMIT 1
        """, (sku.upper(),))

        result = cursor.fetchone()
        if result:
            cursor.close()
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

    def find_attachment_by_path(self, relative_path: str) -> Optional[int]:
        """Find attachment by relative path"""
        cursor = self.db.cursor()

        # Construct GUID
        guid = f"http://localhost:8080/wp-content/uploads/{relative_path}"

        cursor.execute("""
            SELECT ID FROM lx_posts
            WHERE guid = %s
            AND post_type = 'attachment'
            LIMIT 1
        """, (guid,))

        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    def set_featured_image(self, product_id: int, attachment_id: int) -> bool:
        """Set product featured image"""
        try:
            cursor = self.db.cursor()

            # Check if exists
            cursor.execute("""
                SELECT meta_id FROM lx_postmeta
                WHERE post_id = %s AND meta_key = '_thumbnail_id'
            """, (product_id,))

            if cursor.fetchone():
                # Update
                cursor.execute("""
                    UPDATE lx_postmeta
                    SET meta_value = %s
                    WHERE post_id = %s AND meta_key = '_thumbnail_id'
                """, (attachment_id, product_id))
            else:
                # Insert
                cursor.execute("""
                    INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
                    VALUES (%s, '_thumbnail_id', %s)
                """, (product_id, attachment_id))

            self.db.commit()
            cursor.close()
            return True

        except Exception as e:
            self.add_error(f"Failed to set featured image: {e}")
            return False

    def set_product_gallery(self, product_id: int, attachment_ids: List[int]) -> bool:
        """Set product image gallery"""
        if not attachment_ids:
            return True

        try:
            cursor = self.db.cursor()

            gallery_value = ','.join(map(str, attachment_ids))

            # Check if exists
            cursor.execute("""
                SELECT meta_id FROM lx_postmeta
                WHERE post_id = %s AND meta_key = '_product_image_gallery'
            """, (product_id,))

            if cursor.fetchone():
                # Update
                cursor.execute("""
                    UPDATE lx_postmeta
                    SET meta_value = %s
                    WHERE post_id = %s AND meta_key = '_product_image_gallery'
                """, (gallery_value, product_id))
            else:
                # Insert
                cursor.execute("""
                    INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
                    VALUES (%s, '_product_image_gallery', %s)
                """, (product_id, gallery_value))

            self.db.commit()
            cursor.close()
            return True

        except Exception as e:
            self.add_error(f"Failed to set gallery: {e}")
            return False

    def link_product_images(self, sku: str, inventory_data: Dict) -> bool:
        """Link all images for a product"""
        # Find product
        product_id = None
        for candidate in inventory_data.get('sku_candidates', []):
            product_id = self.find_product_by_sku(candidate)
            if product_id:
                break

        if not product_id:
            self.add_warning(f"Product not found for SKU candidates: {inventory_data.get('sku_candidates')}")
            return False

        # Find featured image (prioritize processed/editorial)
        featured_attachment_id = None
        gallery_attachment_ids = []

        # Priority: processed > editorial
        for photo_type in ['processed', 'editorial']:
            photos = inventory_data['photos_by_type'].get(photo_type, [])
            if photos:
                # Use first photo as featured
                photo_path = photos[0]['path']
                attachment_id = self.find_attachment_by_path(photo_path)

                if attachment_id:
                    featured_attachment_id = attachment_id
                    break

        if not featured_attachment_id:
            self.add_warning(f"No suitable featured image for {sku}")
            return False

        # Collect gallery images (angle, lifestyle, detail)
        for photo_type in ['angle', 'lifestyle', 'detail']:
            photos = inventory_data['photos_by_type'].get(photo_type, [])
            for photo in photos[:8]:  # Max 8 gallery images
                attachment_id = self.find_attachment_by_path(photo['path'])
                if attachment_id and attachment_id != featured_attachment_id:
                    gallery_attachment_ids.append(attachment_id)

        # Set featured image
        if not self.set_featured_image(product_id, featured_attachment_id):
            return False

        # Set gallery
        if gallery_attachment_ids:
            if not self.set_product_gallery(product_id, gallery_attachment_ids):
                return False

        self.logger.info(f"Linked {sku}: featured={featured_attachment_id}, gallery={len(gallery_attachment_ids)}")
        return True

    def run(self) -> int:
        """Main execution"""
        # Load image inventory
        if not self.load_image_inventory():
            return 1

        self.metrics.items_total = len(self.image_inventory)

        # Create backup
        self.create_backup("gallerylinker_pre")

        # Link images for each product
        for sku, inventory_data in self.image_inventory.items():
            if self.link_product_images(sku, inventory_data):
                self.record_success()
                self.log_progress(
                    f"Linked {sku}",
                    self.metrics.completion_rate * 100
                )
            else:
                self.record_failure()

        # Success if 70%+ products linked
        return 0 if self.metrics.success_rate >= 0.7 else 1


if __name__ == '__main__':
    agent = GalleryLinkerAgent()
    sys.exit(agent.execute())
