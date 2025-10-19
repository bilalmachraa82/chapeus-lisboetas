# 🚀 Guia Completo de Importação WordPress/WooCommerce

## ✅ O QUE TENS PRONTO:

- **180 fotos profissionais** em `processed_images/professional/`
- **CSV WooCommerce** com 180 produtos: `woocommerce_import_180_produtos.csv`
- **Categorias estruturadas**: `categorias_estruturadas.json`
- **Classificação completa**: `catalog_completo_classificado.json`

---

## 📋 PASSO A PASSO (30-60 minutos)

### **PASSO 1: Upload das Imagens (15-20 min)**

#### Opção A: Via WordPress Admin (mais fácil)
```
1. Login no WordPress: https://seusite.com/wp-admin
2. Ir para: Media → Add New
3. Arrastar TODAS as pastas:
   - processed_images/professional/fotos site1/
   - processed_images/professional/fotos site2/
   - processed_images/professional/CLOCHE/
   - processed_images/professional/PALHA/
   - etc...
4. Aguardar upload completar
5. Verificar que temos 180 imagens na biblioteca
```

#### Opção B: Via FTP (mais rápido para muitas imagens)
```
1. Conectar FTP ao servidor
2. Navegar para: /wp-content/uploads/2024/10/
3. Upload da pasta: processed_images/professional/
4. No WordPress: Media → Library → "Rescan"
```

---

### **PASSO 2: Configurar WooCommerce (5 min)**

Antes de importar, verificar configurações:

```
WooCommerce → Settings:

1. Geral:
   ✓ Moeda: EUR (€)
   ✓ País: Portugal
   ✓ Estado/Província: Lisboa

2. Produtos:
   ✓ Shop Page: Criar página "Loja" ou "Produtos"
   ✓ Dimensões: Centímetros (cm)
   ✓ Peso: Gramas (g)

3. Envio:
   ✓ Adicionar zona: Portugal
   ✓ Métodos: CTT, Correio Azul, ou Taxa Fixa
   ✓ Preço exemplo: €5 envio nacional

4. Pagamentos:
   ✓ Ativar: Transferência Bancária
   ✓ Ativar: PayPal (se tiver)
   ✓ Ativar: MB Way / Multibanco (via plugin)
```

---

### **PASSO 3: Criar Estrutura de Categorias (5 min)**

Antes de importar produtos, criar categorias manualmente:

```
Products → Categories → Add New:

📁 Chapéus (pai)
  └─ 📁 Homem
      ├─ Boinas
      ├─ Fedora
      ├─ Panama
      └─ Bucket Hat
  └─ 📁 Mulher
      ├─ Capeline
      ├─ Cloche
      ├─ Boinas
      └─ Fedora
  └─ 📁 Unisex
      ├─ Boinas
      ├─ Fedora
      ├─ Panama
      ├─ Bucket Hat
      └─ Gorros

📁 Bonés (pai)
  ├─ Homem
  ├─ Mulher
  └─ Unisex

📁 Acessórios
```

**Dica:** Adicionar imagens de categoria para cada uma (melhor SEO)

---

### **PASSO 4: Importar Produtos (10-15 min)**

```
1. WooCommerce → Products → Import

2. Choose File: woocommerce_import_180_produtos.csv

3. Click "Continue"

4. Column Mapping (verificar):
   ✓ ID → ID
   ✓ Type → Type
   ✓ SKU → SKU
   ✓ Name → Name
   ✓ Published → Published
   ✓ Regular price → Regular price
   ✓ Categories → Categories
   ✓ Images → Images
   ✓ ... (resto automático)

5. Update existing products: ☐ (deixar desmarcado)

6. Click "Run the importer"

7. Aguardar progresso: 180/180 produtos

8. Success! Ver link: "View Products"
```

---

### **PASSO 5: Associar Imagens aos Produtos**

**Problema comum:** Imagens podem não associar automaticamente.

