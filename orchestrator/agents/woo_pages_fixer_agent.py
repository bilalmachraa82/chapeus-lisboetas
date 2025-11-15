#!/usr/bin/env python3
"""
WOOPAGESFIXER-AGENT - WooCommerce Pages Setup
Phase 3: UX Polish

Ensures WooCommerce core pages are configured:
- Shop page
- Cart page
- Checkout page
- My Account page
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from base_agent import BaseAgent

class WooPagesFixerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="WooPagesFixer-Agent",
            description="Páginas Shop/Cart/Checkout corretas"
        )

    def ensure_woo_page(self, page_name: str, page_slug: str, shortcode: str) -> bool:
        try:
            cursor = self.db.cursor()
            
            # Check if page exists
            cursor.execute("""
                SELECT ID FROM lx_posts
                WHERE post_name = %s
                AND post_type = 'page'
                LIMIT 1
            """, (page_slug,))
            
            result = cursor.fetchone()
            
            if result:
                page_id = result[0]
                self.logger.info(f"Page '{page_name}' exists (ID: {page_id})")
            else:
                # Create page
                from datetime import datetime
                now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute("""
                    INSERT INTO lx_posts (
                        post_author, post_date, post_date_gmt, post_content,
                        post_title, post_status, post_name, post_type,
                        post_modified, post_modified_gmt,
                        to_ping, pinged, post_content_filtered
                    ) VALUES (
                        1, %s, %s, %s, %s, 'publish', %s, 'page',
                        %s, %s, '', '', ''
                    )
                """, (now, now, shortcode, page_name, page_slug, now, now))
                
                page_id = cursor.lastrowid
                self.logger.info(f"Created page '{page_name}' (ID: {page_id})")
            
            self.db.commit()
            cursor.close()
            return True
            
        except Exception as e:
            self.add_error(f"Failed to ensure page '{page_name}': {e}")
            return False

    def run(self) -> int:
        pages = [
            ("Shop", "shop", "[woocommerce_product_page]"),
            ("Cart", "cart", "[woocommerce_cart]"),
            ("Checkout", "checkout", "[woocommerce_checkout]"),
            ("My Account", "my-account", "[woocommerce_my_account]")
        ]
        
        self.metrics.items_total = len(pages)
        
        for page_name, page_slug, shortcode in pages:
            if self.ensure_woo_page(page_name, page_slug, shortcode):
                self.record_success()
            else:
                self.record_failure()
        
        return 0 if self.metrics.success_rate >= 0.75 else 1

if __name__ == '__main__':
    agent = WooPagesFixerAgent()
    sys.exit(agent.execute())
