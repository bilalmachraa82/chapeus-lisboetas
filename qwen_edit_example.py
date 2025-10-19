#!/usr/bin/env python3
"""
Qwen-Image-Edit-2509 - Exemplo Edição Local (Mac M4)

Requisitos:
- Python 3.11+
- PyTorch 2.5+ com MPS
- Diffusers, Transformers, etc
- 16GB RAM (M4)

Uso:
    python3 qwen_edit_example.py
"""

import torch
from diffusers import AutoPipelineForImage2Image
from PIL import Image
import os
from pathlib import Path

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

# Input/Output
INPUT_IMAGE = "input.png"  # Sua imagem original
OUTPUT_DIR = "output_qwen"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Prompt de edição
EDIT_PROMPT = """
Extract hat/accessory from the image, isolate on white background, 
professional product photography, studio lighting, maintain product identity and colors,
e-commerce ready, high quality
"""

# Configurações de performance para Mac M4
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
DTYPE = torch.float16 if DEVICE == "mps" else torch.float32

print("=" * 70)
print("🍎 Qwen-Image-Edit-2509 - Mac M4 (Apple Silicon)")
print("=" * 70)
print(f"Device: {DEVICE}")
print(f"Dtype: {DTYPE}")
print()

# ============================================================================
# CARREGAR MODELO
# ============================================================================

print("📥 Carregando modelo Qwen-Image-Edit-2509...")
print("   (Primeira vez: download ~8GB, pode demorar 10-30 min)")
print()

try:
    pipe = AutoPipelineForImage2Image.from_pretrained(
        "Qwen/Qwen-Image-Edit-2509",
        torch_dtype=DTYPE,
        use_safetensors=True,
        low_cpu_mem_usage=True,
    )
    
    # Mover para MPS (GPU Apple Silicon)
    pipe = pipe.to(DEVICE)
    
    # Otimizações para M4 (16GB RAM)
    pipe.enable_attention_slicing()  # Reduz uso de memória
    
    print("✅ Modelo carregado com sucesso!")
    print()

except Exception as e:
    print(f"❌ Erro ao carregar modelo: {e}")
    print()
    print("💡 Troubleshooting:")
    print("   1. Verificar que fez login: huggingface-cli login")
    print("   2. Aceitar licença: https://huggingface.co/Qwen/Qwen-Image-Edit-2509")
    print("   3. Verificar espaço em disco (>20GB)")
    print("   4. Reinstalar PyTorch para ARM64")
    exit(1)

# ============================================================================
# CARREGAR IMAGEM
# ============================================================================

print(f"📸 Carregando imagem: {INPUT_IMAGE}")

if not os.path.exists(INPUT_IMAGE):
    print(f"❌ Erro: {INPUT_IMAGE} não encontrado!")
    print()
    print("💡 Criar imagem de teste:")
    print(f"   Coloque uma foto com chapéu em: {INPUT_IMAGE}")
    exit(1)

try:
    image = Image.open(INPUT_IMAGE).convert("RGB")
    print(f"   Tamanho original: {image.size}")
    
    # Redimensionar se muito grande (economiza RAM)
    max_size = 1024
    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size), Image.LANCZOS)
        print(f"   Redimensionado para: {image.size}")
    
    print("✅ Imagem carregada!")
    print()

except Exception as e:
    print(f"❌ Erro ao carregar imagem: {e}")
    exit(1)

# ============================================================================
# GERAR EDIÇÃO
# ============================================================================

print("🎨 Gerando edição...")
print(f"   Prompt: {EDIT_PROMPT[:100]}...")
print()

try:
    # Gerar 4 variações
    num_images = 4
    
    for i in range(num_images):
        print(f"   Gerando variação {i+1}/{num_images}...")
        
        # Inferência
        with torch.no_grad():
            result = pipe(
                prompt=EDIT_PROMPT,
                image=image,
                num_inference_steps=25,  # Reduzir para 15-20 se muito lento
                guidance_scale=7.5,
                num_images_per_prompt=1
            ).images[0]
        
        # Salvar
        output_path = Path(OUTPUT_DIR) / f"edited_{i+1}.png"
        result.save(output_path)
        print(f"   ✅ Salvo: {output_path}")
    
    print()
    print("=" * 70)
    print("🎉 SUCESSO! Edições geradas!")
    print("=" * 70)
    print(f"📁 Output: {OUTPUT_DIR}/")
    print(f"   • edited_1.png")
    print(f"   • edited_2.png")
    print(f"   • edited_3.png")
    print(f"   • edited_4.png")
    print()

except Exception as e:
    print(f"❌ Erro durante inferência: {e}")
    print()
    print("💡 Troubleshooting:")
    print("   1. Reduzir num_inference_steps para 15")
    print("   2. Usar imagem menor (<1024px)")
    print("   3. Gerar apenas 1 imagem por vez")
    print("   4. Fechar outros apps (liberar RAM)")
    exit(1)
