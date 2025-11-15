#!/usr/bin/env python3
"""
DESCRIPTIONBUILDER-AGENT - Template-Based Descriptions
Phase 2: Product Enrichment

Generates professional product descriptions using templates
Zero AI cost - pure template-based approach
- Short descriptions (2-3 lines)
- Long descriptions (detailed specs)
- SEO-optimized keywords
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from base_agent import BaseAgent
from typing import Dict, Optional

class DescriptionBuilderAgent(BaseAgent):
    """Generate product descriptions from templates"""

    def __init__(self):
        super().__init__(
            name="DescriptionBuilder-Agent",
            description="Descrições baseadas em templates (zero custo AI)"
        )
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict:
        """Load description templates by category"""
        return {
            'boinas': {
                'short': 'Boina {material} de alta qualidade. {estilo}. Disponível em várias cores.',
                'long': '''Boina clássica portuguesa em {material} premium.

Características:
- Material: {material}
- Estilo: {estilo}
- Composição: {composicao}
- Tamanhos: {tamanhos}
- Origem: {origem}

{descricao_extra}

Perfeita para todas as estações. Combina tradição e elegância.'''
            },
            'panama': {
                'short': 'Chapéu Panamá {material}. Elegante e versátil. {caracteristica}.',
                'long': '''Chapéu Panamá autêntico em {material} natural.

Características:
- Material: {material}
- Aba: {aba_size}
- Composição: {composicao}
- Proteção UV: {protecao_uv}
- Estilo: {estilo}

{descricao_extra}

Ideal para verão. Elegância atemporal.'''
            },
            'feminino': {
                'short': 'Chapéu feminino {material}. {estilo}. Elegante e moderno.',
                'long': '''Chapéu feminino sofisticado em {material}.

Características:
- Material: {material}
- Design: {estilo}
- Composição: {composicao}
- Ocasiões: {ocasioes}

{descricao_extra}

Perfeito para completar qualquer look com elegância.'''
            },
            'default': {
                'short': 'Chapéu {tipo} em {material}. Qualidade premium.',
                'long': '''Chapéu {tipo} de qualidade superior.

Características:
- Material: {material}
- Composição: {composicao}
- Estilo: {estilo}

{descricao_extra}

Produto de alta qualidade, fabricado com atenção ao detalhe.'''
            }
        }

    def detect_category(self, product: Dict) -> str:
        """Detect product category for template selection"""
        category = product.get('category', '').lower()
        title = product.get('title', '').lower()

        if 'boina' in title or 'boina' in category:
            return 'boinas'
        elif 'panama' in title or 'panamá' in category:
            return 'panama'
        elif 'feminino' in category or 'mulher' in title:
            return 'feminino'
        else:
            return 'default'

    def extract_product_attributes(self, product: Dict) -> Dict[str, str]:
        """Extract attributes from product data"""
        # Extract material from composition or title
        composition = product.get('composition', '')
        material = 'lã' if 'lã' in composition.lower() else \
                   'algodão' if 'algodão' in composition.lower() else \
                   'palha' if 'palha' in composition.lower() else \
                   'tecido'

        # Detect style
        title = product.get('title', '').lower()
        estilo = 'clássico' if 'classic' in title else \
                 'moderno' if 'modern' in title else \
                 'tradicional'

        return {
            'material': material,
            'composicao': composition if composition else f'100% {material}',
            'estilo': estilo,
            'tamanhos': 'Único (ajustável)',
            'origem': 'Portugal/Europa',
            'aba_size': 'Média',
            'protecao_uv': 'Alta',
            'ocasioes': 'Casual, Formal, Eventos',
            'caracteristica': 'Leve e respirável',
            'descricao_extra': 'Fabricado com materiais de primeira qualidade.',
            'tipo': product.get('type', 'Chapéu')
        }

    def generate_descriptions(self, product: Dict) -> tuple[str, str]:
        """Generate short and long descriptions"""
        category = self.detect_category(product)
        template = self.templates.get(category, self.templates['default'])
        attributes = self.extract_product_attributes(product)

        try:
            short_desc = template['short'].format(**attributes)
            long_desc = template['long'].format(**attributes)
            return short_desc, long_desc
        except KeyError as e:
            self.add_warning(f"Missing attribute for template: {e}")
            # Fallback to simple description
            return (
                f"Chapéu de qualidade premium.",
                f"Produto de alta qualidade. {product.get('title', '')}"
            )

    def update_product_descriptions(self, product_id: int, short_desc: str, long_desc: str) -> bool:
        """Update product descriptions in WordPress"""
        try:
            cursor = self.db.cursor()

            # Update post content and excerpt
            cursor.execute("""
                UPDATE lx_posts
                SET post_content = %s,
                    post_excerpt = %s
                WHERE ID = %s
            """, (long_desc, short_desc, product_id))

            self.db.commit()
            cursor.close()
            return True

        except Exception as e:
            self.add_error(f"Failed to update descriptions for product {product_id}: {e}")
            return False

    def run(self) -> int:
        """Main execution"""
        cursor = self.db.cursor()

        # Get all products needing descriptions
        cursor.execute("""
            SELECT p.ID, p.post_title, p.post_content, p.post_excerpt,
                   pm_comp.meta_value as composition,
                   pm_sku.meta_value as sku
            FROM lx_posts p
            LEFT JOIN lx_postmeta pm_comp ON p.ID = pm_comp.post_id AND pm_comp.meta_key = '_composition'
            LEFT JOIN lx_postmeta pm_sku ON p.ID = pm_sku.post_id AND pm_sku.meta_key = '_sku'
            WHERE p.post_type = 'product'
            AND p.post_status IN ('publish', 'draft')
        """)

        products = cursor.fetchall()
        cursor.close()

        self.metrics.items_total = len(products)
        self.logger.info(f"Processing {len(products)} products")

        for product_data in products:
            product_id, title, content, excerpt, composition, sku = product_data

            # Skip if already has good descriptions
            if content and len(content) > 100 and excerpt and len(excerpt) > 20:
                self.record_skip()
                continue

            # Prepare product dict
            product = {
                'title': title,
                'composition': composition or '',
                'sku': sku or '',
                'category': '',  # TODO: Get from term relationships
                'type': 'Chapéu'
            }

            # Generate descriptions
            short_desc, long_desc = self.generate_descriptions(product)

            # Update in database
            if self.update_product_descriptions(product_id, short_desc, long_desc):
                self.record_success()
                self.log_progress(
                    f"Updated {sku or product_id}: {title[:30]}",
                    self.metrics.completion_rate * 100
                )
            else:
                self.record_failure()

        # Success if 80%+ products updated
        return 0 if self.metrics.success_rate >= 0.8 else 1


if __name__ == '__main__':
    agent = DescriptionBuilderAgent()
    sys.exit(agent.execute())
