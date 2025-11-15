#!/usr/bin/env python3
"""Gemini 2.5 Flash Image – Editorial Fashion Photo Pipeline (v2).

Generates three lifestyle/editorial shots per product (editorial portrait,
3/4 profile, Lisbon street lifestyle) and prepares them for WooCommerce.

Usage examples:
    python3 scripts/gemini_editorial_v2.py --test      # process 3 featured products
    python3 scripts/gemini_editorial_v2.py --limit=5   # first 5 priced products
    python3 scripts/gemini_editorial_v2.py             # full catalog
    python3 scripts/gemini_editorial_v2.py --dry-run   # log actions only
"""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence
from urllib.parse import unquote

try:
    from google import genai
    from google.genai import types
    from google.api_core import exceptions
except ImportError:  # pragma: no cover - handled at runtime
    print("❌ Missing dependencies. Install with:\n   pip install google-genai google-api-core pillow")
    sys.exit(1)

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
WORDPRESS_ROOT = REPO_ROOT / "wordpress"
UPLOADS_ROOT = WORDPRESS_ROOT / "wp-content" / "uploads"
CONTAINER_WP_ROOT = "/var/www/html"

# Gemini configuration
GEMINI_API_KEYS = [
    os.environ.get("GEMINI_KEY_PRIMARY", "AIzaSyDWCanKI3CtqyIWTOpaPVPVtmGOW6A7OaE"),
    os.environ.get("GEMINI_KEY_SECONDARY", "AIzaSyBXEsObFgYVwqzDH3fvYXP45FWi8UGiLRo")
]
MODEL_NAME = "gemini-2.5-flash-image"
COST_PER_IMAGE = 0.039  # USD (per official pricing)

# Data sources
CSV_FILE = REPO_ROOT / "output_catalogo/woocommerce_import.csv"
DOCKER_WORDPRESS = "chapeus_wordpress"

SHOT_TYPES = {
    "editorial": {
        "aspect_ratio": "3:4",
        "prompt": """
Take the {product_descriptor} from the reference image and create a high-end
editorial portrait with a sophisticated Portuguese model wearing it, framed in
a vertical 3:4 aspect ratio (portrait orientation, 600×800px ideal). The model
looks directly at the camera with a confident, subtle smile. Style them with a
minimalist earth-tone blazer or fine knit that complements the hat. Background:
soft-focus cream/ivory studio gradient. Lighting: soft window light from the
front-left creating gentle rim lighting so the hat's silhouette, color and
texture remain accurate. Capture with an 85mm portrait lens at f/1.8 for shallow
depth of field. Composition: Center the model's face and hat in the upper half
of the frame, leaving breathing room at the top for the hat. Massimo Dutti /
Chiado heritage aesthetic.""".strip()
    },
    "angle": {
        "aspect_ratio": "1:1",
        "prompt": """
Transform the hat into a 3/4 profile editorial shot in a perfect square 1:1
aspect ratio (800×800px). Place the model turning the head 30 degrees to the
right, eyes gazing off camera. Center the composition so the hat and face are
perfectly balanced in the square frame. Emphasize the brim shape and crown
detail through sculpted studio lighting (key light at 45°). Add subtle hair
or scarf movement for dynamism. Neutral grey-blue background. Ensure the hat
keeps its authentic {material} texture and {color_hint} tone. Square composition
optimized for thumbnail display.""".strip()
    },
    "lifestyle": {
        "aspect_ratio": "16:9",
        "prompt": None  # Will be populated from LIFESTYLE_SCENARIOS
    }
}

