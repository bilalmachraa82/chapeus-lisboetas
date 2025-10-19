# 🚀 EXECUTAR AGORA - Passo a Passo

**Pipeline completo automatizado em ~60 minutos**

---

## 📋 **PRÉ-REQUISITOS (5 min)**

### **1. Configurar .env**

```bash
# Abrir .env
nano .env

# OU
open -e .env
```

**Adicionar:**

```bash
# ============================================================================
# INSTAGRAM LOGIN (para obter 372 fotos)
# ============================================================================
INSTAGRAM_LOGIN=seu_email_ou_username
INSTAGRAM_PASSWORD=sua_password

# ============================================================================
# SEEDREAM 4.0 API
# ============================================================================
# Opção A: BytePlus (recomendado)
# 1. Criar conta: https://console.byteplus.com/auth/signup
# 2. Ir para: https://console.byteplus.com/api/access-keys
# 3. Copiar Access Key ID e Secret Key

SEEDREAM_API_KEY=your_access_key_id
SEEDREAM_SECRET_KEY=your_secret_access_key

# Opção B: Replicate (alternativa)
# 1. Criar conta: https://replicate.com/signup
# 2. Ir para: https://replicate.com/account/api-tokens
# 3. Copiar token

REPLICATE_API_TOKEN=r8_your_token_here
```

**Salvar e fechar!**

---

## 🎯 **EXECUÇÃO (3 COMANDOS)**

### **COMANDO 1: Download + Classificação (15-20 min)** 📸

```bash
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

python3 download-and-classify-instagram.py --limit 372

# O que faz:
# ✅ Download 372 fotos Instagram
# ✅ Classificação AI com Gemini Vision (FREE)
# ✅ Organização por categorias
# ✅ CSV WooCommerce gerado

# Output:
# - instagram_catalog/raw_photos/ (372 fotos)
# - instagram_catalog/catalog_metadata.json
# - instagram_catalog/woocommerce-import.csv
```

---

### **COMANDO 2A: Teste Seedream (10 fotos, 2-3 min)** 🧪

```bash
# TESTAR PRIMEIRO com 10 fotos!
python3 seedream_batch_processing.py --test

# O que faz:
# ✅ Processa 10 fotos
# ✅ Verifica API funcionando
# ✅ Valida qualidade output
# ✅ GRÁTIS (usa créditos free)

# Output:
# - output_seedream/ (10 imagens profissionais)
```

**VERIFICAR QUALIDADE:**
```bash
open output_seedream/
```

Se ficou bom → Avançar para COMANDO 2B  
Se não ficou bom → Ajustar prompts e testar novamente

---

### **COMANDO 2B: Processar TODAS (30-40 min)** ⚡

**OPÇÃO A: Apenas FREE (200 fotos, €0)**
```bash
python3 seedream_batch_processing.py --limit 200

# Custo: €0
# Tempo: ~15-20 min
# Output: 200 imagens profissionais
```

**OPÇÃO B: TODAS as fotos (372, ~€5)**
```bash
python3 seedream_batch_processing.py --limit 372

# Custo:
#   - 200 FREE: €0
#   - 172 PAID: €5.16
#   - TOTAL: €5.16
# Tempo: ~30-40 min
# Output: 372 imagens profissionais 4K
```

**Output:**
```
output_seedream/
├── chapeuslisboetas_DO8jxFKiJko_professional.jpg
├── chapeuslisboetas_DO53ge6COrf_professional.jpg
├── ... (372 imagens)
└── metadata.json
```

---

### **COMANDO 3: Verificar Resultados** 📊

```bash
# Ver estatísticas
cat output_seedream/metadata.json | python3 -m json.tool

# Abrir pasta
open output_seedream/

# Ver CSV WooCommerce
open instagram_catalog/woocommerce-import.csv
```

---

## ✅ **CHECKLIST DE EXECUÇÃO**

