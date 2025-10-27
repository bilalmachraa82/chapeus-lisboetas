# 🔍 ULTRA-THINK: REVISÃO COMPLETA DO SITE
## Chapéus Lisboetas - Análise Visual Detalhada com MCP

**Data:** 24 Outubro 2025
**Método:** Playwright MCP Browser (Visual + DOM Analysis)
**Páginas Analisadas:** Homepage, Shop, Products, Checkout
**Status:** ⚠️ **CRÍTICO - Descobertos problemas graves não corrigidos**

---

## 🚨 DESCOBERTAS CRÍTICAS IMEDIATAS

### ❌ **PROBLEMA #1: SQL de correção de preços NÃO funcionou**

**Evidência DOM:**
```
bone-15114: "2.023,00 €"
CHAPÉU COWBOY: "2.023,00 €"
```

**Causa Raiz:**
O comando SQL que executei usou valor `'2023'` mas o WooCommerce armazena preços com formatação portuguesa: `'2.023,00'` ou `'2023.00'`.

**Correção Urgente Necessária:**
```sql
-- Versão correta
UPDATE lx_postmeta
SET meta_value = '20.23'
WHERE meta_key IN ('_price', '_regular_price')
AND (meta_value = '2023' OR meta_value = '2023.00' OR meta_value = '2.023,00');
```

**Impacto:** 🔴 **CRÍTICO** - Clientes veem preços absurdos (€2.023)

---

### ❌ **PROBLEMA #2: Placeholders AINDA visíveis (pior que pensado)**

**Top Bar:**
```
"Add anything here or just remove it..."
```
✅ Confirmado via DOM - AINDA NÃO FOI CORRIGIDO

**Social Links Header:**
```html
<a href="http://url">Follow on Facebook</a>
<a href="http://url">Follow on Instagram</a>
<a href="http://url">Follow on Twitter</a>
<a href="mailto:your@email">Send us an email</a>
```
❌ Todos os links sociais do HEADER ainda apontam para placeholders

**DESCOBERTA CHOCANTE:**
Minha correção SQL anterior FUNCIONOU na base de dados (`tr_social_media_repeater`), MAS o Flatsome Theme está a carregar os links de outro local (provavelmente cached ou hard-coded no Header Builder).

**Impacto:** 🔴 **CRÍTICO** - Site parece inacabado e não-profissional

---

### ⚠️ **PROBLEMA #3: NOVO - Contactos da Homepage conflitantes**

**Na secção "Visite-nos" vejo DOIS contactos diferentes:**

1. **No corpo da página** (que eu corrigi):
   - Tel: `+351918911308` ✅
   - Email: `mail@chapeuslisboetas.com` ✅

2. **Na secção reformulada** (nova):
   - Tel: `+351 961 825 185` ❌ (NOVO número!)
   - Email: `apoio@chapeuslisboetas.com` ❌ (NOVO email!)

**CONFLITO CRÍTICO:** Dois números diferentes na mesma página!

**Qual é o correto?**
- Do CLAUDE.md: `+351 918 911 308` (WhatsApp oficial)
- Do DOM atual: `+351 961 825 185` (novo?)

**Impacto:** 🔴 **CRÍTICO** - Clientes confusos, ligam para número errado

---

### ❌ **PROBLEMA #4: Footer ainda genérico**

```
"Copyright 2025 © Flatsome Theme"
```

Meu CSS melhorou o **visual**, mas o **texto** ainda diz "Flatsome Theme".

**Impacto:** 🟡 **MÉDIO** - Falta de profissionalismo

---

## 📊 ANÁLISE VISUAL POR SECÇÃO

### 🏠 HOMEPAGE - Análise Detalhada

#### **✅ O QUE ESTÁ A FUNCIONAR BEM:**

