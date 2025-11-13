#!/usr/bin/env python3
"""Generate 7 more products to reach 10 total for preview."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ Missing dependencies")
    sys.exit(1)

from PIL import Image

# 7 additional products
NEW_PRODUCTS = [
    {
        "name": "CHAPÉU IMPERMEÁVEL DOBRÁVEL",
        "sku": "chapeu-impermeavel-art-181054",
        "folder": "wordpress/wp-content/uploads/products/chapéus lã/chapeu-impermeavel-art-181054-pack-12-tags-fabricado-na-italia-la-esmagavel-impermeavel",
        "source_image": "img_01.jpg"
    },
    {
        "name": "GORRO MIKI DOCKER",
        "sku": "gorro-miki-12601",
        "folder": "wordpress/wp-content/uploads/products/cowboy/gorro-miki-12601-gorro-640182503",
        "source_image": "img_01.jpg"
    },
    {
        "name": "BONÉ COWBOY ESTILO AMERICANO",
        "sku": "bone-15125",
        "folder": "wordpress/wp-content/uploads/products/cowboy/bone-15125",
        "source_image": "img_01.jpg"
    },
    {
        "name": "CHAPÉU PALHA NATURAL",
        "sku": "palha-941216-couro",
        "folder": "wordpress/wp-content/uploads/products/palha/palha-941216-couro",
        "source_image": "img_01.jpg"
    },
    {
        "name": "LUVAS MASCULINAS EM PELE",
        "sku": "gants-17119",
        "folder": "wordpress/wp-content/uploads/products/artigos em pele/gants-17119",
        "source_image": "img_01.jpg"
    },
    {
        "name": "LUVAS FEMININAS EM PELE",
        "sku": "gants-17120",
        "folder": "wordpress/wp-content/uploads/products/artigos em pele/gants-17120",
        "source_image": "img_01.jpg"
    },
    {
        "name": "BOINA INVERNO HARRIS TWEED",
        "sku": "bone-18438mc-18502mi",
        "folder": "wordpress/wp-content/uploads/products/boinas inverno/bone-18438mc-18502mi",
        "source_image": "img_01.jpg"
    }
]

REPO_ROOT = Path(__file__).resolve().parents[1]
GEMINI_API_KEY = os.environ.get("GEMINI_KEY_PRIMARY", "AIzaSyDWCanKI3CtqyIWTOpaPVPVtmGOW6A7OaE")
MODEL_NAME = "gemini-2.5-flash-image"

SHOT_TYPES = {
    "editorial": {
        "aspect_ratio": "3:4",
        "prompt": """Take the {product_name} from the reference image and create a high-end
editorial portrait with a sophisticated Portuguese model wearing it, framed in
a vertical 3:4 aspect ratio (portrait orientation, 600×800px ideal). The model
looks directly at the camera with a confident, subtle smile. Style them with a
minimalist earth-tone blazer or fine knit that complements the item. Background:
soft-focus cream/ivory studio gradient. Lighting: soft window light from the
front-left creating gentle rim lighting so the product's silhouette, color and
texture remain accurate. Capture with an 85mm portrait lens at f/1.8 for shallow
depth of field. Composition: Center the model's face and product in the upper half
of the frame. Massimo Dutti / Chiado heritage aesthetic."""
    },
    "angle": {
        "aspect_ratio": "1:1",
        "prompt": """Transform the product into a 3/4 profile editorial shot in a perfect square 1:1
aspect ratio (800×800px). Place the model turning the head 30 degrees to the
right, eyes gazing off camera. Center the composition so the product and face are
perfectly balanced in the square frame. Emphasize the shape and detail through
sculpted studio lighting (key light at 45°). Add subtle hair or scarf movement
for dynamism. Neutral grey-blue background. Ensure the product keeps its authentic
texture. Square composition optimized for thumbnail display."""
    }
}

LIFESTYLE_SCENARIOS = {
    "miradouro": {
        "name": "Miradouro Panorâmico",
        "prompt": """Lisbon rooftop viewpoint scene in cinematic 16:9 widescreen format (1200×675px):
Model wearing the product standing at a miradouro (Santa Luzia or Graça), leaning on
traditional ornate iron railing with panoramic view of terracotta rooftops and
Tejo river in soft-focus background. Golden hour light, warm ochre tones.
Composition with model positioned in left third, vast cityscape breathing room
on right. Contemporary Portuguese style (linen blazer, relaxed elegance). Keep
product's authentic materials and palette. Rule of thirds, shallow depth of field,
35mm lens at f/2.8."""
    },
    "alfama": {
        "name": "Alfama Azulejos",
        "prompt": """Authentic Alfama narrow street in cinematic 16:9 widescreen (1200×675px): Model
walking past traditional Portuguese azulejo tile wall (blue and white geometric
patterns), weathered pastel buildings with wrought-iron balconies. Dappled
afternoon sunlight through laundry lines. Widescreen with model centered,
colorful tiles framing composition. Contemporary urban Portuguese wardrobe
(cotton shirt, tailored trousers). Preserve product's real texture and color. 35mm
street photography aesthetic, f/2.8."""
    },
    "tejo": {
        "name": "Tejo Riverside",
        "prompt": """Lisbon riverside promenade scene in cinematic 16:9 (1200×675px): Model strolling
along Cais do Sodré or Belém waterfront, Rio Tejo sparkling in background with
25 de Abril bridge softly visible. Late afternoon golden light reflecting on
water. Widescreen with model in right third, river expanse on left. Light linen
coat, modern Portuguese elegance. Wind gently moving fabric. Preserve product's
authentic materials. Widescreen travel photography style, 35mm lens at f/2.8."""
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
    print("GENERATING 7 MORE PRODUCTS (4-10)")
    print("=" * 70)
    print(f"Cost: 7 products × 3 shots = 21 images × $0.039 = $0.819\n")

    client = genai.Client(api_key=GEMINI_API_KEY)

    scenario_keys = list(LIFESTYLE_SCENARIOS.keys())

    for idx, product in enumerate(NEW_PRODUCTS, 4):  # Start from 4 (we have 3 already)
        print(f"\n[{idx}/10] 🎩 {product['name']} (SKU: {product['sku']})")

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

        # Generate Lifestyle (16:9) - rotate through 3 new scenarios
        scenario_key = scenario_keys[(idx - 4) % 3]  # Rotate miradouro, alfama, tejo
        try:
            data = generate_shot(client, product['name'], source_path, "lifestyle", scenario_key)
            output_path = output_folder / f"{source_path.stem}_lifestyle_{scenario_key}_test.jpg"
            output_path.write_bytes(data)
            print(f"      ✓ Lifestyle saved: {output_path.name}")
        except Exception as e:
            print(f"      ❌ Lifestyle failed: {e}")

    print("\n" + "=" * 70)
    print("7 MORE PRODUCTS COMPLETED")
    print("=" * 70)
    print("\nTotal: 10 products × 3 shots = 30 images")
    print("Total cost so far: $0.35 + $0.82 = $1.17 USD\n")

if __name__ == "__main__":
    main()
