#!/usr/bin/env python3
"""
Download fotos a partir de lista de shortcodes
Lê arquivo shortcodes.txt e baixa todas as fotos
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

SHORTCODES_FILE = Path("shortcodes.txt")

# Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
}


def get_image_url_from_post(shortcode: str) -> str:
    """
    Obter URL da imagem de um post
    """
    url = f"https://www.instagram.com/p/{shortcode}/"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            
            # Procurar "display_url" no HTML
            pattern = r'"display_url":"(https://[^"]+)"'
            matches = re.findall(pattern, content)
            
            if matches:
                img_url = matches[0].replace(r'\u0026', '&')
                return img_url
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return None


def download_image(url: str, filename: Path) -> bool:
    """
    Download imagem
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


def load_shortcodes() -> list:
    """
    Carregar shortcodes de arquivo
    """
    if not SHORTCODES_FILE.exists():
        print(f"❌ Arquivo não encontrado: {SHORTCODES_FILE}")
        print()
        print("💡 Criar arquivo shortcodes.txt com:")
        print("   1 shortcode por linha")
        print()
        print("   Exemplo:")
        print("   DO8jxFKiJko")
        print("   DO53ge6COrf")
        print("   DO1YuMVCHCU")
        print("   ...")
        print()
        print("Ver: DOWNLOAD-MANUAL-SIMPLES.md")
        return []
    
    with open(SHORTCODES_FILE, 'r') as f:
        lines = f.read().strip().split('\n')
        
        # Limpar linhas (remover espaços, URLs, etc)
        shortcodes = []
        for line in lines:
            line = line.strip()
            
            # Se for URL, extrair shortcode
            if '/p/' in line:
                match = re.search(r'/p/([A-Za-z0-9_-]+)', line)
                if match:
                    shortcodes.append(match.group(1))
            # Se for só shortcode
            elif line and re.match(r'^[A-Za-z0-9_-]+$', line):
                shortcodes.append(line)
        
        # Remover duplicados
        shortcodes = list(set(shortcodes))
        
        return shortcodes


def main():
    print("=" * 70)
    print("📥 Download from Shortcodes List")
    print("=" * 70)
    print()
    
    # Carregar shortcodes
    shortcodes = load_shortcodes()
    
    if not shortcodes:
        return
    
    print(f"📋 Loaded {len(shortcodes)} shortcodes from {SHORTCODES_FILE}")
    print()
    
    # Verificar quais já existem
    existing = []
    for f in OUTPUT_DIR.glob("*.jpg"):
        match = re.search(r'_([A-Za-z0-9_-]+)\.jpg$', f.name)
        if match:
            existing.append(match.group(1))
    
    new_shortcodes = [s for s in shortcodes if s not in existing]
    
    print(f"📊 Status:")
    print(f"   • Total shortcodes: {len(shortcodes)}")
    print(f"   • Já baixados: {len(existing)}")
    print(f"   • Novos para baixar: {len(new_shortcodes)}")
    print()
    
    if not new_shortcodes:
        print("✅ Todas as fotos já foram baixadas!")
        return
    
    # Download
    downloaded = 0
    failed = 0
    
    for idx, shortcode in enumerate(tqdm(new_shortcodes, desc="Downloading")):
        try:
            # Get image URL
            img_url = get_image_url_from_post(shortcode)
            
            if img_url:
                filename = OUTPUT_DIR / f"{USERNAME}_{shortcode}.jpg"
                
                if download_image(img_url, filename):
                    downloaded += 1
                    tqdm.write(f"   ✅ {shortcode}")
                else:
                    failed += 1
                    tqdm.write(f"   ❌ {shortcode} - download failed")
            else:
                failed += 1
                tqdm.write(f"   ⚠️  {shortcode} - URL not found")
            
            # Rate limiting
            time.sleep(2)
            
            # Checkpoint
            if (idx + 1) % 10 == 0:
                print(f"\n   💾 Checkpoint: {downloaded} OK, {failed} failed")
                time.sleep(5)
        
        except Exception as e:
            failed += 1
            tqdm.write(f"   ❌ {shortcode} - error: {e}")
    
    # Summary
    print()
    print("=" * 70)
    print("✅ DOWNLOAD COMPLETE!")
    print("=" * 70)
    print(f"📊 Results:")
    print(f"   • Downloaded: {downloaded}")
    print(f"   • Failed: {failed}")
    print(f"   • Total now: {len(existing) + downloaded}")
    print(f"   • Output: {OUTPUT_DIR}")
    print()
    
    # Next step
    if downloaded > 0:
        print("🎯 Next step:")
        print("   python3 download-and-classify-instagram.py --limit 0")
        print("   (Vai classificar as novas fotos)")


if __name__ == "__main__":
    main()
