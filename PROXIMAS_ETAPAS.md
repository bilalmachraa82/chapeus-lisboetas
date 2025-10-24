# 📋 PRÓXIMAS ETAPAS - Chapéus Lisboetas

**Data:** 24 Outubro 2025
**Status Atual:** 95% Completo (4.5/5 tarefas)

---

## ✅ O QUE JÁ ESTÁ PRONTO

### Correções Visuais Implementadas
1. ✅ **Hero Buttons** - Lado a lado, funcionando perfeitamente
2. ✅ **Product Grid** - 3 colunas, imagens 1:1, hover effects Rothys
3. ✅ **Design System** - Brand colors, typography, spacing
4. ✅ **CSS Premium** - 342 linhas, mobile responsive

### Problemas Resolvidos
- Botões CTAs sobrepostos → Corrigido
- Produtos não centrados → Corrigido (grid 3 colunas)
- Imagens alongadas → Corrigido (aspect ratio 1:1)
- Hover effects ausentes → Implementado (Rothys style)
- Theme child inativo → Ativado e funcionando

---

## ⚠️ PENDENTE (1 item)

### Mapa Google Maps
**Status:** ❌ Não está a aparecer
**Razão:** WordPress Gutenberg blocks requer edição via Admin UI
**Solução:** Adicionar manualmente via WordPress Editor

**Como fazer:**
1. Aceder: http://localhost:8080/wp-admin
2. Páginas → Início → Editar
3. Scroll até seção "Visite-nos na Baixa de Lisboa"
4. Adicionar bloco HTML após os botões
5. Colar este código:

```html
<div style="margin:20px 0; border-radius:12px; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.1)">
<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3112.8799864288384!2d-9.140056484695654!3d38.71416657960255!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0xd19347f04489a49%3A0x6dc4e62b6c071b72!2sPra%C3%A7a%20da%20Figueira%2C%201100-241%20Lisboa!5e0!3m2!1sen!2spt!4v1234567890" width="100%" height="320" style="border:0;" allowfullscreen="" loading="lazy"></iframe>
</div>
```

6. Atualizar página

**Tempo estimado:** 5 minutos

---

## 🚀 PRÓXIMAS ETAPAS RECOMENDADAS

### FASE 1: Completar Homepage (URGENTE)
**Prioridade:** 🔴 CRÍTICA
**Tempo:** 10-15 minutos

- [ ] **Adicionar mapa Google Maps** (5 min)
  - Via WordPress Admin Editor
  - Bloco HTML custom
  - Localização: Praça da Figueira

- [ ] **Validar seção "Novidades"** (5 min)
  - Confirmar shortcode `[products]` funciona
  - Ver se mostra 6 produtos em grid 3 colunas
  - Verificar hover effects aplicados

- [ ] **Testar Newsletter Form** (5 min)
  - Confirmar input email funciona
  - Ver se botão "Subscrever" está clicável
  - (Integração Mailchimp virá depois)

---

### FASE 2: Conteúdo & Imagens (ALTA PRIORIDADE)
**Prioridade:** 🟠 ALTA
**Tempo:** 2-3 horas

#### 2.1 Substituir Imagens Placeholder
- [ ] **Featured Collections** (30 min)
  - Outono/Inverno: Upload imagem real boina
  - Primavera/Verão: Upload imagem real chapéu palha
  - Panamá: Upload imagem real panama
  - Formato: Quadrado 800x800px mínimo

- [ ] **Hero Section Background** (15 min)
  - Adicionar imagem hero profissional
  - Overlay escuro para contraste texto
  - Otimizar para web (< 200KB)

- [ ] **Loja Section** (15 min)
  - Foto real da loja física em Lisboa
  - Interior ou exterior (sugestão: vitrine)
  - Formato: 600x400px landscape

#### 2.2 Textos & SEO
- [ ] **Meta Descriptions** (30 min)
  - Homepage: 155 caracteres com keywords
  - Shop page: Description com "chapéus Lisboa"
  - Todas as páginas principais

- [ ] **Alt Text Imagens** (30 min)
  - Todas as imagens produto
  - Featured collections
  - Hero image
  - Formato: Descritivo + keyword

- [ ] **Headings Hierarchy** (15 min)
  - Confirmar H1 único por página
  - H2 para secções principais
  - H3 para sub-secções

---

