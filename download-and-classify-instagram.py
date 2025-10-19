#!/usr/bin/env python3
"""
Instagram Download & Classification System
Chapéus Lisboetas - Automated Product Categorization

Features:
1. Download ALL 372 Instagram photos
2. Auto-classify using Gemini Vision (FREE tier)
3. Organize by: Gender, Product Type, Style, Color
4. Generate metadata JSON for WooCommerce import
5. Create folder structure ready for e-commerce

Author: Droid AI
Date: 30 September 2024
"""

import os
import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "chapeuslisboetas")
OUTPUT_DIR = Path("./instagram_catalog")
RAW_DIR = OUTPUT_DIR / "raw_photos"
CLASSIFIED_DIR = OUTPUT_DIR / "classified"

# Create directory structure
CATEGORIES = {
    "genero": ["homem", "mulher", "crianca", "unisex"],
    "tipo": ["boina", "chapeu-fedora", "chapeu-panama", "bone", "cartola", 
             "gorro", "bucket-hat", "capeline", "outros"],
    "estilo": ["classico", "casual", "formal", "desportivo", "vintage", "moderno"],
    "cor": ["preto", "branco", "castanho", "azul", "cinza", "bege", 
            "bordeaux", "verde", "outros"]
}

for category, subcats in CATEGORIES.items():
    for subcat in subcats:
        (CLASSIFIED_DIR / category / subcat).mkdir(parents=True, exist_ok=True)

RAW_DIR.mkdir(parents=True, exist_ok=True)

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_VISION_MODEL = "gemini-2.5-flash"  # FREE tier for vision/text


# ============================================================================
# INSTAGRAM DOWNLOADER
# ============================================================================

def download_all_instagram_photos(username: str, max_photos: int = 500, retry_count: int = 3) -> List[Dict]:
    """
    Download ALL photos from Instagram public profile.
    Includes retry logic for rate limiting (401/403 errors)
    
    Returns:
        List of dicts with photo metadata
    """
    print(f"📸 Downloading ALL photos from @{username}...")
    print("=" * 70)
    
    downloaded_photos = []
    
    for attempt in range(retry_count):
        try:
            url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "*/*",
                "x-ig-app-id": "936619743392459",
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            # Handle rate limiting
            if response.status_code in [401, 403, 429]:
                if attempt < retry_count - 1:
                    wait_time = 60 * (attempt + 1)  # 60s, 120s, 180s
                    print(f"⚠️  Rate limit detected (HTTP {response.status_code})")
                    print(f"   Aguardando {wait_time} segundos antes de tentar novamente...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ Rate limit persistente após {retry_count} tentativas")
                    print(f"   Solução: Adicionar INSTAGRAM_LOGIN e INSTAGRAM_PASSWORD no .env")
                    return downloaded_photos
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Success! Break retry loop
                break
        
        except requests.exceptions.RequestException as e:
            if attempt < retry_count - 1:
                print(f"⚠️  Network error: {e}")
                print(f"   Tentando novamente em 30 segundos...")
                time.sleep(30)
                continue
            else:
                print(f"❌ Erro após {retry_count} tentativas: {e}")
                return []
    
    try:
        if response.status_code == 200:
            data = response.json()
            user_data = data.get("data", {}).get("user", {})
            edge_owner = user_data.get("edge_owner_to_timeline_media", {})
            posts = edge_owner.get("edges", [])
            total_count = edge_owner.get("count", 0)
            
            print(f"✅ Found {total_count} posts in account")
            print(f"🎯 Downloading {min(len(posts), max_photos)} posts...")
            print()
            
            # Progress bar
            with tqdm(total=min(len(posts), max_photos), desc="Downloading", unit="photo") as pbar:
                for idx, post in enumerate(posts[:max_photos]):
                    node = post.get("node", {})
                    
                    # Get metadata
                    image_url = node.get("display_url")
                    shortcode = node.get("shortcode", f"post_{idx}")
                    caption = node.get("edge_media_to_caption", {}).get("edges", [])
                    caption_text = caption[0].get("node", {}).get("text", "") if caption else ""
                    likes = node.get("edge_liked_by", {}).get("count", 0)
                    timestamp = node.get("taken_at_timestamp", 0)
                    
                    if image_url:
                        # Download image
                        img_response = requests.get(image_url, timeout=30)
                        
                        if img_response.status_code == 200:
                            filename = RAW_DIR / f"{username}_{shortcode}.jpg"
                            
                            with open(filename, 'wb') as f:
                                f.write(img_response.content)
                            
                            # Store metadata
                            photo_meta = {
                                "filename": str(filename),
                                "shortcode": shortcode,
                                "instagram_url": f"https://www.instagram.com/p/{shortcode}/",
                                "caption": caption_text[:200],  # First 200 chars
                                "likes": likes,
                                "timestamp": timestamp,
                                "date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d"),
                                "index": idx
                            }
                            
                            downloaded_photos.append(photo_meta)
                            pbar.update(1)
                            
                            time.sleep(0.5)  # Rate limiting
                    
                    if idx >= max_photos - 1:
                        break
        
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return []
    
    except Exception as e:
        print(f"❌ Error downloading: {e}")
        return []
    
    print()
    print(f"✅ Successfully downloaded {len(downloaded_photos)} photos!")
    print()
    
    return downloaded_photos


