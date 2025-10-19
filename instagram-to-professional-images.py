#!/usr/bin/env python3
"""
Instagram to Professional E-commerce Images Pipeline
Chapéus Lisboetas - Automated Image Processing

Workflow:
1. Download public Instagram photos (@chapeuslisboetas)
2. Send to Google Gemini Flash 2.5 (Nano Banana)
3. Generate 4 professional product photos per image:
   - 3x Product-only views (front, 3/4 angle, detail)
   - 1x Professional lifestyle shot with person

Based on Fashion E-commerce Best Practices 2024
"""

import os
import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Optional
import google.generativeai as genai

# ============================================================================
# CONFIGURATION
# ============================================================================

INSTAGRAM_USERNAME = "chapeuslisboetas"
OUTPUT_DIR = Path("./processed_images")
RAW_DIR = OUTPUT_DIR / "raw_instagram"
PROFESSIONAL_DIR = OUTPUT_DIR / "professional"

# Create directories
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROFESSIONAL_DIR.mkdir(parents=True, exist_ok=True)

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
GEMINI_MODEL = "gemini-2.5-flash-image-preview"  # Nano Banana (CorrectModel)


# ============================================================================
# BEST PRACTICES PROMPTS (Fashion E-commerce 2024)
# ============================================================================

PROMPT_TEMPLATES = {
    "product_front": """
    Transform this hat/accessory image into a professional e-commerce product photo:
    
    REQUIREMENTS:
    - Remove person completely, show ONLY the hat/product
    - Clean white background (pure #FFFFFF)
    - Front-facing view, perfectly centered
    - Professional studio lighting (soft, even, no harsh shadows)
    - High resolution, sharp focus on product details
    - Show true colors and textures accurately
    - Product should fill 70-80% of frame
    - Slightly elevated angle (10-15 degrees)
    
    STYLE:
    - Minimalist, premium e-commerce aesthetic
    - Match Zara/Massimo Dutti product photography style
    - Clean, professional, timeless
    
    OUTPUT: Professional product photo ready for online store listing
    """,
    
    "product_three_quarter": """
    Transform this hat/accessory into a professional 3/4 angle product shot:
    
    REQUIREMENTS:
    - Remove person, show ONLY the hat/product
    - Clean white background (#FFFFFF)
    - 45-degree angle view (3/4 perspective)
    - Shows depth, dimension, and shape of hat
    - Professional studio lighting with subtle shadow for depth
    - High detail on texture, stitching, materials
    - Product centered, properly proportioned
    
    STYLE:
    - Premium fashion e-commerce aesthetic
    - Similar to Hermès/Borsalino product photography
    - Emphasize craftsmanship and quality
    
    OUTPUT: Professional 3/4 angle product photo for e-commerce gallery
    """,
    
    "product_detail": """
    Create an extreme close-up detail shot of this hat/accessory:
    
    REQUIREMENTS:
    - Focus on key details: texture, weave, stitching, logo, materials
    - Clean white or subtle gray background
    - Macro photography style - show craftsmanship
    - Perfect focus on material quality
    - Professional lighting highlighting texture
    - Show what makes this product premium/unique
    
    STYLE:
    - Luxury product photography
    - Match Brunello Cucinelli detail shots
    - Emphasize artisanal quality and materials
    
    OUTPUT: Professional detail/macro shot showing product quality
    """,
    
    "lifestyle_professional": """
    Transform this into a PROFESSIONAL lifestyle e-commerce photo:
    
    REQUIREMENTS (Person):
    - Keep person wearing the hat naturally and stylishly
    - Professional model pose (confident, relaxed, not stiff)
    - Proper fit and positioning of hat on head
    - Natural, genuine expression
    - Clean, simple styling
    
    REQUIREMENTS (Background):
    - Soft neutral background (light gray, beige, or subtle outdoor)
    - Clean, uncluttered, professional setting
    - Natural or studio lighting (soft, flattering)
    - Focus remains on the hat, not background
    
    REQUIREMENTS (Composition):
    - Upper body or head-and-shoulders framing
    - Hat is the hero product, clearly visible
    - Professional fashion editorial style
    - Colors look natural and accurate
    
    STYLE:
    - Match Mango/COS lifestyle photography
    - Aspirational but approachable
    - Premium casual aesthetic
    - Portuguese/European style sensibility
    
    OUTPUT: Professional lifestyle photo showing hat in real-world context
    """
}