**Solução:**

#### Método A: Plugin (Recomendado) 
```
1. Instalar plugin: "Product Image Association"
2. Settings: Match by filename
3. Run: Associa todas as 180 imagens
```

#### Método B: Manual (se poucas falhas)
```
1. Products → All Products
2. Filtrar: Products without images
3. Edit cada produto
4. Product Image: Selecionar da biblioteca
5. Update
```

#### Método C: Script automático (se souber SSH)
```bash
# Renomear imagens para SKU correspondente
# Exemplo: CL-BOINA-0001.jpg
# WooCommerce associa automaticamente por SKU
```

---

### **PASSO 6: Configurar Atributos (Opcional, 5 min)**

Para filtros avançados na loja:

```
Products → Attributes:

1. Add Attribute: "Material"
   Terms: Lã, Algodão, Palha, Pele, Sintético, Linho

2. Add Attribute: "Temporada"
   Terms: Verão, Inverno, Meia-Estação, Todas

3. Add Attribute: "Cor"
   Terms: Preto, Branco, Castanho, Azul, Cinza, Bege...

4. Add Attribute: "Género"
   Terms: Homem, Mulher, Unisex, Criança
```

**Nota:** Os atributos já estão nos produtos importados!

---

### **PASSO 7: SEO & Otimização (10-15 min)**

#### A) Instalar plugin SEO:
```
Plugins → Add New → "Yoast SEO" ou "Rank Math"
```

#### B) Configurar SEO básico:
```
1. SEO → General Settings:
   ✓ Site Title: Chapéus Lisboetas | Chapelaria Portuguesa
   ✓ Tagline: Chapéus Artesanais desde Lisboa

2. SEO → Search Appearance → Products:
   ✓ Title template: %%title%% | Chapéus Lisboetas
   ✓ Meta description: Automático (já vem do CSV)

3. SEO → XML Sitemaps:
   ✓ Ativar sitemap
   ✓ Submit to Google Search Console
```

#### C) Otimizar imagens:
```
Plugins → Add New → "Smush" ou "ShortPixel"
→ Bulk Optimize: 180 imagens
→ Aguardar compressão automática
```

---

### **PASSO 8: Design & Tema (10 min)**

#### Configurar página Loja:

```
1. Appearance → Customize → WooCommerce:

   ✓ Product Catalog:
     - Products per page: 12 ou 24
     - Columns: 3 ou 4
     - Layout: Grid

   ✓ Product Images:
     - Thumbnail: 300x300
     - Single: 600x600
     - Gallery: 100x100

2. Pages → Shop → Edit:
   - Add banner/header image
   - Add texto de boas-vindas
   - Publish
```

#### Widget Sidebar (opcional):
```
Appearance → Widgets:

Sidebar Shop:
  ✓ WooCommerce Price Filter
  ✓ WooCommerce Product Categories
  ✓ WooCommerce Attribute Filters (Material, Temporada)
  ✓ WooCommerce Recent Products
```

---

### **PASSO 9: Testar Loja (5-10 min)**

#### Checklist de testes:

```
□ Visitar página da Loja: /shop
□ Ver produto individual: Clicar em qualquer chapéu
□ Imagem aparece correta?
□ Preço aparece: €35-85?
□ Categorias funcionam: Filtrar por "Boinas"
□ Adicionar ao carrinho
□ Ver carrinho: Produto está lá?
□ Ir para checkout
□ Preencher formulário teste
□ Verificar métodos de pagamento
□ NÃO completar pagamento (é teste!)
```

---

### **PASSO 10: Ajustes Finais (10-15 min)**

#### A) Produtos Destacados:
```
Products → All Products:
→ Selecionar 5-10 melhores produtos
→ Quick Edit → Featured: ✓
→ Update

Homepage/Shop: Aparecerão em destaque
```

#### B) Preços finais:
```
- Revisar preços sugeridos pela AI (€35-85)
- Ajustar se necessário
- Bulk Edit para mudanças em massa
```

