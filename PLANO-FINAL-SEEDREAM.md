# 🚀 PLANO FINAL REVISADO - Seedream 4.0 API

**Pipeline completo: Instagram → Classificação → Seedream 4.0 → E-commerce**

---

## 🎯 **DECISÃO FINAL**

❌ ~~Qwen Local~~ (muito lento, 4-5 horas)  
✅ **Seedream 4.0 API** (rápido, 200 créditos GRÁTIS para teste!)

---

## 📊 **PLANO REVISADO**

### **FASE 1: Download Instagram (10-15 min)** 📸
```
Objetivo: Obter TODAS as fotos do @chapeuslisboetas
Status atual: 12 fotos (rate limit 401)

Solução:
1. Adicionar login Instagram no .env
2. Aguardar 15 min rate limit
3. Download completo 372 fotos

Saída: 372 imagens JPG
```

---

### **FASE 2: Classificação AI Gemini (10-15 min)** 🤖
```
Objetivo: Classificar cada foto (género, tipo, estilo, cor, preço)
API: Gemini Vision (FREE tier)

Processo:
- 372 fotos × 2 seg/foto = ~12 minutos
- Extrair metadata + classificação
- Organizar por categorias

Saída: JSON com classificações + CSV WooCommerce
Custo: €0
```

---

### **FASE 3: Seedream 4.0 Image Generation (30-60 min)** ⚡
```
Objetivo: Transformar 372 fotos → 372 imagens profissionais e-commerce

API: Seedream 4.0 (BytePlus)
Créditos FREE: 200 imagens (teste)
Créditos PAID: 172 imagens restantes

Processo:
- 200 fotos FREE (teste qualidade)
- 172 fotos PAID ($0.03/img = $5.16)
- Prompt otimizado para e-commerce
- Background removal automático
- 4K resolution

Saída: 372 imagens profissionais prontas para site
Tempo: ~2-3 segundos/imagem = 30-40 min total
Custo: €0 (200 grátis) + €5 (172 pagas) = ~€5 total
```

---

## 💰 **CUSTO TOTAL REVISADO**

| Item | Quantidade | Preço | Total |
|------|------------|-------|-------|
| Instagram Download | 372 fotos | €0 | €0 |
| Classificação Gemini | 372 fotos | €0 | €0 |
| Seedream FREE | 200 imgs | €0 | €0 |
| Seedream PAID | 172 imgs | €0.03 | **€5.16** |
| **TOTAL** | | | **~€5** |

**vs Qwen Local:** €0 mas 4-5 horas  
**vs Seedream Full:** €11 (372 imgs)

---

## 🎨 **PROMPT OTIMIZADO SEEDREAM 4.0**

### **Para Chapéus Lisboetas E-commerce:**

```
Professional e-commerce product photography: 

EXTRACT the hat/accessory from the image and isolate it completely.
REMOVE the person and background entirely.
PLACE the product on a clean, pure white background (#FFFFFF).
MAINTAIN the exact product identity, colors, textures, and details.
APPLY professional studio lighting with soft shadows.
ENSURE the product is centered and properly scaled.
CREATE a high-quality, commercial-ready image suitable for online retail.

Style: clean, minimal, professional product shot
Quality: 4K, high detail, sharp focus
Format: square 1:1 aspect ratio for e-commerce consistency
```

**Variações por tipo de produto:**

**Para Boinas/Fedoras (produtos estruturados):**
```
Professional product photo: extract [tipo] hat, isolated on pure white background,
studio lighting, maintain fabric texture and shape, centered composition,
shadow below product, e-commerce ready, 4K quality
```

**Para Chapéus com Pessoa (preservar contexto):**
```
Professional lifestyle product photo: focus on [tipo] hat worn by model,
clean white background, maintain product details and colors,
natural lighting, fashion photography style, e-commerce quality, 4K
```

**Para Acessórios (lenços, pins):**
```
Professional product photo: extract accessory, flat lay style,
pure white background, studio lighting, show material texture,
centered composition, e-commerce ready, 4K detail
```

---

## 🔧 **SETUP SEEDREAM 4.0**

### **PASSO 1: Criar Conta BytePlus** (5 min)

```bash
# 1.1 Ir para:
https://console.volcengine.com/auth/signup

# 1.2 Preencher:
- Email
- Password
- Verificar email

# 1.3 Acessar console:
https://console.byteplus.com/

# 1.4 Ativar Seedream 4.0:
- Ir para "Products" > "Seedream"
- Clicar "Get Started"
- Aceitar termos
```

---

### **PASSO 2: Obter API Key** (2 min)

```bash
# 2.1 Ir para API settings:
https://console.byteplus.com/api/access-keys

# 2.2 Criar Access Key:
- Clicar "Create Access Key"
- Copiar:
  - Access Key ID
  - Secret Access Key

# 2.3 Guardar em local seguro!
```

---

### **PASSO 3: Verificar Créditos FREE** (1 min)

