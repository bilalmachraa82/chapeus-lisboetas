#!/usr/bin/env python3
"""
Seedream 4.0 Batch Processing - Chapéus Lisboetas
Transform Instagram photos → Professional e-commerce images

Supports:
- BytePlus API (official)
- Replicate API (alternative)
- 200 FREE credits
- Optimized prompts per product category
"""

import os
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv
from tqdm import tqdm
import base64

# Load environment
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

# API Selection (auto-detect based on keys)
BYTEPLUS_KEY = os.getenv("SEEDREAM_API_KEY")
BYTEPLUS_SECRET = os.getenv("SEEDREAM_SECRET_KEY")
REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Choose API
if BYTEPLUS_KEY and BYTEPLUS_SECRET:
    API_MODE = "byteplus"
    print("🚀 Usando BytePlus Seedream API")
elif REPLICATE_TOKEN:
    API_MODE = "replicate"
    print("🚀 Usando Replicate Seedream API")
else:
    print("❌ Erro: Nenhuma API key configurada!")
    print("   Configure no .env:")
    print("   - SEEDREAM_API_KEY + SEEDREAM_SECRET_KEY (BytePlus)")
    print("   - OU REPLICATE_API_TOKEN (Replicate)")
    exit(1)

# Paths
INPUT_DIR = Path("instagram_catalog/raw_photos")
OUTPUT_DIR = Path("output_seedream")
METADATA_FILE = Path("instagram_catalog/catalog_metadata.json")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Processing limits
FREE_CREDITS = 200  # Test first 200 images FREE
MAX_RETRIES = 3
SLEEP_BETWEEN_CALLS = 2  # seconds


# ============================================================================
# PROMPT TEMPLATES POR CATEGORIA
# ============================================================================

PROMPTS = {
    "boina": """
Professional product photography: extract boina hat from image,
isolated on pure white background (#FFFFFF),
studio lighting with soft shadows,
maintain fabric texture (wool/cotton),
centered composition,
show natural drape and shape,
e-commerce ready, 4K quality, sharp focus
""",
    
    "chapeu-fedora": """
Professional product photography: extract fedora hat from image,
isolated on pure white background,
studio lighting highlighting brim and crown details,
maintain felt/straw texture and ribbon band,
centered composition with slight 3/4 angle,
show hat structure and proportions,
e-commerce ready, 4K quality
""",
    
    "chapeu-panama": """
Professional product photography: extract panama/straw hat from image,
isolated on pure white background,
studio lighting showing weave pattern and texture,
maintain natural straw color and details,
centered composition,
emphasize summer/elegant style,
e-commerce ready, 4K quality
""",
    
    "bucket-hat": """
Professional product photography: extract bucket hat from image,
isolated on pure white background,
studio lighting showing fabric texture,
maintain casual/streetwear style,
centered flat lay or 3/4 view,
e-commerce ready, 4K quality
""",
    
    "bone": """
Professional product photography: extract baseball cap from image,
isolated on pure white background,
studio lighting showing front logo/design,
maintain fabric texture and cap structure,
centered composition, slight angle view,
e-commerce ready, 4K quality
""",
    
    "default": """
Professional e-commerce product photography:
EXTRACT the hat/accessory from the image and isolate it completely,
REMOVE person and background entirely,
PLACE on clean pure white background (#FFFFFF),
MAINTAIN exact product identity, colors, textures, and details,
APPLY professional studio lighting with soft shadows,
ENSURE product is centered and properly scaled,
CREATE high-quality commercial-ready image,
4K resolution, sharp focus, e-commerce optimized
"""
}


# ============================================================================
# API FUNCTIONS
# ============================================================================