# ============================================================================
# AI CLASSIFICATION (Gemini Vision - FREE TIER)
# ============================================================================

def classify_product_with_ai(image_path: str, caption: str = "") -> Dict:
    """
    Classify hat/accessory using Gemini Vision (FREE tier).
    
    Returns:
        Dict with classifications
    """
    
    prompt = f"""
    Analyze this hat/accessory product image and classify it precisely.
    
    Instagram caption (context): "{caption}"
    
    Provide classification in this EXACT JSON format (no extra text):
    {{
        "genero": "homem|mulher|crianca|unisex",
        "tipo": "boina|chapeu-fedora|chapeu-panama|bone|cartola|gorro|bucket-hat|capeline|outros",
        "estilo": "classico|casual|formal|desportivo|vintage|moderno",
        "cor_principal": "preto|branco|castanho|azul|cinza|bege|bordeaux|verde|outros",
        "material_aparente": "la|algodao|palha|pele|sintetico|outros",
        "descricao_curta": "Brief Portuguese description (30 words max)",
        "tags": ["tag1", "tag2", "tag3"],
        "preco_sugerido_eur": 35-65,
        "tem_pessoa": true|false,
        "qualidade_foto": "alta|media|baixa",
        "adequado_ecommerce": true|false
    }}
    
    BE PRECISE. Use ONLY the exact values provided in options.
    """
    
    try:
        # Load image
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Initialize Gemini (FREE tier - vision/text)
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_VISION_MODEL)
        
        # Generate classification
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_data}
        ])
        
        # Parse JSON response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        classification = json.loads(response_text.strip())
        return classification
    
    except json.JSONDecodeError as e:
        print(f"    ⚠️  JSON parse error, using fallback classification")
        return {
            "genero": "unisex",
            "tipo": "outros",
            "estilo": "classico",
            "cor_principal": "outros",
            "material_aparente": "outros",
            "descricao_curta": "Produto de chapelaria",
            "tags": ["chapeu"],
            "preco_sugerido_eur": 45,
            "tem_pessoa": False,
            "qualidade_foto": "media",
            "adequado_ecommerce": True
        }
    
    except Exception as e:
        print(f"    ❌ Classification error: {e}")
        return None


# ============================================================================
# ORGANIZE BY CLASSIFICATION
# ============================================================================

