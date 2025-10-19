#!/usr/bin/env python3
"""
Instagram Photo Downloader - One by One
Tenta baixar cada foto individual usando várias técnicas
"""

import os
import json
import time
import requests
from pathlib import Path
from tqdm import tqdm
import re

# Configuration
USERNAME = "chapeuslisboetas"
OUTPUT_DIR = Path("instagram_catalog/raw_photos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Lista de shortcodes conhecidos (dos 12 já baixados + API)
KNOWN_POSTS = []

# Headers variados para evitar detecção
HEADERS_VARIANTS = [
    {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    },
    {
        "User-Agent": "Instagram 150.0.0.0 Android (25/7.1.1; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US)",
        "Accept": "*/*",
    }
]


def get_post_info_from_web(shortcode: str) -> dict:
    """
    Tenta obter info do post via web scraping suave
    """
    url = f"https://www.instagram.com/p/{shortcode}/"
    
    for headers in HEADERS_VARIANTS:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Procurar URLs de imagem no HTML
                content = response.text
                
                # Padrão: "display_url":"https://..."
                pattern = r'"display_url":"(https://[^"]+)"'
                matches = re.findall(pattern, content)
                
                if matches:
                    # Pegar a maior resolução (geralmente a primeira)
                    img_url = matches[0].replace(r'\u0026', '&')
                    return {"url": img_url, "shortcode": shortcode}
            
            time.sleep(1)
        
        except Exception as e:
            print(f"   ⚠️  Error with headers variant: {e}")
            continue
    
    return None


def download_image_from_url(url: str, filename: str) -> bool:
    """
    Download imagem de URL
    """
    try:
        response = requests.get(url, timeout=30, stream=True)
        
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    
    except Exception as e:
        print(f"   ❌ Download error: {e}")
    
    return False


def get_shortcodes_from_profile_page() -> list:
    """
    Extrair shortcodes da página do perfil (grid)
    """
    print("🔍 Extraindo shortcodes da página do perfil...")
    
    url = f"https://www.instagram.com/{USERNAME}/"
    shortcodes = []
    
    for headers in HEADERS_VARIANTS:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                content = response.text
                
                # Padrão: "/p/SHORTCODE/"
                pattern = r'"/p/([A-Za-z0-9_-]+)/"'
                matches = re.findall(pattern, content)
                
                # Remover duplicados
                shortcodes = list(set(matches))
                
                if len(shortcodes) > 0:
                    print(f"   ✅ Encontrados {len(shortcodes)} shortcodes!")
                    return shortcodes
            
            time.sleep(2)
        
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            continue
    
    return shortcodes


def download_from_shortcodes(shortcodes: list) -> int:
    """
    Download fotos de lista de shortcodes
    """
    print(f"\n📥 Baixando {len(shortcodes)} fotos...")
    
    downloaded = 0
    
    for idx, shortcode in enumerate(tqdm(shortcodes, desc="Downloading")):
        # Verificar se já existe
        existing_files = list(OUTPUT_DIR.glob(f"*{shortcode}*"))
        if existing_files:
            tqdm.write(f"   ⏭️  {shortcode} já existe")
            downloaded += 1
            continue
        
        # Obter info do post
        post_info = get_post_info_from_web(shortcode)
        
        if post_info:
            img_url = post_info['url']
            filename = OUTPUT_DIR / f"{USERNAME}_{shortcode}.jpg"
            
            # Download
            if download_image_from_url(img_url, filename):
                tqdm.write(f"   ✅ {shortcode} baixado")
                downloaded += 1
            else:
                tqdm.write(f"   ❌ {shortcode} falhou download")
        else:
            tqdm.write(f"   ⚠️  {shortcode} - não conseguiu obter URL")
        
        # Rate limiting
        time.sleep(2)
        
        # Checkpoint a cada 10
        if (idx + 1) % 10 == 0:
            print(f"\n   💾 Checkpoint: {downloaded}/{idx+1} baixados")
            time.sleep(5)
    
    return downloaded


def load_existing_shortcodes() -> list:
    """
    Carregar shortcodes dos 12 já baixados
    """
    metadata_file = Path("instagram_catalog/catalog_metadata.json")
    
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            data = json.load(f)
            photos = data.get('photos', [])
            return [p.get('shortcode') for p in photos if p.get('shortcode')]
    
    return []


def main():
    print("=" * 70)
    print("📸 Instagram Downloader - One by One")
    print("=" * 70)
    print(f"Target: @{USERNAME}")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    # Carregar shortcodes existentes
    existing = load_existing_shortcodes()
    print(f"✅ Já temos {len(existing)} fotos baixadas")
    
    # Tentar obter lista completa de shortcodes
    all_shortcodes = get_shortcodes_from_profile_page()
    
    if not all_shortcodes:
        print("❌ Não conseguiu extrair shortcodes da página")
        print("\n💡 Solução alternativa:")
        print("   1. Abrir: https://www.instagram.com/chapeuslisboetas/")
        print("   2. Scroll até carregar TODAS as fotos (372)")
        print("   3. F12 > Console")
        print("   4. Colar este código:")
        print()
        print("   document.querySelectorAll('a[href*=\"/p/\"]').forEach(a => {")
        print("     const match = a.href.match(/\\/p\\/([^\\/]+)/);")
        print("     if(match) console.log(match[1]);")
        print("   });")
        print()
        print("   5. Copiar lista de shortcodes")
        print("   6. Criar arquivo: shortcodes.txt (1 por linha)")
        print("   7. Rodar novamente")
        
        # Tentar usar os que já temos
        if existing:
            print(f"\n🔄 Usando {len(existing)} shortcodes já conhecidos...")
            all_shortcodes = existing
        else:
            return
    
    # Filtrar novos (que ainda não temos)
    new_shortcodes = [s for s in all_shortcodes if s not in existing]
    
    print(f"\n📊 Status:")
    print(f"   • Total encontrados: {len(all_shortcodes)}")
    print(f"   • Já baixados: {len(existing)}")
    print(f"   • Novos para baixar: {len(new_shortcodes)}")
    print()
    
    if new_shortcodes:
        # Download
        downloaded = download_from_shortcodes(new_shortcodes)
        
        print("\n" + "=" * 70)
        print("✅ DOWNLOAD COMPLETE!")
        print("=" * 70)
        print(f"📊 Results:")
        print(f"   • Novos baixados: {downloaded}")
        print(f"   • Total agora: {len(existing) + downloaded}")
        print(f"   • Output: {OUTPUT_DIR}")
    else:
        print("✅ Todas as fotos disponíveis já foram baixadas!")


if __name__ == "__main__":
    main()
