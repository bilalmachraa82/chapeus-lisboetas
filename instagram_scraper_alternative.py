#!/usr/bin/env python3
"""
Instagram Photo Scraper - Método Alternativo
Usa múltiplas técnicas para obter TODAS as 372 fotos

Métodos:
1. API pública (já tentado - limita ~12)
2. Web scraping HTML
3. RSS/Sitemap
4. Picuki proxy
"""

import os
import json
import time
import requests
from pathlib import Path
from typing import List, Dict
from bs4 import BeautifulSoup
from tqdm import tqdm

# Configuration
USERNAME = "chapeuslisboetas"
OUTPUT_DIR = Path("instagram_all_photos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


# ============================================================================
# MÉTODO 2: Picuki Proxy (não requer login)
# ============================================================================

def download_via_picuki(username: str) -> List[Dict]:
    """
    Usar Picuki como proxy para Instagram (público)
    """
    print(f"🔍 MÉTODO 2: Picuki Proxy")
    print("=" * 70)
    
    photos = []
    base_url = f"https://www.picuki.com/profile/{username}"
    
    try:
        response = requests.get(base_url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all posts
            posts = soup.find_all('div', class_='post-image')
            
            print(f"✅ Encontrados {len(posts)} posts via Picuki")
            
            for idx, post in enumerate(tqdm(posts[:100], desc="Downloading")):
                try:
                    # Get image URL
                    img_tag = post.find('img')
                    if img_tag and img_tag.get('src'):
                        img_url = img_tag['src']
                        
                        # Download
                        img_response = requests.get(img_url, timeout=30)
                        
                        if img_response.status_code == 200:
                            filename = OUTPUT_DIR / f"picuki_{username}_{idx:04d}.jpg"
                            
                            with open(filename, 'wb') as f:
                                f.write(img_response.content)
                            
                            photos.append({
                                "filename": str(filename),
                                "method": "picuki",
                                "index": idx
                            })
                        
                        time.sleep(0.5)  # Rate limiting
                
                except Exception as e:
                    print(f"   ⚠️  Error on post {idx}: {e}")
                    continue
        
        else:
            print(f"❌ Picuki error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Picuki error: {e}")
    
    return photos


# ============================================================================
# MÉTODO 3: Imginn Proxy
# ============================================================================

def download_via_imginn(username: str) -> List[Dict]:
    """
    Usar Imginn como proxy
    """
    print(f"\n🔍 MÉTODO 3: Imginn Proxy")
    print("=" * 70)
    
    photos = []
    base_url = f"https://imginn.com/{username}/"
    
    try:
        response = requests.get(base_url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find image containers
            images = soup.find_all('img', class_='post-image')
            
            print(f"✅ Encontrados {len(images)} posts via Imginn")
            
            for idx, img in enumerate(tqdm(images[:100], desc="Downloading")):
                try:
                    img_url = img.get('src') or img.get('data-src')
                    
                    if img_url:
                        img_response = requests.get(img_url, timeout=30)
                        
                        if img_response.status_code == 200:
                            filename = OUTPUT_DIR / f"imginn_{username}_{idx:04d}.jpg"
                            
                            with open(filename, 'wb') as f:
                                f.write(img_response.content)
                            
                            photos.append({
                                "filename": str(filename),
                                "method": "imginn",
                                "index": idx
                            })
                        
                        time.sleep(0.5)
                
                except Exception as e:
                    print(f"   ⚠️  Error on image {idx}: {e}")
                    continue
        
        else:
            print(f"❌ Imginn error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Imginn error: {e}")
    
    return photos


# ============================================================================
# MÉTODO 4: Storiesig
# ============================================================================

def download_via_storiesig(username: str) -> List[Dict]:
    """
    Usar Storiesig proxy
    """
    print(f"\n🔍 MÉTODO 4: Storiesig")
    print("=" * 70)
    
    photos = []
    base_url = f"https://storiesig.info/stories/{username}"
    
    try:
        response = requests.get(base_url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            # Parse JSON or HTML
            try:
                data = response.json()
                items = data.get('items', [])
            except:
                # HTML parsing
                soup = BeautifulSoup(response.content, 'html.parser')
                items = soup.find_all('img')
            
            print(f"✅ Encontrados {len(items)} posts via Storiesig")
            
            for idx, item in enumerate(tqdm(items[:100], desc="Downloading")):
                try:
                    if isinstance(item, dict):
                        img_url = item.get('url')
                    else:
                        img_url = item.get('src')
                    
                    if img_url:
                        img_response = requests.get(img_url, timeout=30)
                        
                        if img_response.status_code == 200:
                            filename = OUTPUT_DIR / f"storiesig_{username}_{idx:04d}.jpg"
                            
                            with open(filename, 'wb') as f:
                                f.write(img_response.content)
                            
                            photos.append({
                                "filename": str(filename),
                                "method": "storiesig",
                                "index": idx
                            })
                        
                        time.sleep(0.5)
                
                except Exception as e:
                    print(f"   ⚠️  Error on item {idx}: {e}")
                    continue
        
        else:
            print(f"❌ Storiesig error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Storiesig error: {e}")
    
    return photos


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("📸 Instagram Scraper - Métodos Alternativos")
    print("=" * 70)
    print(f"Target: @{USERNAME}")
    print(f"Goal: 372 photos")
    print()
    
    all_photos = []
    
    # Try all methods
    methods = [
        ("Picuki", download_via_picuki),
        ("Imginn", download_via_imginn),
        ("Storiesig", download_via_storiesig),
    ]
    
    for method_name, method_func in methods:
        try:
            photos = method_func(USERNAME)
            all_photos.extend(photos)
            print(f"   ✅ {method_name}: {len(photos)} fotos")
        except Exception as e:
            print(f"   ❌ {method_name} failed: {e}")
        
        time.sleep(2)  # Between methods
    
    # Save metadata
    metadata = {
        "username": USERNAME,
        "total_photos": len(all_photos),
        "methods_used": [m[0] for m in methods],
        "photos": all_photos
    }
    
    with open(OUTPUT_DIR / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    # Summary
    print()
    print("=" * 70)
    print("✅ DOWNLOAD COMPLETE!")
    print("=" * 70)
    print(f"📊 Results:")
    print(f"   • Total photos: {len(all_photos)}")
    print(f"   • Output: {OUTPUT_DIR}")
    print()


if __name__ == "__main__":
    # Install dependencies
    try:
        import bs4
    except ImportError:
        print("📦 Installing beautifulsoup4...")
        os.system("pip3 install beautifulsoup4 --quiet")
    
    main()