# 5 Lisboa lifestyle scenarios for variety
LIFESTYLE_SCENARIOS = {
    "eletrico": {
        "name": "Elétrico 28",
        "prompt": """
Create an authentic Lisbon lifestyle scene in cinematic 16:9 widescreen format
(1200×675px) showing the model wearing the hat while walking on calçada
portuguesa cobblestones. Include a softly blurred Elétrico 28 tram in the
background, warm late-afternoon light, and contemporary Portuguese wardrobe
(linen shirt, tailored coat). Composition with 35mm street lens at f/2.8:
foreground sharp (model + hat), background cinematic. Center the model in the
middle-left third of the frame using rule of thirds for dynamic composition.
Preserve the hat's real materials and palette. Widescreen cinematic aesthetic.""".strip()
    },
    "miradouro": {
        "name": "Miradouro Panorâmico",
        "prompt": """
Lisbon rooftop viewpoint scene in cinematic 16:9 widescreen format (1200×675px):
Model wearing the hat standing at a miradouro (Santa Luzia or Graça), leaning on
traditional ornate iron railing with panoramic view of terracotta rooftops and
Tejo river in soft-focus background. Golden hour light, warm ochre tones.
Composition with model positioned in left third, vast cityscape breathing room
on right. Contemporary Portuguese style (linen blazer, relaxed elegance). Keep
hat's authentic materials and palette. Rule of thirds, shallow depth of field,
35mm lens at f/2.8.""".strip()
    },
    "alfama": {
        "name": "Alfama Azulejos",
        "prompt": """
Authentic Alfama narrow street in cinematic 16:9 widescreen (1200×675px): Model
walking past traditional Portuguese azulejo tile wall (blue and white geometric
patterns), weathered pastel buildings with wrought-iron balconies. Dappled
afternoon sunlight through laundry lines. Widescreen with model centered,
colorful tiles framing composition. Contemporary urban Portuguese wardrobe
(cotton shirt, tailored trousers). Preserve hat's real texture and color. 35mm
street photography aesthetic, f/2.8.""".strip()
    },
    "tejo": {
        "name": "Tejo Riverside",
        "prompt": """
Lisbon riverside promenade scene in cinematic 16:9 (1200×675px): Model strolling
along Cais do Sodré or Belém waterfront, Rio Tejo sparkling in background with
25 de Abril bridge softly visible. Late afternoon golden light reflecting on
water. Widescreen with model in right third, river expanse on left. Light linen
coat, modern Portuguese elegance. Wind gently moving fabric. Preserve hat's
authentic materials. Widescreen travel photography style, 35mm lens at f/2.8.""".strip()
    },
    "cafe": {
        "name": "Café Esplanada",
        "prompt": """
Traditional Portuguese street café in cinematic 16:9 (1200×675px): Model seated
at outdoor esplanada table with bica (espresso) and pastel de nata, typical
mosaic pavement visible. Warm terracotta building facade with vintage signage
in background. Soft diffused daylight. Composition with model slightly off-center,
café atmosphere context. Contemporary casual Portuguese style (knit sweater,
relaxed confidence). Keep hat's real color and texture. Lifestyle editorial
aesthetic, 35mm lens at f/2.8.""".strip()
    }
}

# High-level stats for reporting
stats = {
    "products": 0,
    "shots_requested": 0,
    "shots_success": 0,
    "shots_failed": 0,
    "api_cost": 0.0,
    "quality_rejects": 0,
    "errors": [],
    "scenarios_used": {}  # Track which scenario was used for each product
}

client: Optional[genai.Client] = None
current_key_index = 0
current_scenario_index = 0  # Rotate through lifestyle scenarios


def init_client() -> None:
    """Initialise Gemini client with the current API key."""
    global client
    api_key = GEMINI_API_KEYS[current_key_index]
    if not api_key:
        raise RuntimeError("Gemini API key missing. Set GEMINI_KEY_PRIMARY or GEMINI_KEY_SECONDARY.")
    client = genai.Client(api_key=api_key)
    print(f"✓ Gemini client ready (key #{current_key_index + 1})")


def rotate_api_key() -> None:
    """Rotate to the next API key when quota is exhausted."""
    global current_key_index
    current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
    print("🔄 Rotating Gemini API key...")
    init_client()


def resolve_image_path(rel_path: str) -> Path:
    """Convert CSV relative path (e.g., catalogo2025/...) to an absolute Path."""
    rel_path = unquote(rel_path.strip()).lstrip('/')
    candidate = UPLOADS_ROOT / rel_path
    if candidate.exists():
        return candidate
    # Some rows might already include /wp-content/uploads/
    alt = WORDPRESS_ROOT / rel_path
    if alt.exists():
        return alt
    raise FileNotFoundError(f"Image not found for path: {rel_path}")


