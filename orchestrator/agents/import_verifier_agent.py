#!/usr/bin/env python3
"""
IMPORTVERIFIER-AGENT - Post-Import Verification
Phase 6: Client Handoff
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from base_agent import BaseAgent

class ImportVerifierAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ImportVerifier-Agent",
            description="Validação pós-import completa"
        )

    def run(self) -> int:
        cursor = self.db.cursor()
        
        # Verify products
        cursor.execute("SELECT COUNT(*) FROM lx_posts WHERE post_type = 'product'")
        total_products = cursor.fetchone()[0]
        
        # Verify with featured images
        cursor.execute("""
            SELECT COUNT(DISTINCT post_id) FROM lx_postmeta
            WHERE meta_key = '_thumbnail_id'
        """)
        products_with_images = cursor.fetchone()[0]
        
        # Verify with prices
        cursor.execute("""
            SELECT COUNT(DISTINCT post_id) FROM lx_postmeta
            WHERE meta_key = '_price' AND CAST(meta_value AS DECIMAL) > 0
        """)
        products_with_prices = cursor.fetchone()[0]
        
        self.logger.info(f"Products: {total_products}")
        self.logger.info(f"With images: {products_with_images}")
        self.logger.info(f"With prices: {products_with_prices}")
        
        self.metrics.items_total = total_products
        self.metrics.items_succeeded = min(products_with_images, products_with_prices)
        self.metrics.items_processed = total_products
        
        cursor.close()
        return 0 if self.metrics.success_rate >= 0.7 else 1

if __name__ == '__main__':
    agent = ImportVerifierAgent()
    sys.exit(agent.execute())