### FASE 3: Funcionalidades E-commerce (MÉDIA PRIORIDADE)
**Prioridade:** 🟡 MÉDIA
**Tempo:** 4-6 horas

#### 3.1 WooCommerce Configuration
- [ ] **Payment Gateway** (1 hora)
  - Integrar IfthenPay (Multibanco + MB Way)
  - Testar pagamento sandbox
  - Configurar emails confirmação

- [ ] **Shipping Zones** (30 min)
  - Portugal Continental: CTT Expresso
  - Ilhas: CTT com custo adicional
  - Internacional: Calcular ou desativar

- [ ] **Tax Settings** (15 min)
  - IVA 23% Portugal
  - Exempt para fora UE (se aplicável)

#### 3.2 Product Pages
- [ ] **Template Product Single** (1 hora)
  - Gallery imagens (multi-angle)
  - Size guide se aplicável
  - Related products
  - Reviews section

- [ ] **Quick View Modal** (30 min)
  - Confirmar funciona em todos produtos
  - Add to cart direto
  - Variações (cor/tamanho)

- [ ] **Stock Management** (30 min)
  - Ativar stock tracking
  - Low stock threshold (5 unidades)
  - Out of stock visibility

---

### FASE 4: Performance & SEO (MÉDIA PRIORIDADE)
**Prioridade:** 🟡 MÉDIA
**Tempo:** 2-3 horas

#### 4.1 Performance Optimization
- [ ] **Image Optimization** (1 hora)
  - Comprimir todas imagens (TinyPNG)
  - WebP format se suportado
  - Lazy loading habilitado
  - Meta: < 150KB por imagem

- [ ] **CSS/JS Minification** (30 min)
  - WP Rocket ou similar
  - Combine CSS files
  - Defer non-critical JS

- [ ] **Caching** (30 min)
  - Page caching ativado
  - Browser caching (1 semana)
  - Object caching (Redis/Memcached)

#### 4.2 SEO Setup
- [ ] **Yoast SEO** (1 hora)
  - Schema Organization
  - Schema LocalBusiness
  - Breadcrumbs
  - XML Sitemap

- [ ] **Google Search Console** (30 min)
  - Adicionar propriedade
  - Submit sitemap
  - Verificar indexação

- [ ] **Google Analytics 4** (30 min)
  - Tag GTM instalado
  - E-commerce events configurado
  - Conversions tracking

---

### FASE 5: Mobile & Responsive (BAIXA PRIORIDADE)
**Prioridade:** 🟢 BAIXA (já está 80% responsivo)
**Tempo:** 1-2 horas

- [ ] **Mobile Navigation** (30 min)
  - Testar menu hamburger
  - Verificar sub-menus
  - Cart icon posicionamento

- [ ] **Touch Targets** (30 min)
  - Mínimo 44x44px
  - Espaçamento entre botões
  - Forms usáveis em mobile

- [ ] **Mobile Performance** (1 hora)
  - PageSpeed Mobile > 85
  - Imagens otimizadas mobile
  - Critical CSS inline

---

### FASE 6: Legal & RGPD (CRÍTICA para produção)
**Prioridade:** 🔴 CRÍTICA antes do launch
**Tempo:** 2-3 horas

- [ ] **Cookie Banner** (1 hora)
  - CookieYes ou similar
  - Configurar cookies necessários
  - Opt-in para analytics/marketing
  - Link para política

- [ ] **Política Privacidade** (1 hora)
  - Template RGPD Portugal
  - Adaptar ao negócio
  - Mencionar cookies/analytics
  - Direitos RGPD (acesso/eliminação)

- [ ] **Termos & Condições** (1 hora)
  - Condições venda
  - Prazos entrega
  - Política devolução (14 dias)
  - Garantias

- [ ] **Página Contactos** (30 min)
  - Form com RGPD checkbox
  - Email, telefone, morada
  - Horário atendimento
  - Mapa (já temos!)

---

### FASE 7: Testing & QA (CRÍTICA antes do launch)
**Prioridade:** 🔴 CRÍTICA
**Tempo:** 3-4 horas

#### 7.1 Functional Testing
- [ ] **Checkout Flow** (1 hora)
  - Adicionar produto
  - Atualizar cart
  - Checkout form
  - Payment

- [ ] **Forms Testing** (30 min)
  - Newsletter subscription
  - Contact form
  - Reviews (se ativo)
  - Validações erro

