#!/usr/bin/env python3
"""
Download Agressivo - Tenta TODAS as técnicas possíveis
Baixa uma a uma, testando múltiplos métodos
"""

import os
import json
import time
import requests
from pathlib import Path
from tqdm import tqdm
import re
import random

USERNAME = "chapeuslisboetas"
OUTPUT_DIR = Path("instagram_catalog/raw_photos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Múltiplos User-Agents para rotacionar
USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Instagram 150.0.0.0 Android",
]

# Lista conhecida de shortcodes (expandir manualmente)
KNOWN_SHORTCODES = [
    "DO8jxFKiJko", "DO53ge6COrf", "DO1YuMVCHCU", "DOwDq6WjcUR",
    "DN5--uojSLW", "DN5lICAirxp", "DNyTzUT2gf7", "DNn-LYdtJAa",
    "DNVyxfvt489", "DNQ1eR1s0LE", "DND36SVML27", "DL-Xt9oNI6H",
]


def get_image_url_aggressive(shortcode: str) -> str:
    """Tentar TODOS os métodos para obter URL da imagem"""
    
    # MÉTODO 1: Direct Instagram
    for attempt in range(3):
        try:
            url = f"https://www.instagram.com/p/{shortcode}/"
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                content = response.text
                
                # Procurar display_url
                patterns = [
                    r'"display_url":"(https://[^"]+)"',
                    r'"display_src":"(https://[^"]+)"',
                    r'content="(https://[^"]+\.jpg[^"]*)"',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        img_url = matches[0].replace(r'\u0026', '&')
                        return img_url
            
            time.sleep(random.uniform(1, 3))
        
        except:
            time.sleep(2)
    
    # MÉTODO 2: Via embed
    try:
        url = f"https://www.instagram.com/p/{shortcode}/embed/"
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            pattern = r'src="(https://[^"]+\.jpg[^"]*)"'
            matches = re.findall(pattern, response.text)
            if matches:
                return matches[0]
    except:
        pass
    
    # MÉTODO 3: Via media endpoint (público)
    try:
        url = f"https://www.instagram.com/p/{shortcode}/media/?size=l"
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        
        if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
            return response.url
    except:
        pass
    
    return None


def download_image(url: str, filepath: Path) -> bool:
    """Download imagem com retry"""
    for attempt in range(3):
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            
            time.sleep(random.uniform(1, 2))
        
        except:
            time.sleep(2)
    
    return False


def main():
    print("=" * 70)
    print("🔥 Download Agressivo - Uma a Uma")
    print("=" * 70)
    print(f"Target: {len(KNOWN_SHORTCODES)} shortcodes conhecidos")
    print()
    
    # Verificar existentes
    existing = [f.stem.split('_')[-1] for f in OUTPUT_DIR.glob("*.jpg")]
    new_codes = [s for s in KNOWN_SHORTCODES if s not in existing]
    
    print(f"📊 Status:")
    print(f"   • Já baixados: {len(existing)}")
    print(f"   • Novos: {len(new_codes)}")
    print()
    
    if not new_codes:
        print("✅ Todos já baixados!")
        return
    
    # Download
    success = 0
    failed = 0
    
    for idx, shortcode in enumerate(tqdm(new_codes, desc="Downloading")):
        try:
            tqdm.write(f"\n[{idx+1}/{len(new_codes)}] {shortcode}")
            
            # Get URL
            img_url = get_image_url_aggressive(shortcode)
            
            if img_url:
                tqdm.write(f"   ✅ URL obtida")
                
                # Download
                filepath = OUTPUT_DIR / f"{USERNAME}_{shortcode}.jpg"
                if download_image(img_url, filepath):
                    success += 1
                    tqdm.write(f"   ✅ Baixado!")
                else:
                    failed += 1
                    tqdm.write(f"   ❌ Download falhou")
            else:
                failed += 1
                tqdm.write(f"   ❌ URL não encontrada")
            
            # Rate limiting
            time.sleep(random.uniform(3, 6))
        
        except Exception as e:
            failed += 1
            tqdm.write(f"   ❌ Erro: {e}")
    
    print()
    print("=" * 70)
    print("✅ Download Complete!")
    print("=" * 70)
    print(f"Success: {success}")
    print(f"Failed: {failed}")
    print(f"Total: {len(existing) + success}")


if __name__ == "__main__":
    main()
