#!/usr/bin/env python3
"""
Batch processing Qwen-Image-Edit para 372 fotos Instagram
Otimizado para Mac M4 (16GB RAM)
"""

import torch
from diffusers import AutoPipelineForImage2Image
from PIL import Image
from pathlib import Path
import time
from tqdm import tqdm
import json

# Configuração
INPUT_DIR = Path("instagram_catalog/raw_photos")
OUTPUT_DIR = Path("output_qwen_batch")
OUTPUT_DIR.mkdir(exist_ok=True)

PROMPT = """
Professional e-commerce product photo: extract hat/accessory, 
white background, studio lighting, maintain product identity and colors,
remove person if present, focus on product only, high quality
"""

# Setup device
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
DTYPE = torch.float16 if DEVICE == "mps" else torch.float32

print("=" * 70)
print("🚀 Batch Processing - Qwen-Image-Edit (Mac M4)")
print("=" * 70)
print(f"Device: {DEVICE}")
print(f"Input: {INPUT_DIR}")
print(f"Output: {OUTPUT_DIR}")
print()

print("🚀 Carregando modelo...")
pipe = AutoPipelineForImage2Image.from_pretrained(
    "Qwen/Qwen-Image-Edit-2509",
    torch_dtype=DTYPE,
    use_safetensors=True,
    low_cpu_mem_usage=True
).to(DEVICE)

pipe.enable_attention_slicing()
print("✅ Modelo carregado!")
print()

# Obter todas as imagens
images = sorted(list(INPUT_DIR.glob("*.jpg")) + list(INPUT_DIR.glob("*.png")))
print(f"📸 Encontradas {len(images)} imagens")
print()

# Processar
results = []
start_time = time.time()

for idx, img_path in enumerate(tqdm(images, desc="Processing")):
    try:
        # Load
        img = Image.open(img_path).convert("RGB")
        img.thumbnail((768, 768), Image.LANCZOS)
        
        # Generate 4 variations
        for var_idx in range(4):
            with torch.no_grad():
                result = pipe(
                    prompt=PROMPT,
                    image=img,
                    num_inference_steps=20,
                    guidance_scale=7.5,
                    num_images_per_prompt=1
                ).images[0]
            
            # Save
            out_name = f"{img_path.stem}_var{var_idx+1}.png"
            out_path = OUTPUT_DIR / out_name
            result.save(out_path)
            
            results.append({
                "original": str(img_path),
                "output": str(out_path),
                "variation": var_idx + 1
            })
        
        # Sleep a cada 10 imagens (liberar RAM)
        if (idx + 1) % 10 == 0:
            time.sleep(3)
            tqdm.write(f"   💤 Checkpoint {idx+1}/{len(images)} - RAM liberada")
    
    except Exception as e:
        tqdm.write(f"❌ Erro em {img_path.name}: {e}")
        continue

elapsed = time.time() - start_time

# Save metadata
with open(OUTPUT_DIR / "metadata.json", "w") as f:
    json.dump({
        "total_images": len(images),
        "total_variations": len(results),
        "processing_time_seconds": elapsed,
        "results": results
    }, f, indent=2)

print()
print("=" * 70)
print("✅ BATCH PROCESSING COMPLETO!")
print("=" * 70)
print(f"📊 Estatísticas:")
print(f"   • Imagens processadas: {len(results)//4}")
print(f"   • Variações geradas: {len(results)}")
print(f"   • Tempo total: {int(elapsed//60)} min {int(elapsed%60)} seg")
print(f"   • Média: {elapsed/len(results):.1f} seg/imagem")
print()
print(f"📁 Output: {OUTPUT_DIR}/")
print(f"💾 Metadata: {OUTPUT_DIR}/metadata.json")
print()
