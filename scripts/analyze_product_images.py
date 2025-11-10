#!/usr/bin/env python3
"""
Análise Detalhada de Imagens por Produto
Verifica URLs, faz scraping de fornecedores, e gera relatório completo
"""

import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import re

CATALOG_PATH = Path("output_catalogo/catalogo.json")
REPORT_PATH = Path("relatorios/product_images_analysis.json")
SUMMARY_PATH = Path("relatorios/product_images_summary.md")

def check_url_valid(url, timeout=10):
    """Check if URL is accessible and returns image"""
    if not url or url == 'N/A':
        return False, "URL vazia"

    try:
        # Handle Google Photos links
        if 'googleusercontent' in url or 'photos.google' in url:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    return True, f"Google Photos (200 OK, {content_type})"
                else:
                    return False, f"Google Photos não é imagem ({content_type})"
            else:
                return False, f"Google Photos {response.status_code}"

        # Regular image URLs
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type:
                return True, f"OK ({content_type})"
            else:
                return False, f"Não é imagem ({content_type})"
        else:
            return False, f"HTTP {response.status_code}"

    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.RequestException as e:
        return False, f"Erro: {str(e)[:50]}"

def scrape_hologramme_images(url, timeout=15):
    """Scrape images from hologrammeparis.com product page"""
    if not url or 'hologrammeparis.com' not in url:
        return [], "Não é URL Hologramme"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)

        if response.status_code == 404:
            return [], "404 Not Found"

        if response.status_code != 200:
            return [], f"HTTP {response.status_code}"

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find product images (various selectors for WooCommerce/Flatsome)
        images = []

        # Method 1: WooCommerce gallery
        gallery = soup.select('.woocommerce-product-gallery__image img')
        for img in gallery:
            src = img.get('src') or img.get('data-src') or img.get('data-large_image')
            if src:
                images.append(urljoin(url, src))

        # Method 2: Product images
        if not images:
            product_imgs = soup.select('.product-images img, .product-gallery img')
            for img in product_imgs:
                src = img.get('src') or img.get('data-src')
                if src:
                    images.append(urljoin(url, src))

        # Method 3: Any large images
        if not images:
            all_imgs = soup.select('img[src*="jpg"], img[src*="jpeg"], img[src*="png"]')
            for img in all_imgs:
                src = img.get('src')
                # Filter out logos, icons, etc
                if src and any(x in src.lower() for x in ['product', 'wp-content/uploads']):
                    images.append(urljoin(url, src))

        # Remove duplicates
        images = list(dict.fromkeys(images))

        if images:
            return images, f"Scraped {len(images)} images"
        else:
            return [], "Sem imagens encontradas na página"

    except requests.exceptions.Timeout:
        return [], "Timeout ao scraping"
    except Exception as e:
        return [], f"Erro scraping: {str(e)[:50]}"