```
PRÉ-REQUISITOS:
[ ] .env configurado com Instagram login
[ ] .env configurado com Seedream API keys
[ ] Créditos Seedream verificados (200 free)

EXECUÇÃO:
[ ] COMANDO 1: Download + Classificação (372 fotos)
[ ] Verificar: instagram_catalog/raw_photos tem 372 fotos
[ ] Verificar: catalog_metadata.json existe
[ ] COMANDO 2A: Teste Seedream (10 fotos)
[ ] Verificar qualidade das 10 imagens
[ ] COMANDO 2B: Processar todas (200 ou 372)
[ ] COMANDO 3: Verificar resultados finais

PÓS-PROCESSAMENTO:
[ ] Upload imagens para WordPress/WooCommerce
[ ] Importar CSV produtos
[ ] Configurar categorias
[ ] Publicar site!
```

---

## 🐛 **TROUBLESHOOTING RÁPIDO**

### **Erro: Instagram 401 Unauthorized**
```bash
# Solução 1: Aguardar 15 minutos
sleep 900

# Solução 2: Adicionar login/password no .env
# Solução 3: Usar VPN
```

### **Erro: Seedream API "Invalid key"**
```bash
# Verificar formato no .env:
SEEDREAM_API_KEY=AKxxxxxxxxxxxxx
SEEDREAM_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxx

# SEM aspas, SEM espaços, SEM "Bearer"
```

### **Erro: Seedream "Out of credits"**
```bash
# Ver créditos restantes:
# https://console.byteplus.com/billing

# Opções:
# 1. Usar apenas 200 free (--limit 200)
# 2. Adicionar cartão (processar restantes)
# 3. Usar Replicate API (alternativa)
```

### **Erro: Gemini "Quota exceeded"**
```bash
# Free tier tem limite/minuto
# Solução: Script já tem rate limiting
# Aguardar automaticamente ou adicionar sleep maior
```

---

## 📊 **RESULTADOS ESPERADOS**

### **Após COMANDO 1:**
```
✅ 372 fotos Instagram baixadas
✅ Classificação completa:
   - Género (homem/mulher/unisex)
   - Tipo (boina/fedora/panama/etc)
   - Estilo (clássico/casual/formal)
   - Cor principal
   - Preço sugerido €35-65
✅ CSV WooCommerce pronto
```

### **Após COMANDO 2:**
```
✅ 200-372 imagens profissionais geradas
✅ Background branco puro
✅ Produto isolado e centrado
✅ Lighting profissional
✅ 4K quality
✅ Pronto para e-commerce
```

---

## ⏱️ **TIMELINE TOTAL**

| Etapa | Tempo | Custo |
|-------|-------|-------|
| Configurar .env | 5 min | €0 |
| Download + Classificação | 15 min | €0 |
| Teste Seedream (10 fotos) | 3 min | €0 |
| Processar 200 FREE | 15 min | €0 |
| Processar 172 PAID | 15 min | €5 |
| **TOTAL** | **~50 min** | **€5** |

---

## 🎯 **PRÓXIMO PASSO AGORA**

### **1. Configurar .env (5 min)**
```bash
open -e .env
```

Adicionar:
- Instagram login/password
- Seedream API keys (BytePlus OU Replicate)

### **2. Começar execução**
```bash
python3 download-and-classify-instagram.py --limit 372
```

---

## 💡 **DICAS FINAIS**

✅ **Testar primeiro com 10 fotos** antes de processar todas  
✅ **Verificar qualidade** das imagens geradas  
✅ **Usar 200 FREE primeiro** depois decidir se compra restantes  
✅ **Manter terminal aberto** durante processamento  
✅ **Não fechar Mac** (pode suspender processing)  

---

**PRONTO PARA COMEÇAR?** 🚀

**Primeiro passo:**
```bash
# Ver se tem tudo pronto
cat .env | grep -E "(INSTAGRAM|SEEDREAM|REPLICATE)"
```

Se aparecer as keys → **EXECUTAR COMANDO 1!** 🎯