# ============================================================================
# INSTAGRAM SCRAPER (Public Profiles)
# ============================================================================

def download_instagram_photos(username: str, limit: int = 50) -> List[str]:
    """
    Download photos from public Instagram profile using Instagram's JSON API.
    
    Method: Access public JSON endpoint (no login required)
    Endpoint: https://www.instagram.com/api/v1/users/web_profile_info/?username=X
    
    Args:
        username: Instagram username (e.g., 'chapeuslisboetas')
        limit: Max number of photos to download
    
    Returns:
        List of local file paths to downloaded images
    """
    print(f"📸 Downloading photos from @{username}...")
    
    downloaded_files = []
    
    try:
        # Instagram JSON API endpoint
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "x-ig-app-id": "936619743392459",  # Instagram Web App ID
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Navigate to posts
            user_data = data.get("data", {}).get("user", {})
            edge_owner = user_data.get("edge_owner_to_timeline_media", {})
            posts = edge_owner.get("edges", [])
            
            print(f"✅ Found {len(posts)} posts")
            
            # Download images
            for idx, post in enumerate(posts[:limit]):
                node = post.get("node", {})
                
                # Get image URL (highest quality)
                image_url = node.get("display_url")
                shortcode = node.get("shortcode", f"post_{idx}")
                
                if image_url:
                    # Download image
                    img_response = requests.get(image_url, timeout=30)
                    
                    if img_response.status_code == 200:
                        filename = RAW_DIR / f"{username}_{shortcode}.jpg"
                        
                        with open(filename, 'wb') as f:
                            f.write(img_response.content)
                        
                        downloaded_files.append(str(filename))
                        print(f"  ✓ Downloaded {idx+1}/{limit}: {shortcode}")
                        
                        time.sleep(1)  # Rate limiting
                
                if idx >= limit - 1:
                    break
        
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print("💡 Fallback: Using Instaloader library...")
            
            # Fallback to instaloader
            downloaded_files = download_with_instaloader(username, limit)
    
    except Exception as e:
        print(f"❌ Error downloading: {e}")
        print("💡 Trying alternative method...")
        downloaded_files = download_with_instaloader(username, limit)
    
    return downloaded_files


def download_with_instaloader(username: str, limit: int) -> List[str]:
    """Fallback method using instaloader library"""
    try:
        import instaloader
        
        L = instaloader.Instaloader(
            dirname_pattern=str(RAW_DIR),
            filename_pattern=f"{username}_{{shortcode}}"
        )
        
        profile = instaloader.Profile.from_username(L.context, username)
        
        downloaded = []
        for idx, post in enumerate(profile.get_posts()):
            if idx >= limit:
                break
            
            L.download_post(post, target=str(RAW_DIR))
            
            # Find downloaded file
            files = list(RAW_DIR.glob(f"{username}_{post.shortcode}*.jpg"))
            if files:
                downloaded.append(str(files[0]))
            
            print(f"  ✓ Downloaded {idx+1}/{limit}")
            time.sleep(2)
        
        return downloaded
    
    except ImportError:
        print("❌ Instaloader not installed. Install: pip install instaloader")
        return []
    except Exception as e:
        print(f"❌ Instaloader error: {e}")
        return []


# ============================================================================
# GEMINI IMAGE GENERATION (Nano Banana)
# ============================================================================

def initialize_gemini():
    """Initialize Gemini API"""
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Test connection
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        print("✅ Gemini API initialized successfully")
        return model
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        print("💡 Make sure GEMINI_API_KEY environment variable is set")
        return None


