# 🎨 Google Gemini AI - Para Que Serve?

## ✅ Já Configurado!

A Gemini API key **já está no ficheiro `.env`**:
```bash
GEMINI_API_KEY=AIzaSyDWCanKI3CtqyIWTOpaPVPVtmGOW6A7OaE
```

---

## 🎯 Finalidade no Projeto

### Problema:
O Instagram @chapeuslisboetas tem **372 fotos de produtos** com:
- ❌ Fundos caóticos (loja, rua, ambientes variados)
- ❌ Iluminação amadora
- ❌ Ângulos limitados (1-2 fotos/produto)
- ❌ Pessoas usando chapéus (não ideal para catálogo limpo)

### Solução AI:
O script `instagram-to-professional-images.py` usa **Google Gemini Flash 2.5** para transformar cada foto Instagram em **4 imagens profissionais de e-commerce**:

1. **Produto Frontal** → Fundo branco, vista frontal, studio lighting (estilo Zara)
2. **Produto 3/4** → Ângulo 45°, mostra profundidade (estilo Hermès)
3. **Close-up Detalhes** → Macro de texturas, costuras, qualidade (estilo Brunello Cucinelli)
4. **Lifestyle Editorial** → Pessoa usando chapéu, fundo limpo (estilo Mango/COS)

**Resultado:** 372 fotos → **1,488 imagens profissionais** prontas para WooCommerce!

---

## 💰 Custo

- **Por imagem Instagram:** ~$0.005 (meio cêntimo)
- **Projeto completo (372 fotos):** ~$1.86 (€1.75)
- **vs Fotógrafo profissional:** €2,000+ 
- **Economia: 99.9%** 🎉

---

## 🚀 Como Usar

### 1. Testar (5 fotos, sem processar AI)
```bash
python3 instagram-to-professional-images.py --limit 5 --dry-run
```

### 2. Processar 10 fotos (gera 40 imagens)
```bash
python3 instagram-to-professional-images.py --limit 10
```

### 3. Processar TUDO (372 fotos → 1,488 imagens)
```bash
python3 instagram-to-professional-images.py --limit 372
```

**Duração estimada:** ~3.5 horas (automático)

---

## 📁 Output

```
processed_images/
├── raw_instagram/              # Originais Instagram
│   └── chapeuslisboetas_ABC123.jpg
│
└── professional/               # 4 fotos profissionais/cada
    ├── chapeuslisboetas_ABC123_product_front.jpg
    ├── chapeuslisboetas_ABC123_product_three_quarter.jpg
    ├── chapeuslisboetas_ABC123_product_detail.jpg
    └── chapeuslisboetas_ABC123_lifestyle_professional.jpg
```

---

## 📊 ROI Esperado (E-commerce Best Practices 2024)

- **+24% conversão** (fotos profissionais vs amadoras)
- **+15% ticket médio** (qualidade percebida)
- **-60% devoluções** (cliente vê melhor o produto)

---

## 🔗 Recursos

- API Key: https://makersuite.google.com/app/apikey
- Docs: https://ai.google.dev/gemini-api/docs/image-generation
- Best Practices: https://www.shopify.com/blog/clothing-photography

---

**Status:** ✅ Configurado e pronto a usar
**Custo total projeto:** €1.75 (372 fotos)
**Tempo processamento:** 3.5h automático