```bash
# 3.1 Ir para Billing:
https://console.byteplus.com/billing

# 3.2 Verificar:
- Free trial credits
- Seedream 4.0 quota
- Should show: 200 free generations

# Se não aparecer:
# - Verificar email de boas-vindas
# - Contactar suporte (chat)
# - Alternativamente: Replicate API (ver abaixo)
```

---

### **PASSO 4: Configurar .env** (1 min)

```bash
# Adicionar ao .env:
SEEDREAM_API_KEY=your_access_key_id
SEEDREAM_SECRET_KEY=your_secret_access_key
SEEDREAM_ENDPOINT=https://api.byteplus.com/v1/images/generation
```

---

## 📝 **SCRIPTS COMPLETOS**

### **Script 1: Download + Classificação** 

Já existe: `download-and-classify-instagram.py`

Modificações: adicionar retry para rate limit

---

### **Script 2: Seedream 4.0 Processing**

Vou criar: `seedream_batch_processing.py`

Funcionalidades:
- ✅ Ler fotos classificadas
- ✅ Gerar prompt personalizado por categoria
- ✅ API call Seedream 4.0
- ✅ Download imagens geradas
- ✅ Organizar por categoria
- ✅ Track créditos (200 free → 172 paid)
- ✅ Progress bar
- ✅ Retry logic
- ✅ Error handling

---

### **Script 3: WooCommerce Export**

Já existe parcialmente em `download-and-classify-instagram.py`

Melhorias:
- ✅ Associar imagens Seedream aos produtos
- ✅ Gerar SKUs únicos
- ✅ Preços baseados em classificação
- ✅ Descrições SEO-friendly
- ✅ Tags automáticas

---

## 🚀 **EXECUÇÃO (ORDEM)**

### **COMANDO 1: Download Instagram + Classificação**

```bash
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

# Adicionar login ao .env primeiro!
nano .env
# INSTAGRAM_LOGIN=seu_email
# INSTAGRAM_PASSWORD=sua_senha

# Executar download + classificação
python3 download-and-classify-instagram.py --limit 372

# Tempo: ~15-20 min
# Output: 
#   - instagram_catalog/raw_photos/ (372 fotos)
#   - instagram_catalog/catalog_metadata.json (classificações)
#   - instagram_catalog/woocommerce-import.csv
```

---

### **COMANDO 2: Processar com Seedream 4.0**

```bash
# Adicionar API keys ao .env primeiro!

# Executar processing
python3 seedream_batch_processing.py

# Opções:
#   --limit 200    # Apenas FREE credits
#   --limit 372    # FREE + PAID (€5)
#   --test 10      # Testar com 10 fotos primeiro

# Tempo: 30-40 min (372 fotos)
# Output:
#   - output_seedream/ (372 imagens 4K)
#   - output_seedream/metadata.json
```

---

### **COMANDO 3: Gerar CSV Final WooCommerce**

```bash
# Gerar CSV com imagens Seedream associadas
python3 generate_woocommerce_csv.py

# Output:
#   - woocommerce_final_import.csv
#   - Pronto para upload!
```

---

## 🎁 **ALTERNATIVA: Replicate API (Se BytePlus não der créditos grátis)**

### **Replicate tem Seedream 4.0:**

```bash
# 1. Criar conta:
https://replicate.com/signup

# 2. Obter API token:
https://replicate.com/account/api-tokens

# 3. Preços:
# - $0.03/imagem (igual BytePlus)
# - $5 crédito inicial FREE
# - 166 imagens grátis!

# 4. Adicionar ao .env:
REPLICATE_API_TOKEN=r8_your_token_here

# 5. Usar endpoint diferente:
# https://api.replicate.com/v1/predictions
```

Vou criar script compatível com ambos!

---

## ⚡ **PERFORMANCE ESPERADA**

| Fase | Tempo | Custo |
|------|-------|-------|
| Download Instagram | 15 min | €0 |
| Classificação Gemini | 12 min | €0 |
| Seedream 200 FREE | 10 min | €0 |
| Seedream 172 PAID | 20 min | €5 |
| Generate CSV | 2 min | €0 |
| **TOTAL** | **~60 min** | **€5** |

---

## 📋 **CHECKLIST EXECUÇÃO**

### **PRÉ-REQUISITOS:**
- [ ] Conta BytePlus/Replicate criada
- [ ] API keys obtidas
- [ ] Créditos FREE verificados
- [ ] .env configurado com:
  - Instagram login/password
  - Seedream API keys

### **EXECUÇÃO:**
- [ ] Download 372 fotos Instagram
- [ ] Classificação 372 fotos (Gemini)
- [ ] Teste Seedream (10 fotos)
- [ ] Processar 200 fotos FREE
- [ ] Decisão: continuar com 172 PAID?
- [ ] Processar restantes (se sim)
- [ ] Gerar CSV WooCommerce
- [ ] Upload para WordPress

---

## 🎯 **PRÓXIMO PASSO IMEDIATO**

Vou criar agora:

1. ✅ Script Seedream 4.0 batch processing
2. ✅ Compatibilidade BytePlus + Replicate
3. ✅ Prompt engineering por categoria
4. ✅ Modificar download script (retry rate limit)
5. ✅ Script geração CSV final

**Quer que avance?** 🚀