def generate_professional_images(
    model: genai.GenerativeModel,
    source_image_path: str,
    output_prefix: str
) -> Dict[str, str]:
    """
    Generate 4 professional product images from Instagram photo.
    
    Args:
        model: Gemini model instance
        source_image_path: Path to source Instagram image
        output_prefix: Prefix for output filenames
    
    Returns:
        Dictionary mapping view type to output file path
    """
    print(f"\n🎨 Processing: {Path(source_image_path).name}")
    
    results = {}
    
    # Load source image
    with open(source_image_path, 'rb') as f:
        source_image_data = f.read()
    
    # Generate each view
    for view_name, prompt in PROMPT_TEMPLATES.items():
        print(f"  → Generating {view_name}...")
        
        try:
            # Create prompt with image
            response = model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": source_image_data}
            ])
            
            # Save generated image
            if response and hasattr(response, 'images') and response.images:
                output_path = PROFESSIONAL_DIR / f"{output_prefix}_{view_name}.jpg"
                
                # Save image
                with open(output_path, 'wb') as f:
                    f.write(response.images[0])
                
                results[view_name] = str(output_path)
                print(f"    ✅ Saved: {output_path.name}")
            
            else:
                print(f"    ⚠️  No image generated for {view_name}")
            
            time.sleep(2)  # Rate limiting
        
        except Exception as e:
            print(f"    ❌ Error generating {view_name}: {e}")
    
    return results


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def process_instagram_to_ecommerce(
    instagram_username: str = INSTAGRAM_USERNAME,
    max_photos: int = 10,
    dry_run: bool = False
):
    """
    Main pipeline: Instagram → Professional E-commerce Images
    
    Args:
        instagram_username: Instagram profile to scrape
        max_photos: Maximum number of photos to process
        dry_run: If True, only download, don't process with Gemini
    """
    print("=" * 70)
    print("🎩 CHAPÉUS LISBOETAS - Instagram to E-commerce Image Pipeline")
    print("=" * 70)
    print()
    
    # Step 1: Download Instagram photos
    print("STEP 1: Download Instagram Photos")
    print("-" * 70)
    downloaded_photos = download_instagram_photos(instagram_username, max_photos)
    
    if not downloaded_photos:
        print("❌ No photos downloaded. Exiting.")
        return
    
    print(f"\n✅ Downloaded {len(downloaded_photos)} photos")
    print()
    
    if dry_run:
        print("🏁 Dry run complete. Skipping Gemini processing.")
        return
    
    # Step 2: Initialize Gemini
    print("STEP 2: Initialize Gemini API")
    print("-" * 70)
    model = initialize_gemini()
    
    if not model:
        print("❌ Cannot initialize Gemini. Exiting.")
        return
    
    print()
    
    # Step 3: Process each image
    print("STEP 3: Generate Professional E-commerce Images")
    print("-" * 70)
    
    all_results = {}
    
    for idx, photo_path in enumerate(downloaded_photos):
        photo_name = Path(photo_path).stem
        
        print(f"\n[{idx+1}/{len(downloaded_photos)}] Processing {photo_name}...")
        
        results = generate_professional_images(
            model=model,
            source_image_path=photo_path,
            output_prefix=photo_name
        )
        
        all_results[photo_name] = results
    
    # Step 4: Summary
    print("\n" + "=" * 70)
    print("✅ PIPELINE COMPLETE!")
    print("=" * 70)
    print()
    print(f"📊 Statistics:")
    print(f"  • Source photos: {len(downloaded_photos)}")
    print(f"  • Products processed: {len(all_results)}")
    print(f"  • Professional images: {sum(len(r) for r in all_results.values())}")
    print()
    print(f"📁 Output directories:")
    print(f"  • Raw Instagram: {RAW_DIR}")
    print(f"  • Professional: {PROFESSIONAL_DIR}")
    print()
    
    # Save metadata
    metadata_file = OUTPUT_DIR / "processing_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump({
            "instagram_username": instagram_username,
            "total_processed": len(downloaded_photos),
            "results": all_results
        }, f, indent=2)
    
    print(f"💾 Metadata saved: {metadata_file}")
    print()
    print("🎉 Ready to import to WooCommerce!")


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Instagram to Professional E-commerce Images Pipeline"
    )
    parser.add_argument(
        "--username",
        default=INSTAGRAM_USERNAME,
        help="Instagram username to scrape"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Max number of photos to process"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only download, don't process with Gemini"
    )
    parser.add_argument(
        "--api-key",
        help="Gemini API key (or set GEMINI_API_KEY env var)"
    )
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        GEMINI_API_KEY = args.api_key
        os.environ["GEMINI_API_KEY"] = args.api_key
    
    # Run pipeline
    process_instagram_to_ecommerce(
        instagram_username=args.username,
        max_photos=args.limit,
        dry_run=args.dry_run
    )