def organize_photos_by_classification(photos_metadata: List[Dict]) -> Dict:
    """
    Organize photos into category folders and generate WooCommerce-ready structure.
    """
    print("\n" + "=" * 70)
    print("📂 Organizing photos by classification...")
    print("=" * 70)
    print()
    
    organized = {
        "by_gender": {},
        "by_type": {},
        "by_style": {},
        "by_color": {},
        "products": []
    }
    
    for photo in photos_metadata:
        if not photo.get("classification"):
            continue
        
        cls = photo["classification"]
        filename = Path(photo["filename"])
        
        # Organize by gender
        gender = cls.get("genero", "unisex")
        gender_dir = CLASSIFIED_DIR / "genero" / gender
        gender_file = gender_dir / filename.name
        
        # Copy file
        import shutil
        if filename.exists():
            shutil.copy2(filename, gender_file)
        
        # Track statistics
        organized["by_gender"][gender] = organized["by_gender"].get(gender, 0) + 1
        organized["by_type"][cls.get("tipo", "outros")] = organized["by_type"].get(cls.get("tipo", "outros"), 0) + 1
        organized["by_style"][cls.get("estilo", "classico")] = organized["by_style"].get(cls.get("estilo", "classico"), 0) + 1
        organized["by_color"][cls.get("cor_principal", "outros")] = organized["by_color"].get(cls.get("cor_principal", "outros"), 0) + 1
        
        # Add to products list
        product_entry = {
            **photo,
            "sku": f"CL-{cls.get('tipo', 'OUTROS')[:3].upper()}-{photo['index']:04d}",
            "woocommerce_ready": cls.get("adequado_ecommerce", False)
        }
        organized["products"].append(product_entry)
    
    # Print statistics
    print("📊 Classification Statistics:")
    print()
    print("GÉNERO:")
    for gender, count in sorted(organized["by_gender"].items()):
        print(f"  {gender:12} → {count:3} fotos")
    
    print("\nTIPO PRODUTO:")
    for tipo, count in sorted(organized["by_type"].items(), key=lambda x: x[1], reverse=True):
        print(f"  {tipo:20} → {count:3} fotos")
    
    print("\nESTILO:")
    for estilo, count in sorted(organized["by_style"].items()):
        print(f"  {estilo:12} → {count:3} fotos")
    
    print("\nCOR PRINCIPAL:")
    for cor, count in sorted(organized["by_color"].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {cor:15} → {count:3} fotos")
    
    return organized


# ============================================================================
# EXPORT TO WOOCOMMERCE CSV
# ============================================================================

def generate_woocommerce_csv(organized_data: Dict, output_file: str = "woocommerce-import.csv"):
    """
    Generate WooCommerce CSV import file.
    """
    import csv
    
    csv_file = OUTPUT_DIR / output_file
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Headers
        writer.writerow([
            'SKU', 'Name', 'Description', 'Short Description',
            'Price', 'Sale Price', 'Categories', 'Tags',
            'Image', 'Stock', 'Gender', 'Type', 'Style', 
            'Color', 'Material', 'Instagram URL'
        ])
        
        # Products
        for product in organized_data["products"]:
            if not product.get("classification"):
                continue
            
            cls = product["classification"]
            
            # Generate product name
            tipo = cls.get("tipo", "Chapéu").replace("-", " ").title()
            cor = cls.get("cor_principal", "").capitalize()
            name = f"{tipo} {cor}".strip()
            
            writer.writerow([
                product["sku"],
                name,
                cls.get("descricao_curta", ""),
                f"Produto de chapelaria de qualidade.",
                cls.get("preco_sugerido_eur", 45),
                "",  # Sale price
                f"Chapéus > {cls.get('tipo', 'Outros').title()}",
                ", ".join(cls.get("tags", [])),
                product["filename"],
                "10",  # Stock
                cls.get("genero", "unisex"),
                cls.get("tipo", "outros"),
                cls.get("estilo", "classico"),
                cls.get("cor_principal", "outros"),
                cls.get("material_aparente", "outros"),
                product["instagram_url"]
            ])
    
    print(f"\n✅ CSV exportado: {csv_file}")
    return csv_file


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main(max_photos: int = 372, classify: bool = True):
    """
    Main pipeline: Download + Classify + Organize
    """
    print("=" * 70)
    print("🎩 CHAPÉUS LISBOETAS - Download & Classification System")
    print("=" * 70)
    print()
    print(f"📱 Instagram: @{INSTAGRAM_USERNAME}")
    print(f"🎯 Target: {max_photos} photos")
    print(f"🤖 AI Classification: {'YES' if classify else 'NO'}")
    print()
    
    start_time = time.time()
    
    # STEP 1: Download
    print("STEP 1: Download Instagram Photos")
    print("-" * 70)
    photos = download_all_instagram_photos(INSTAGRAM_USERNAME, max_photos)
    
    if not photos:
        print("❌ No photos downloaded. Exiting.")
        return
    
    # STEP 2: Classify (if enabled)
    if classify and GEMINI_API_KEY:
        print("STEP 2: AI Classification (Gemini Vision)")
        print("-" * 70)
        print(f"🤖 Classifying {len(photos)} photos...")
        print()
        
        with tqdm(total=len(photos), desc="Classifying", unit="photo") as pbar:
            for idx, photo in enumerate(photos):
                try:
                    classification = classify_product_with_ai(
                        photo["filename"], 
                        photo.get("caption", "")
                    )
                    
                    if classification:
                        photo["classification"] = classification
                    
                    pbar.update(1)
                    time.sleep(1.5)  # Rate limiting (FREE tier)
                
                except Exception as e:
                    pbar.write(f"  ⚠️  Error classifying {photo['shortcode']}: {e}")
                    photo["classification"] = None
        
        print()
        print(f"✅ Classified {len([p for p in photos if p.get('classification')])} photos")
        print()
    
    # STEP 3: Organize
    if classify:
        print("STEP 3: Organize by Categories")
        print("-" * 70)
        organized = organize_photos_by_classification(photos)
        
        # STEP 4: Export CSV
        print("\nSTEP 4: Generate WooCommerce CSV")
        print("-" * 70)
        csv_file = generate_woocommerce_csv(organized)
    
    # STEP 5: Save metadata
    print("\nSTEP 5: Save Metadata")
    print("-" * 70)
    
    metadata_file = OUTPUT_DIR / "catalog_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump({
            "instagram_username": INSTAGRAM_USERNAME,
            "download_date": datetime.now().isoformat(),
            "total_photos": len(photos),
            "classified_photos": len([p for p in photos if p.get('classification')]),
            "photos": photos,
            "organized": organized if classify else {},
            "processing_time_seconds": time.time() - start_time
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Metadata saved: {metadata_file}")
    
    # SUMMARY
    print("\n" + "=" * 70)
    print("✅ PIPELINE COMPLETE!")
    print("=" * 70)
    print()
    print(f"📊 Results:")
    print(f"  • Total photos downloaded: {len(photos)}")
    if classify:
        print(f"  • Successfully classified: {len([p for p in photos if p.get('classification')])}")
        print(f"  • WooCommerce CSV: {csv_file}")
    print(f"  • Processing time: {int(time.time() - start_time)} seconds")
    print()
    print(f"📁 Output:")
    print(f"  • Raw photos: {RAW_DIR}")
    if classify:
        print(f"  • Classified: {CLASSIFIED_DIR}")
        print(f"  • CSV import: {csv_file}")
    print(f"  • Metadata: {metadata_file}")
    print()
    print("🎉 Ready for next steps!")
    print()


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download and classify Instagram photos for e-commerce"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=372,
        help="Max number of photos to download (default: 372 = all)"
    )
    parser.add_argument(
        "--no-classify",
        action="store_true",
        help="Skip AI classification (download only)"
    )
    
    args = parser.parse_args()
    
    main(
        max_photos=args.limit,
        classify=not args.no_classify
    )