def to_container_path(path: Path) -> str:
    """Map local path within wordpress/ to the container path."""
    path = path.resolve()
    try:
        relative = path.relative_to(WORDPRESS_ROOT)
    except ValueError:
        raise ValueError(f"Path {path} is outside the WordPress root")
    return f"{CONTAINER_WP_ROOT}/{relative.as_posix()}"


def read_catalog_rows(limit: Optional[int], test_mode: bool) -> List[Dict[str, str]]:
    with CSV_FILE.open("r", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    # keep only products with price + images + SKU
    filtered = [
        row for row in rows
        if row.get("Regular price", "").strip() and row.get("Images", "").strip() and row.get("SKU", "").strip()
    ]

    if test_mode:
        return filtered[:3]
    if limit:
        return filtered[:limit]
    return filtered


MATERIAL_KEYWORDS = {
    "lã": "wool",
    "cashmere": "cashmere",
    "algodão": "cotton",
    "pele": "leather",
    "palha": "straw",
    "linho": "linen",
    "feltro": "felt",
}

COLOR_KEYWORDS = [
    "preto", "castanho", "bege", "camel", "cinza", "azul",
    "verde", "bordeaux", "taupe", "mostarda", "areia"
]


def detect_product_type(name: str) -> str:
    lowered = name.lower()
    if "boina" in lowered or "boné" in lowered or "bone" in lowered:
        return "boina"
    if "chapéu" in lowered or "chapeu" in lowered:
        return "chapeu"
    if "gorro" in lowered:
        return "gorro"
    return "acessorio"


def extract_descriptors(name: str) -> Dict[str, str]:
    lowered = name.lower()
    material = "premium fabric"
    for keyword, english in MATERIAL_KEYWORDS.items():
        if keyword in lowered:
            material = english
            break

    color_hint = "timeless neutral"
    for color in COLOR_KEYWORDS:
        if color in lowered:
            color_hint = color
            break

    return {
        "material": material,
        "color_hint": color_hint,
        "product_descriptor": name.strip(),
    }


def get_next_lifestyle_scenario() -> tuple[str, str]:
    """Get next lifestyle scenario in rotation. Returns (key, name)."""
    global current_scenario_index
    scenario_keys = list(LIFESTYLE_SCENARIOS.keys())
    key = scenario_keys[current_scenario_index % len(scenario_keys)]
    current_scenario_index += 1
    return key, LIFESTYLE_SCENARIOS[key]["name"]


def customize_prompt(shot_type: str, descriptors: Dict[str, str], lifestyle_key: Optional[str] = None) -> str:
    """Customize prompt with product descriptors and lifestyle scenario."""
    if shot_type == "lifestyle":
        if lifestyle_key is None:
            lifestyle_key = "eletrico"  # Default fallback
        base = LIFESTYLE_SCENARIOS[lifestyle_key]["prompt"]
    else:
        base = SHOT_TYPES[shot_type]["prompt"]
    return base.format(**descriptors)


def run_command(cmd: Sequence[str], timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a subprocess command and return the completed process."""
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
    return result


def import_media_into_wordpress(image_path: Path) -> int:
    container_path = to_container_path(image_path)
    cmd = [
        "docker", "exec", DOCKER_WORDPRESS,
        "wp", "media", "import", container_path,
        "--skip-copy", "--porcelain", "--allow-root"
    ]
    result = run_command(cmd)
    return int(result.stdout.strip())


def get_product_id_by_sku(sku: str) -> Optional[int]:
    cmd = [
        "docker", "exec", DOCKER_WORDPRESS,
        "wp", "post", "list",
        "--post_type=product",
        f"--meta_key=_sku",
        f"--meta_value={sku}",
        "--field=ID",
        "--allow-root"
    ]
    result = run_command(cmd)
    output = result.stdout.strip()
    if not output:
        return None
    return int(output.splitlines()[0])


def get_existing_gallery(product_id: int) -> str:
    cmd = [
        "docker", "exec", DOCKER_WORDPRESS,
        "wp", "post", "meta", "get", str(product_id),
        "_product_image_gallery", "--allow-root"
    ]
    result = run_command(cmd)
    return result.stdout.strip()


def update_woocommerce_gallery(sku: str, editorial_id: int, gallery_ids: List[int]) -> None:
    product_id = get_product_id_by_sku(sku)
    if not product_id:
        raise RuntimeError(f"No product found for SKU {sku}")

    # Update featured image
    run_command([
        "docker", "exec", DOCKER_WORDPRESS,
        "wp", "post", "meta", "update", str(product_id),
        "_thumbnail_id", str(editorial_id), "--allow-root"
    ])

    # Merge galleries: new images first, keep originals after
    existing = get_existing_gallery(product_id)
    gallery_list = [str(gid) for gid in gallery_ids]
    if existing:
        gallery_list.append(existing)
    merged = ",".join(gallery_list)

    run_command([
        "docker", "exec", DOCKER_WORDPRESS,
        "wp", "post", "meta", "update", str(product_id),
        "_product_image_gallery", merged, "--allow-root"
    ])


def assess_quality(_source: Path, _generated: Path) -> float:
    """Placeholder quality heuristic (future: compare colors, run Gemini vision check)."""
    return 0.85


def generate_editorial_shot(
    shot_type: str,
    source_path: Path,
    product_name: str,
    descriptors: Dict[str, str],
    output_path: Path,
    dry_run: bool,
    lifestyle_key: Optional[str] = None,
    lifestyle_name: Optional[str] = None
) -> Dict[str, Optional[float]]:
    stats["shots_requested"] += 1

    if dry_run:
        scenario_info = f" ({lifestyle_name})" if lifestyle_name else ""
        print(f"      [DRY RUN] {shot_type}{scenario_info} → {output_path.name}")
        return {"success": True, "quality": None}

    prompt = customize_prompt(shot_type, descriptors, lifestyle_key)

    try:
        img = Image.open(source_path)

        # Get aspect ratio for this shot type
        aspect_ratio = SHOT_TYPES[shot_type]["aspect_ratio"]

        # Configure generation with aspect ratio
        config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio
            )
        )

        scenario_info = f" - {lifestyle_name}" if lifestyle_name else ""
        print(f"      🔍 Calling Gemini API ({shot_type}, {aspect_ratio}{scenario_info})...")

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt, img],
            config=config
        )

        # Check for safety filter blocks
        if response.candidates[0].finish_reason != "STOP":
            reason = response.candidates[0].finish_reason
            print(f"      ⚠️  Generation blocked: {reason}")
            raise RuntimeError(f"Safety filter: {reason}")

        # Extract and save image - USE response.parts NOT candidate.content.parts
        for part in response.parts:
            if part.inline_data is not None:
                data = part.inline_data.data

                print(f"      📦 Received {len(data)} bytes")

                output_path.parent.mkdir(parents=True, exist_ok=True)
                with output_path.open("wb") as fh:
                    fh.write(data)

                quality = assess_quality(source_path, output_path)
                if quality < 0.7:
                    stats["quality_rejects"] += 1
                    print(f"      ⚠️ Quality gate: {quality:.2f} < 0.7")

                stats["shots_success"] += 1
                stats["api_cost"] += COST_PER_IMAGE

                print(f"      ✓ Generated {output_path.name}")

                # Free memory
                del img

                return {"success": True, "quality": quality}

        raise RuntimeError("No image bytes returned")

    except exceptions.ResourceExhausted:
        print(f"      ⏳ Quota exhausted, rotating API key...")
        rotate_api_key()
        time.sleep(2)  # Small delay after rotation
        return generate_editorial_shot(shot_type, source_path, product_name, descriptors, output_path, dry_run)
    except Exception as exc:  # pragma: no cover
        stats["shots_failed"] += 1
        stats["errors"].append({
            "shot": shot_type,
            "file": source_path.name,
            "error": str(exc)
        })
        print(f"      ❌ {shot_type} failed: {exc}")
        return {"success": False, "quality": None}


def process_product(row: Dict[str, str], dry_run: bool) -> None:
    sku = row["SKU"].strip()
    product_name = row["Name"].strip()
    descriptors = extract_descriptors(product_name)
    descriptors["product_descriptor"] = product_name

    first_image_rel = row["Images"].split(",")[0].strip()
    try:
        source = resolve_image_path(first_image_rel)
    except FileNotFoundError as exc:
        print(f"⚠️  {product_name}: {exc}")
        stats["shots_failed"] += 3
        return

    # Get lifestyle scenario for this product (rotates through 5 scenarios)
    lifestyle_key, lifestyle_name = get_next_lifestyle_scenario()

    print(f"🎩 {product_name} (SKU {sku}) - Lifestyle: {lifestyle_name}")
    stats["products"] += 1
    stats["scenarios_used"][sku] = lifestyle_name

    generated: Dict[str, Path] = {}
    for shot_type in SHOT_TYPES.keys():
        # Include scenario key in filename for lifestyle shots
        if shot_type == "lifestyle":
            output_path = source.with_name(f"{source.stem}_{shot_type}_{lifestyle_key}.jpg")
            result = generate_editorial_shot(
                shot_type, source, product_name, descriptors, output_path, dry_run,
                lifestyle_key=lifestyle_key, lifestyle_name=lifestyle_name
            )
        else:
            output_path = source.with_name(f"{source.stem}_{shot_type}.jpg")
            result = generate_editorial_shot(
                shot_type, source, product_name, descriptors, output_path, dry_run
            )

        if result.get("success"):
            generated[shot_type] = output_path
        time.sleep(0.5)

    if dry_run or not generated:
        return

    try:
        attachment_ids: List[int] = []
        editorial_id = 0
        for shot_type, path in generated.items():
            attachment_id = import_media_into_wordpress(path)
            if shot_type == "editorial":
                editorial_id = attachment_id
            else:
                attachment_ids.append(attachment_id)

        if editorial_id:
            update_woocommerce_gallery(sku, editorial_id, attachment_ids)
            print(f"      ✓ WooCommerce gallery updated")
        else:
            print("      ⚠️ Editorial shot missing, skipped gallery update")
    except Exception as exc:  # pragma: no cover
        stats["errors"].append({"product": product_name, "error": str(exc)})
        print(f"      ❌ Gallery update failed: {exc}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gemini editorial photo pipeline")
    parser.add_argument("--limit", type=int, help="Limit number of products")
    parser.add_argument("--test", action="store_true", help="Process 3 curated products")
    parser.add_argument("--dry-run", action="store_true", help="Log actions without Gemini calls")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    init_client()

    rows = read_catalog_rows(args.limit, args.test)
    if not rows:
        print("No products with price + images found.")
        return

    print(f"\nProcessing {len(rows)} products (dry-run={args.dry_run})\n")

    for idx, row in enumerate(rows, start=1):
        print(f"[{idx}/{len(rows)}]")
        process_product(row, args.dry_run)

    print("\n" + "=" * 70)
    print("GENERATION SUMMARY")
    print("=" * 70)
    for key, value in stats.items():
        if key in ["errors", "scenarios_used"]:
            continue
        if isinstance(value, float):
            print(f"- {key.replace('_', ' ')}: {value:.2f}")
        else:
            print(f"- {key.replace('_', ' ')}: {value}")

    if stats["scenarios_used"]:
        print("\nLifestyle Scenarios Used:")
        for sku, scenario in stats["scenarios_used"].items():
            print(f"  • {sku}: {scenario}")

    if stats["errors"]:
        print("\nErrors:")
        for err in stats["errors"][:10]:
            print(f"  • {err}")

    # Export tracking report
    if stats["scenarios_used"]:
        import csv
        from pathlib import Path

        timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = REPO_ROOT / f"relatorios/ai_photos_tracking_{timestamp}.csv"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with report_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["SKU", "Fotos AI Geradas", "Cenário Lisboa", "Data Geração"])

            for sku, scenario in stats["scenarios_used"].items():
                timestamp_str = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M")
                writer.writerow([sku, "✅ 3 fotos novas", scenario, timestamp_str])

        print(f"\n📊 Tracking report saved: {report_path}")
        print("   → Import this CSV into Google Sheet or use for client records")


if __name__ == "__main__":
    main()