def call_byteplus_api(image_path: Path, prompt: str) -> Optional[bytes]:
    """
    Call BytePlus Seedream 4.0 API
    """
    endpoint = "https://api.byteplus.com/v1/images/generation"
    
    # Read image as base64
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()
    
    headers = {
        "Authorization": f"Bearer {BYTEPLUS_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "seedream-4.0",
        "prompt": prompt,
        "image": image_b64,
        "resolution": "2K",
        "aspect_ratio": "1:1",
        "output_format": "jpeg",
        "quality": 95
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            # Download generated image
            img_url = result.get("data", {}).get("image_url")
            if img_url:
                img_response = requests.get(img_url, timeout=30)
                if img_response.status_code == 200:
                    return img_response.content
        
        else:
            print(f"   ⚠️  API Error {response.status_code}: {response.text[:200]}")
            return None
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def call_replicate_api(image_path: Path, prompt: str) -> Optional[bytes]:
    """
    Call Replicate Seedream 4.0 API
    """
    endpoint = "https://api.replicate.com/v1/predictions"
    
    headers = {
        "Authorization": f"Token {REPLICATE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Upload image to temporary URL (Replicate requires URL)
    # For now, use local file reading and base64
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()
    
    payload = {
        "version": "bytedance/seedream-4",  # Model version
        "input": {
            "prompt": prompt,
            "image": f"data:image/jpeg;base64,{image_b64}",
            "resolution": "2048",
            "aspect_ratio": "1:1",
            "output_format": "jpeg"
        }
    }
    
    try:
        # Create prediction
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 201:
            prediction = response.json()
            prediction_id = prediction.get("id")
            
            # Poll for result (max 60 seconds)
            for _ in range(30):
                status_url = f"{endpoint}/{prediction_id}"
                status_response = requests.get(status_url, headers=headers, timeout=10)
                
                if status_response.status_code == 200:
                    result = status_response.json()
                    status = result.get("status")
                    
                    if status == "succeeded":
                        output_url = result.get("output")
                        if output_url:
                            img_response = requests.get(output_url, timeout=30)
                            if img_response.status_code == 200:
                                return img_response.content
                    
                    elif status == "failed":
                        print(f"   ⚠️  Prediction failed: {result.get('error')}")
                        return None
                
                time.sleep(2)
            
            print("   ⚠️  Timeout waiting for result")
            return None
        
        else:
            print(f"   ⚠️  API Error {response.status_code}: {response.text[:200]}")
            return None
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def process_image(image_path: Path, category: str, index: int) -> Optional[Path]:
    """
    Process single image with Seedream 4.0
    """
    # Select prompt based on category
    prompt = PROMPTS.get(category, PROMPTS["default"])
    
    # Call API based on mode
    for attempt in range(MAX_RETRIES):
        if API_MODE == "byteplus":
            image_data = call_byteplus_api(image_path, prompt)
        else:
            image_data = call_replicate_api(image_path, prompt)
        
        if image_data:
            # Save result
            output_filename = f"{image_path.stem}_professional.jpg"
            output_path = OUTPUT_DIR / output_filename
            
            with open(output_path, "wb") as f:
                f.write(image_data)
            
            return output_path
        
        if attempt < MAX_RETRIES - 1:
            time.sleep(5)  # Wait before retry
    
    return None


# ============================================================================
# MAIN PROCESSING
# ============================================================================

def main(limit: Optional[int] = None, test_mode: bool = False):
    """
    Main batch processing pipeline
    """
    print("=" * 70)
    print("🎨 Seedream 4.0 Batch Processing - Chapéus Lisboetas")
    print("=" * 70)
    print(f"API: {API_MODE.upper()}")
    print(f"Input: {INPUT_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    # Load classifications
    if not METADATA_FILE.exists():
        print(f"❌ Metadata file not found: {METADATA_FILE}")
        print("   Run download-and-classify-instagram.py first!")
        exit(1)
    
    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)
    
    photos = metadata.get("photos", [])
    
    if not photos:
        print("❌ No photos found in metadata!")
        exit(1)
    
    # Apply limit
    if test_mode:
        limit = 10
        print(f"🧪 TEST MODE: Processing only {limit} images")
    elif limit:
        print(f"🎯 Processing {limit} images (FREE credits)")
    else:
        print(f"🎯 Processing ALL {len(photos)} images")
    
    photos_to_process = photos[:limit] if limit else photos
    
    print(f"📸 Total images: {len(photos_to_process)}")
    print()
    
    # Process
    results = []
    free_count = 0
    paid_count = 0
    
    start_time = time.time()
    
    for idx, photo in enumerate(tqdm(photos_to_process, desc="Processing")):
        try:
            image_path = Path(photo["filename"])
            
            if not image_path.exists():
                tqdm.write(f"   ⚠️  Image not found: {image_path.name}")
                continue
            
            # Get category
            classification = photo.get("classification", {})
            category = classification.get("tipo", "default")
            
            # Track free vs paid
            if idx < FREE_CREDITS:
                free_count += 1
                credit_type = "FREE"
            else:
                paid_count += 1
                credit_type = "PAID"
            
            tqdm.write(f"   [{idx+1}/{len(photos_to_process)}] {image_path.name} ({category}) [{credit_type}]")
            
            # Process
            output_path = process_image(image_path, category, idx)
            
            if output_path:
                results.append({
                    "original": str(image_path),
                    "output": str(output_path),
                    "category": category,
                    "classification": classification,
                    "credit_type": credit_type,
                    "index": idx
                })
                tqdm.write(f"   ✅ Saved: {output_path.name}")
            else:
                tqdm.write(f"   ❌ Failed to process")
            
            # Rate limiting
            time.sleep(SLEEP_BETWEEN_CALLS)
        
        except Exception as e:
            tqdm.write(f"   ❌ Error: {e}")
            continue
    
    elapsed = time.time() - start_time
    
    # Save metadata
    output_metadata = {
        "api_mode": API_MODE,
        "total_processed": len(results),
        "free_credits_used": free_count,
        "paid_credits_used": paid_count,
        "processing_time_seconds": elapsed,
        "cost_eur": paid_count * 0.03 * 0.92,  # $0.03 → EUR
        "results": results
    }
    
    with open(OUTPUT_DIR / "metadata.json", "w") as f:
        json.dump(output_metadata, f, indent=2, ensure_ascii=False)
    
    # Summary
    print()
    print("=" * 70)
    print("✅ PROCESSING COMPLETE!")
    print("=" * 70)
    print(f"📊 Statistics:")
    print(f"   • Total processed: {len(results)}")
    print(f"   • FREE credits: {free_count}")
    print(f"   • PAID credits: {paid_count}")
    print(f"   • Failed: {len(photos_to_process) - len(results)}")
    print()
    print(f"⏱️  Time: {int(elapsed//60)} min {int(elapsed%60)} sec")
    print(f"   • Average: {elapsed/len(results):.1f} sec/image")
    print()
    print(f"💰 Cost:")
    print(f"   • FREE: €0 ({free_count} images)")
    print(f"   • PAID: €{paid_count * 0.03 * 0.92:.2f} ({paid_count} images)")
    print(f"   • TOTAL: €{paid_count * 0.03 * 0.92:.2f}")
    print()
    print(f"📁 Output: {OUTPUT_DIR}/")
    print(f"💾 Metadata: {OUTPUT_DIR}/metadata.json")
    print()


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Seedream 4.0 batch processing for e-commerce"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of images (default: all)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode: process only 10 images"
    )
    
    args = parser.parse_args()
    
    main(limit=args.limit, test_mode=args.test)
