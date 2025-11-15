#!/usr/bin/env python3
"""
DATAINTEGRITYVALIDATOR-AGENT - Database Health Validator
Phase 3: UX Polish (Validation Layer)

Validates database integrity to prevent corruption
- No orphan meta fields (meta without parent post)
- No duplicate SKUs
- All published products have price >0
- All products have category assignment
- Foreign key consistency
- Meta field completeness

CRITICAL: This agent MUST pass before production deployment
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))
from base_agent import BaseAgent

# Thresholds
MAX_ORPHAN_META_PERCENT = 1  # Max 1% orphan meta fields acceptable
MAX_DUPLICATE_SKUS = 0  # Zero duplicates allowed
MIN_PRODUCTS_WITH_PRICE = 95  # 95% products must have price
MIN_PRODUCTS_WITH_CATEGORY = 98  # 98% products must have category


class DataIntegrityValidatorAgent(BaseAgent):
    """
    Validate database integrity

    Ensures:
    - No orphan meta fields
    - No duplicate SKUs
    - Price coverage
    - Category assignment
    - Foreign key consistency
    """

    def __init__(self):
        super().__init__(
            name="DataIntegrityValidator-Agent",
            description="Valida integridade da base de dados (orphans, duplicates, consistency)"
        )
        self.validation_results = {}

    def check_orphan_meta(self) -> Dict:
        """Check for orphan meta fields (meta without parent post)"""
        cursor = self.db.cursor()

        # Count total meta entries
        cursor.execute("SELECT COUNT(*) FROM lx_postmeta")
        total_meta = cursor.fetchone()[0]

        # Find orphan meta (post_id doesn't exist in lx_posts)
        cursor.execute("""
            SELECT COUNT(DISTINCT pm.meta_id)
            FROM lx_postmeta pm
            LEFT JOIN lx_posts p ON pm.post_id = p.ID
            WHERE p.ID IS NULL
        """)
        orphan_count = cursor.fetchone()[0]

        # Get sample orphan IDs for reporting
        cursor.execute("""
            SELECT pm.meta_id, pm.post_id, pm.meta_key
            FROM lx_postmeta pm
            LEFT JOIN lx_posts p ON pm.post_id = p.ID
            WHERE p.ID IS NULL
            LIMIT 20
        """)
        orphan_samples = cursor.fetchall()

        cursor.close()

        orphan_percent = (orphan_count / max(total_meta, 1)) * 100
        passed = orphan_percent <= MAX_ORPHAN_META_PERCENT

        return {
            'total_meta': total_meta,
            'orphan_count': orphan_count,
            'orphan_percent': orphan_percent,
            'orphan_samples': [
                {'meta_id': mid, 'post_id': pid, 'meta_key': key}
                for mid, pid, key in orphan_samples
            ],
            'passed': passed,
            'threshold': MAX_ORPHAN_META_PERCENT
        }

    def check_duplicate_skus(self) -> Dict:
        """Check for duplicate SKU values"""
        cursor = self.db.cursor()

        # Find duplicate SKUs
        cursor.execute("""
            SELECT meta_value as sku, COUNT(*) as count, GROUP_CONCAT(post_id) as product_ids
            FROM lx_postmeta
            WHERE meta_key = '_sku'
            AND meta_value IS NOT NULL
            AND meta_value != ''
            GROUP BY meta_value
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)

        duplicates = []
        for sku, count, product_ids in cursor.fetchall():
            # Get product titles
            ids = [int(id.strip()) for id in product_ids.split(',')]
            cursor.execute(f"""
                SELECT ID, post_title
                FROM lx_posts
                WHERE ID IN ({','.join(map(str, ids))})
            """)
            products = cursor.fetchall()

            duplicates.append({
                'sku': sku,
                'count': count,
                'products': [{'id': pid, 'title': title} for pid, title in products]
            })

        cursor.close()

        total_duplicates = len(duplicates)
        passed = total_duplicates <= MAX_DUPLICATE_SKUS

        return {
            'duplicate_count': total_duplicates,
            'duplicates': duplicates[:20],  # First 20
            'passed': passed,
            'threshold': MAX_DUPLICATE_SKUS
        }

    def check_price_coverage(self) -> Dict:
        """Check product price coverage"""
        cursor = self.db.cursor()

        # Get all published products
        cursor.execute("""
            SELECT COUNT(*)
            FROM lx_posts
            WHERE post_type = 'product'
            AND post_status = 'publish'
        """)
        total_products = cursor.fetchone()[0]

        # Count products with price >0
        cursor.execute("""
            SELECT COUNT(DISTINCT p.ID)
            FROM lx_posts p
            INNER JOIN lx_postmeta pm ON p.ID = pm.post_id
            WHERE p.post_type = 'product'
            AND p.post_status = 'publish'
            AND pm.meta_key = '_price'
            AND CAST(pm.meta_value AS DECIMAL(10,2)) > 0
        """)
        products_with_price = cursor.fetchone()[0]

        # Get products without price
        cursor.execute("""
            SELECT p.ID, p.post_title, sku.meta_value as sku
            FROM lx_posts p
            LEFT JOIN lx_postmeta pm ON p.ID = pm.post_id AND pm.meta_key = '_price'
            LEFT JOIN lx_postmeta sku ON p.ID = sku.post_id AND sku.meta_key = '_sku'
            WHERE p.post_type = 'product'
            AND p.post_status = 'publish'
            AND (pm.meta_value IS NULL OR CAST(pm.meta_value AS DECIMAL(10,2)) <= 0)
            LIMIT 50
        """)
        no_price_products = [
            {'id': pid, 'title': title, 'sku': sku or 'NO_SKU'}
            for pid, title, sku in cursor.fetchall()
        ]

        cursor.close()

        coverage_percent = (products_with_price / max(total_products, 1)) * 100
        passed = coverage_percent >= MIN_PRODUCTS_WITH_PRICE

        return {
            'total_products': total_products,
            'products_with_price': products_with_price,
            'products_without_price': total_products - products_with_price,
            'coverage_percent': coverage_percent,
            'no_price_samples': no_price_products[:20],
            'passed': passed,
            'threshold': MIN_PRODUCTS_WITH_PRICE
        }

    def check_category_assignment(self) -> Dict:
        """Check product category assignment"""
        cursor = self.db.cursor()

        # Get all published products
        cursor.execute("""
            SELECT COUNT(*)
            FROM lx_posts
            WHERE post_type = 'product'
            AND post_status = 'publish'
        """)
        total_products = cursor.fetchone()[0]

        # Count products with category
        cursor.execute("""
            SELECT COUNT(DISTINCT p.ID)
            FROM lx_posts p
            INNER JOIN lx_term_relationships tr ON p.ID = tr.object_id
            INNER JOIN lx_term_taxonomy tt ON tr.term_taxonomy_id = tt.term_taxonomy_id
            WHERE p.post_type = 'product'
            AND p.post_status = 'publish'
            AND tt.taxonomy = 'product_cat'
        """)
        products_with_category = cursor.fetchone()[0]

        # Get products without category
        cursor.execute("""
            SELECT p.ID, p.post_title, sku.meta_value as sku
            FROM lx_posts p
            LEFT JOIN lx_postmeta sku ON p.ID = sku.post_id AND sku.meta_key = '_sku'
            LEFT JOIN lx_term_relationships tr ON p.ID = tr.object_id
            LEFT JOIN lx_term_taxonomy tt ON tr.term_taxonomy_id = tt.term_taxonomy_id AND tt.taxonomy = 'product_cat'
            WHERE p.post_type = 'product'
            AND p.post_status = 'publish'
            AND tt.term_taxonomy_id IS NULL
            LIMIT 50
        """)
        no_category_products = [
            {'id': pid, 'title': title, 'sku': sku or 'NO_SKU'}
            for pid, title, sku in cursor.fetchall()
        ]

        cursor.close()

        coverage_percent = (products_with_category / max(total_products, 1)) * 100
        passed = coverage_percent >= MIN_PRODUCTS_WITH_CATEGORY

        return {
            'total_products': total_products,
            'products_with_category': products_with_category,
            'products_without_category': total_products - products_with_category,
            'coverage_percent': coverage_percent,
            'no_category_samples': no_category_products[:20],
            'passed': passed,
            'threshold': MIN_PRODUCTS_WITH_CATEGORY
        }

    def check_meta_completeness(self) -> Dict:
        """Check required WooCommerce meta fields exist for all products"""
        cursor = self.db.cursor()

        required_meta_keys = [
            '_sku',
            '_price',
            '_regular_price',
            '_stock_status',
            '_manage_stock',
            '_visibility',
        ]

        # Get all published products
        cursor.execute("""
            SELECT COUNT(*)
            FROM lx_posts
            WHERE post_type = 'product'
            AND post_status = 'publish'
        """)
        total_products = cursor.fetchone()[0]

        completeness = {}
        for meta_key in required_meta_keys:
            cursor.execute(f"""
                SELECT COUNT(DISTINCT p.ID)
                FROM lx_posts p
                INNER JOIN lx_postmeta pm ON p.ID = pm.post_id
                WHERE p.post_type = 'product'
                AND p.post_status = 'publish'
                AND pm.meta_key = %s
                AND pm.meta_value IS NOT NULL
                AND pm.meta_value != ''
            """, (meta_key,))
            count = cursor.fetchone()[0]
            percent = (count / max(total_products, 1)) * 100

            completeness[meta_key] = {
                'count': count,
                'percent': percent,
                'missing': total_products - count
            }

        cursor.close()

        # Consider passed if all required fields have >90% coverage
        passed = all(data['percent'] >= 90 for data in completeness.values())

        return {
            'total_products': total_products,
            'completeness': completeness,
            'passed': passed
        }

    def generate_report(self, results: Dict) -> str:
        """Generate comprehensive data integrity report"""

        report = f"""# DATA INTEGRITY VALIDATION REPORT

**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🎯 SUMMARY

"""

        # Overall status
        all_passed = all([
            results['orphan_meta']['passed'],
            results['duplicate_skus']['passed'],
            results['price_coverage']['passed'],
            results['category_assignment']['passed'],
            results['meta_completeness']['passed']
        ])

        if all_passed:
            report += "**Status:** ✅ **PASSED** - Database integrity is good\n\n"
        else:
            report += "**Status:** ❌ **FAILED** - Issues detected, requires attention\n\n"

        # Orphan meta check
        orphan = results['orphan_meta']
        report += f"""## 🔗 ORPHAN META FIELDS CHECK

- **Total meta entries:** {orphan['total_meta']:,}
- **Orphan meta entries:** {orphan['orphan_count']:,} ({orphan['orphan_percent']:.1f}%)
- **Threshold:** <{orphan['threshold']}%
- **Status:** {"✅ PASS" if orphan['passed'] else "❌ FAIL"}

"""

        if orphan['orphan_samples']:
            report += "**Sample orphan meta (no parent post):**\n"
            for sample in orphan['orphan_samples'][:10]:
                report += f"- Meta ID {sample['meta_id']}: post_id={sample['post_id']}, key={sample['meta_key']}\n"
            report += "\n"

        # Duplicate SKUs check
        dupes = results['duplicate_skus']
        report += f"""## 🔢 DUPLICATE SKU CHECK

- **Duplicate SKUs found:** {dupes['duplicate_count']}
- **Threshold:** {dupes['threshold']} (zero tolerance)
- **Status:** {"✅ PASS" if dupes['passed'] else "❌ FAIL"}

"""

        if dupes['duplicates']:
            report += "**Duplicate SKUs:**\n"
            for dupe in dupes['duplicates'][:10]:
                report += f"- **SKU {dupe['sku']}:** {dupe['count']} products\n"
                for product in dupe['products']:
                    report += f"  - {product['title']} (ID: {product['id']})\n"
            report += "\n"

        # Price coverage check
        price = results['price_coverage']
        report += f"""## 💰 PRICE COVERAGE CHECK

- **Total products:** {price['total_products']}
- **Products with price >0:** {price['products_with_price']} ({price['coverage_percent']:.1f}%)
- **Products without price:** {price['products_without_price']}
- **Threshold:** ≥{price['threshold']}%
- **Status:** {"✅ PASS" if price['passed'] else "❌ FAIL"}

"""

        if price['no_price_samples']:
            report += f"**Products without price ({len(price['no_price_samples'])} samples):**\n"
            for product in price['no_price_samples'][:10]:
                report += f"- {product['title']} (SKU: {product['sku']}, ID: {product['id']})\n"
            report += "\n"

        # Category assignment check
        cat = results['category_assignment']
        report += f"""## 📁 CATEGORY ASSIGNMENT CHECK

- **Total products:** {cat['total_products']}
- **Products with category:** {cat['products_with_category']} ({cat['coverage_percent']:.1f}%)
- **Products without category:** {cat['products_without_category']}
- **Threshold:** ≥{cat['threshold']}%
- **Status:** {"✅ PASS" if cat['passed'] else "❌ FAIL"}

"""

        if cat['no_category_samples']:
            report += f"**Products without category ({len(cat['no_category_samples'])} samples):**\n"
            for product in cat['no_category_samples'][:10]:
                report += f"- {product['title']} (SKU: {product['sku']}, ID: {product['id']})\n"
            report += "\n"

        # Meta completeness check
        meta = results['meta_completeness']
        report += f"""## 📋 META FIELD COMPLETENESS CHECK

**Total products:** {meta['total_products']}

| Meta Key | Coverage | Missing | Status |
|----------|----------|---------|--------|
"""

        for key, data in meta['completeness'].items():
            status = "✅" if data['percent'] >= 90 else "⚠️"
            report += f"| {key} | {data['count']} ({data['percent']:.1f}%) | {data['missing']} | {status} |\n"

        meta_status = "✅ PASS" if meta['passed'] else "❌ FAIL"
        report += f"\n**Status:** {meta_status} (all fields ≥90%)\n\n"

        # Recommendations
        report += "## 🔧 RECOMMENDATIONS\n\n"

        if not orphan['passed']:
            report += f"1. **Clean orphan meta entries** - Remove {orphan['orphan_count']} orphan meta records\n"

        if not dupes['passed']:
            report += f"2. **Fix duplicate SKUs** - Resolve {dupes['duplicate_count']} SKU conflicts\n"

        if not price['passed']:
            report += f"3. **Add missing prices** - {price['products_without_price']} products need pricing\n"

        if not cat['passed']:
            report += f"4. **Assign categories** - {cat['products_without_category']} products need category assignment\n"

        if not meta['passed']:
            report += "5. **Complete meta fields** - Some required WooCommerce fields missing\n"

        if all_passed:
            report += "✅ No action required - Database integrity is good\n"

        report += "\n---\n\n"
        report += "**GO/NO-GO Decision:** "
        if all_passed:
            report += "✅ **GO** - Database integrity verified\n"
        else:
            report += "❌ **NO-GO** - Fix integrity issues before deployment\n"

        report += "\n---\n\n"
        report += "**Generated by:** DataIntegrityValidator-Agent\n"
        report += "**For:** Chapéus Lisboeta (Tiago Andrade)\n"

        return report

    def run(self) -> int:
        """Main validation execution"""

        self.logger.info("Starting data integrity validation...")

        # Run all validation checks
        self.logger.info("Checking orphan meta fields...")
        orphan_meta = self.check_orphan_meta()
        if orphan_meta['passed']:
            self.record_success()
        else:
            self.record_failure()
            self.add_error(f"Orphan meta: {orphan_meta['orphan_count']} entries ({orphan_meta['orphan_percent']:.1f}%)")

        self.logger.info("Checking duplicate SKUs...")
        duplicate_skus = self.check_duplicate_skus()
        if duplicate_skus['passed']:
            self.record_success()
        else:
            self.record_failure()
            self.add_error(f"Duplicate SKUs: {duplicate_skus['duplicate_count']} conflicts")

        self.logger.info("Checking price coverage...")
        price_coverage = self.check_price_coverage()
        if price_coverage['passed']:
            self.record_success()
        else:
            self.record_failure()
            self.add_error(f"Price coverage: {price_coverage['coverage_percent']:.1f}% < {price_coverage['threshold']}%")

        self.logger.info("Checking category assignment...")
        category_assignment = self.check_category_assignment()
        if category_assignment['passed']:
            self.record_success()
        else:
            self.record_failure()
            self.add_error(f"Category coverage: {category_assignment['coverage_percent']:.1f}% < {category_assignment['threshold']}%")

        self.logger.info("Checking meta field completeness...")
        meta_completeness = self.check_meta_completeness()
        if meta_completeness['passed']:
            self.record_success()
        else:
            self.record_failure()
            self.add_error("Meta completeness: Some required fields <90%")

        # Collect all results
        self.validation_results = {
            'orphan_meta': orphan_meta,
            'duplicate_skus': duplicate_skus,
            'price_coverage': price_coverage,
            'category_assignment': category_assignment,
            'meta_completeness': meta_completeness
        }

        # Generate report
        report = self.generate_report(self.validation_results)

        # Save report
        report_path = Path(__file__).resolve().parent.parent.parent / 'relatorios' / 'orchestrator' / 'data_integrity_validation.md'
        report_path.write_text(report, encoding='utf-8')
        self.logger.info(f"Report saved: {report_path}")

        # Overall pass/fail
        all_passed = all([
            orphan_meta['passed'],
            duplicate_skus['passed'],
            price_coverage['passed'],
            category_assignment['passed'],
            meta_completeness['passed']
        ])

        if all_passed:
            self.logger.info("✅ Data integrity validation PASSED")
            return 0
        else:
            self.logger.info("❌ Data integrity validation FAILED")
            return 1


if __name__ == '__main__':
    agent = DataIntegrityValidatorAgent()
    sys.exit(agent.execute())