def analyze_product_images(product):
    """Analyze all images for a single product"""
    slug = product.get('slug', 'unknown')
    name = product.get('name', 'N/A')
    price = product.get('price')
    supplier_url = product.get('supplier_url', '')

    # Get image URLs and local paths from product
    image_urls = []
    local_images = []

    # From 'downloaded_images' field (list of objects with path/url)
    downloaded = product.get('downloaded_images', [])
    if isinstance(downloaded, list):
        for img in downloaded:
            if isinstance(img, dict):
                # Check if URL exists
                url = img.get('url', '').strip()
                if url and url != 'N/A':
                    image_urls.append(url)

                # Check if local path exists
                path = img.get('path', '').strip()
                if path:
                    local_images.append({
                        'path': path,
                        'position': img.get('position', 0),
                        'origin': img.get('origin', 'unknown')
                    })

    # From 'filtered_images' field
    filtered = product.get('filtered_images', [])
    if isinstance(filtered, list):
        for img in filtered:
            if isinstance(img, dict):
                url = img.get('url', '').strip()
                if url and url != 'N/A':
                    image_urls.append(url)

    # From 'images' field (legacy)
    if isinstance(product.get('images'), list):
        for img in product.get('images', []):
            if isinstance(img, str) and img.strip():
                image_urls.append(img.strip())

    # From 'image' field (single, legacy)
    if product.get('image'):
        if isinstance(product.get('image'), str):
            img = product.get('image').strip()
            if img:
                image_urls.append(img)
        elif isinstance(product.get('image'), list):
            image_urls.extend([i.strip() for i in product.get('image') if i and i.strip()])

    # Remove duplicates, None, empty strings
    image_urls = [url for url in image_urls if url and url != 'N/A']
    image_urls = list(dict.fromkeys(image_urls))

    # Check local images exist
    valid_local = []
    invalid_local = []

    for local_img in local_images:
        img_path = Path(local_img['path'])

        # Try multiple locations for relative paths
        candidates = [
            img_path,  # As-is (if absolute)
            Path('output_catalogo') / img_path,  # Most likely: output_catalogo/images/...
            Path('wordpress') / img_path  # WordPress uploads
        ]

        found = False
        for candidate in candidates:
            if candidate.exists():
                valid_local.append({
                    'path': str(candidate),
                    'original_path': local_img['path'],
                    'position': local_img['position'],
                    'type': 'local',
                    'status': f'Exists ({candidate.parent})'
                })
                found = True
                break

        if not found:
            invalid_local.append({
                'path': local_img['path'],
                'error': 'File not found in any location'
            })

    # Analyze each image URL
    valid_urls = []
    invalid_urls = []

    for url in image_urls:
        is_valid, status = check_url_valid(url)
        if is_valid:
            valid_urls.append({
                'url': url,
                'status': status,
                'type': 'url'
            })
        else:
            invalid_urls.append({
                'url': url,
                'error': status
            })

    # Try scraping supplier URL if no valid images from URLs or local
    scraped_images = []
    scrape_status = None

    if len(valid_urls) == 0 and len(valid_local) == 0 and supplier_url:
        scraped_imgs, scrape_status = scrape_hologramme_images(supplier_url)
        if scraped_imgs:
            # Verify scraped images
            for img_url in scraped_imgs:
                is_valid, status = check_url_valid(img_url)
                if is_valid:
                    scraped_images.append({
                        'url': img_url,
                        'status': f"Scraped - {status}",
                        'type': 'scraped'
                    })

    # Combine all valid images
    all_valid_images = valid_local + valid_urls + scraped_images

    return {
        'slug': slug,
        'name': name,
        'price': price,
        'total_image_urls': len(image_urls),
        'total_local_paths': len(local_images),
        'valid_local': len(valid_local),
        'valid_urls': len(valid_urls),
        'valid_images': len(all_valid_images),
        'invalid_images': len(invalid_urls) + len(invalid_local),
        'scraped_images': len(scraped_images),
        'supplier_url': supplier_url,
        'scrape_status': scrape_status,
        'image_details': {
            'local': valid_local,
            'urls': valid_urls,
            'scraped': scraped_images,
            'invalid_local': invalid_local,
            'invalid_urls': invalid_urls
        },
        'status': 'OK' if all_valid_images else 'SEM_FOTOS'
    }

