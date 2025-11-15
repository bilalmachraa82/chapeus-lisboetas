#!/usr/bin/env python3
"""Quick test script to generate editorial photos for 5 products with available source images."""

import os
import sys
from pathlib import Path

# Add parent directory to path to import from gemini_editorial_v2
sys.path.insert(0, str(Path(__file__).parent))

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ Missing dependencies. Install with:\n   pip install google-genai google-api-core pillow")
    sys.exit(1)

from PIL import Image

# Test products with available source images
TEST_PRODUCTS = [
    {
        "name": "BOINA JORNALEIRO PURE WOOL",
        "sku": "tags-fabricado-na-italia-la-pura",
        "folder": "wordpress/wp-content/uploads/products/chapéus lã/tags-fabricado-na-italia-la-pura",
        "source_image": "img_01.jpg"
    },
    {
        "name": "CHAPÉU FEMININO RÁFIA",
        "sku": "chapeu-art-970-pack-12",
        "folder": "wordpress/wp-content/uploads/products/chapéus lã/chapeu-art-970-pack-12",
        "source_image": "img_01.jpg"
    },
    {
        "name": "CHAPÉU IMPERMEÁVEL",
        "sku": "chapeu-impermeavel-art-181056",
        "folder": "wordpress/wp-content/uploads/products/chapéus lã/chapeu-impermeavel-art-181056-tags-fabricado-na-italia-la-esmagavel-impermeavel",
        "source_image": "img_01.jpg"
    },
    {
        "name": "CHAPÉU COWBOY",
        "sku": "chapeu-cowboy",
        "folder": "wordpress/wp-content/uploads/products/cowboy/chapeu-cowboy",
        "source_image": "img_01.jpg"
    },
    {
        "name": "CHAPÉU DOBRÁVEL IMPERMEÁVEL",
        "sku": "chapeu-dobravel",
        "folder": "wordpress/wp-content/uploads/products/à prova d´água/chapeu-dobravel",
        "source_image": "img_01.jpg"
    }
]

REPO_ROOT = Path(__file__).resolve().parents[1]
GEMINI_API_KEY = os.environ.get("GEMINI_KEY_PRIMARY", "AIzaSyDWCanKI3CtqyIWTOpaPVPVtmGOW6A7OaE")
MODEL_NAME = "gemini-2.5-flash-image"

# Shot configurations from gemini_editorial_v2.py
SHOT_TYPES = {
    "editorial": {
        "aspect_ratio": "3:4",
        "prompt": """Take the {product_name} from the reference image and create a high-end
editorial portrait with a sophisticated Portuguese model wearing it, framed in
a vertical 3:4 aspect ratio (portrait orientation, 600×800px ideal). The model
looks directly at the camera with a confident, subtle smile. Style them with a
minimalist earth-tone blazer or fine knit that complements the hat. Background:
soft-focus cream/ivory studio gradient. Lighting: soft window light from the
front-left creating gentle rim lighting so the hat's silhouette, color and
texture remain accurate. Capture with an 85mm portrait lens at f/1.8 for shallow
depth of field. Composition: Center the model's face and hat in the upper half
of the frame, leaving breathing room at the top for the hat. Massimo Dutti /
Chiado heritage aesthetic."""
    },
    "angle": {
        "aspect_ratio": "1:1",
        "prompt": """Transform the hat into a 3/4 profile editorial shot in a perfect square 1:1
aspect ratio (800×800px). Place the model turning the head 30 degrees to the
right, eyes gazing off camera. Center the composition so the hat and face are
perfectly balanced in the square frame. Emphasize the brim shape and crown
detail through sculpted studio lighting (key light at 45°). Add subtle hair
or scarf movement for dynamism. Neutral grey-blue background. Ensure the hat
keeps its authentic texture. Square composition optimized for thumbnail display."""
    }
}

LIFESTYLE_SCENARIOS = {
    "eletrico": {
        "name": "Elétrico 28",
        "prompt": """Create an authentic Lisbon lifestyle scene in cinematic 16:9 widescreen format
(1200×675px) showing the model wearing the hat while walking on calçada
portuguesa cobblestones. Include a softly blurred Elétrico 28 tram in the
background, warm late-afternoon light, and contemporary Portuguese wardrobe
(linen shirt, tailored coat). Composition with 35mm street lens at f/2.8:
foreground sharp (model + hat), background cinematic. Center the model in the
middle-left third of the frame using rule of thirds for dynamic composition.
Preserve the hat's real materials and palette. Widescreen cinematic aesthetic."""
    },
    "cafe": {
        "name": "Café Esplanada",
        "prompt": """Traditional Portuguese street café in cinematic 16:9 (1200×675px): Model seated
at outdoor esplanada table with bica (espresso) and pastel de nata, typical
mosaic pavement visible. Warm terracotta building facade with vintage signage
in background. Soft diffused daylight. Composition with model slightly off-center,
café atmosphere context. Contemporary casual Portuguese style (knit sweater,
relaxed confidence). Keep hat's real color and texture. Lifestyle editorial
aesthetic, 35mm lens at f/2.8."""
    }
}

