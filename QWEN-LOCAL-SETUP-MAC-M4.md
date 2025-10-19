# 🍎 Qwen-Image-Edit-2509 - Setup Completo Mac M4 (Apple Silicon)

**Guia completo para rodar Qwen-Image-Edit localmente no Mac M4 (16GB RAM)**

---

## 📋 **PRÉ-REQUISITOS**

### **Seu Sistema:**
- ✅ Mac M4 (Apple Silicon ARM64)
- ✅ 16GB RAM
- ✅ macOS 14+ (Sonoma ou superior recomendado)
- ⚠️ **Espaço em disco:** Mínimo 20GB livres (modelo ~8GB + dependências)

---

## 🔧 **PASSO 1: Preparar Ambiente Python**

### **Opção A: Usar Homebrew (Recomendado para M4)**

```bash
# 1.1 Instalar Homebrew (se ainda não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 1.2 Instalar Python 3.11 (melhor compatibilidade com ARM64)
brew install python@3.11

# 1.3 Verificar instalação
python3.11 --version
# Deve mostrar: Python 3.11.x

# 1.4 Criar virtual environment
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"
python3.11 -m venv venv-qwen
source venv-qwen/bin/activate

# 1.5 Upgrade pip
pip install --upgrade pip setuptools wheel
```

### **Opção B: Usar Conda (Alternativa, mais estável)**

```bash
# 1.1 Instalar Miniforge (Conda para ARM64)
brew install miniforge

# 1.2 Criar environment
conda create -n qwen python=3.11 -y
conda activate qwen

# 1.3 Verificar
which python
# Deve mostrar: /opt/homebrew/Caskroom/miniforge/...
```

---

## 🎯 **PASSO 2: Instalar PyTorch para Apple Silicon**

### **CRÍTICO: Usar build oficial ARM64 do PyTorch**

```bash
# 2.1 ATIVAR environment primeiro!
source venv-qwen/bin/activate
# OU se usando conda: conda activate qwen

# 2.2 Instalar PyTorch 2.5+ com Metal Performance Shaders (MPS)
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 2.3 Verificar instalação MPS
python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'MPS available: {torch.backends.mps.is_available()}')
print(f'MPS built: {torch.backends.mps.is_built()}')
"

# Deve mostrar:
# PyTorch version: 2.5.x
# MPS available: True  ✅
# MPS built: True  ✅
```

**⚠️ TROUBLESHOOTING PyTorch:**
```bash
# Se MPS não estiver disponível, reinstalar:
pip3 uninstall torch torchvision torchaudio -y
pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu

# Ou forçar CPU-only (mais lento mas funciona sempre):
pip3 install torch torchvision torchaudio
```

---

## 📦 **PASSO 3: Instalar Hugging Face Diffusers + Dependências**

```bash
# 3.1 Instalar libs principais
pip3 install diffusers transformers accelerate

# 3.2 Instalar libs de imagem
pip3 install pillow opencv-python

# 3.3 Instalar Hugging Face Hub (para download do modelo)
pip3 install huggingface_hub

# 3.4 Instalar outras dependências
pip3 install safetensors sentencepiece protobuf

# 3.5 OPCIONAL: Instalar gradio para UI interativa
pip3 install gradio

# 3.6 Verificar tudo instalado
pip3 list | grep -E "(torch|diffusers|transformers|accelerate|pillow)"
```

### **Requirements.txt completo (para referência):**

```txt
# requirements-qwen-local.txt
torch>=2.5.0
torchvision>=0.20.0
torchaudio>=2.5.0
diffusers>=0.30.0
transformers>=4.45.0
accelerate>=0.34.0
pillow>=10.0.0
opencv-python>=4.9.0
huggingface_hub>=0.25.0
safetensors>=0.4.0
sentencepiece>=0.2.0
protobuf>=4.25.0
gradio>=4.0.0  # opcional
```

Instalar tudo de uma vez:
```bash
pip3 install -r requirements-qwen-local.txt
```

---

## 🔐 **PASSO 4: Login Hugging Face (NECESSÁRIO)**

### **O modelo Qwen-Image-Edit-2509 requer aceitar licença!**

