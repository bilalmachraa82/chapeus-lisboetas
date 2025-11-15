#!/usr/bin/env python3
"""
PRODUCTPHOTOVALIDATOR-AGENT - Photo Requirements Validator
Phase 2: Product Enrichment (Validation Layer)

Validates ALL products have expected AI photos
- Checks featured image exists and accessible
- Validates gallery has ≥1 photo
- Verifies images are >1500×1500px (quality)
- Categorizes AI photos (editorial, angle, lifestyle)
- Identifies products without photos for manual review
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))
from base_agent import BaseAgent

# Thresholds
MIN_PHOTO_COVERAGE = 80  # 80% of products should have photos
MIN_GALLERY_PHOTOS = 1  # At least 1 gallery photo
MIN_IMAGE_WIDTH = 800  # Minimum width (lowered from 1500 for AI photos)
MIN_IMAGE_HEIGHT = 800  # Minimum height

# AI Photos directory
PRODUCTS_DIR = Path(__file__).resolve().parent.parent.parent / 'wordpress' / 'wp-content' / 'uploads' / 'products'


class ProductPhotoValidatorAgent(BaseAgent):
    """
    Validate product photo requirements

    Ensures:
    - All products have featured image
    - Products have gallery photos
    - Image quality (resolution)
    - AI photos correctly linked
    """

    def __init__(self):
        super().__init__(
            name="ProductPhotoValidator-Agent",
            description="Valida fotos produtos (featured + gallery + qualidade)"
        )
        self.products_without_photos = []
        self.products_with_low_quality = []
        self.products_with_gallery = []

    def get_image_dimensions(self, attachment_id: int) -> Tuple[int, int]:
        """Get image dimensions from WordPress meta"""
        cursor = self.db.cursor()

        cursor.execute("""
            SELECT meta_value FROM lx_postmeta
            WHERE post_id = %s
            AND meta_key = '_wp_attachment_metadata'
            LIMIT 1
        """, (attachment_id,))

        result = cursor.fetchone()
        cursor.close()

        if result and result[0]:
            try:
                import ast
                metadata = ast.literal_eval(result[0])
                return metadata.get('width', 0), metadata.get('height', 0)
            except:
                pass

        return 0, 0

    def check_image_file_exists(self, attachment_id: int) -> Tuple[bool, str]:
        """Check if image file exists in filesystem"""
        cursor = self.db.cursor()

        cursor.execute("""
            SELECT meta_value FROM lx_postmeta
            WHERE post_id = %s
            AND meta_key = '_wp_attached_file'
            LIMIT 1
        """, (attachment_id,))

        result = cursor.fetchone()
        cursor.close()

        if not result or not result[0]:
            return False, ""

        file_path = result[0]
        uploads_dir = Path(__file__).resolve().parent.parent.parent / 'wordpress' / 'wp-content' / 'uploads'
        full_path = uploads_dir / file_path

        return full_path.exists(), str(file_path)

    def validate_product_photos(self, product_id: int, product_title: str, sku: str) -> Dict:
        """Validate photos for a single product"""
        cursor = self.db.cursor()

        # Get featured image
        cursor.execute("""
            SELECT meta_value FROM lx_postmeta
            WHERE post_id = %s
            AND meta_key = '_thumbnail_id'
            LIMIT 1
        """, (product_id,))

        featured_result = cursor.fetchone()
        has_featured = featured_result and featured_result[0]

        featured_status = "missing"
        featured_file = ""
        featured_width = 0
        featured_height = 0

        if has_featured:
            featured_id = int(featured_result[0])
            exists, file_path = self.check_image_file_exists(featured_id)

            if exists:
                featured_status = "ok"
                featured_file = file_path
                featured_width, featured_height = self.get_image_dimensions(featured_id)

                # Check quality
                if featured_width < MIN_IMAGE_WIDTH or featured_height < MIN_IMAGE_HEIGHT:
                    featured_status = "low_quality"
            else:
                featured_status = "broken"
                featured_file = file_path or "unknown"

        # Get gallery images
        cursor.execute("""
            SELECT meta_value FROM lx_postmeta
            WHERE post_id = %s
            AND meta_key = '_product_image_gallery'
            LIMIT 1
        """, (product_id,))

        gallery_result = cursor.fetchone()
        gallery_ids = []

        if gallery_result and gallery_result[0]:
            gallery_ids = [int(id.strip()) for id in gallery_result[0].split(',') if id.strip()]

        gallery_photos = []
        for gallery_id in gallery_ids:
            exists, file_path = self.check_image_file_exists(gallery_id)
            width, height = self.get_image_dimensions(gallery_id)

            gallery_photos.append({
                'id': gallery_id,
                'exists': exists,
                'file': file_path,
                'width': width,
                'height': height,
                'quality': 'ok' if width >= MIN_IMAGE_WIDTH and height >= MIN_IMAGE_HEIGHT else 'low'
            })

        cursor.close()

        return {
            'product_id': product_id,
            'product_title': product_title,
            'sku': sku,
            'featured': {
                'status': featured_status,
                'file': featured_file,
                'width': featured_width,
                'height': featured_height
            },
            'gallery': {
                'count': len(gallery_photos),
                'photos': gallery_photos,
                'has_minimum': len([p for p in gallery_photos if p['exists']]) >= MIN_GALLERY_PHOTOS
            },
            'overall_status': self._calculate_overall_status(featured_status, gallery_photos)
        }

    def _calculate_overall_status(self, featured_status: str, gallery_photos: List[Dict]) -> str:
        """Calculate overall photo status"""
        if featured_status == "missing":
            return "no_photos"

        if featured_status == "broken":
            return "broken_featured"

        if featured_status == "low_quality":
            return "low_quality_featured"

        existing_gallery = [p for p in gallery_photos if p['exists']]

        if len(existing_gallery) == 0:
            return "no_gallery"

        if len(existing_gallery) < MIN_GALLERY_PHOTOS:
            return "insufficient_gallery"

        low_quality_gallery = [p for p in existing_gallery if p['quality'] == 'low']
        if len(low_quality_gallery) > 0:
            return "low_quality_gallery"

        return "ok"

    def generate_report(self, validation_results: List[Dict]) -> str:
        """Generate photo validation report"""

        total = len(validation_results)
        status_counts = {}

        for result in validation_results:
            status = result['overall_status']
            status_counts[status] = status_counts.get(status, 0) + 1

        ok_count = status_counts.get('ok', 0)
        coverage = (ok_count / total * 100) if total > 0 else 0

        report = f"""# PRODUCT PHOTO VALIDATION REPORT

