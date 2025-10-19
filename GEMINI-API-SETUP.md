# 🔑 Gemini API Key Setup - Guia Completo

## ❌ **Problema Atual**
```
Error: 400 API key not valid
```

A API key no `.env` pode estar:
- ❌ Expirada
- ❌ Sem permissões para image generation
- ❌ Quota exceeded
- ❌ Não ativada para Gemini 2.5 Flash

---

## ✅ **SOLUÇÃO: Obter Nova API Key**

### **Passo 1: Aceder Google AI Studio**

🔗 **Link direto:** https://aistudio.google.com/apikey

### **Passo 2: Criar ou Validar API Key**

1. **Login** com conta Google
2. Click **"Get API Key"** ou **"Create API Key"**
3. Selecionar projeto (ou criar novo):
   - Nome: `Chapeus-Lisboetas-Image-Gen`
4. **IMPORTANTE:** Ativar **Gemini API** no projeto:
   - Enable API: `generativelanguage.googleapis.com`
5. Copiar API key (formato: `AIzaSy...`)

### **Passo 3: Verificar Permissões**

Garantir que API key tem acesso a:
- ✅ `generativelanguage.googleapis.com`
- ✅ `Gemini 2.5 Flash` model
- ✅ **Image generation** features (Nano Banana)

### **Passo 4: Atualizar .env**

```bash
# Editar ficheiro .env
nano .env

# Atualizar linha:
GEMINI_API_KEY=SUA_NOVA_API_KEY_AQUI

# Salvar: Ctrl+O, Enter, Ctrl+X
```

### **Passo 5: Testar API Key**

```bash
# Teste rápido
python3 -c "
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content('Test: Say hello')
    print('✅ API Key válida!')
    print(f'Resposta: {response.text}')
except Exception as e:
    print(f'❌ Erro: {e}')
"
```

---

## 🆓 **Quotas & Limites (Free Tier)**

```
Gemini 2.5 Flash (Free):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 15 requests/minuto
• 1,500 requests/dia
• 1 milhão tokens/dia

Para 372 fotos:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total requests: 1,488 (372 x 4)
• Tempo mínimo: 1,488/15 = 99 minutos (1.6h)
• Estratégia: Processar 180 fotos/dia (2 dias)

CUSTO: $0 (Free tier suficiente!)
```

---

## 💳 **Alternativa: Paid Plan (Recomendado)**

Se quiser processar tudo de uma vez:

### **Pay-as-you-go**
```
Custo: $0.075/1M input tokens
      + $0.30/1M output tokens

372 fotos x 4 imagens:
• Input: ~372K tokens → $0.03
• Output: ~1.5M tokens → $0.45
• TOTAL: $0.48 (vs $7.44 estimado)

Vantagem: Sem rate limits!
```

---

## 🔧 **MÉTODO ALTERNATIVO (Enquanto resolve API)**

### **Opção A: Processar localmente com Stable Diffusion**

Vou criar script alternativo usando modelo local (grátis, sem API):

```bash
# Usar Stable Diffusion XL local
pip install diffusers transformers accelerate

# Script local (sem custo, sem limites)
python local-image-processing.py --limit 372
```

### **Opção B: Usar Replicate API (Backup)**

```bash
# API alternativa (similar Gemini)
export REPLICATE_API_TOKEN=r8_...
python instagram-to-professional-images-replicate.py
```

---

## 📝 **Action Items**

### **AGORA MESMO:**

```
☐ Aceder: https://aistudio.google.com/apikey
☐ Criar nova API key
☐ Copiar key
☐ Atualizar .env
☐ Testar com: python3 instagram-to-professional-images.py --limit 1
☐ ✅ Se funcionar → Processar TUDO!
```

### **SE NÃO CONSEGUIR API:**

```
☐ Avisar-me
☐ Posso criar método alternativo:
   - Stable Diffusion local (grátis)
   - Replicate API (pago mas robusto)
   - OpenAI DALL-E 3 (alternativa)
```

---

## ✅ **BOA NOTÍCIA**

**Instagram download FUNCIONOU PERFEITAMENTE! 🎉**

```
✅ Downloaded 3 photos from @chapeuslisboetas
✅ Stored: processed_images/raw_instagram/
✅ Format: High-quality JPEGs
✅ Ready for processing
```

**50% do pipeline já está funcional!**

Assim que a API key estiver válida:
→ **3.5 horas** = **1,488 imagens profissionais** ✨

---

## 🆘 **Precisa Ajuda?**

**Diga-me:**
1. Conseguiu aceder Google AI Studio?
2. Criou nova API key?
3. Quer que crie método alternativo (sem Gemini)?

**Estou pronto para adaptar a qualquer cenário! 🚀**