def main():
    print("\n" + "="*80)
    print("ANÁLISE DETALHADA DE IMAGENS POR PRODUTO")
    print("="*80 + "\n")

    # Load catalog
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    print(f"📊 Total produtos: {len(catalog)}\n")
    print("🔍 Verificando URLs e fazendo scraping...\n")

    results = []

    for i, product in enumerate(catalog, 1):
        slug = product.get('slug', 'unknown')
        print(f"  [{i}/{len(catalog)}] {slug[:40]:<40}", end=" ", flush=True)

        analysis = analyze_product_images(product)
        results.append(analysis)

        status_icon = "✅" if analysis['valid_images'] > 0 else "❌"
        print(f"{status_icon} {analysis['valid_images']} fotos")

        # Rate limiting
        time.sleep(0.5)

    # Save detailed report
    REPORT_PATH.parent.mkdir(exist_ok=True)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Generate summary
    with_photos = [r for r in results if r['valid_images'] > 0]
    without_photos = [r for r in results if r['valid_images'] == 0]

    multi_photo = [r for r in results if r['valid_images'] > 1]
    single_photo = [r for r in results if r['valid_images'] == 1]

    # Generate markdown summary
    summary_md = f"""# ANÁLISE DE FOTOS POR PRODUTO

**Data:** {time.strftime('%Y-%m-%d %H:%M')}
**Catalog:** {CATALOG_PATH}

---

## 📊 RESUMO GERAL

- **Total produtos:** {len(catalog)}
- **Com fotos:** {len(with_photos)} ({len(with_photos)*100//len(catalog)}%)
- **Sem fotos:** {len(without_photos)} ({len(without_photos)*100//len(catalog)}%)

### Distribuição de Fotos

- **Com 1 foto:** {len(single_photo)} produtos
- **Com 2+ fotos:** {len(multi_photo)} produtos
- **Máximo fotos:** {max(r['valid_images'] for r in results)} fotos
- **Média fotos:** {sum(r['valid_images'] for r in results) / len(results):.1f} fotos/produto

---

## ✅ PRODUTOS COM FOTOS ({len(with_photos)} produtos)

"""

    for result in sorted(with_photos, key=lambda x: x['valid_images'], reverse=True):
        summary_md += f"\n### {result['name']}\n"
        summary_md += f"- **SKU:** `{result['slug']}`\n"
        summary_md += f"- **Preço:** €{result['price']}\n"
        summary_md += f"- **Total fotos:** {result['valid_images']}\n"

        if result.get('valid_local', 0) > 0:
            summary_md += f"- **Fotos locais:** {result['valid_local']}\n"

        if result.get('valid_urls', 0) > 0:
            summary_md += f"- **Fotos URLs:** {result['valid_urls']}\n"

        if result['image_details'].get('scraped'):
            summary_md += f"- **Fotos scraped:** {len(result['image_details']['scraped'])} (de {result['supplier_url']})\n"

        summary_md += "\n"

    summary_md += f"\n---\n\n## ❌ PRODUTOS SEM FOTOS ({len(without_photos)} produtos)\n\n"

    for result in without_photos:
        price_str = f"€{result['price']}" if result['price'] else 'N/A'
        summary_md += f"\n### {result['name']}\n"
        summary_md += f"- **SKU:** `{result['slug']}`\n"
        summary_md += f"- **Preço:** {price_str}\n"
        summary_md += f"- **URL Supplier:** {result['supplier_url'] or 'N/A'}\n"

        if result['scrape_status']:
            summary_md += f"- **Scraping:** {result['scrape_status']}\n"

        invalid_count = len(result['image_details'].get('invalid_urls', [])) + len(result['image_details'].get('invalid_local', []))
        if invalid_count > 0:
            summary_md += f"- **Imagens inválidas:** {invalid_count}\n"

        summary_md += f"- **Ação:** {'❌ REMOVER (sem preço)' if not result['price'] else '📸 Cliente fornecer fotos'}\n"
        summary_md += "\n"

    summary_md += f"""
---

## 🎯 RECOMENDAÇÕES

### Produtos para Remover ({len([r for r in without_photos if not r['price']])})
Produtos sem preço E sem fotos devem ser removidos do catálogo.

### Produtos Aguardam Fotos ({len([r for r in without_photos if r['price']])})
Produtos com preço mas sem fotos precisam de fotos do cliente ou remoção.

### Produtos com 1 Foto ({len(single_photo)})
Idealmente todos os produtos devem ter 2-4 fotos (frente, costas, detalhe, lifestyle).

---

**Relatório completo:** `{REPORT_PATH}`
"""

    with open(SUMMARY_PATH, 'w', encoding='utf-8') as f:
        f.write(summary_md)

    print(f"\n✅ Análise completa!")
    print(f"📄 Relatório JSON: {REPORT_PATH}")
    print(f"📄 Relatório MD: {SUMMARY_PATH}")
    print(f"\n📊 Resumo:")
    print(f"   Com fotos: {len(with_photos)}/{len(catalog)} ({len(with_photos)*100//len(catalog)}%)")
    print(f"   Sem fotos: {len(without_photos)}/{len(catalog)} ({len(without_photos)*100//len(catalog)}%)")
    print(f"   Com 2+ fotos: {len(multi_photo)}/{len(catalog)} ({len(multi_photo)*100//len(catalog)}%)")
    print()

    return {
        'total': len(catalog),
        'with_photos': len(with_photos),
        'without_photos': len(without_photos),
        'multi_photo': len(multi_photo)
    }

if __name__ == "__main__":
    result = main()
    print(f"Resultado: {result}")
