#!/usr/bin/env python3
"""
PRICEGATE-AGENT - Price Enforcement  
Phase 1: Data Foundation

Enforces NO PRICE = NO PUBLISH rule
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from base_agent import BaseAgent

class PriceGateAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="PriceGate-Agent",
            description="Bloqueia produtos sem preço (NO PRICE = NO PUBLISH)"
        )

    def run(self) -> int:
        cursor = self.db.cursor()
        
        # Find published products without valid price
        cursor.execute("""
            SELECT p.ID, p.post_title, pm.meta_value as price
            FROM lx_posts p
            LEFT JOIN lx_postmeta pm ON p.ID = pm.post_id AND pm.meta_key = '_price'
            WHERE p.post_type = 'product'
            AND p.post_status = 'publish'
        """)
        
        products = cursor.fetchall()
        self.metrics.items_total = len(products)
        
        for product_id, title, price in products:
            try:
                price_val = float(price.replace('€', '').replace(',', '.')) if price else 0
            except:
                price_val = 0
            
            if price_val <= 0:
                # Set to draft
                cursor.execute("""
                    UPDATE lx_posts
                    SET post_status = 'draft'
                    WHERE ID = %s
                """, (product_id,))
                self.logger.info(f"Blocked: {title} (no price)")
                self.record_success()
            else:
                self.record_skip()
        
        self.db.commit()
        cursor.close()
        return 0

if __name__ == '__main__':
    agent = PriceGateAgent()
    sys.exit(agent.execute())