def generate_shot(client, product_name, source_path, shot_type, scenario_key=None):
    """Generate a single shot using Gemini API."""
    img = Image.open(source_path)

    if shot_type == "lifestyle":
        prompt_template = LIFESTYLE_SCENARIOS[scenario_key]["prompt"]
        aspect_ratio = "16:9"
        scenario_name = LIFESTYLE_SCENARIOS[scenario_key]["name"]
    else:
        prompt_template = SHOT_TYPES[shot_type]["prompt"]
        aspect_ratio = SHOT_TYPES[shot_type]["aspect_ratio"]
        scenario_name = None

    prompt = prompt_template.format(product_name=product_name)

    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio=aspect_ratio)
    )

    scenario_info = f" ({scenario_name})" if scenario_name else ""
    print(f"      🔍 Calling Gemini API ({shot_type}, {aspect_ratio}{scenario_info})...")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt, img],
        config=config
    )

    if response.candidates[0].finish_reason != "STOP":
        reason = response.candidates[0].finish_reason
        raise RuntimeError(f"Safety filter: {reason}")

    for part in response.parts:
        if part.inline_data is not None:
            data = part.inline_data.data
            print(f"      📦 Received {len(data)} bytes")
            del img
            return data

    raise RuntimeError("No image bytes returned")

def main():
    print("=" * 70)
    print("TEST: EDITORIAL PHOTOS FOR 5 PRODUCTS")
    print("=" * 70)
    print(f"Gemini API Key: {'Set' if GEMINI_API_KEY else 'Missing'}")
    print(f"Model: {MODEL_NAME}")
    print(f"Cost: 5 products × 3 shots = 15 images × $0.039 = $0.585\n")

    client = genai.Client(api_key=GEMINI_API_KEY)

    for idx, product in enumerate(TEST_PRODUCTS, 1):
        print(f"\n[{idx}/5] 🎩 {product['name']} (SKU: {product['sku']})")

        source_path = REPO_ROOT / product['folder'] / product['source_image']
        if not source_path.exists():
            print(f"      ❌ Source image not found: {source_path}")
            continue

        print(f"      ✓ Source: {source_path.name}")

        output_folder = source_path.parent

        # Generate Editorial (3:4)
        try:
            data = generate_shot(client, product['name'], source_path, "editorial")
            output_path = output_folder / f"{source_path.stem}_editorial_test.jpg"
            output_path.write_bytes(data)
            print(f"      ✓ Editorial saved: {output_path.name}")
        except Exception as e:
            print(f"      ❌ Editorial failed: {e}")

        # Generate Angle (1:1)
        try:
            data = generate_shot(client, product['name'], source_path, "angle")
            output_path = output_folder / f"{source_path.stem}_angle_test.jpg"
            output_path.write_bytes(data)
            print(f"      ✓ Angle saved: {output_path.name}")
        except Exception as e:
            print(f"      ❌ Angle failed: {e}")

        # Generate Lifestyle (16:9) - rotate scenarios
        scenario_key = list(LIFESTYLE_SCENARIOS.keys())[idx % 2]  # Alternate between eletrico and cafe
        try:
            data = generate_shot(client, product['name'], source_path, "lifestyle", scenario_key)
            output_path = output_folder / f"{source_path.stem}_lifestyle_{scenario_key}_test.jpg"
            output_path.write_bytes(data)
            print(f"      ✓ Lifestyle saved: {output_path.name}")
        except Exception as e:
            print(f"      ❌ Lifestyle failed: {e}")

    print("\n" + "=" * 70)
    print("TEST COMPLETED")
    print("=" * 70)
    print("\nPhotos saved in respective product folders. Review them at:")
    for product in TEST_PRODUCTS:
        folder = REPO_ROOT / product['folder']
        if folder.exists():
            print(f"  • {folder}")
    print("\n")

if __name__ == "__main__":
    main()
