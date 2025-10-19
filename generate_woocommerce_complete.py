#!/usr/bin/env python3
"""
Gerar CSV WooCommerce a partir do catálogo classificado
"""

import json
import csv
from pathlib import Path
from collections import defaultdict

# Paths
INPUT_FILE = Path("catalog_completo_classificado.json")
OUTPUT_CSV = Path("woocommerce_import_180_produtos.csv")
OUTPUT_CATEGORIES = Path("categorias_estruturadas.json")

# Mapping de categorias PT -> WooCommerce
CATEGORY_MAPPING = {
    "boina": "Chapéus > Boinas",
    "chapeu-fedora": "Chapéus > Fedora",
    "chapeu-panama": "Chapéus > Panama",
    "bone": "Bonés",
    "bucket-hat": "Chapéus > Bucket Hat",
    "capeline": "Chapéus > Capeline",
    "gorro": "Chapéus > Gorros",
    "cartola": "Chapéus > Cartola",
    "trilby": "Chapéus > Trilby",
    "outros": "Acessórios"
}

GENDER_CATEGORY = {
    "homem": "Homem",
    "mulher": "Mulher",
    "crianca": "Criança",
    "unisex": "Unisex"
}


def generate_sku(tipo: str, index: int) -> str:
    """Gerar SKU único"""
    tipo_code = tipo.upper().replace("-", "")[:6]
    return f"CL-{tipo_code}-{index:04d}"


def clean_text(text: str) -> str:
    """Limpar texto para CSV"""
    if not text:
        return ""
    return text.replace('"', '""').strip()


def format_categories(genero: str, tipo: str) -> str:
    """Formatar hierarquia de categorias"""
    cats = []
    
    # Género
    if genero in GENDER_CATEGORY:
        cats.append(GENDER_CATEGORY[genero])
    
    # Tipo
    if tipo in CATEGORY_MAPPING:
        cat = CATEGORY_MAPPING[tipo]
        # Se género for unisex, não duplicar categoria
        if genero != "unisex":
            cat = f"{GENDER_CATEGORY.get(genero, 'Unisex')} > {cat}"
        cats.append(cat)
    
    return ", ".join(cats) if cats else "Chapéus"


