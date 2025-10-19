#!/usr/bin/env python3
"""
Classificar TODAS as fotos das novas pastas
Usar Gemini Vision para classificação automática
"""

import os
import json
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
import time

# Load environment
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Paths
BASE_DIR = Path("processed_images/professional")
OUTPUT_FILE = Path("catalog_completo_classificado.json")

# Categories
CATEGORIES = {
    "genero": ["homem", "mulher", "crianca", "unisex"],
    "tipo": ["boina", "chapeu-fedora", "chapeu-panama", "bone", "cartola", 
             "gorro", "bucket-hat", "capeline", "trilby", "outros"],
    "estilo": ["classico", "casual", "formal", "desportivo", "vintage", "moderno"],
    "cor": ["preto", "branco", "castanho", "azul", "cinza", "bege", 
            "bordeaux", "verde", "caramelo", "outros"],
    "material": ["la", "algodao", "palha", "pele", "sintetico", "linho", "outros"]
}


def classify_image(image_path: Path) -> dict:
    """
    Classificar imagem com Gemini Vision
    """
    prompt = """
Analisa esta foto de chapéu/acessório e classifica PRECISAMENTE.

Retorna APENAS JSON válido (sem markdown, sem ```):
{
    "genero": "homem|mulher|crianca|unisex",
    "tipo": "boina|chapeu-fedora|chapeu-panama|bone|cartola|gorro|bucket-hat|capeline|trilby|outros",
    "estilo": "classico|casual|formal|desportivo|vintage|moderno",
    "cor_principal": "preto|branco|castanho|azul|cinza|bege|bordeaux|verde|caramelo|outros",
    "cor_secundaria": "preto|branco|castanho|azul|cinza|bege|bordeaux|verde|caramelo|outros|nenhuma",
    "material_aparente": "la|algodao|palha|pele|sintetico|linho|outros",
    "nome_produto": "Nome comercial curto (max 50 chars)",
    "descricao_curta": "Descrição SEO-friendly em PT (max 100 chars)",
    "descricao_longa": "Descrição detalhada para e-commerce (max 300 chars)",
    "tags": ["tag1", "tag2", "tag3", "tag4"],
    "preco_sugerido_eur": 35-85,
    "stock_sugerido": 5-20,
    "temporada": "verao|inverno|meia-estacao|todas",
    "qualidade_foto": "alta|media|baixa",
    "adequado_ecommerce": true|false,
    "background_limpo": true|false,
    "produto_centrado": true|false
}

IMPORTANTE: Retorna SÓ o JSON, sem texto adicional!
"""
    
    try:
        # Load image
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Classify
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content([
            prompt,
            {'mime_type': 'image/jpeg', 'data': image_data}
        ])
        
        # Parse JSON
        response_text = response.text.strip()
        
        # Remove markdown if present
        if '```' in response_text:
            parts = response_text.split('```')
            if len(parts) >= 2:
                response_text = parts[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
        
        classification = json.loads(response_text.strip())
        return classification
    
    except Exception as e:
        print(f"      ⚠️  Error: {e}")
        return None


def scan_folders(base_path: Path) -> list:
    """
    Encontrar todas as imagens em subpastas
    """
    extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    images = []
    
    for ext in extensions:
        images.extend(base_path.rglob(f"*{ext}"))
        images.extend(base_path.rglob(f"*{ext.upper()}"))
    
    return sorted(images)


def main():
    print("=" * 70)
    print("🎯 Classificação Automática - Novas Fotos Profissionais")
    print("=" * 70)
    print()
    
    # Scan folders
    print("📂 Scanning folders...")
    images = scan_folders(BASE_DIR)
    
    print(f"✅ Found {len(images)} images")
    print()
    
    # Group by folder
    folders = {}
    for img in images:
        folder = img.parent.name
        if folder not in folders:
            folders[folder] = []
        folders[folder].append(img)
    
    print("📊 Distribution:")
    for folder, imgs in sorted(folders.items()):
        print(f"   • {folder}: {len(imgs)} images")
    print()
    
    # Classify all
    print("🤖 Classifying with Gemini Vision...")
    print()
    
    results = []
    start_time = time.time()
    
    for idx, img_path in enumerate(tqdm(images, desc="Classifying")):
        try:
            # Classify
            classification = classify_image(img_path)
            
            if classification:
                result = {
                    "file_path": str(img_path),
                    "file_name": img_path.name,
                    "folder": img_path.parent.name,
                    "relative_path": str(img_path.relative_to(BASE_DIR)),
                    "classification": classification,
                    "index": idx
                }
                results.append(result)
                
                # Show summary
                tqdm.write(f"   ✅ [{idx+1}/{len(images)}] {img_path.name}")
                tqdm.write(f"      → {classification.get('nome_produto', 'N/A')}")
                tqdm.write(f"      → {classification.get('genero', 'N/A')} / {classification.get('tipo', 'N/A')} / €{classification.get('preco_sugerido_eur', 0)}")
            else:
                tqdm.write(f"   ❌ [{idx+1}/{len(images)}] {img_path.name} - Failed")
            
            # Rate limiting
            time.sleep(1.5)
        
        except Exception as e:
            tqdm.write(f"   ❌ Error on {img_path.name}: {e}")
            continue
    
    elapsed = time.time() - start_time
    
    # Save results
    output_data = {
        "total_images": len(images),
        "classified": len(results),
        "failed": len(images) - len(results),
        "processing_time_seconds": elapsed,
        "folders": {folder: len(imgs) for folder, imgs in folders.items()},
        "products": results
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Statistics
    print()
    print("=" * 70)
    print("✅ CLASSIFICAÇÃO COMPLETA!")
    print("=" * 70)
    print()
    print(f"📊 Statistics:")
    print(f"   • Total images: {len(images)}")
    print(f"   • Classified: {len(results)}")
    print(f"   • Failed: {len(images) - len(results)}")
    print(f"   • Time: {int(elapsed//60)} min {int(elapsed%60)} sec")
    print()
    
    # By category
    if results:
        generos = {}
        tipos = {}
        for r in results:
            c = r['classification']
            g = c.get('genero', 'unknown')
            t = c.get('tipo', 'unknown')
            generos[g] = generos.get(g, 0) + 1
            tipos[t] = tipos.get(t, 0) + 1
        
        print("📈 By Gender:")
        for g, count in sorted(generos.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {g}: {count}")
        
        print()
        print("📈 By Type:")
        for t, count in sorted(tipos.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   • {t}: {count}")
    
    print()
    print(f"💾 Saved: {OUTPUT_FILE}")
    print()
    print("🎯 Next step:")
    print("   python3 generate_woocommerce_complete.py")
    print()


if __name__ == "__main__":
    main()