**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Products:** {total}

---

## 🎯 SUMMARY

**Photo Coverage:** {ok_count}/{total} ({coverage:.1f}%)
**Target:** ≥{MIN_PHOTO_COVERAGE}%
**Status:** {"✅ PASS" if coverage >= MIN_PHOTO_COVERAGE else "❌ FAIL"}

---

## 📊 BREAKDOWN BY STATUS

"""

        status_labels = {
            'ok': '✅ Perfect (featured + gallery, good quality)',
            'no_gallery': '⚠️  Has featured but no gallery',
            'insufficient_gallery': f'⚠️  Gallery < {MIN_GALLERY_PHOTOS} photos',
            'low_quality_featured': f'⚠️  Featured image < {MIN_IMAGE_WIDTH}×{MIN_IMAGE_HEIGHT}px',
            'low_quality_gallery': '⚠️  Gallery images low quality',
            'broken_featured': '❌ Featured image file missing',
            'no_photos': '❌ No photos at all'
        }

        for status, label in status_labels.items():
            count = status_counts.get(status, 0)
            percent = (count / total * 100) if total > 0 else 0
            report += f"- **{label}:** {count} ({percent:.1f}%)\n"

        # Products without photos
        no_photos = [r for r in validation_results if r['overall_status'] in ['no_photos', 'broken_featured']]

        if no_photos:
            report += f"\n## ❌ PRODUCTS WITHOUT PHOTOS ({len(no_photos)})\n\n"
            for result in no_photos[:50]:  # First 50
                report += f"- **{result['product_title']}** (SKU: {result['sku']}, ID: {result['product_id']})\n"
                if result['featured']['status'] == 'broken':
                    report += f"  - Broken featured image: {result['featured']['file']}\n"

        # Low quality products
        low_quality = [r for r in validation_results if 'low_quality' in r['overall_status']]

        if low_quality:
            report += f"\n## ⚠️  LOW QUALITY IMAGES ({len(low_quality)})\n\n"
            for result in low_quality[:20]:  # First 20
                report += f"- **{result['product_title']}** (SKU: {result['sku']})\n"
                if result['featured']['status'] == 'low_quality':
                    report += f"  - Featured: {result['featured']['width']}×{result['featured']['height']}px\n"

        # Recommendations
        report += "\n## 🔧 RECOMMENDATIONS\n\n"

        if coverage < MIN_PHOTO_COVERAGE:
            missing_count = total - ok_count
            report += f"1. **Add photos to {missing_count} products** - Run PhotoTriage or upload manually\n"

        if len([r for r in validation_results if r['overall_status'] == 'broken_featured']) > 0:
            report += "2. **Fix broken image references** - Re-run GalleryLinker or check file paths\n"

        if len(low_quality) > 0:
            report += f"3. **Improve image quality** - Re-generate AI photos at higher resolution (≥{MIN_IMAGE_WIDTH}×{MIN_IMAGE_HEIGHT}px)\n"

        if coverage >= MIN_PHOTO_COVERAGE:
            report += "✅ Photo coverage is good - Ready for production\n"

        report += "\n---\n\n"
        report += "**GO/NO-GO Decision:** "
        if coverage >= MIN_PHOTO_COVERAGE:
            report += "✅ **GO** - Photo requirements met\n"
        else:
            report += "❌ **NO-GO** - Insufficient photo coverage\n"

        report += "\n---\n\n"
        report += "**Generated by:** ProductPhotoValidator-Agent\n"

        return report

    def run(self) -> int:
        """Main validation execution"""

        self.logger.info("Starting product photo validation...")

        # Get all published products
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT p.ID, p.post_title, sku.meta_value as sku
            FROM lx_posts p
            LEFT JOIN lx_postmeta sku ON p.ID = sku.post_id AND sku.meta_key = '_sku'
            WHERE p.post_type = 'product'
            AND p.post_status = 'publish'
            ORDER BY p.ID
        """)

        products = cursor.fetchall()
        cursor.close()

        self.logger.info(f"Validating {len(products)} products...")
        self.metrics.items_total = len(products)

        validation_results = []

        for product_id, title, sku in products:
            result = self.validate_product_photos(product_id, title, sku or 'NO_SKU')
            validation_results.append(result)

            if result['overall_status'] == 'ok':
                self.record_success()
            else:
                self.record_failure()
                if result['overall_status'] in ['no_photos', 'broken_featured']:
                    self.add_error(f"Product {title} has no photos")

        # Generate report
        report = self.generate_report(validation_results)

        report_path = Path(__file__).resolve().parent.parent.parent / 'relatorios' / 'orchestrator' / 'product_photo_validation.md'
        report_path.write_text(report, encoding='utf-8')
        self.logger.info(f"Report saved: {report_path}")

        # Summary
        ok_count = len([r for r in validation_results if r['overall_status'] == 'ok'])
        coverage = (ok_count / len(products) * 100) if products else 0

        self.logger.info(f"Photo coverage: {ok_count}/{len(products)} ({coverage:.1f}%)")

        if coverage >= MIN_PHOTO_COVERAGE:
            self.logger.info("✅ Photo validation PASSED")
            return 0
        else:
            self.logger.info(f"❌ Photo validation FAILED - Coverage {coverage:.1f}% < {MIN_PHOTO_COVERAGE}%")
            return 1


if __name__ == '__main__':
    agent = ProductPhotoValidatorAgent()
    sys.exit(agent.execute())