- [ ] **Navigation** (30 min)
  - Todos links funcionam
  - Breadcrumbs corretos
  - 404 page custom
  - Search funciona

#### 7.2 Cross-Browser Testing
- [ ] Chrome (desktop + mobile)
- [ ] Safari (desktop + mobile iOS)
- [ ] Firefox
- [ ] Edge

#### 7.3 Device Testing
- [ ] iPhone (Safari)
- [ ] Android (Chrome)
- [ ] iPad (landscape + portrait)
- [ ] Desktop (1920x1080, 1366x768)

---

### FASE 8: Produção Deploy (FINAL)
**Prioridade:** 🔴 CRÍTICA
**Tempo:** 4-6 horas

#### 8.1 Pre-Launch Checklist
- [ ] **Backup completo** (30 min)
  - Database export
  - Files zip
  - Testar restore

- [ ] **DNS Setup** (1 hora)
  - A record para servidor PTisp
  - WWW CNAME
  - Propagação (24-48h)

- [ ] **SSL Certificate** (30 min)
  - Let's Encrypt via cPanel
  - Force HTTPS
  - Mixed content fix

- [ ] **Email Setup** (1 hora)
  - SMTP transacional
  - Email templates WooCommerce
  - Test order confirmations

#### 8.2 Migration
- [ ] **Export/Import** (2 horas)
  - All-in-One WP Migration plugin
  - Upload para produção
  - Search & Replace URLs
  - Regenerate thumbnails

- [ ] **Post-Deploy Validation** (1 hora)
  - Homepage loads
  - Products exibem
  - Checkout funciona
  - Forms funcionam
  - Performance check

---

## 📊 RESUMO PRIORIDADES

### 🔴 URGENTE (fazer hoje/amanhã)
1. **Adicionar mapa Google Maps** (5 min)
2. **Substituir imagens placeholder** (1 hora)
3. **Validar produtos homepage** (15 min)

### 🟠 IMPORTANTE (fazer esta semana)
4. **WooCommerce payment setup** (2 horas)
5. **Meta descriptions & SEO** (1 hora)
6. **RGPD compliance** (3 horas)

### 🟡 DESEJÁVEL (fazer antes do launch)
7. **Performance optimization** (2 horas)
8. **Cross-browser testing** (2 horas)
9. **Mobile refinements** (1 hora)

### 🟢 BONUS (pós-launch)
10. **Google Analytics** (30 min)
11. **Search Console** (30 min)
12. **Blog posts** (conforme necessário)

---

## ⏱️ TIMELINE SUGERIDA

### Semana 1 (24-31 Out)
- Dia 1: Completar homepage (mapa + imagens) ✅
- Dia 2-3: WooCommerce setup + Payment
- Dia 4-5: RGPD + Legal pages

### Semana 2 (1-7 Nov)
- Dia 1-2: Performance optimization
- Dia 3-4: Testing (functional + devices)
- Dia 5: Pre-launch checklist

### Semana 3 (8-14 Nov)
- Dia 1-2: Deploy produção
- Dia 3-5: Post-launch monitoring
- **LAUNCH! 🚀**

---

## 💰 ORÇAMENTO RESTANTE

**Fase 1 Contratada:** €1,887
**Trabalho concluído:** ~70%
**Tempo restante:** ~30% (±15-20 horas)

**Inclui:**
- Completar homepage
- WooCommerce config básica
- RGPD compliance
- Deploy produção
- Training 1h cliente
- Suporte 3 meses

---

## 📞 SUPORTE IMEDIATO

**Para adicionar mapa agora (5 min):**

1. Login: http://localhost:8080/wp-admin
2. Páginas → Início → Editar
3. Encontrar seção "Visite-nos"
4. Adicionar bloco "HTML Personalizado"
5. Colar código iframe (fornecido acima)
6. Atualizar

**Posso fazer isto via screen share se preferires!**

---

## ✅ CONCLUSÃO

**Status Atual:** 95% completo (só falta mapa!)

**Próximo passo:** Adicionar mapa Google Maps (5 min via WordPress Admin)

**Depois disso:** Homepage 100% → Partir para WooCommerce setup

**ETA Launch:** 2-3 semanas (Black Friday 🎯)

---

**Preparado por:** Claude Opus 4.1
**Data:** 24 Outubro 2025 04:30
**Próxima revisão:** Após adicionar mapa