```bash
# 4.1 Criar conta Hugging Face (se não tiver)
# Ir para: https://huggingface.co/join

# 4.2 Aceitar licença do modelo
# Ir para: https://huggingface.co/Qwen/Qwen-Image-Edit-2509
# Clicar em "Agree and access repository"

# 4.3 Gerar Access Token
# Ir para: https://huggingface.co/settings/tokens
# Criar token com permissão "read"

# 4.4 Login via CLI
huggingface-cli login

# Cole o token quando pedido
# Token: hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Alternativa: Login via Python:**
```python
from huggingface_hub import login
login(token="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
```

---

## 💾 **PASSO 5: Download do Modelo (Manual + Otimizado)**

### **IMPORTANTE: Modelo tem ~8GB, pode demorar!**

```bash
# 5.1 Criar pasta para cache local
mkdir -p ~/huggingface_models
export HF_HOME=~/huggingface_models

# 5.2 Download do modelo (opção 1: automático)
python3 -c "
from diffusers import AutoPipelineForImage2Image
import torch

print('📥 Downloading Qwen-Image-Edit-2509...')
print('⚠️  Isto pode demorar 10-30 min (8GB)...')

# Baixar modelo
pipe = AutoPipelineForImage2Image.from_pretrained(
    'Qwen/Qwen-Image-Edit-2509',
    torch_dtype=torch.float16,  # Economiza RAM
    use_safetensors=True,
    low_cpu_mem_usage=True
)

print('✅ Modelo baixado com sucesso!')
print(f'📁 Localização: {pipe.config._name_or_path}')
"

# 5.3 OU download manual via git-lfs
# brew install git-lfs
# git lfs install
# git clone https://huggingface.co/Qwen/Qwen-Image-Edit-2509 ~/huggingface_models/Qwen-Image-Edit-2509
```

---

## 🚀 **PASSO 6: Código Python - Exemplo Básico**

### **`qwen_edit_example.py` - Script Completo**

```python
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
print(f"RAM disponível: {os.popen('sysctl hw.memsize').read().split()[1]} bytes")
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

# ============================================================================
# BATCH PROCESSING (OPCIONAL)
# ============================================================================

def process_batch(input_folder, output_folder, prompt):
    """
    Processar múltiplas imagens em batch
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)
    
    images = list(input_path.glob("*.jpg")) + list(input_path.glob("*.png"))
    
    print(f"📦 Processando {len(images)} imagens...")
    
    for idx, img_path in enumerate(images):
        print(f"\n[{idx+1}/{len(images)}] Processando: {img_path.name}")
        
        try:
            img = Image.open(img_path).convert("RGB")
            img.thumbnail((1024, 1024), Image.LANCZOS)
            
            with torch.no_grad():
                result = pipe(
                    prompt=prompt,
                    image=img,
                    num_inference_steps=20,
                    guidance_scale=7.5,
                    num_images_per_prompt=1
                ).images[0]
            
            out_path = output_path / f"{img_path.stem}_edited.png"
            result.save(out_path)
            print(f"✅ Salvo: {out_path.name}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            continue

# Descomentar para usar batch processing:
# process_batch("instagram_catalog/raw_photos", "output_qwen_batch", EDIT_PROMPT)
```

---

## 🎯 **PASSO 7: Rodar o Exemplo**

```bash
# 7.1 Preparar imagem de teste
# Copiar uma das fotos Instagram:
cp instagram_catalog/raw_photos/chapeuslisboetas_DNyTzUT2gf7.jpg input.png

# 7.2 Rodar script
python3 qwen_edit_example.py

# 7.3 Ver resultados
ls -lh output_qwen/
open output_qwen/  # Abre pasta no Finder
```

---

## ⚡ **OTIMIZAÇÕES PARA MAC M4 (16GB RAM)**

### **1. Reduzir uso de memória:**

```python
# Usar float16 (metade da RAM)
pipe = pipe.to("mps", dtype=torch.float16)

# Attention slicing (reduz picos de memória)
pipe.enable_attention_slicing()

# Model CPU offloading (se ficar sem RAM)
pipe.enable_model_cpu_offload()

# Sequential CPU offload (mais lento mas usa menos RAM)
pipe.enable_sequential_cpu_offload()
```

### **2. Acelerar inferência:**

```python
# Reduzir steps (qualidade vs velocidade)
num_inference_steps=15  # Rápido mas ok
num_inference_steps=25  # Balanceado (recomendado)
num_inference_steps=50  # Lento mas melhor qualidade

# Usar scheduler mais rápido
from diffusers import DPMSolverMultistepScheduler
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
```

### **3. Processar em batch com sleep:**

```python
import time

for i, image in enumerate(batch_images):
    result = pipe(prompt=prompt, image=image)
    result.save(f"output_{i}.png")
    
    # Dar tempo ao sistema para liberar RAM
    if (i + 1) % 10 == 0:
        time.sleep(5)
```

---

## 🐛 **TROUBLESHOOTING - Problemas Comuns**

### **Erro: "MPS backend not available"**
```bash
# Verificar macOS version
sw_vers

# Atualizar para Sonoma 14+ ou usar CPU
PYTORCH_ENABLE_MPS_FALLBACK=1 python3 qwen_edit_example.py
```

### **Erro: "Out of memory"**
```python
# Adicionar ao script:
pipe.enable_sequential_cpu_offload()
pipe.enable_attention_slicing(1)  # slice_size=1 = mínimo RAM

# Ou processar imagens menores:
image.thumbnail((768, 768), Image.LANCZOS)
```

### **Erro: "Repository not found"**
```bash
# Fazer login novamente
huggingface-cli logout
huggingface-cli login

# Verificar que aceitou licença:
# https://huggingface.co/Qwen/Qwen-Image-Edit-2509
```

### **Modelo baixa mas inferência trava**
```bash
# Limpar cache e tentar novamente
rm -rf ~/.cache/huggingface/
pip3 uninstall diffusers -y
pip3 install diffusers --no-cache-dir

# Ou forçar CPU mode:
python3 -c "
import torch
pipe = pipe.to('cpu')  # Lento mas funciona
"
```

### **Erro: "illegal hardware instruction"**
```bash
# PyTorch não compilado para ARM64
pip3 uninstall torch torchvision torchaudio -y
pip3 install torch torchvision torchaudio

# Verificar:
python3 -c "import torch; print(torch.__version__)"
file $(python3 -c "import torch; print(torch.__file__)")
# Deve mostrar: "arm64"
```

---

## 📊 **PERFORMANCE ESPERADA (Mac M4 16GB)**

| Configuração | Tempo/Imagem | RAM Usada | Qualidade |
|--------------|--------------|-----------|-----------|
| Steps=15, 512px | ~15-25 seg | ~4-6 GB | Boa |
| Steps=25, 768px | ~30-45 seg | ~6-8 GB | Muito Boa |
| Steps=25, 1024px | ~45-70 seg | ~8-12 GB | Excelente |
| Steps=50, 1024px | ~90-120 seg | ~10-14 GB | Máxima |

**Recomendação para 372 fotos:**
- Steps=20, 768px
- Batch de 10 em 10
- Tempo total: ~3-4 horas
- **100% GRÁTIS!** 🎉

---

## 🎁 **SCRIPT COMPLETO PARA BATCH (372 FOTOS)**

### **`batch_process_qwen.py`**

```python
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

print("🚀 Carregando modelo...")
pipe = AutoPipelineForImage2Image.from_pretrained(
    "Qwen/Qwen-Image-Edit-2509",
    torch_dtype=DTYPE,
    use_safetensors=True,
    low_cpu_mem_usage=True
).to(DEVICE)

pipe.enable_attention_slicing()

# Obter todas as imagens
images = sorted(list(INPUT_DIR.glob("*.jpg")) + list(INPUT_DIR.glob("*.png")))
print(f"📸 Encontradas {len(images)} imagens")
print()

# Processar
results = []
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
        
        # Sleep a cada 10 imagens
        if (idx + 1) % 10 == 0:
            time.sleep(3)
    
    except Exception as e:
        tqdm.write(f"❌ Erro em {img_path.name}: {e}")
        continue

# Save metadata
with open(OUTPUT_DIR / "metadata.json", "w") as f:
    json.dump(results, f, indent=2)

print()
print(f"✅ Processadas {len(results)//4} imagens")
print(f"📁 Output: {OUTPUT_DIR}/")
```

Rodar:
```bash
python3 batch_process_qwen.py
```

---

## 📚 **LINKS ÚTEIS**

- **Modelo Qwen:** https://huggingface.co/Qwen/Qwen-Image-Edit-2509
- **Diffusers Docs:** https://huggingface.co/docs/diffusers
- **PyTorch Mac:** https://pytorch.org/get-started/locally/
- **Metal Performance Shaders:** https://developer.apple.com/metal/pytorch/

---

## ✅ **CHECKLIST FINAL**

- [ ] Python 3.11 instalado via Homebrew
- [ ] Virtual environment criado e ativado
- [ ] PyTorch 2.5+ com MPS instalado
- [ ] Diffusers + Transformers instalados
- [ ] Login Hugging Face feito
- [ ] Licença Qwen aceita
- [ ] Modelo baixado (~8GB)
- [ ] Script de exemplo funcionando
- [ ] Batch processing testado

---

🎉 **PRONTO! Qwen-Image-Edit rodando 100% LOCAL e GRÁTIS no seu Mac M4!**
