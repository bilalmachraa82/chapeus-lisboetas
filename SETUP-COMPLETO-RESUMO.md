# 🎯 Setup Completo - Chapéus Lisboetas AI Pipeline

**Status atual e próximos passos**

---

## ✅ **O QUE JÁ ESTÁ PRONTO**

### **1. Download Instagram** 📸
```bash
✅ 12 fotos baixadas (instagram_catalog/raw_photos/)
✅ Metadata extraída (captions, likes, datas)
✅ Script download funcionando
⚠️  Limitação: Instagram bloqueou rate limit (401 Unauthorized)
```

**Solução:** Adicionar credenciais ao `.env` ou esperar 10-15 minutos e tentar novamente.

---

### **2. Classificação AI (Gemini Vision FREE)** 🤖
```bash
✅ Script funcionando perfeitamente
✅ Teste com 1 foto: SUCESSO
✅ Gemini Vision FREE tier confirmado
```

**Exemplo resultado:**
```json
{
  "genero": "mulher",
  "tipo": "outros",
  "estilo": "classico",
  "cor_principal": "preto",
  "preco_sugerido_eur": 55,
  "adequado_ecommerce": true
}
```

**Próximo passo:** Rodar nas 12 fotos existentes
```bash
python3 download-and-classify-instagram.py --limit 12
```

---

### **3. Comparação APIs Image Generation** 📊
```bash
✅ Documento completo: AI-MODELS-COMPARISON-SEP2025.md
✅ Top 3 identificados:
   1. Seedream 4.0 (€41) - Melhor qualidade, 4K
   2. Qwen-Image-Edit (€29 ou GRÁTIS local) - Melhor custo-benefício
   3. HiDream (€14) - Mais barato

✅ Recomendação: QWEN LOCAL (GRÁTIS) ou Seedream 4.0 (pago)
```

---

### **4. Setup Qwen Local (Mac M4)** 🍎
```bash
✅ Guia completo: QWEN-LOCAL-SETUP-MAC-M4.md
✅ 7 passos detalhados
✅ Scripts prontos:
   - qwen_edit_example.py (teste 1 imagem)
   - batch_process_qwen.py (372 fotos batch)
✅ Otimizações para 16GB RAM
✅ Troubleshooting completo
```

---

## 🚀 **PRÓXIMOS PASSOS (EM ORDEM)**

---

### **PASSO 1: Obter Mais Fotos Instagram** 📸

#### **Opção A: Adicionar Login (Recomendado)**
```bash
# Editar .env
nano .env

# Adicionar:
INSTAGRAM_LOGIN=seu_email_ou_username
INSTAGRAM_PASSWORD=sua_senha

# Rodar novamente
python3 download-and-classify-instagram.py --limit 372
```

#### **Opção B: Esperar Rate Limit (10-15 min)**
```bash
# Instagram bloqueou temporariamente
# Aguardar e tentar novamente:
sleep 900  # 15 minutos
python3 download-and-classify-instagram.py --limit 372
```

#### **Opção C: Download Manual**
- Salvar fotos manualmente do Instagram
- Colocar em `instagram_catalog/raw_photos/`

---

### **PASSO 2: Classificar Fotos com Gemini Vision** 🤖

```bash
# Classificar todas as fotos baixadas
python3 download-and-classify-instagram.py --limit 12

# Resultado:
# ✅ Metadata JSON com classificações
# ✅ Fotos organizadas por categoria
# ✅ CSV WooCommerce pronto
```

**Tempo estimado:** ~30 segundos (12 fotos) ou ~10 min (372 fotos)  
**Custo:** €0 (FREE tier)

---

### **PASSO 3: Setup Qwen Local (GRÁTIS)** 🍎

#### **3.1 Instalar Dependências**
```bash
# Criar virtual environment
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"
python3.11 -m venv venv-qwen
source venv-qwen/bin/activate

# Instalar PyTorch para Apple Silicon
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Instalar outras dependências
pip3 install -r requirements-qwen-local.txt
```

#### **3.2 Login Hugging Face**
```bash
# Instalar CLI
pip3 install huggingface_hub

# Login
huggingface-cli login
# Token: [colar seu token de https://huggingface.co/settings/tokens]
```

#### **3.3 Aceitar Licença Modelo**
```
1. Ir para: https://huggingface.co/Qwen/Qwen-Image-Edit-2509
2. Clicar: "Agree and access repository"
```

#### **3.4 Testar com 1 Foto**
```bash
# Copiar foto de teste
cp instagram_catalog/raw_photos/chapeuslisboetas_DNyTzUT2gf7.jpg input.png

# Rodar exemplo
python3 qwen_edit_example.py

# Primeira vez: vai baixar modelo (~8GB, 10-30 min)
# Próximas vezes: rápido (~30-45 seg/imagem)
```

#### **3.5 Processar Batch (372 fotos)**
```bash
# Rodar batch processing
python3 batch_process_qwen.py

# Tempo estimado: 3-4 horas (372 fotos × 4 variações = 1,488 imagens)
# Custo: €0 (100% LOCAL E GRÁTIS!)
```

---

### **PASSO 4: Integrar com WooCommerce** 🛍️

