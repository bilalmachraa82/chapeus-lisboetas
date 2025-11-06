# ✅ CHECKLIST: Site Chapéus Lisboetas - 100% Online

**Objetivo:** Levar site de localhost → produção (PTisp hosting) **ANTES da Black Friday**

**Status atual:** ~75% completo | Faltam ~2-3 semanas de trabalho

---

## 📊 PROGRESSO GERAL

| Categoria | Status | Progresso |
|-----------|--------|-----------|
| **Design & UX** | ✅ 95% | P0 completo, P1 pendente |
| **Conteúdo** | ⚠️ 60% | Faltam produtos + páginas |
| **WooCommerce** | ❌ 40% | Configuração básica OK, faltam integrações |
| **SEO & Performance** | ⚠️ 50% | Básico OK, falta otimização |
| **Legal & RGPD** | ❌ 30% | Estrutura criada, falta conteúdo |
| **Hosting & Deploy** | ❌ 0% | Ainda não iniciado |

---

## 🎨 1. DESIGN & UX [95% ✅]

### ✅ Completo
- [x] Hero section otimizado (overlay, contrast WCAG AAA)
- [x] CTAs terracota (#E07A31) - client approved
- [x] Top fold padding optimized (58vh desktop, 460px mobile)
- [x] Solid secondary buttons (wheat background)
- [x] Blog images fixed (5 posts com featured images)
- [x] "Loja física · Baixa de Lisboa" text size increased (20px, weight 600)
- [x] Parallax scrolling implemented
- [x] Lazy loading images
- [x] Mobile responsive (375px, 414px tested)
- [x] AOS animations

### ⚠️ Pendente (P1 - Esta semana)
- [ ] **Zebra backgrounds** (.section-zebra alternating sections)
- [ ] **Social proof badge** antes da secção Instagram
- [ ] **"Ver todas as coleções"** CTA após featured collections
- [ ] **Micro-CTAs "Saber mais"** nos icon boxes
- [ ] **Hero image preload** (`<link rel="preload">` para LCP)
- [ ] **Newsletter left-align** (desktop) mantendo centralizado mobile

### 📝 WordPress Integration Needed
```bash
# Estas mudanças requerem edição no UX Builder:
1. Adicionar classes .section-zebra manualmente OU
2. Executar script JavaScript (já criado em custom.js)
3. Adicionar HTML para badges/CTAs (já criado em functions.php)
```

---

## 📦 2. PRODUTOS & CATÁLOGO [40% ⚠️]

### ✅ Completo
- [x] 62 produtos no catalogo.json com preços
- [x] 54 produtos validados (clean & ready)
- [x] Imagens organizadas em output_catalogo/images/
- [x] Google Sheet integrado (17 categorias)
- [x] Scripts de sincronização funcionais

### ❌ CRÍTICO - Falta Fazer
- [ ] **Importar 54 produtos para WooCommerce**
  - CSV ready: `output_catalogo/catalogo_clean_ready.csv`
  - Via: WooCommerce → Products → Import
  - Tempo estimado: 2-3 horas (manual review de cada produto)

- [ ] **Atribuir imagens aos produtos**
  - Método 1: Upload manual via Media Library
  - Método 2: Script PHP de import automático
  - Tempo: 3-4 horas

- [ ] **Configurar variações de produto**
  - SKUs com letras (18456-A, 18456-B) = variações
  - Atributos: Cor, Tamanho, Material
  - Tempo: 2-3 horas

- [ ] **Criar categorias WooCommerce**
  - Boinas Inverno, Boinas Verão, Panamá (prioridade)
  - Estrutura hierárquica: Chapéus > Boinas > Inverno
  - Tempo: 1 hora

- [ ] **Stock management**
  - Definir quantidades iniciais
  - Ativar "out of stock" notifications
  - Tempo: 1 hora

---

## 💳 3. WOOCOMMERCE & PAGAMENTOS [40% ⚠️]

### ✅ Completo
- [x] WooCommerce instalado e ativado
- [x] Moeda: EUR (€)
- [x] Locale: Português (Portugal)
- [x] Basic shop page configurada

### ❌ CRÍTICO - Integrações
- [ ] **IfthenPay Gateway** (OBRIGATÓRIO!)
  - Plugin: https://www.ifthenpay.com/downloads/
  - Configurar: MB Way + Multibanco
  - Taxas: 0.8-1% por transação
  - Account setup: mail@chapeuslisboetas.com
  - Tempo: 2 horas + 1-2 dias aprovação IfthenPay

- [ ] **CTT Expresso Shipping** (OBRIGATÓRIO!)
  - Plugin: WooCommerce CTT
  - API key via CTT portal
  - Automatic tracking numbers
  - Label generation
  - Tempo: 3 horas

- [ ] **Email transacionais**
  - Templates personalizados (logo, cores brand)
  - Order confirmation, shipping, etc.
  - Tempo: 2 horas

- [ ] **Tax settings**
  - IVA 23% Portugal
  - EU VAT rules (se aplicável)
  - Tempo: 1 hora

### ⚠️ Recomendado
- [ ] **Abandoned cart recovery** (plugin)
- [ ] **Product reviews** (ativar + moderar)
- [ ] **Wishlists** (YITH WooCommerce Wishlist - já instalado?)
- [ ] **Cross-sells / Upsells** configurar

---

## 📄 4. PÁGINAS ESSENCIAIS [50% ⚠️]

### ✅ Completo
- [x] Homepage (com hero, collections, Instagram)
- [x] Blog (5 posts com imagens)

### ❌ CRÍTICO - Falta Criar
- [ ] **Sobre Nós**
  - História 75 anos na Baixa
  - Tiago + Sr. Andrade
  - Fotos loja física Praça da Figueira
  - Tempo: 2-3 horas

- [ ] **Contactos**
  - Morada: Praça da Figueira, Lisboa
  - Telefone: +351 918 911 308
  - Email: mail@chapeuslisboetas.com
  - Horário: (confirmar com cliente)
  - Google Maps embed
  - Contact Form 7
  - Tempo: 1-2 horas

- [ ] **Política de Privacidade** (RGPD - OBRIGATÓRIO!)
  - Template legal português
  - Cookies, dados pessoais, direitos RGPD
  - Tempo: 2 horas (adaptar template)

- [ ] **Termos e Condições** (OBRIGATÓRIO!)
  - Compra e venda
  - Devoluções 14 dias (Lei PT)
  - Garantias
  - Tempo: 2 horas

- [ ] **Política de Devoluções**
  - 14 dias Lei Portuguesa
  - Processo de devolução
  - Reembolsos
  - Tempo: 1 hora

- [ ] **Envios e Entregas**
  - CTT Expresso prazos
  - Grátis >50€
  - Custos por zona
  - Tempo: 1 hora

- [ ] **FAQ**
  - Tamanhos chapéus
  - Cuidados e limpeza
  - Devolução/troca
  - Pagamentos aceites
  - Tempo: 2-3 horas

### ⚠️ Recomendado
- [ ] **Guia de Tamanhos**
- [ ] **Como Medir a Cabeça**
- [ ] **Lookbook / Coleções** (páginas dedicadas)

---

## 🔒 5. RGPD & LEGAL [30% ❌]

### ❌ CRÍTICO - OBRIGATÓRIO por lei PT/EU
- [ ] **CookieYes Banner** (ou similar RGPD-compliant)
  - Free tier: https://www.cookieyes.com/
  - Configurar: Estritamente necessários, Analytics, Marketing
  - Tempo: 1 hora

- [ ] **Consent checkboxes**
  - Newsletter opt-in
  - Marketing communications
  - Termos aceites no checkout
  - Tempo: 30 min

- [ ] **Política Privacidade página** (ver acima)

- [ ] **Livro de Reclamações** (OBRIGATÓRIO Portugal!)
  - Link/badge no footer
  - https://www.livroreclamacoes.pt/
  - Tempo: 15 min

### ⚠️ Recomendado
- [ ] **SSL Certificate** (Let's Encrypt via PTisp)
- [ ] **HTTPS redirect** (força HTTPS)
- [ ] **Security headers** (CSP, HSTS)

---

## 🚀 6. SEO & PERFORMANCE [50% ⚠️]

### ✅ Completo
- [x] Yoast SEO instalado
- [x] Meta descriptions homepage
- [x] Image lazy loading
- [x] Parallax otimizado

### ❌ Falta Fazer
- [ ] **SEO On-Page**
  - [ ] Meta title/description para TODAS as páginas
  - [ ] Alt text em TODAS as imagens (>95% coverage)
  - [ ] Schema.org markup:
    - Organization
    - LocalBusiness (loja física)
    - Product (produtos WooCommerce)
    - BreadcrumbList
  - [ ] XML sitemap submission (Google Search Console)
  - Tempo: 4-5 horas

- [ ] **Performance Optimization**
  - [ ] Image compression (TinyPNG ou similar)
  - [ ] WP Rocket cache plugin
  - [ ] Minify CSS/JS
  - [ ] Database optimization
  - [ ] Remove unused plugins
  - Target: PageSpeed >85 mobile, >90 desktop
  - Tempo: 3-4 horas

- [ ] **Google Analytics 4 + GTM**
  - [ ] GA4 property setup
  - [ ] E-commerce tracking events
  - [ ] Conversion goals
  - Tempo: 2 horas

### ⚠️ Recomendado
- [ ] **Bing Webmaster Tools**
- [ ] **Google My Business** (loja física)
- [ ] **Rich snippets testing**

---

## 🌐 7. HOSTING & DEPLOY [0% ❌]

### ❌ CRÍTICO - Deploy para Produção
- [ ] **PTisp Account Setup**
  - [ ] Criar conta (1 ano incluído no orçamento)
  - [ ] Configurar domain: chapeuslisboeta.pt (ou .com?)
  - [ ] SSL certificate (Let's Encrypt)
  - Tempo: 1 hora + 24-48h propagação DNS

- [ ] **WordPress Migration**
  - [ ] Export database (mysqldump)
  - [ ] Upload files via FTP/SFTP
  - [ ] Import database no PTisp
  - [ ] Search & Replace URLs (localhost → production)
  - [ ] Test EVERYTHING!
  - Tempo: 3-4 horas

- [ ] **DNS Configuration**
  - [ ] A record → PTisp IP
  - [ ] MX records (email)
  - [ ] SPF/DKIM records (email deliverability)
  - Tempo: 1 hora

- [ ] **Email Setup**
  - [ ] mail@chapeuslisboetas.com
  - [ ] Configure SMTP for WooCommerce emails
  - Tempo: 1 hora

### ⚠️ Backups (CRÍTICO - cliente perdeu site anterior!)
- [ ] **UpdraftPlus** (backup plugin)
  - Daily backups
  - Remote storage (Google Drive ou Dropbox)
  - 30 days retention
  - Tempo: 30 min

- [ ] **JetBackup** (PTisp hosting - já incluído)
  - Verificar configuração
  - Test restore

---

## 📧 8. EMAIL MARKETING [0% ❌]

### ⚠️ Recomendado (não crítico para launch)
- [ ] **MailChimp Integration**
  - [ ] Newsletter signup form
  - [ ] Welcome automation
  - [ ] Abandoned cart emails
  - Tempo: 2-3 horas

---

## 🧪 9. TESTING [30% ⚠️]

### ❌ PRÉ-LAUNCH - OBRIGATÓRIO
- [ ] **Functional Testing**
  - [ ] Adicionar produto ao carrinho
  - [ ] Checkout completo (test mode)
  - [ ] Pagamento IfthenPay test
  - [ ] Emails recebidos
  - [ ] Admin order management
  - Tempo: 2-3 horas

- [ ] **Browser Testing**
  - [ ] Chrome (desktop + mobile)
  - [ ] Firefox
  - [ ] Safari (iOS)
  - [ ] Edge
  - Tempo: 2 horas

- [ ] **Device Testing**
  - [ ] iPhone SE (375px)
  - [ ] iPhone 12 Pro (414px)
  - [ ] iPad
  - [ ] Desktop 1440px, 1920px
  - Tempo: 2 horas

- [ ] **User Acceptance Testing** (cliente)
  - [ ] Demo completo com Tiago
  - [ ] Corrigir feedback
  - Tempo: 3-4 horas (+ iterações)

---

## 📚 10. DOCUMENTAÇÃO & TRAINING [0% ❌]

### ❌ Entrega ao Cliente
- [ ] **Manual de Administração**
  - [ ] Como adicionar produtos
  - [ ] Como gerir encomendas
  - [ ] Como processar devoluções
  - [ ] Como fazer backups
  - Formato: PDF + vídeo screencast
  - Tempo: 4-5 horas

- [ ] **Sessão de Treino** (1h incluída no orçamento)
  - [ ] Agendar com Tiago
  - [ ] Gravação para referência futura
  - Tempo: 1 hora

---

## 🎯 PRIORIDADES IMEDIATAS (Esta Semana)

### 🔥 SPRINT 1: Produtos & Pagamentos (3-4 dias)
1. ✅ **Importar 54 produtos** para WooCommerce
2. ✅ **Configurar IfthenPay** (iniciar processo aprovação)
3. ✅ **Configurar CTT Expresso**
4. ✅ **Testar checkout end-to-end**

### 🔥 SPRINT 2: Conteúdo & Legal (2-3 dias)
5. ✅ **Criar páginas essenciais** (Sobre, Contactos, FAQ)
6. ✅ **Política Privacidade + Termos** (templates legais PT)
7. ✅ **CookieYes RGPD banner**
8. ✅ **Livro de Reclamações**

### 🔥 SPRINT 3: SEO & Deploy (3-4 dias)
9. ✅ **SEO on-page completo** (meta, alt text, schema)
10. ✅ **Performance optimization** (PageSpeed >85)
11. ✅ **PTisp setup + migration**
12. ✅ **Testing completo**

### 🔥 SPRINT 4: Launch & Training (2 dias)
13. ✅ **UAT com cliente**
14. ✅ **Correções finais**
15. ✅ **Manual + training session**
16. ✅ **GO LIVE! 🚀**

---

## ⏱️ ESTIMATIVA TOTAL

| Fase | Horas | Dias (8h/dia) |
|------|-------|---------------|
| Design P1 (WordPress integration) | 4h | 0.5 |
| Produtos import + config | 12h | 1.5 |
| WooCommerce integrações | 10h | 1.25 |
| Páginas conteúdo | 12h | 1.5 |
| RGPD & Legal | 5h | 0.6 |
| SEO & Performance | 10h | 1.25 |
| Hosting & Deploy | 8h | 1 |
| Testing | 8h | 1 |
| Documentação & Training | 6h | 0.75 |
| **TOTAL** | **75h** | **~10 dias** |

**Com imprevistos e feedback loops:** 12-15 dias úteis = **2-3 semanas**

---

## 🎁 BONUS (Fase 2 - Pós-Launch)

Já incluído no orçamento Fase 2 (€1,348-€1,938):
- [ ] AI Chatbot (Tidio/Elfsight)
- [ ] Product importer automático (web scraper hologrammeparis.com)
- [ ] Instagram feed automation
- [ ] Email marketing avançado
- [ ] Relatórios analytics mensais

---

## 📞 PRÓXIMOS PASSOS

### AGORA (hoje):
1. ✅ Commit P1 changes (zebra, social proof, etc.)
2. ✅ Testar "Loja física · Baixa de Lisboa" text size
3. 📧 **EMAIL CLIENTE:** Enviar este checklist + timeline
4. 🗓️ **AGENDAR:** Reunião sexta-feira 15h (confirmação prioridades)

### ESTA SEMANA:
- Segunda-feira: Importar produtos WooCommerce
- Terça-feira: IfthenPay + CTT setup
- Quarta-feira: Páginas legais + RGPD
- Quinta-feira: SEO on-page
- Sexta-feira: Reunião + UAT prep

### PRÓXIMA SEMANA:
- Deploy PTisp
- Testing intensivo
- Training cliente
- **GO LIVE! 🎉**

---

**Documento criado:** 2025-10-30
**Autor:** Claude Code @ Anthropic
**Cliente:** Chapéus Lisboetas (Tiago Andrade)
**Objetivo:** Black Friday-ready e-commerce site

---

## 🚨 BLOQUEADORES CRÍTICOS

Sem estes, NÃO podemos lançar:

1. ❌ **IfthenPay aprovação** (pode demorar 1-2 dias úteis)
2. ❌ **Domain name** (chapeuslisboeta.pt ou .com? - confirmar com cliente)
3. ❌ **Conteúdo legal** (Termos, Privacidade - pode usar templates)
4. ❌ **Produtos importados** (sem produtos = sem vendas)
5. ❌ **SSL certificate** (HTTPS obrigatório para pagamentos)

**Ação imediata:** Iniciar processo IfthenPay HOJE para não atrasar timeline!

---

✅ **Pronto para revisão com cliente e início dos sprints!**
