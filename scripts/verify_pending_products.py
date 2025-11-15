#!/usr/bin/env python3
"""
Verify Pending Products - Check supplier URLs and attempt image retrieval
For the 13 products without images identified in PRODUTOS_PENDING_FOTOS.md
"""

import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
from urllib.parse import urljoin

# List of 13 pending products (from PRODUTOS_PENDING_FOTOS.md)
PENDING_PRODUCTS = [
    "bone-22174",
    "casquette-18534n",
    "chapeu-australiano",
    "chapeu-colonial-pith-helmet",
    "palha-12403",
    "bone-2018016",
    "chapeu-cloche",
    "casquete",
    "chapeu-cerimonia-perolas",
    "chapeu-cerimonia-flores",
    "solid",
    "bucket-hat-reversivel",
    "chapeu-cowboy"
]

def load_catalog():
    """Load the catalog.json file"""
    catalog_path = Path("output_catalogo/catalogo.json")
    with open(catalog_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_url(url, timeout=10):
    """Check if URL is accessible and return status"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return {
            'accessible': response.status_code == 200,
            'status_code': response.status_code,
            'final_url': response.url
        }
    except requests.RequestException as e:
        return {
            'accessible': False,
            'status_code': None,
            'error': str(e)
        }

def scrape_images_from_url(url, timeout=15):
    """Attempt to scrape images from product URL"""
    try:
        response = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.content, 'html.parser')

        # Common image selectors for e-commerce sites
        image_selectors = [
            'div.product-images img',
            'div.woocommerce-product-gallery img',
            'img.wp-post-image',
            'div.product-image img',
            'img[itemprop="image"]',
            'div.images img',
            'figure.woocommerce-product-gallery__wrapper img'
        ]

        images = []
        for selector in image_selectors:
            imgs = soup.select(selector)
            for img in imgs:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and not src.startswith('data:'):
                    # Make absolute URL
                    absolute_url = urljoin(url, src)
                    # Filter out thumbnails and small images
                    if not any(x in absolute_url.lower() for x in ['thumbnail', 'thumb', 'icon', 'logo', '100x100', '150x150']):
                        images.append(absolute_url)

        # Remove duplicates while preserving order
        seen = set()
        unique_images = []
        for img in images:
            if img not in seen:
                seen.add(img)
                unique_images.append(img)

        return unique_images[:6]  # Return max 6 images

    except Exception as e:
        return []

def verify_pending_products():
    """Main function to verify all pending products"""
    catalog = load_catalog()

    results = {
        'verified': [],
        'not_found': [],
        'images_found': [],
        'summary': {}
    }

    print("\n" + "="*80)
    print("VERIFICAÇÃO DE 13 PRODUTOS SEM FOTOS")
    print("="*80 + "\n")

    for slug in PENDING_PRODUCTS:
        # Find product in catalog
        product = next((p for p in catalog if p.get('slug') == slug), None)

        if not product:
            print(f"❌ {slug}: NOT FOUND IN CATALOG")
            results['not_found'].append({
                'slug': slug,
                'reason': 'Not in catalog.json'
            })
            continue

        print(f"\n{'='*80}")
        print(f"📦 PRODUTO: {product.get('name', 'N/A')}")
        print(f"   SKU: {slug}")
        print(f"   Preço: €{product.get('price', 'N/A')}")
        print(f"   Categoria: {product.get('sheet', 'N/A')}")

        # Check supplier URL
        supplier_url = product.get('supplier_url')

        if not supplier_url or supplier_url == "N/A":
            print(f"   ⚠️  Sem URL do fornecedor")
            results['not_found'].append({
                'slug': slug,
                'name': product.get('name'),
                'price': product.get('price'),
                'category': product.get('sheet'),
                'reason': 'No supplier URL'
            })
            continue

        print(f"   🔗 URL Fornecedor: {supplier_url}")

        # Check URL accessibility
        print(f"   🔍 Verificando URL...", end=" ")
        url_check = check_url(supplier_url)

        if url_check['accessible']:
            print(f"✅ OK (200)")

            # Try to scrape images
            print(f"   📸 Buscando imagens...", end=" ")
            images = scrape_images_from_url(supplier_url)

            if images:
                print(f"✅ {len(images)} imagens encontradas!")
                for i, img_url in enumerate(images, 1):
                    print(f"      {i}. {img_url}")

                results['images_found'].append({
                    'slug': slug,
                    'name': product.get('name'),
                    'price': product.get('price'),
                    'category': product.get('sheet'),
                    'supplier_url': supplier_url,
                    'images': images,
                    'image_count': len(images)
                })
            else:
                print(f"❌ Nenhuma imagem encontrada")
                results['verified'].append({
                    'slug': slug,
                    'name': product.get('name'),
                    'price': product.get('price'),
                    'category': product.get('sheet'),
                    'supplier_url': supplier_url,
                    'status': 'URL OK but no images'
                })
        else:
            status = url_check.get('status_code', 'ERROR')
            print(f"❌ {status}")
            results['not_found'].append({
                'slug': slug,
                'name': product.get('name'),
                'price': product.get('price'),
                'category': product.get('sheet'),
                'supplier_url': supplier_url,
                'reason': f"URL returned {status}",
                'status_code': status
            })

        # Check extra URLs
        extra_urls = product.get('extra_urls', [])
        if extra_urls:
            print(f"   📎 {len(extra_urls)} URLs extra encontradas")
            for extra_url in extra_urls:
                print(f"      🔗 {extra_url}")
                url_check = check_url(extra_url)
                if url_check['accessible']:
                    print(f"         ✅ Acessível")
                    # Could scrape these too
                else:
                    print(f"         ❌ {url_check.get('status_code', 'ERROR')}")

        time.sleep(1)  # Polite scraping delay

    # Generate summary
    print(f"\n{'='*80}")
    print("📊 RESUMO FINAL")
    print(f"{'='*80}\n")

    results['summary'] = {
        'total_verified': len(PENDING_PRODUCTS),
        'images_found': len(results['images_found']),
        'no_images': len(results['not_found']) + len(results['verified']),
        'not_in_catalog': sum(1 for x in results['not_found'] if x.get('reason') == 'Not in catalog.json'),
        'url_404': sum(1 for x in results['not_found'] if '404' in str(x.get('status_code', ''))),
        'no_supplier_url': sum(1 for x in results['not_found'] if x.get('reason') == 'No supplier URL')
    }

    print(f"Total produtos verificados:     {results['summary']['total_verified']}")
    print(f"✅ Imagens encontradas:          {results['summary']['images_found']}")
    print(f"❌ Sem imagens disponíveis:      {results['summary']['no_images']}")
    print(f"   - Não no catálogo:            {results['summary']['not_in_catalog']}")
    print(f"   - URL 404:                    {results['summary']['url_404']}")
    print(f"   - Sem URL fornecedor:         {results['summary']['no_supplier_url']}")

    # Save results
    output_path = Path("relatorios/pending_products_verification.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Resultados salvos em: {output_path}")

    # Generate recommendation report
    print(f"\n{'='*80}")
    print("💡 RECOMENDAÇÕES")
    print(f"{'='*80}\n")

    if results['images_found']:
        print(f"✅ {len(results['images_found'])} produtos COM imagens disponíveis:")
        print("   → AÇÃO: Download automático possível")
        for product in results['images_found']:
            print(f"   - {product['slug']}: {product['image_count']} imagens")

    if results['not_found'] or results['verified']:
        no_image_count = len(results['not_found']) + len(results['verified'])
        print(f"\n❌ {no_image_count} produtos SEM imagens disponíveis:")
        print("   → DECISÃO: NÃO PUBLICAR")
        print("   → AÇÃO: Atualizar Google Sheets com status")

        for product in results['not_found'] + results['verified']:
            print(f"   - {product['slug']}: {product.get('reason', 'No images found')}")

    return results

if __name__ == "__main__":
    results = verify_pending_products()

    # Generate client update for Google Sheets
    print(f"\n{'='*80}")
    print("📝 ATUALIZAÇÃO GOOGLE SHEETS")
    print(f"{'='*80}\n")

    print("Adicionar coluna 'Status Publicação' com:")
    for product in results['not_found'] + results['verified']:
        print(f"  {product['slug']}: NÃO PUBLICAR - {product.get('reason', 'Sem imagens')}")

    if results['images_found']:
        print("\nAdicionar coluna 'Imagens Disponíveis' com:")
        for product in results['images_found']:
            print(f"  {product['slug']}: {product['image_count']} imagens encontradas")