#### C) Stock:
```
- Todos importados com stock=10
- Ajustar conforme estoque real
- Ativar "Low stock notification" em Settings
```

#### D) Cross-sells / Upsells:
```
- Editar produtos individualmente
- Linked Products → Add cross-sells
- Exemplo: Boina → Sugerir outras boinas
```

---

## 🎯 GO LIVE! (5 min)

### Checklist Final:

```
✓ 180 produtos importados
✓ Todas imagens associadas
✓ Categorias estruturadas
✓ SEO configurado
✓ Pagamentos ativos
✓ Envios configurados
✓ Testes de compra OK
✓ Design bonito
✓ Mobile responsive (testar!)
```

### Lançamento:

```
1. Settings → Reading:
   ✓ Desmarcar: "Discourage search engines"

2. Anunciar nas redes sociais:
   📸 Instagram: @chapeuslisboetas
   📘 Facebook: Post com link da loja
   📧 Email: Newsletter para clientes

3. Google My Business:
   → Adicionar link da loja online

4. Google Search Console:
   → Submit sitemap: seusite.com/sitemap_index.xml
```

---

## 📊 Monitorização (depois do lançamento)

### Analytics:

```
1. Instalar Google Analytics 4:
   - Plugin: "GA Google Analytics"
   - Código tracking: UA-XXXXX

2. Instalar Facebook Pixel (se tiver FB Ads):
   - WooCommerce → Settings → Integration
   - Add Facebook Pixel ID

3. WooCommerce Analytics:
   - Analytics → Overview
   - Monitorar: Vendas, Conversão, Produtos mais vistos
```

---

## 🆘 TROUBLESHOOTING

### Imagens não aparecem:
```
1. Verificar permissões: /wp-content/uploads (755)
2. Regenerar thumbnails: Plugin "Regenerate Thumbnails"
3. Verificar paths no CSV: Devem ser relativos
```

### Produtos não importaram:
```
1. Verificar CSV encoding: UTF-8 (não UTF-8 BOM)
2. Verificar categorias: Criar antes manualmente
3. Log de erros: WooCommerce → Status → Logs
```

### Preços aparecem errados:
```
1. WooCommerce → Settings → General → Currency: EUR
2. Decimal separator: , (vírgula)
3. Thousand separator: . (ponto)
4. Re-importar CSV se necessário
```

### Site lento:
```
1. Instalar cache: "WP Super Cache"
2. Otimizar imagens: "Smush"
3. CDN: Cloudflare (grátis)
4. Hosting: Upgrade se necessário
```

---

## 📞 PRÓXIMOS PASSOS DEPOIS DO LANÇAMENTO

### Semana 1:
- Monitorar Analytics
- Responder comentários/reviews
- Ajustar descrições se necessário
- Marketing: Instagram stories

### Semana 2-4:
- Adicionar mais fotos (se tiver)
- Blog posts: "Como escolher o chapéu perfeito"
- Email marketing: Descontos primeira compra
- Anúncios: Facebook/Instagram Ads

### Longo prazo:
- Newsletter mensal
- Coleções sazonais
- Descontos especiais
- Programa fidelidade

---

## 🎉 PARABÉNS!

**Loja completa com 180 produtos prontos a vender!**

**Estatísticas finais:**
- ✅ 180 produtos classificados automaticamente
- ✅ 81 Boinas, 33 Bonés, 29 Bucket Hats
- ✅ 149 Unisex, 19 Mulher, 12 Homem
- ✅ Preços €35-85
- ✅ SEO otimizado
- ✅ Pronto para vendas!

---

**Tempo total investido:**
- Classificação AI: 36 min
- Geração CSV: 2 min
- Upload WordPress: 30-60 min

**Custo total: €0** (Gemini Vision Free Tier)

🚀 **BOA SORTE COM AS VENDAS!**
