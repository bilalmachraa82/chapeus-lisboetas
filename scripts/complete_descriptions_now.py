#!/usr/bin/env python3
"""
Complete Missing Product Descriptions - IMMEDIATE EXECUTION
Generate professional short descriptions for 61 products without descriptions
"""

import json
import re
from pathlib import Path

CATALOG_PATH = Path("output_catalogo/catalogo.json")

# Templates baseados em análise das descrições existentes
TEMPLATES = {
    'boina': {
        'patterns': [
            "Boina {style} em {material}. {feature}",
            "Boina {style} {material}, {feature}. Fabricada em {origin}",
            "{material} premium. {feature}. Tamanho {size}"
        ],
        'features': [
            "Qualidade premium",
            "Conforto garantido",
            "Estilo clássico português",
            "Design tradicional",
            "Acabamento de excelência"
        ]
    },
    'chapeu': {
        'patterns': [
            "Chapéu {style} em {material}. {feature}",
            "Chapéu {style} {material}, {feature}",
            "{material} de qualidade. {feature}"
        ],
        'features': [
            "Elegância atemporal",
            "Proteção solar garantida",
            "Conforto todo o dia",
            "Estilo sofisticado",
            "Qualidade superior"
        ]
    },
    'bone': {
        'patterns': [
            "Boné {style} em {material}. {feature}",
            "Boné {style}, {material}. {feature}"
        ],
        'features': [
            "Conforto e estilo",
            "Design moderno",
            "Versatilidade garantida",
            "Qualidade premium"
        ]
    },
    'panama': {
        'patterns': [
            "Chapéu Panamá {material}. {feature}",
            "Panamá clássico em {material}, {feature}"
        ],
        'features': [
            "Elegância tropical",
            "Estilo verão",
            "Frescura garantida",
            "Clássico intemporal"
        ]
    }
}

def detect_product_type(product):
    """Detect product type from name/slug"""
    name = product.get('name') or ''
    slug = product.get('slug') or ''
    name_lower = str(name).lower()
    slug_lower = str(slug).lower()

    if 'boina' in name_lower or 'casquette' in slug_lower:
        return 'boina'
    elif 'panamá' in name_lower or 'panama' in slug_lower:
        return 'panama'
    elif 'boné' in name_lower or 'bone' in slug_lower:
        return 'bone'
    elif 'chapéu' in name_lower or 'chapeau' in slug_lower:
        return 'chapeu'
    else:
        return 'chapeu'  # default

def extract_material(product):
    """Extract material from specs or tags"""
    specs = product.get('specs', {})
    tags = product.get('tags', [])

    # From composition
    comp = specs.get('COMPOSIÇÃO', '')
    if '100% Lã' in comp or 'lã pura' in comp.lower():
        return "100% lã pura"
    elif 'lã' in comp.lower():
        return "lã"
    elif '100% Poliéster' in comp:
        return "poliéster"
    elif 'algodão' in comp.lower():
        return "algodão"
    elif 'pele' in comp.lower() or any('pele' in t.lower() for t in tags):
        return "pele genuína"
    elif 'palha' in product.get('name', '').lower():
        return "palha natural"
    elif 'cortiça' in product.get('sheet', '').lower():
        return "cortiça premium"

    return "materiais de qualidade"

def extract_origin(product):
    """Extract origin from tags"""
    tags = product.get('tags', [])
    for tag in tags:
        if 'Fabricado na Itália' in tag or 'Itália' in tag:
            return "Itália"
        elif 'Fabricado em Portugal' in tag or 'Portugal' in tag:
            return "Portugal"
        elif 'Fabricado na China' in tag:
            return "China"
        elif 'Fabricado na França' in tag:
            return "França"
    return None

def extract_style(product):
    """Extract style from name"""
    name = product.get('name') or ''
    name = str(name)

    # Common styles
    if 'Oitavada' in name:
        return "oitavada"
    elif 'Sextavada' in name:
        return "sextavada"
    elif 'Clássica' in name or 'Classica' in name:
        return "clássica"
    elif 'Bico de Pato' in name:
        return "bico de pato"
    elif 'Cowboy' in name:
        return "cowboy"
    elif 'Australiano' in name:
        return "australiano"
    elif 'Colonial' in name:
        return "colonial"

    return ""

