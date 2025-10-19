# 🚀 Setup Rápido Seedream - 2 Minutos

**Apenas falta 1 passo para começar!**

---

## ✅ **JÁ ESTÁ FEITO:**

- ✅ 12 fotos baixadas
- ✅ 12 fotos classificadas (100%)
- ✅ Seedream API key parcial: `api-key-20250930210508`

---

## ⚠️ **FALTA 1 COISA:**

### **OPÇÃO A: BytePlus Seedream (Oficial)** 🔥

**Precisa de 2 keys:**
1. ✅ `SEEDREAM_API_KEY` - Já tem! `api-key-20250930210508`
2. ❌ `SEEDREAM_SECRET_KEY` - **FALTA ESTA!**

**Como obter Secret Key:**

```bash
# 1. Ir para:
https://console.byteplus.com/ark/region:ark+ap-southeast-1/apiKey

# 2. Encontrar "api-key-20250930210508"

# 3. Deve mostrar algo como:
#    Access Key ID: api-key-20250930210508
#    Secret Access Key: [clicar "Show" para ver]

# 4. Copiar Secret Access Key

# 5. Adicionar ao .env:
SEEDREAM_SECRET_KEY=seu_secret_key_aqui
```

---

### **OPÇÃO B: Replicate (Mais Fácil!)** ⭐ **RECOMENDO**

**Apenas 1 token! Muito mais simples:**

```bash
# 1. Criar conta (30 segundos):
https://replicate.com/signup

# 2. Obter token (20 segundos):
https://replicate.com/account/api-tokens

# 3. Clicar "Create token"

# 4. Copiar token (começa com r8_)

# 5. Adicionar ao .env:
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Vantagens Replicate:**
- ✅ Mais simples (1 token só)
- ✅ $5 crédito FREE inicial
- ✅ ~166 imagens grátis ($0.03/img)
- ✅ Mesma qualidade Seedream 4.0
- ✅ Funciona na hora

---

## 🎯 **MINHA RECOMENDAÇÃO:**

### **Use REPLICATE (Opção B)!**

**Porquê:**
1. Muito mais rápido setup (1 min vs 5 min)
2. Apenas 1 token (vs 2 keys)
3. Interface mais simples
4. Mesmo modelo Seedream 4.0
5. Funciona na hora!

---

## 📝 **EXECUTAR DEPOIS:**

```bash
# 1. Adicionar ao .env:
REPLICATE_API_TOKEN=r8_seu_token

# 2. Processar 12 fotos teste:
python3 seedream_batch_processing.py --limit 12

# 3. Ver resultados:
open output_seedream/

# 4. Se ficou bom, processar mais:
#    - 166 FREE (Replicate)
#    - ou quantas quiser (PAID $0.03/img)
```

---

## 🔗 **LINKS DIRETOS:**

**BytePlus (Opção A):**
- Console: https://console.byteplus.com/
- API Keys: https://console.byteplus.com/ark/region:ark+ap-southeast-1/apiKey

**Replicate (Opção B - Recomendado):**
- Signup: https://replicate.com/signup
- API Token: https://replicate.com/account/api-tokens
- Seedream Model: https://replicate.com/bytedance/seedream-4

---

## ⏱️ **PRÓXIMOS 2 MINUTOS:**

```bash
# OPÇÃO RÁPIDA (Replicate):
# 1. Ir: https://replicate.com/signup
# 2. Criar conta (email + senha)
# 3. Ir: https://replicate.com/account/api-tokens
# 4. Copiar token
# 5. Colar no .env: REPLICATE_API_TOKEN=r8_...
# 6. Executar: python3 seedream_batch_processing.py --limit 12
```

---

**Quer que ajude a escolher qual?** 
- **Replicate = mais fácil, recomendo!**
- **BytePlus = oficial, mas precisa achar Secret Key**