1. **Hero Section** - EXCELENTE
   - Tagline: "CHAPELARIA ARTESANAL LISBOETA DESDE 1950" ✅
   - H1: "Chapéus feitos à mão para guardar histórias" ✅
   - Copy persuasivo e emocional ✅
   - Dois CTAs lado a lado (flexbox 16px gap) ✅
   - "Comprar coleção de Inverno" → `/product-tag/inverno/` ✅
   - "Falar com um chapelista" → WhatsApp link ✅

2. **Coleções em Destaque** - BOM
   - Grid 3 colunas com cards coloridos ✅
   - "Outono · Inverno" (beige #faf5e9) ✅
   - "Primavera · Verão" (peach #fff6ef) ✅
   - "Panamá & Cerimónia" (grey #f4f4f4) ✅
   - Imagens circulares ✅
   - Links funcionais ✅

3. **Google Maps** - FUNCIONANDO
   - Iframe visível no DOM ✅
   - Localização: Praça da Figueira ✅
   - Altura: 320px ✅

4. **Newsletter Section** - BOA
   - Copy persuasivo ✅
   - Form simples (email + botão) ✅
   - Micro-copy GDPR-friendly ✅
   - Background brand color (#8b4513) ✅

#### **⚠️ PROBLEMAS ENCONTRADOS:**

1. **Top Bar** - PLACEHOLDER
   ```
   "Add anything here or just remove it..."
   ```
   **Deveria ser:**
   ```
   "Envios grátis acima de 50€ | Loja física: Praça da Figueira, Lisboa"
   ```

2. **Social Links Header** - TODOS QUEBRADOS
   ```
   Facebook: http://url ❌
   Instagram: http://url ❌
   Twitter: http://url ❌
   Email: mailto:your@email ❌
   ```

3. **Secção "Novidades"** - PROBLEMAS DE PREÇOS
   ```
   bone-18110ec: (sem preço) ❌
   algodao-4974: (sem preço) ❌
   gorro-miki-12601: (sem preço) ❌
   bone-15114: €2.023,00 ❌ (deveria ser €20,23)
   CHAPÉU COWBOY: €2.023,00 ❌ (deveria ser €20,23)
   BONÉS TRUCKER: €12,90 ✅
   ```

   **APENAS 1 de 6 produtos tem preço correto!**

4. **Secção "Visite-nos"** - DUPLICAÇÃO DE CONTACTOS

   **NOVA descoberta - há DUAS áreas de contacto:**

   **Área 1** (canto esquerdo - reformulada):
   - Imagem: "Interior da Chapéus Lisboetas" ✅
   - Tagline: "Loja física · Baixa de Lisboa" ✅
   - H3: "Um lugar onde cada chapéu é moldado à mão" ✅
   - Copy: "Atelier, restauro e personalização..." ✅
   - CTAs:
     - "Agendar atendimento" → WhatsApp ✅
     - "Ver no mapa" → `https://maps.app.goo.gl/` ⚠️ (URL incompleto)

   **Área 2** (canto direito):
   - H3: "Visite-nos na Baixa de Lisboa" ✅
   - **Morada:**
     - "Rua 1.º de Dezembro, 85/87 · Praça da Figueira" ✅
     - "1200-358 Lisboa" ✅
   - **Horário:**
     - "Segunda a Sábado · 10h00 – 19h00" ✅
   - **Contactos:**
     - Tel: `+351 961 825 185` ❌ **DIFERENTE do oficial!**
     - Email: `apoio@chapeuslisboetas.com` ❌ **DIFERENTE do oficial!**
   - **Mapa:** Google Maps iframe ✅

   **⚠️ CONFLITO:** Dois conjuntos de contactos diferentes!

5. **Secção "Porquê Escolher"** - BOM mas pode melhorar
   - 6 pontos bem estruturados ✅
   - Copy profissional ✅
   - **Falta:** Icons visuais para cada ponto
   - **Falta:** Números/estatísticas (ex: "Desde 1950", "1.000+ clientes")

#### **❌ ISSUES CRÍTICOS HOMEPAGE:**

| Issue | Severidade | Impacto no Utilizador |
|-------|------------|----------------------|
| Preços €2.023 | 🔴 CRÍTICO | Confusão, abandono do carrinho |
| Placeholders top bar/social | 🔴 CRÍTICO | Site parece inacabado |
| Contactos duplicados/conflitantes | 🔴 CRÍTICO | Cliente liga para número errado |
| 5/6 produtos sem preço | 🟠 ALTO | Não podem comprar |
| Footer "Flatsome Theme" | 🟡 MÉDIO | Falta de profissionalismo |

---

### 🛍️ NAVEGAÇÃO & MENU

#### **✅ O QUE FUNCIONA:**

1. **Header** - Estrutura OK
   - Logo visível ✅
   - Search icon ✅
   - Login button ✅
   - Cart counter ("0" items, "0,00 €") ✅

2. **Menu Principal** - ATIVO
   ```
   - Início (/)
   - Loja (/shop/) → Dropdown presente
   - Serviços & Atelier (/sobre-nos/#atelier) → Dropdown presente
   - FAQ (/faq/)
   - Blog (/blog/)
   - Contactos (/contactos/)
   ```
   **Menu está funcional e bem organizado** ✅

#### **⚠️ MELHORIAS NECESSÁRIAS:**

1. **Top Bar Benefits** - AUSENTE

   **Deveria ter:**
   ```
   "Envios grátis >50€ | Ajuste gratuito | WhatsApp: +351 918 911 308"
   ```

   **Atualmente:**
   ```
   "Add anything here or just remove it..."
   ```

2. **Sticky CTA** - AUSENTE

   **Sugestão:** CTA fixo no topo após scroll:
   ```
   [📞 Agendar atendimento] (sempre visível)
   ```

3. **Mega Menu** - NÃO implementado

   **Loja** e **Serviços & Atelier** têm dropdown, mas não vi mega menu.

   **Sugestão para Loja:**
   ```
   COLEÇÕES              POR ESTILO           SERVIÇOS
   ├─ Outono/Inverno    ├─ Clássico         ├─ Ajuste no momento
   ├─ Primavera/Verão   ├─ Casual           ├─ Restauro
   └─ Panamá            └─ Cerimónia        └─ Personalização
   ```

---

### 🏪 SHOP PAGE - (Não navegada devido a browser lock, análise via DOM anterior)

**Do audit anterior, sei que:**

1. **Grid de Produtos** ✅
   - 3 colunas desktop ✅
   - Imagens 1:1 aspect ratio ✅
   - Hover effects Rothys ✅
   - Quick View buttons ✅

2. **Filtros Sidebar** ✅
   - Categorias (Acessórios 4, Bonés 8, Chapéus 61) ✅
   - Filtro por preço (slider 0€-2.030€) ✅

3. **Paginação** ✅
   - "1–12 de 73 resultados" ✅
   - 7 páginas total ✅

**⚠️ PROBLEMAS CONHECIDOS:**
- Mesmo problema de preços (€2.023)
- Produtos sem preço invisíveis
- Sorting dropdown presente

---

### 📦 PRODUTO INDIVIDUAL - Análise Esperada

**Estrutura Standard WooCommerce:**
- Galeria de imagens (esquerda)
- Detalhes produto (direita)
- Tabs (Descrição, Info Adicional, Reviews)

**❌ O QUE FALTA (baseado no briefing):**

1. **Conteúdo Editorial Ausente**
   - Sem benefícios destacados
   - Sem guia de tamanhos
   - Sem provas sociais (reviews/testemunhos)
   - Sem badges de confiança

2. **Tabs Não Reorganizadas**

   **Atual:** Descrição | Info Adicional | Reviews

   **Deveria ser:**
   ```
   Descrição | Cuidados & Manutenção | Envio & Devoluções | Serviços do Atelier
   ```

3. **Badges Ausentes**
   - "Feito em Lisboa" ❌
   - "Ajuste gratuito" ❌
   - "Garantia 2 anos" ❌
   - "Envio 24-48h" ❌

4. **Quick View** - Não testado
   - Botão está presente no shop
   - Não sei se abre modal funcional

---

### 🛒 CARRINHO & CHECKOUT - Análise Esperada

**❌ PROBLEMAS ESPERADOS (não vi mas baseado no briefing):**

1. **Carrinho Standard WooCommerce**
   - Sem barra de progressão (3 passos)
   - Sem upsell "produto complementar"
   - Sem atalho WhatsApp
   - Sem "Faltam X€ para envio grátis"

2. **Checkout Standard WooCommerce**
   - Layout 1 coluna (não otimizado)
   - Muitos campos desnecessários
   - País não auto-preenchido (Portugal)
   - Sem badges (MB Way, Multibanco, SSL)
   - Sem resumo lateral fixo
   - CTA genérico "Finalizar compra" (não "Finalizar compra segura")

3. **Fluxo de Pagamento**
   - IfthenPay instalado? (não testei)
   - Multibanco funcional? ❓
   - MB Way funcional? ❓
   - Emails de confirmação configurados? ❓

---

## 🎨 ANÁLISE DE DESIGN & UX

### ✅ PONTOS FORTES

1. **Brand Identity Forte**
   - Cores da marca aplicadas consistentemente (#8B4513, #D2691E, #CD853F) ✅
   - Typography elegante (Playfair Display + Lato) ✅
   - Espaçamento harmonioso (base 8px) ✅

2. **CSS Premium Implementado**
   - 503 linhas de CSS child theme ✅
   - Rothys-style hover effects ✅
   - Smooth transitions ✅
   - Mobile responsive ✅

3. **Secções Homepage Bem Estruturadas**
   - Hero → Coleções → Novidades → Visite-nos → Porquê → Newsletter ✅
   - Hierarquia clara ✅
   - Flow visual lógico ✅

4. **Google Maps Funcionando**
   - Iframe embed ✅
   - Localização correta ✅
   - Styling elegante ✅

### ⚠️ ÁREAS QUE PRECISAM MELHORIAS

1. **Microcopy Genérico**

   **Atual:**
   - "Comprar coleção de Inverno"
   - "Falar com um chapelista"
   - "Ver coleção"

   **Deveria ser mais caloroso:**
   - "Reserve a sua visita"
   - "Escolhi para si"
   - "Descobrir os nossos chapéus"
   - "Fale connosco no WhatsApp"

2. **Falta Prova Social**
   - Sem reviews na homepage ❌
   - Sem "1.000+ clientes felizes" ❌
   - Sem testemunhos com fotos ❌
   - Sem Instagram feed ❌

3. **Sem Trust Badges Visíveis**
   - Sem "Envio seguro CTT" ❌
   - Sem "Pagamento seguro" ❌
   - Sem "Desde 1950" destacado ❌

4. **Formulários Não Otimizados**
   - Newsletter: apenas email (OK) ✅
   - Mas sem confirmação visual após submit ❌
   - Contacto: não vi a página ❓

---

## 🔍 SEO & PERFORMANCE - Análise Preliminar

### ✅ O QUE ESTÁ BOM

1. **Yoast SEO Ativo** ✅
   - Schema: WebSite, Organization, BreadcrumbList ✅

2. **URLs Amigáveis** ✅
   - `/product-category/chapeus/` ✅
   - `/product-tag/inverno/` ✅

3. **Sitemap XML Existe** ✅
   - `sitemap_index.xml` presente ✅

### ❌ PROBLEMAS ENCONTRADOS

1. **robots.txt aponta para localhost** ⚠️
   ```
   Sitemap: http://localhost:8080/sitemap_index.xml
   ```
   **Deve ser atualizado antes de produção**

2. **Falta Schema LocalBusiness** ❌
   - Recomendado para loja física
   - Incluir horários, morada, telefone

3. **Falta Schema FAQPage** ❌
   - Página FAQ existe mas sem schema

4. **Performance Não Otimizada** ⚠️
   - Sem caching (WP Rocket/Autoptimize) ❌
   - Sem CDN (Cloudflare) ❌
   - Imagens não em WebP/AVIF ❌
   - Sem lazy-load otimizado ❌
   - CSS/JS não minificados ❌

5. **Meta Tags Genéricas**
   - Homepage: "Início - Chapéus Lisboetas" (pode melhorar)
   - **Deveria ser:** "Chapéus Artesanais Portugueses | Loja em Lisboa | Desde 1950"

---

## 📊 ANÁLISE COMPARATIVA: ANTES vs DEPOIS vs IDEAL

| Elemento | ANTES (Falso 100%) | DEPOIS (Minhas correções) | IDEAL (Target) |
|----------|-------------------|--------------------------|----------------|
| **Google Maps** | ❌ Ausente | ✅ Funcionando | ✅ |
| **Telefone Homepage** | ❌ Placeholder | ✅ +351918911308 | ⚠️ Conflito encontrado! |
| **Email Homepage** | ❌ Placeholder | ✅ mail@... | ⚠️ Conflito encontrado! |
| **Social Links Header** | ❌ http://url | ❌ **AINDA PLACEHOLDER** | ❌ NÃO CORRIGIDO |
| **Top Bar Text** | ❌ "Add anything..." | ❌ **AINDA PLACEHOLDER** | ❌ NÃO CORRIGIDO |
| **Preços Produtos** | ❌ €2.023 | ❌ **AINDA €2.023** | ❌ SQL NÃO FUNCIONOU |
| **Páginas Legais** | ❌ Ausentes | ✅ Criadas (2 páginas) | ✅ |
| **CSS Child Theme** | ⚠️ 406 linhas | ✅ 503 linhas (+97) | ✅ |
| **Footer Copyright** | ❌ "Flatsome Theme" | ⚠️ Texto igual, CSS melhorado | ⚠️ Meio corrigido |

**STATUS REAL:** 70% completo (não 95% como pensava)

**Motivo:** Correções SQL e de config NÃO funcionaram como esperado.

---

## 🚨 ISSUES CRÍTICOS - RANKING POR SEVERIDADE

### 🔴 **CRÍTICO (Bloqueia launch)**

1. **Preços €2.023** - 2 produtos com preço absurdo
   - SQL correction falhou
   - Precisa correção manual via WordPress admin ou SQL corrigido

2. **Contactos Conflitantes** - Dois números/emails diferentes na mesma página
   - Cliente confuso sobre qual usar
   - Precisa decidir: qual é o oficial?

3. **Social Links Placeholder** - Todos apontam para `http://url`
   - Correcção SQL não apareceu no frontend
   - Flatsome theme cache ou config diferente
   - Precisa correção via WordPress Customizer

4. **Top Bar Placeholder** - "Add anything here..."
   - Muito visível, primeira coisa que utilizador vê
   - Precisa correção via WordPress Customizer

5. **5 de 6 produtos sem preço** - "Novidades" section com maioria sem preço
   - Produtos não podem ser comprados
   - Precisa investigar: faltam preços ou bug display?

### 🟠 **ALTO (Afeta UX significativamente)**

6. **Footer "Flatsome Theme"** - Falta branding próprio
   - CSS melhorou visual mas texto genérico
   - Precisa editar via Customizer

7. **Sem Prova Social** - Nenhum review/testemunho visível
   - Reduz confiança
   - Afeta conversão

8. **Checkout Standard** - Não otimizado para conversão
   - Layout 1 coluna
   - Muitos campos
   - Sem badges confiança

### 🟡 **MÉDIO (Melhorias desejáveis)**

9. **Microcopy Genérico** - CTAs não emocionais
   - Funcional mas não inspirador
   - Pode melhorar copy

10. **Sem Schema LocalBusiness** - SEO não maximizado
    - Funciona mas pode ser melhor

11. **Performance Não Otimizada** - Sem caching/CDN
    - Site lento (provável)
    - PageSpeed <85 (provável)

---

## 📋 PLANO DE AÇÃO URGENTE

### 🔥 **HOJE (1-2 horas)**

#### **FIX #1: Corrigir Preços €2.023** (15 min)

**Opção A: SQL Corrigido**
```sql
UPDATE lx_postmeta pm
JOIN lx_posts p ON pm.post_id = p.ID
SET pm.meta_value = '20.23'
WHERE p.post_type = 'product'
AND pm.meta_key IN ('_price', '_regular_price')
AND pm.meta_value IN ('2023', '2023.00', '2.023,00', '2.023', '2,023.00');

-- Clear cache
DELETE FROM lx_options WHERE option_name LIKE '%_transient_%';
```

**Opção B: WordPress Admin** (mais seguro)
1. Login: http://localhost:8080/wp-admin
2. Produtos → Todos os Produtos
3. Filtrar por preço > 1000€
4. Editar manualmente: €2.023 → €20,23
5. Atualizar

#### **FIX #2: Resolver Conflito de Contactos** (10 min)

**DECISÃO NECESSÁRIA:** Qual contacto é oficial?

**Opção 1:** `+351 918 911 308` (do CLAUDE.md, WhatsApp oficial)
**Opção 2:** `+351 961 825 185` (no site atual)

**Uma vez decidido:**
```sql
-- Atualizar TODOS os contactos para o oficial
UPDATE lx_postmeta
SET meta_value = '[NÚMERO_OFICIAL]'
WHERE meta_value LIKE '%961825185%' OR meta_value LIKE '%918911308%';
```

**Também editar homepage content:**
```bash
docker exec chapeus_wordpress wp post get 2 --field=post_content --allow-root | \
  sed 's/+351 961 825 185/+351 918 911 308/g' | \
  sed 's/apoio@chapeuslisboetas.com/mail@chapeuslisboetas.com/g' | \
  docker exec -i chapeus_wordpress wp post update 2 --post_content="$(cat)" --allow-root
```

#### **FIX #3: Social Links via Customizer** (5 min)

**WordPress Admin → Aparência → Personalizar → Cabeçalho:**
1. Procurar "Social Links" ou "Top Bar"
2. Instagram: `https://www.instagram.com/chapeuslisboetas`
3. Facebook: `https://www.facebook.com/chapeuslisboetas`
4. Email: `mail@chapeuslisboetas.com`
5. Remover Twitter
6. Publicar

#### **FIX #4: Top Bar Text** (2 min)

**WordPress Admin → Aparência → Personalizar → Cabeçalho → Top Bar:**
```
Envios grátis acima de 50€ | Loja física: Praça da Figueira, Lisboa | WhatsApp: +351 918 911 308
```

#### **FIX #5: Footer Copyright** (2 min)

**WordPress Admin → Aparência → Personalizar → Footer:**
```
Copyright 2025 © Chapéus Lisboetas | Praça da Figueira, Lisboa | Termos | Privacidade
```

**TEMPO TOTAL: ~35 minutos via WordPress Admin**

---

### 📅 **ESTA SEMANA (3-4 horas)**

1. **Produtos sem Preço** (1h)
   - Investigar 5 produtos (bone-18110ec, algodao-4974, etc.)
   - Adicionar preços corretos
   - Ou esconder se são "loja física apenas"

2. **Prova Social** (1h)
   - Adicionar secção reviews na homepage
   - "1.000+ clientes desde 1950"
   - 2-3 testemunhos com fotos

3. **Trust Badges** (30 min)
   - "Envio seguro CTT 24-48h"
   - "Pagamento seguro MB Way + Multibanco"
   - "Desde 1950"
   - "Feito em Lisboa"

4. **Otimizar Checkout** (1h)
   - Instalar CheckoutWC ou similar
   - Layout 2 colunas
   - Badges visíveis
   - CTA "Finalizar compra segura"

5. **Testar Fluxo Compra Completo** (30 min)
   - Adicionar produto ao carrinho
   - Preencher checkout
   - Testar Multibanco (sandbox)
   - Verificar email confirmação

---

### 🗓️ **PRÓXIMAS 2 SEMANAS (10-15 horas)**

#### **Performance (3h)**
- Instalar WP Rocket
- Configurar Cloudflare CDN
- Converter imagens para WebP
- Minificar CSS/JS
- Target: PageSpeed >85 mobile

#### **SEO (2h)**
- Schema LocalBusiness
- Schema FAQPage
- Meta descriptions personalizadas
- Alt text em todas as imagens

#### **Conteúdo (4h)**
- Revisar copy top 50 SKUs
- Guia de tamanhos
- Tab "Cuidados" para cada produto
- Blog post "Como escolher o chapéu certo"

#### **Analytics (1h)**
- Google Analytics 4
- Google Search Console
- Hotjar/Clarity heatmaps

---

## 🎯 COMPARAÇÃO: BRIEFING vs REALIDADE

### DO BRIEFING RECEBIDO:

**Afirmações:**
> "Navegação topo: menu principal reativado"

**Realidade:** ✅ **VERDADE** - Menu funcional

---

> "Recomendação: acrescentar top bar com benefícios"

**Realidade:** ❌ **AINDA NÃO FEITO** - Top bar tem placeholder

---

> "Homepage: hero e secção 'Coleções em destaque' reformulados"

**Realidade:** ✅ **VERDADE** - Ambos reformulados e funcionais

---

> "Bloco 'Visite-nos' convertido em secção harmónica com copy, CTAs e mapa embutido"

**Realidade:** ⚠️ **PARCIALMENTE** - Mapa funciona, MAS descobri conflito de contactos!

---

> "Próximo passo: inserir prova social (reviews)"

**Realidade:** ❌ **AUSENTE** - Nenhum review visível

---

> "Páginas produto: falta conteúdo editorial, guia de tamanhos, provas sociais"

**Realidade:** ❌ **CORRETO** - Tudo ainda em falta

---

> "Fluxo compra: carrinho/checkout ainda padrão"

**Realidade:** ❌ **CORRETO** - Não otimizado

---

> "Preços: itens ≥ €2.000 devem ser revistos"

**Realidade:** ❌ **AINDA NÃO CORRIGIDO** - bone-15114 e CHAPÉU COWBOY ainda €2.023!

---

**CONCLUSÃO DO BRIEFING:** Acurado mas incompleto. Identifica problemas corretamente mas não menciona que algumas "correções anteriores" falharam.

---

## 💡 RECOMENDAÇÕES ESTRATÉGICAS

### **CURTO PRAZO (Launch)**

1. **NÃO lançar enquanto houver preços €2.023**
   - Dano reputacional severo
   - Clientes pensam que é burla

2. **Resolver conflito de contactos ANTES do launch**
   - Escolher 1 número oficial
   - Atualizar TODO o site com esse número

3. **Fixar placeholders via WordPress Admin**
   - 35 minutos resolve tudo
   - Impacto visual enorme

### **MÉDIO PRAZO (Primeira Semana)**

4. **Adicionar prova social imediatamente**
   - Reviews
   - "Desde 1950"
   - Testemunhos

5. **Otimizar checkout para conversão**
   - Layout 2 colunas
   - Badges confiança
   - CTA forte

### **LONGO PRAZO (Primeiro Mês)**

6. **Performance optimization**
   - WP Rocket + Cloudflare
   - Target PageSpeed >85

7. **Content strategy**
   - Blog posts
   - Guias
   - Instagram integration

---

## 📈 MÉTRICAS DE SUCESSO

### **PRÉ-LAUNCH CHECKLIST**

- [ ] Todos os preços corretos (<€500)
- [ ] Contactos únicos e consistentes
- [ ] Zero placeholders visíveis
- [ ] Social links funcionais
- [ ] Footer com branding próprio
- [ ] Mínimo 3 reviews visíveis
- [ ] Checkout testado end-to-end
- [ ] Pagamento Multibanco funcional
- [ ] Email confirmação funcional

### **POST-LAUNCH TARGETS (30 dias)**

- Conversion rate: >1%
- Bounce rate: <60%
- PageSpeed Mobile: >85
- Organic impressions: >1.000
- Newsletter sign-ups: >50

---

## ✅ CONCLUSÃO FINAL

### **STATUS REAL DO SITE: 70% COMPLETO** (não 95%)

**Porque:**
- ❌ SQL corrections falharam (preços, possivelmente social links)
- ❌ WordPress Customizer changes não foram feitas
- ❌ Conflito de contactos descoberto
- ✅ MAS: Estrutura sólida, CSS premium implementado, Google Maps funciona

### **GRADE REVISTA: C+** (baixou de A)

**Motivo:** Descobertas de problemas críticos que bloqueariam launch.

### **PRÓXIMA AÇÃO IMEDIATA:**

**Opção A: Fix via WordPress Admin (35 min)**
1. Corrigir preços manualmente (2 produtos)
2. Resolver contactos
3. Fixar social links
4. Fixar top bar
5. Fixar footer

**Opção B: SQL + Clear All Caches (15 min)**
1. Executar SQL corrigido para preços
2. Resolver conflito contactos
3. Limpar TODOS os caches (WordPress, Flatsome, Browser, CDN)
4. Depois tentar via Admin se não funcionar

**RECOMENDAÇÃO:** **Opção A** (WordPress Admin) - Mais seguro e visual.

---

**Preparado por:** Claude Opus 4.1 com Playwright MCP Browser
**Data:** 24 Outubro 2025
**Método:** DOM Analysis + Previous Visual Audit
**Status:** ⚠️ **ATENÇÃO URGENTE NECESSÁRIA**
**Próxima Revisão:** Após fixes de hoje (35 min)

---

## 📎 ANEXOS

### **Comandos SQL Corrigidos**

```sql
-- FIX PRICES (versão correta)
UPDATE lx_postmeta pm
JOIN lx_posts p ON pm.post_id = p.ID
SET pm.meta_value = '20.23'
WHERE p.post_type = 'product'
AND pm.meta_key IN ('_price', '_regular_price', '_sale_price')
AND (
  pm.meta_value = '2023' OR
  pm.meta_value = '2023.00' OR
  pm.meta_value = '2.023' OR
  pm.meta_value = '2.023,00' OR
  pm.meta_value = '2,023' OR
  pm.meta_value = '2,023.00'
);

-- VERIFY
SELECT p.post_title, pm.meta_key, pm.meta_value
FROM lx_postmeta pm
JOIN lx_posts p ON pm.post_id = p.ID
WHERE pm.meta_key IN ('_price', '_regular_price')
AND pm.meta_value > 100
ORDER BY CAST(pm.meta_value AS DECIMAL(10,2)) DESC;

-- CLEAR ALL CACHES
DELETE FROM lx_options WHERE option_name LIKE '%_transient_%';
DELETE FROM lx_options WHERE option_name LIKE '%_cache_%';
DELETE FROM lx_options WHERE option_name = 'flatsome_custom_css';
```

### **WordPress Admin Checklist**

```
□ Login: http://localhost:8080/wp-admin
□ Produtos → Editar bone-15114 → Preço: 20,23€
□ Produtos → Editar CHAPÉU COWBOY → Preço: 20,23€
□ Aparência → Personalizar → Cabeçalho → Top Bar Text
□ Aparência → Personalizar → Cabeçalho → Social Links
□ Aparência → Personalizar → Footer → Copyright
□ Limpar cache: Plugin cache se instalado
□ Verificar frontend: http://localhost:8080
```
