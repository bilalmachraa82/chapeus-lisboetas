#!/usr/bin/env python3
"""
Test AI Classification with Gemini Vision (FREE tier)
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Testar com 1 foto
photo_dir = Path('instagram_catalog/raw_photos')
test_photo = list(photo_dir.glob('*.jpg'))[0]

print(f'📸 Testando com: {test_photo.name}')
print()

prompt = """
Analisa esta imagem de chapéu/acessório e classifica precisamente.

Retorna APENAS JSON (sem texto extra):
{
    "genero": "homem|mulher|crianca|unisex",
    "tipo": "boina|chapeu-fedora|chapeu-panama|bone|cartola|gorro|bucket-hat|capeline|outros",
    "estilo": "classico|casual|formal|desportivo|vintage|moderno",
    "cor_principal": "preto|branco|castanho|azul|cinza|bege|bordeaux|verde|outros",
    "material_aparente": "la|algodao|palha|pele|sintetico|outros",
    "descricao_curta": "Descrição PT curta (max 30 palavras)",
    "tags": ["tag1", "tag2", "tag3"],
    "preco_sugerido_eur": 35-65,
    "tem_pessoa": true|false,
    "qualidade_foto": "alta|media|baixa",
    "adequado_ecommerce": true|false
}
"""

# Load image
with open(test_photo, 'rb') as f:
    image_data = f.read()

model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content([
    prompt,
    {'mime_type': 'image/jpeg', 'data': image_data}
])

# Parse response
response_text = response.text.strip()
if '```' in response_text:
    parts = response_text.split('```')
    if len(parts) >= 2:
        response_text = parts[1]
        if response_text.startswith('json'):
            response_text = response_text[4:]

classification = json.loads(response_text.strip())

print('✅ CLASSIFICAÇÃO OBTIDA:')
print(json.dumps(classification, indent=2, ensure_ascii=False))
print()
print('🎉 Gemini Vision FREE tier FUNCIONA!')
print()
print('📊 Resultado:')
print(f"  • Género: {classification.get('genero', 'N/A')}")
print(f"  • Tipo: {classification.get('tipo', 'N/A')}")
print(f"  • Estilo: {classification.get('estilo', 'N/A')}")
print(f"  • Cor: {classification.get('cor_principal', 'N/A')}")
print(f"  • Preço sugerido: €{classification.get('preco_sugerido_eur', 'N/A')}")
print(f"  • E-commerce ready: {'✅' if classification.get('adequado_ecommerce') else '❌'}")