def extract_size(product):
    """Extract size info from specs"""
    specs = product.get('specs', {})
    size = specs.get('TAMANHO', '')

    # Convert to string if needed
    size = str(size) if size else ''

    if 'ajustável' in size.lower():
        return "ajustável"
    elif size and ',' in size:
        sizes = size.split(',')
        if len(sizes) > 3:
            return f"vários tamanhos ({sizes[0].strip()} a {sizes[-1].strip()})"

    return None

def generate_description(product):
    """Generate professional short description"""
    product_type = detect_product_type(product)
    material = extract_material(product)
    origin = extract_origin(product)
    style = extract_style(product)
    size = extract_size(product)

    template_data = TEMPLATES.get(product_type, TEMPLATES['chapeu'])

    # Build description from template
    import random
    pattern = random.choice(template_data['patterns'])
    feature = random.choice(template_data['features'])

    # Replace placeholders
    desc = pattern
    desc = desc.replace('{material}', material)
    desc = desc.replace('{feature}', feature)

    if '{style}' in desc:
        if style:
            desc = desc.replace('{style}', style)
        else:
            desc = desc.replace(' {style}', '')

    if '{origin}' in desc:
        if origin:
            desc = desc.replace('{origin}', origin)
        else:
            # Remove the origin clause
            desc = re.sub(r'[.,]\s*Fabricada? em \{origin\}', '', desc)

    if '{size}' in desc:
        if size:
            desc = desc.replace('{size}', size)
        else:
            desc = re.sub(r'[.,]?\s*Tamanho \{size\}', '', desc)

    # Clean up any remaining placeholders
    desc = re.sub(r'\{[^}]+\}', '', desc)

    # Clean up extra spaces and punctuation
    desc = re.sub(r'\s+', ' ', desc).strip()
    desc = re.sub(r'\s+([.,])', r'\1', desc)

    # Ensure ends with period
    if desc and desc[-1] not in '.!?':
        desc += '.'

    return desc

def main():
    print("\n" + "="*80)
    print("COMPLETAR DESCRIÇÕES - EXECUÇÃO IMEDIATA")
    print("="*80 + "\n")

    # Load catalog
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    print(f"📊 Total produtos: {len(catalog)}")

    # Find products without description
    without_desc = []
    with_desc = []

    for product in catalog:
        desc = product.get('info_short') or ''
        desc = str(desc).strip()
        if desc and len(desc) > 20:
            with_desc.append(product)
        else:
            without_desc.append(product)

    print(f"✅ Com descrição: {len(with_desc)} ({len(with_desc)*100//len(catalog)}%)")
    print(f"❌ Sem descrição: {len(without_desc)} ({len(without_desc)*100//len(catalog)}%)")

    if not without_desc:
        print("\n✅ Todas as descrições já estão completas!")
        return

    print(f"\n🔧 Gerando descrições para {len(without_desc)} produtos...")

    # Generate descriptions
    generated_count = 0
    for i, product in enumerate(without_desc, 1):
        slug = product.get('slug', 'unknown')
        name = product.get('name', 'Unknown')

        # Generate
        desc = generate_description(product)

        # Update product
        product['info_short'] = desc

        print(f"  [{i}/{len(without_desc)}] {slug:<30} → \"{desc[:60]}...\"")
        generated_count += 1

    # Save updated catalog
    backup_path = CATALOG_PATH.parent / f"catalogo_before_descriptions_{Path(__file__).stem}.json"
    import shutil
    shutil.copy(CATALOG_PATH, backup_path)

    with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Descrições geradas: {generated_count}")
    print(f"💾 Backup: {backup_path}")
    print(f"💾 Catalog atualizado: {CATALOG_PATH}")

    # Verify
    print(f"\n🔍 Verificação final:")
    complete_now = sum(1 for p in catalog if p.get('info_short') and len(p.get('info_short', '')) > 20)
    print(f"   Descrições completas: {complete_now}/{len(catalog)} ({complete_now*100//len(catalog)}%)")

    print("\n✅ COMPLETO!\n")

    return {
        'before': len(with_desc),
        'generated': generated_count,
        'after': complete_now
    }

if __name__ == "__main__":
    result = main()
    print(f"Resultado: {result}")
