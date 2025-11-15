#!/usr/bin/env python3
"""
DIRECTIMAGEIMPORTER-AGENT - Direct Image Import Bypass
Phase 0.5: Image Fix (Workaround)

Bypasses GalleryLinker complexity by directly importing images
from products/ directory structure and assigning to products
"""

import sys
import os
import re
import mimetypes
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))
from base_agent import BaseAgent

PRODUCTS_DIR = Path(__file__).resolve().parent.parent.parent / 'wordpress' / 'wp-content' / 'uploads' / 'products'
UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / 'wordpress' / 'wp-content' / 'uploads'


class DirectImageImporterAgent(BaseAgent):
    """
    Direct image import and assignment

    Bypasses GalleryLinker's complex SKU matching by:
    1. Finding images in products/{category}/{sku-folder}/
    2. Importing to WordPress media library
    3. Assigning as featured image to product
    """

    def __init__(self):
        super().__init__(
            name="DirectImageImporter-Agent",
            description="Importa imagens diretamente do diretório products/"
        )

    def find_images_for_sku(self, sku):
        """Find images in products directory for a given SKU"""
        if not sku:
            return []

        images = []
        sku_clean = str(sku).strip()

        # Search in all category folders
        for category_folder in PRODUCTS_DIR.iterdir():
            if not category_folder.is_dir():
                continue

            # Search in SKU folders within category
            for sku_folder in category_folder.iterdir():
                if not sku_folder.is_dir():
                    continue

                # Check if folder name contains the SKU
                folder_name = sku_folder.name.lower()

                # Match patterns like: "bone-22182", "18220mi", "bone-18106mi-bone-18106k"
                if (sku_clean.lower() in folder_name or
                    f"bone-{sku_clean.lower()}" in folder_name or
                    f"-{sku_clean.lower()}" in folder_name or
                    folder_name.startswith(sku_clean.lower())):

                    # Find main images (img_01.jpg preferred)
                    for img_file in sku_folder.iterdir():
                        if img_file.is_file() and img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                            # Prefer img_01.jpg (full size, not thumbnails)
                            if img_file.name == 'img_01.jpg':
                                return [img_file]  # Best match, return immediately
                            elif 'img_01' in img_file.name and 'x' not in img_file.name and '-' not in img_file.name:
                                images.insert(0, img_file)  # High priority
                            elif 'x' not in img_file.name and '-' not in img_file.name:  # Full size images
                                images.append(img_file)

        return images

    def import_image_to_media_library(self, image_path, product_id, product_title):
        """Import image file to WordPress media library"""
        cursor = self.db.cursor()

        try:
            # Get relative path from uploads directory
            rel_path = image_path.relative_to(UPLOADS_DIR)

            # Check if image already exists
            cursor.execute("""
                SELECT ID FROM lx_posts
                WHERE post_type = 'attachment'
                AND guid LIKE %s
                LIMIT 1
            """, (f'%{rel_path}%',))

            result = cursor.fetchone()
            if result:
                attachment_id = result[0]
                self.logger.debug(f"Image already in media library: {attachment_id}")
                return attachment_id

            # Create attachment post
            mime_type = mimetypes.guess_type(str(image_path))[0] or 'image/jpeg'

            cursor.execute("""
                INSERT INTO lx_posts (
                    post_author, post_date, post_date_gmt, post_content, post_title,
                    post_excerpt, post_status, comment_status, ping_status, post_name,
                    to_ping, pinged, post_modified, post_modified_gmt,
                    post_content_filtered, post_type, post_mime_type, guid
                ) VALUES (
                    1, NOW(), NOW(), '', %s, '', 'inherit', 'closed', 'closed', %s,
                    '', '', NOW(), NOW(),
                    '', 'attachment', %s, %s
                )
            """, (
                product_title,
                f'attachment-{product_id}',
                mime_type,
                f'http://localhost:8080/wp-content/uploads/{rel_path}'
            ))

            attachment_id = cursor.lastrowid

            # Add attachment meta
            cursor.execute("""
                INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
                VALUES (%s, '_wp_attached_file', %s)
            """, (attachment_id, str(rel_path)))

            # Link attachment to product
            cursor.execute("""
                UPDATE lx_posts SET post_parent = %s
                WHERE ID = %s
            """, (product_id, attachment_id))

            self.db.commit()
            return attachment_id

        except Exception as e:
            self.add_error(f"Error importing image: {e}")
            self.db.rollback()
            return None
        finally:
            cursor.close()

    def assign_featured_image(self, product_id, attachment_id):
        """Assign featured image to product"""
        cursor = self.db.cursor()

        try:
            # Check if already has featured image
            cursor.execute("""
                SELECT meta_value FROM lx_postmeta
                WHERE post_id = %s AND meta_key = '_thumbnail_id'
                LIMIT 1
            """, (product_id,))

            if cursor.fetchone():
                # Update existing
                cursor.execute("""
                    UPDATE lx_postmeta
                    SET meta_value = %s
                    WHERE post_id = %s AND meta_key = '_thumbnail_id'
                """, (attachment_id, product_id))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
                    VALUES (%s, '_thumbnail_id', %s)
                """, (product_id, attachment_id))

            self.db.commit()
            return True

        except Exception as e:
            self.add_error(f"Error assigning featured image: {e}")
            self.db.rollback()
            return False
        finally:
            cursor.close()

    def run(self) -> int:
        """Main execution"""

        self.logger.info("Starting direct image import...")

        # Get all products
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT p.ID, p.post_title, pm.meta_value as sku
            FROM lx_posts p
            LEFT JOIN lx_postmeta pm ON p.ID = pm.post_id AND pm.meta_key = '_sku'
            WHERE p.post_type = 'product'
            AND p.post_status = 'publish'
            ORDER BY p.ID
        """)

        products = cursor.fetchall()
        cursor.close()

        self.logger.info(f"Found {len(products)} products")
        self.metrics.items_total = len(products)

        for product_id, title, sku in products:
            self.logger.info(f"[{product_id}] {title} (SKU: {sku or 'NO_SKU'})")

            if not sku:
                self.record_skip()
                self.add_warning(f"No SKU for product: {title}")
                continue

            # Find images
            images = self.find_images_for_sku(sku)

            if not images:
                self.record_failure()
                self.add_warning(f"No images found for SKU {sku}")
                continue

            self.logger.info(f"Found {len(images)} images, using: {images[0].name}")

            # Import to media library
            attachment_id = self.import_image_to_media_library(images[0], product_id, title)

            if not attachment_id:
                self.record_failure()
                continue

            # Assign as featured image
            if self.assign_featured_image(product_id, attachment_id):
                self.record_success()
                self.logger.info(f"✅ Assigned featured image: {attachment_id}")
            else:
                self.record_failure()

        # Summary
        coverage = (self.metrics.items_succeeded / self.metrics.items_total * 100) if self.metrics.items_total > 0 else 0

        self.logger.info(f"Image assignment complete: {self.metrics.items_succeeded}/{self.metrics.items_total} ({coverage:.1f}%)")

        if coverage >= 80:
            self.logger.info("✅ Image coverage >= 80% - SUCCESS")
            return 0
        else:
            self.logger.info(f"❌ Image coverage {coverage:.1f}% < 80% - FAILED")
            return 1


if __name__ == '__main__':
    agent = DirectImageImporterAgent()
    sys.exit(agent.execute())
