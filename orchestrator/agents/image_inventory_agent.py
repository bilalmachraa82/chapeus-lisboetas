#!/usr/bin/env python3
"""
IMAGEINVENTORY-AGENT - Catalog AI Photos by SKU
Phase 2: Product Enrichment

Scans filesystem and catalogs all 7,827 AI photos:
- Maps photos to SKUs
- Categorizes by type (angle, editorial, lifestyle)
- Validates file existence
- Generates inventory report
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from base_agent import BaseAgent
import re
import json
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PRODUCTS_DIR = BASE_DIR / 'wordpress' / 'wp-content' / 'uploads' / 'products'

class ImageInventoryAgent(BaseAgent):
    """Catalog all AI photos by SKU"""

    def __init__(self):
        super().__init__(
            name="ImageInventory-Agent",
            description="Cataloga fotos AI por SKU (7.827 ficheiros)"
        )
        self.inventory = {}

    def categorize_photo(self, photo_path: Path) -> str:
        """Categorize photo by filename pattern"""
        name = photo_path.stem.lower()

        if '_pro' in name:
            return 'processed'
        elif 'editorial' in name or name.startswith('img_01'):
            return 'editorial'
        elif 'angle' in name or re.match(r'img_0[2-9]', name):
            return 'angle'
        elif 'lifestyle' in name:
            return 'lifestyle'
        elif 'detail' in name:
            return 'detail'
        else:
            return 'other'

    def extract_sku_from_folder(self, folder_name: str) -> List[str]:
        """Extract SKU candidates from folder name"""
        candidates = []

        # Pattern 1: Pure numeric
        matches = re.findall(r'\b(\d{4,6})[a-zA-Z]{0,2}\b', folder_name)
        candidates.extend(matches)

        # Pattern 2: After dash
        matches = re.findall(r'-(\d{4,6})[a-zA-Z]{0,2}\b', folder_name)
        candidates.extend(matches)

        # Remove duplicates
        return list(dict.fromkeys([c.upper() for c in candidates]))

    def scan_product_folder(self, folder_path: Path, category: str) -> Dict:
        """Scan a single product folder"""
        folder_name = folder_path.name
        sku_candidates = self.extract_sku_from_folder(folder_name)

        photos_by_type = {
            'editorial': [],
            'angle': [],
            'lifestyle': [],
            'detail': [],
            'processed': [],
            'other': []
        }

        total_photos = 0

        # Scan for photos
        for ext in ['*.jpg', '*.png']:
            for photo in folder_path.glob(ext):
                # Skip thumbnails
                if re.search(r'-\d+x\d+\.(jpg|png)$', photo.name):
                    continue
                if photo.name.startswith('.'):
                    continue

                photo_type = self.categorize_photo(photo)
                photos_by_type[photo_type].append({
                    'filename': photo.name,
                    'path': str(photo.relative_to(BASE_DIR)),
                    'size_bytes': photo.stat().st_size
                })
                total_photos += 1

        if total_photos == 0:
            return None

        return {
            'folder_name': folder_name,
            'folder_path': str(folder_path.relative_to(BASE_DIR)),
            'category': category,
            'sku_candidates': sku_candidates,
            'total_photos': total_photos,
            'photos_by_type': photos_by_type,
            'has_featured': len(photos_by_type['editorial']) > 0 or len(photos_by_type['processed']) > 0
        }

    def scan_all_folders(self) -> Dict:
        """Scan all product folders"""
        inventory = {}

        if not PRODUCTS_DIR.exists():
            self.add_error(f"Products directory not found: {PRODUCTS_DIR}")
            return inventory

        for category_dir in PRODUCTS_DIR.iterdir():
            if not category_dir.is_dir():
                continue

            category_name = category_dir.name

            for product_dir in category_dir.iterdir():
                if not product_dir.is_dir():
                    continue

                folder_data = self.scan_product_folder(product_dir, category_name)

                if folder_data:
                    # Use first SKU candidate as key, or folder name
                    key = folder_data['sku_candidates'][0] if folder_data['sku_candidates'] else folder_data['folder_name']
                    inventory[key] = folder_data
                    self.record_success()
                else:
                    self.record_skip()

        return inventory

    def generate_inventory_report(self):
        """Generate comprehensive inventory report"""
        report_dir = BASE_DIR / 'relatorios' / 'orchestrator'
        report_dir.mkdir(parents=True, exist_ok=True)

        # JSON report (machine-readable)
        json_path = report_dir / 'image_inventory.json'
        json_path.write_text(json.dumps(self.inventory, indent=2, ensure_ascii=False))
        self.logger.info(f"Inventory JSON: {json_path}")

        # Markdown report (human-readable)
        md_path = report_dir / 'image_inventory.md'

        total_photos = sum(data['total_photos'] for data in self.inventory.values())
        folders_with_featured = sum(1 for data in self.inventory.values() if data['has_featured'])

        report = f"""# IMAGE INVENTORY REPORT

**Generated:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
**Total Folders:** {len(self.inventory)}
**Total Photos:** {total_photos}
**Folders with Featured Image:** {folders_with_featured}

## Summary by Category

"""

        # Count by category
        category_stats = {}
        for data in self.inventory.values():
            cat = data['category']
            if cat not in category_stats:
                category_stats[cat] = {'folders': 0, 'photos': 0}
            category_stats[cat]['folders'] += 1
            category_stats[cat]['photos'] += data['total_photos']

        for category, stats in sorted(category_stats.items()):
            report += f"- **{category}**: {stats['folders']} folders, {stats['photos']} photos\n"

        report += "\n## Photo Types Distribution\n\n"

        type_totals = {
            'editorial': 0,
            'angle': 0,
            'lifestyle': 0,
            'detail': 0,
            'processed': 0,
            'other': 0
        }

        for data in self.inventory.values():
            for photo_type, photos in data['photos_by_type'].items():
                type_totals[photo_type] += len(photos)

        for photo_type, count in sorted(type_totals.items(), key=lambda x: x[1], reverse=True):
            report += f"- **{photo_type.title()}**: {count} photos\n"

        report += "\n## Top 20 Products by Photo Count\n\n"

        sorted_products = sorted(
            self.inventory.items(),
            key=lambda x: x[1]['total_photos'],
            reverse=True
        )[:20]

        for sku, data in sorted_products:
            report += f"- **{sku}** ({data['folder_name']}): {data['total_photos']} photos\n"

        md_path.write_text(report)
        self.logger.info(f"Inventory report: {md_path}")

    def run(self) -> int:
        """Main execution"""
        self.logger.info("Scanning product directories...")

        # Scan all folders
        self.inventory = self.scan_all_folders()

        self.metrics.items_total = len(self.inventory) if self.inventory else 1

        if not self.inventory:
            self.add_error("No product folders found")
            return 1

        # Generate reports
        self.generate_inventory_report()

        self.logger.info(f"\nInventory complete:")
        self.logger.info(f"  - {len(self.inventory)} product folders")
        self.logger.info(f"  - {sum(d['total_photos'] for d in self.inventory.values())} total photos")

        return 0


if __name__ == '__main__':
    agent = ImageInventoryAgent()
    sys.exit(agent.execute())