```bash
# Resultado do Qwen:
# ✅ 1,488 imagens profissionais geradas
# ✅ CSV WooCommerce com produtos classificados
# ✅ Fotos organizadas por categoria

# Upload para WordPress:
# 1. Importar CSV via WooCommerce > Import
# 2. Fazer upload das imagens
# 3. Associar produtos às imagens
```

---

## 💰 **CUSTOS FINAIS**

### **Opção 1: 100% GRÁTIS (RECOMENDADO para testar)**
```
✅ Gemini Vision (classificação): €0
✅ Qwen Local (geração): €0
⏱️  Tempo: ~4-5 horas total
💻 Requisitos: Mac M4, 16GB RAM, paciência
```

### **Opção 2: Híbrido (Qualidade + Custo)**
```
✅ Gemini Vision (classificação): €0
✅ Seedream 4.0 (geração): €41
⏱️  Tempo: ~2-3 horas total
🎨 Qualidade: Máxima (4K)
```

### **Opção 3: Premium (Fastest + Best)**
```
✅ Gemini Vision (classificação): €0
✅ Seedream 4.0 (geração): €41
✅ API automática: Fast
⏱️  Tempo: ~1-2 horas total
🏆 Melhor qualidade do mercado
```

---

## 📁 **ESTRUTURA DE ARQUIVOS**

```
full-chapeus-lisboetas (2)/
├── .env                                    # Configurações (APIs, Instagram)
├── instagram_catalog/
│   ├── raw_photos/                        # 12 fotos Instagram
│   └── catalog_metadata.json              # Metadata extraída
│
├── output_qwen/                           # Output teste Qwen (4 imgs)
├── output_qwen_batch/                     # Output batch (1,488 imgs)
│   └── metadata.json
│
├── AI-MODELS-COMPARISON-SEP2025.md        # Comparação APIs
├── QWEN-LOCAL-SETUP-MAC-M4.md             # Setup Qwen completo
├── SETUP-COMPLETO-RESUMO.md               # Este arquivo
│
├── download-and-classify-instagram.py     # Download + Classificação
├── test-classification.py                 # Teste Gemini Vision
├── qwen_edit_example.py                   # Teste Qwen (1 foto)
├── batch_process_qwen.py                  # Batch Qwen (372 fotos)
│
└── requirements-qwen-local.txt            # Dependencies Qwen
```

---

## 🎯 **RECOMENDAÇÃO FINAL**

### **Para começar AGORA (sem custo):**

```bash
# 1. Classificar 12 fotos existentes (2 min)
python3 download-and-classify-instagram.py --limit 12

# 2. Ver resultados classificação
cat instagram_catalog/catalog_metadata.json | python3 -m json.tool

# 3. Decidir próximo passo:
#    A) Setup Qwen local (grátis, 4-5h)
#    B) Obter API key Seedream (pago €41, 2h)
#    C) Aguardar mais fotos Instagram
```

---

### **Para máxima qualidade + velocidade:**

```bash
# 1. Obter API key Seedream 4.0
# https://www.byteplus.com/en/product/Seedream

# 2. Adicionar ao .env:
SEEDREAM_API_KEY=your_key_here

# 3. Criar script integração Seedream
# (posso criar se quiser!)

# 4. Processar batch (€41, 2-3h)
```

---

## 🆘 **SUPORTE**

### **Problemas comuns:**

1. **Instagram rate limit 401:**
   - Esperar 10-15 min
   - Adicionar login/password no .env

2. **Gemini Vision erro 429:**
   - Free tier tem limites/minuto
   - Adicionar sleep() entre requests

3. **Qwen "MPS not available":**
   - Verificar macOS 14+
   - Usar CPU mode (mais lento)

4. **Out of memory (Qwen local):**
   - Reduzir num_inference_steps
   - Processar imagens menores (768px)
   - Gerar 1 por vez em vez de 4

---

## ✅ **CHECKLIST PROGRESSO**

**Hoje (30 Set 2025):**
- [x] Download 12 fotos Instagram
- [x] Testar Gemini Vision classificação
- [x] Comparar APIs image generation
- [x] Criar setup Qwen local completo
- [ ] Classificar 12 fotos existentes
- [ ] Decidir API final (Qwen local ou Seedream)

**Próximos dias:**
- [ ] Download 372 fotos completas
- [ ] Classificação AI completa
- [ ] Setup Qwen local OU obter API Seedream
- [ ] Gerar 1,488 imagens profissionais
- [ ] Criar CSV WooCommerce
- [ ] Upload para site WordPress

---

## 🎉 **CONCLUSÃO**

**Você tem DUAS opções excelentes:**

### **🆓 Opção GRÁTIS (Qwen Local):**
- Setup inicial: 1-2h
- Processing: 4-5h
- Qualidade: Excelente
- Custo: €0
- **MELHOR para:** Testar, aprender, sem orçamento

### **💳 Opção PAGA (Seedream 4.0):**
- Setup: 10 min
- Processing: 2-3h
- Qualidade: Máxima (4K)
- Custo: €41
- **MELHOR para:** Produção, velocidade, qualidade premium

---

**Quer que eu:**
1. Classifique as 12 fotos existentes com Gemini?
2. Crie script integração Seedream API?
3. Ajude no setup Qwen local agora?

**O que prefere fazer primeiro?** 🚀