def main():
    print("=" * 70)
    print("📦 Gerador CSV WooCommerce")
    print("=" * 70)
    print()
    
    # Load classified data
    print(f"📂 Loading: {INPUT_FILE}")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data.get('products', [])
    print(f"✅ Loaded {len(products)} products")
    print()
    
    # WooCommerce CSV Headers
    csv_headers = [
        'ID',
        'Type',
        'SKU',
        'Name',
        'Published',
        'Is featured?',
        'Visibility in catalog',
        'Short description',
        'Description',
        'Date sale price starts',
        'Date sale price ends',
        'Tax status',
        'Tax class',
        'In stock?',
        'Stock',
        'Low stock amount',
        'Backorders allowed?',
        'Sold individually?',
        'Weight (kg)',
        'Length (cm)',
        'Width (cm)',
        'Height (cm)',
        'Allow customer reviews?',
        'Purchase note',
        'Sale price',
        'Regular price',
        'Categories',
        'Tags',
        'Shipping class',
        'Images',
        'Download limit',
        'Download expiry days',
        'Parent',
        'Grouped products',
        'Upsells',
        'Cross-sells',
        'External URL',
        'Button text',
        'Position',
        'Attribute 1 name',
        'Attribute 1 value(s)',
        'Attribute 1 visible',
        'Attribute 1 global',
        'Attribute 2 name',
        'Attribute 2 value(s)',
        'Attribute 2 visible',
        'Attribute 2 global',
        'Meta: _wpcom_is_markdown'
    ]
    
    # Generate CSV rows
    csv_rows = []
    stats = defaultdict(int)
    
    print("🔄 Generating WooCommerce products...")
    print()
    
    for idx, product in enumerate(products, 1):
        classification = product.get('classification', {})
        
        # Basic info
        tipo = classification.get('tipo', 'outros')
        genero = classification.get('genero', 'unisex')
        nome = classification.get('nome_produto', f'Produto {idx}')
        desc_curta = classification.get('descricao_curta', '')
        desc_longa = classification.get('descricao_longa', '')
        preco = classification.get('preco_sugerido_eur', 45)
        stock = classification.get('stock_sugerido', 10)
        tags = classification.get('tags', [])
        
        # Generate SKU
        sku = generate_sku(tipo, idx)
        
        # Categories
        categories = format_categories(genero, tipo)
        
        # Tags
        tags_str = ", ".join([str(t) for t in tags]) if tags else ""
        
        # Image path (relative to WordPress uploads)
        img_path = product.get('file_path', '')
        
        # Material and Season as attributes
        material = classification.get('material_aparente', '')
        temporada = classification.get('temporada', '')
        
        # Build row
        row = {
            'ID': '',
            'Type': 'simple',
            'SKU': sku,
            'Name': clean_text(nome),
            'Published': '1',
            'Is featured?': '0',
            'Visibility in catalog': 'visible',
            'Short description': clean_text(desc_curta),
            'Description': clean_text(desc_longa),
            'Date sale price starts': '',
            'Date sale price ends': '',
            'Tax status': 'taxable',
            'Tax class': '',
            'In stock?': '1',
            'Stock': str(stock),
            'Low stock amount': '2',
            'Backorders allowed?': '0',
            'Sold individually?': '0',
            'Weight (kg)': '0.2',
            'Length (cm)': '',
            'Width (cm)': '',
            'Height (cm)': '',
            'Allow customer reviews?': '1',
            'Purchase note': '',
            'Sale price': '',
            'Regular price': str(preco),
            'Categories': categories,
            'Tags': tags_str,
            'Shipping class': '',
            'Images': img_path,
            'Download limit': '',
            'Download expiry days': '',
            'Parent': '',
            'Grouped products': '',
            'Upsells': '',
            'Cross-sells': '',
            'External URL': '',
            'Button text': '',
            'Position': '0',
            'Attribute 1 name': 'Material',
            'Attribute 1 value(s)': material.capitalize() if material else '',
            'Attribute 1 visible': '1',
            'Attribute 1 global': '0',
            'Attribute 2 name': 'Temporada',
            'Attribute 2 value(s)': temporada.capitalize() if temporada else '',
            'Attribute 2 visible': '1',
            'Attribute 2 global': '0',
            'Meta: _wpcom_is_markdown': '0'
        }
        
        csv_rows.append(row)
        
        # Stats
        stats[genero] += 1
        stats[tipo] += 1
        
        # Progress
        if idx % 20 == 0:
            print(f"   ✅ Processed {idx}/{len(products)} products...")
    
    # Write CSV
    print()
    print(f"💾 Writing CSV: {OUTPUT_CSV}")
    
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()
        writer.writerows(csv_rows)
    
    print(f"✅ CSV generated: {len(csv_rows)} products")
    print()
    
    # Generate category structure
    categories_structure = {
        "hierarchy": {
            "Chapéus": {
                "Homem": ["Boinas", "Fedora", "Panama", "Bucket Hat"],
                "Mulher": ["Capeline", "Cloche", "Boinas", "Fedora"],
                "Unisex": ["Boinas", "Fedora", "Panama", "Bucket Hat", "Gorros"]
            },
            "Bonés": ["Homem", "Mulher", "Unisex"],
            "Acessórios": []
        },
        "stats": dict(stats)
    }
    
    with open(OUTPUT_CATEGORIES, 'w', encoding='utf-8') as f:
        json.dump(categories_structure, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Categories structure saved: {OUTPUT_CATEGORIES}")
    print()
    
    # Summary
    print("=" * 70)
    print("✅ CSV GERADO COM SUCESSO!")
    print("=" * 70)
    print()
    print(f"📊 Summary:")
    print(f"   • Total products: {len(csv_rows)}")
    print(f"   • CSV file: {OUTPUT_CSV} ({OUTPUT_CSV.stat().st_size / 1024:.1f} KB)")
    print()
    
    print("📈 By Gender:")
    for gender in ['homem', 'mulher', 'unisex', 'crianca']:
        if gender in stats:
            print(f"   • {GENDER_CATEGORY.get(gender, gender)}: {stats[gender]}")
    
    print()
    print("📈 Top Product Types:")
    type_stats = {k: v for k, v in stats.items() if k in CATEGORY_MAPPING}
    for tipo, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   • {CATEGORY_MAPPING.get(tipo, tipo)}: {count}")
    
    print()
    print("🎯 Next Steps:")
    print()
    print("1. Upload Images to WordPress:")
    print("   - WordPress Admin → Media → Add New")
    print("   - Upload all images from: processed_images/professional/")
    print()
    print("2. Import Products:")
    print("   - WooCommerce → Products → Import")
    print(f"   - Select file: {OUTPUT_CSV}")
    print("   - Map columns automatically")
    print("   - Run import")
    print()
    print("3. Review & Publish:")
    print("   - Check product pages")
    print("   - Adjust prices if needed")
    print("   - Set featured products")
    print("   - GO LIVE! 🚀")
    print()


if __name__ == "__main__":
    main()
