# Guia de Implementação Sistema Bilingue PT/EN
## Chapéus Lisboetas - Passo a Passo Completo

**Data:** 23 Outubro 2025
**Status:** Pronto para executar
**Tempo estimado:** 3-4 horas

---

## CONTEXTO DA IMPLEMENTAÇÃO

### Situação Descoberta

**Database atual:**
- WPML versão 3.1.9.4 (2015) - tabelas presentes mas plugins removidos
- 127 "traduções" vazias (NULL) - sem valor a preservar
- Transposh instalado e ativo, mas configurado errado (EN default)
- Conteúdo em inglês (17 páginas + 131 produtos)

**Decisão tomada:**
✅ **OPÇÃO 1** - Limpar WPML completamente e usar Transposh (free)

**Justificativa:**
- Traduções WPML estão vazias (NULL) - nada a perder
- WPML custaria €258/ano (orçamento apertado)
- Transposh suficiente para turistas PT/EN
- Timeline curta (Black Friday chegando)

---

## FASE 1: BACKUP E PREPARAÇÃO (15 min)

### 1.1 Backup Completo Database

```bash
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

# Backup database (54MB)
docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web > backup_pre_cleanup_$(date +%Y%m%d_%H%M%S).sql

# Verificar backup
ls -lh backup_pre_cleanup_*.sql | tail -1

# Resultado esperado: ~54MB
```

**Status:** ✅ Backup já criado (backup_pre_transposh_20251023_full.sql)

---

### 1.2 Backup Arquivos WordPress (Opcional)

```bash
# Backup wp-content (se quiser segurança extra)
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"
tar -czf backup_wp_content_$(date +%Y%m%d).tar.gz wordpress/wp-content/

# Resultado esperado: ~400MB
```

---

## FASE 2: LIMPAR WPML (30 min)

### 2.1 Executar Script de Limpeza

```bash
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

# Executar script SQL de limpeza
docker exec -i chapeus_mysql mysql -u root -prootpassword lisboetas_web < scripts/cleanup_wpml_database.sql

# Verificar limpeza bem-sucedida
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "SELECT COUNT(*) as 'Tabelas ICL' FROM information_schema.tables WHERE table_schema = 'lisboetas_web' AND table_name LIKE 'lx_icl_%';" 2>/dev/null

# Resultado esperado: Tabelas ICL: 0
```

---

### 2.2 Verificar Limpeza

```bash
# Confirmar remoção tabelas WPML
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "SHOW TABLES LIKE 'lx_icl_%';" 2>/dev/null

# Resultado esperado: Empty set (sem resultados)

# Confirmar remoção opções WPML
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "SELECT COUNT(*) FROM lx_options WHERE option_name LIKE '%wpml%' OR option_name LIKE '%icl%';" 2>/dev/null

# Resultado esperado: COUNT(*) = 0
```

---

## FASE 3: CONFIGURAR TRANSPOSH (30 min)

### 3.1 Aplicar Configuração PT/EN

```bash
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

# Executar script de configuração Transposh
docker exec -i chapeus_mysql mysql -u root -prootpassword lisboetas_web < scripts/configure_transposh_pt_en.sql

# Verificar configuração
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "SELECT option_value FROM lx_options WHERE option_name = 'WPLANG';" 2>/dev/null

# Resultado esperado: pt_PT
```

---

### 3.2 Flush Rewrite Rules (Permalinks)

```bash
# Rebuild permalinks para URLs /en/
docker exec chapeus_wordpress php -r "require '/var/www/html/wp-load.php'; flush_rewrite_rules(); echo 'Permalinks flushed\n';"

# Resultado esperado: Permalinks flushed
```

---

### 3.3 Verificar Transposh via WordPress Admin

1. **Abrir:** http://localhost:8080/wp-admin
2. **Login:** lisboetas / [senha do cliente]
3. **Ir para:** Configurações → Transposh
4. **Verificar:**
   - ✅ Default language: Português (pt)
   - ✅ Viewable languages: pt, en
   - ✅ Enable permalinks: ✓ checked
   - ✅ Auto-translate: ✓ checked
   - ✅ Enable auto-detection: ✓ checked

**Screenshot:** Capturar tela de configuração

---

## FASE 4: LANGUAGE SWITCHER NO HEADER (1h)

### 4.1 Método 1: Widget Transposh (Mais Fácil)

**Via WordPress Admin:**

1. **Aparência → Widgets**
2. Encontrar widget **"Translation"** (Transposh)
3. Arrastar para área **"Header"** ou **"Top Bar"**
4. Configurações:
   - Title: (vazio ou "Idioma / Language")
   - Widget theme: ui-lightness
5. **Salvar**

**Testar:**
- Abrir http://localhost:8080/
- Verificar dropdown de idiomas no header
- Clicar "EN" → redireciona para /en/
- Clicar "PT" → volta para /

---

### 4.2 Método 2: Flatsome Header Builder (Mais Elegante)

**Via Flatsome Theme Options:**

1. **Flatsome → Theme Options → Header Builder**
2. Seção **Top Bar** ou **Main Header**
3. Adicionar elemento **HTML/Text**
4. Inserir código:
   ```php
   <?php
   if (function_exists('transposh_widget')) {
     echo '<div class="language-switcher">';
     transposh_widget(array(
       'title' => '',
       'widget_file' => 'default/tpw_default.php'
     ));
     echo '</div>';
   }
   ?>
   ```
5. **Posicionar:** Top right (ao lado carrinho)
6. **Salvar Header**

---

### 4.3 CSS Customizado (Opcional)

**Melhorar visual do switcher:**

```css
/* Flatsome → Theme Options → Advanced → Custom CSS */

/* Language switcher no header */
.language-switcher {
  display: inline-block;
  margin-left: 20px;
}

.language-switcher select {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 5px 10px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.language-switcher select:hover {
  border-color: #333;
}

/* Bandeiras inline */
.language-switcher img {
  vertical-align: middle;
  margin-right: 5px;
}
```

---

## FASE 5: TRADUZIR CONTEÚDO CRÍTICO (3h)

### 5.1 Estratégia de Tradução

**Prioridades:**

1. **Homepage** (mais importante)
2. **Shop / Loja** (categorias produtos)
3. **About Lisboetas** (institucional)
4. **Contact** (atendimento turistas)
5. **Shipping and Handling** (envios)
6. **Return Policy** (devoluções)
7. **FAQs** (suporte)
8. **Sizing Guide** (guia tamanhos)
9. Outras páginas (menor prioridade)

**Método:** Transposh tradução inline

---

### 5.2 Como Traduzir Página (Passo a Passo)

**Exemplo: Homepage**

1. **Abrir versão EN:**
   ```
   http://localhost:8080/en/
   ```

2. **Ativar editor Transposh:**
   - No topo da página, clicar na **bandeira com lápis** (Edit Translation)
   - Ou pressionar **Alt+Shift+E**

3. **Traduzir texto inline:**
   - Clicar em qualquer texto em inglês
   - Aparecer caixa de edição
   - Digitar tradução em português
   - **Salvar:** Ctrl+S ou botão "Save"

4. **Repetir para todos os blocos:**
   - Títulos (H1, H2)
   - Parágrafos
   - Botões CTAs ("Shop Now" → "Ver Loja")
   - Menu items

**Tempo estimado:** 15-20 min por página (páginas simples)

---

### 5.3 Checklist Páginas para Traduzir

**CRÍTICAS (fazer primeiro):**
- [ ] Homepage (/)
- [ ] Shop (/shop/)
- [ ] About Lisboetas (/about-lisboetas/)
- [ ] Contact (/contact/)

**IMPORTANTES (fazer depois):**
- [ ] Shipping and Handling (/delivery/)
- [ ] Return Policy (/return-policy/)
- [ ] FAQs (/frequently-asked-questions/)
- [ ] Sizing Guide (/sizing-guide/)

**SECUNDÁRIAS (opcional agora):**
- [ ] Privacy Policy (/privacy-policy/)
- [ ] Terms of use (/terms-of-use/)
- [ ] Track Order (/track-order/)
- [ ] Blog (/blog/)

**AUTOMÁTICAS (WooCommerce):**
- [ ] Cart (/cart/) - strings via Loco Translate
- [ ] Checkout (/checkout/) - strings via Loco Translate
- [ ] My Account (/my-account/) - strings via Loco Translate
- [ ] Wishlist (/wishlist/) - strings via Loco Translate

---

### 5.4 Traduzir Produtos WooCommerce

**Estratégia:** Auto-tradução + Revisão seletiva

**Produtos prioritários (top 20):**

```bash
# Query para identificar produtos principais
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "SELECT p.ID, p.post_title, pm.meta_value as total_sales FROM lx_posts p LEFT JOIN lx_postmeta pm ON p.ID = pm.post_id AND pm.meta_key = 'total_sales' WHERE p.post_type = 'product' AND p.post_status = 'publish' ORDER BY CAST(IFNULL(pm.meta_value, 0) AS UNSIGNED) DESC LIMIT 20;" 2>/dev/null
```

**Processo:**

1. **Auto-tradução (131 produtos):**
   - Transposh traduz automaticamente ao visitar /en/produto/nome/
   - Google Translate API (free, 500k chars/mês)

2. **Revisão manual (top 20):**
   - Abrir /en/product/nome-produto/
   - Ativar editor Transposh (Alt+Shift+E)
   - Revisar e corrigir:
     - Nome produto
     - Descrição curta (aparece na página produto)
     - Atributos (Tamanho, Cor, Material)
   - Salvar

**Tempo estimado:**
- Auto-tradução: instantânea
- Revisão top 20: 5-10 min cada = 2-3h total

---

## FASE 6: STRINGS WOOCOMMERCE (2h)

### 6.1 Instalar/Verificar Loco Translate

**Via WordPress Admin:**

1. **Plugins → Installed Plugins**
2. Verificar **Loco Translate** está ativo
3. Se não estiver: Plugins → Add New → Buscar "Loco Translate" → Instalar → Ativar

---

### 6.2 Traduzir WooCommerce EN

**Passos:**

1. **Loco Translate → Plugins**
2. Selecionar **"WooCommerce"**
3. Clicar **"+ New language"**
4. Escolher:
   - Language: **English (UK)** ou **English (US)**
   - Location: `/wp-content/languages/plugins/`
5. **Start translating**

---

### 6.3 Strings Críticas WooCommerce (PT → EN)

**Interface Loja:**
```
PT                          → EN
"Adicionar ao carrinho"    → "Add to cart"
"Carrinho"                 → "Cart"
"Finalizar compra"         → "Checkout"
"A Minha Conta"            → "My Account"
"Produtos"                 → "Products"
"Categorias"               → "Categories"
"Preço"                    → "Price"
"Em stock"                 → "In stock"
"Esgotado"                 → "Out of stock"
"Procurar produtos"        → "Search products"
```

**Checkout:**
```
"Detalhes de faturação"    → "Billing details"
"Informações adicionais"   → "Additional information"
"A sua encomenda"          → "Your order"
"Métodos de pagamento"     → "Payment methods"
"Efetuar encomenda"        → "Place order"
"Cupão"                    → "Coupon"
"Aplicar cupão"            → "Apply coupon"
"Subtotal"                 → "Subtotal"
"Envio"                    → "Shipping"
"Total"                    → "Total"
```

**My Account:**
```
"Encomendas"               → "Orders"
"Downloads"                → "Downloads"
"Endereços"                → "Addresses"
"Detalhes da conta"        → "Account details"
"Terminar sessão"          → "Logout"
"Ver encomenda"            → "View order"
"Detalhes de envio"        → "Shipping address"
```

**Notas de encomenda:**
```
"Olá"                      → "Hello"
"Obrigado pela sua compra" → "Thank you for your purchase"
"Encomenda nº"             → "Order #"
"Data"                     → "Date"
"Estado"                   → "Status"
```

**Tempo estimado:** 90-120 min (100-150 strings)

---

### 6.4 Traduzir Flatsome Theme EN

**Passos:**

1. **Loco Translate → Themes**
2. Selecionar **"Flatsome"**
3. **+ New language** → English (UK)
4. Traduzir strings tema:
   - Botões
   - Breadcrumbs
   - Navegação
   - Footer

**Strings principais:**
```
"Início"                   → "Home"
"Loja"                     → "Shop"
"Sobre"                    → "About"
"Contacto"                 → "Contact"
"Pesquisar..."             → "Search..."
"Menu"                     → "Menu"
"Filtros"                  → "Filters"
"Ordenar por"              → "Sort by"
```

**Tempo estimado:** 30-45 min

---

## FASE 7: TESTES E VALIDAÇÃO (1h)

### 7.1 Testes Funcionais

**Checklist navegação:**

```bash
# Testar URLs PT
curl -I http://localhost:8080/ | grep HTTP
curl -I http://localhost:8080/shop/ | grep HTTP
curl -I http://localhost:8080/about-lisboetas/ | grep HTTP

# Testar URLs EN
curl -I http://localhost:8080/en/ | grep HTTP
curl -I http://localhost:8080/en/shop/ | grep HTTP
curl -I http://localhost:8080/en/about-lisboetas/ | grep HTTP

# Resultado esperado: HTTP/1.1 200 OK
```

**Navegação manual:**

- [ ] Language switcher aparece no header
- [ ] Clique PT → redireciona para /
- [ ] Clique EN → redireciona para /en/
- [ ] Navegação em /en/ mantém idioma (links apontam /en/*)
- [ ] Produtos em /en/product/ mostram textos em inglês
- [ ] Categorias traduzidas
- [ ] Menu navegação em inglês
- [ ] Footer em inglês

---

### 7.2 Testes WooCommerce

**Processo de compra em EN:**

1. **Abrir:** http://localhost:8080/en/shop/
2. **Adicionar produto ao carrinho:** botão "Add to cart" (não "Adicionar ao carrinho")
3. **Ver carrinho:** /en/cart/ com interface em inglês
4. **Checkout:** /en/checkout/ com labels em inglês
5. **My Account:** /en/my-account/ em inglês

**Verificar:**
- [ ] Botões WooCommerce em inglês
- [ ] Labels formulários em inglês
- [ ] Breadcrumbs em inglês
- [ ] Mensagens erro/sucesso em inglês

---

### 7.3 Testes SEO

**Hreflang tags:**

```bash
# Verificar tags hreflang no HTML
curl -s http://localhost:8080/ | grep hreflang

# Resultado esperado:
# <link rel="alternate" hreflang="pt" href="http://localhost:8080/" />
# <link rel="alternate" hreflang="en" href="http://localhost:8080/en/" />
# <link rel="alternate" hreflang="x-default" href="http://localhost:8080/" />
```

**Sitemap XML:**

1. **Yoast SEO → General → Features**
2. Verificar **"XML sitemaps"** está ativo
3. Abrir: http://localhost:8080/sitemap_index.xml
4. Verificar entradas:
   - /sitemap.xml (PT)
   - /en/sitemap.xml (EN)

---

### 7.4 Testes Performance

**Cache Transposh:**

1. **WordPress Admin → Transposh → Advanced**
2. Verificar **"Cache translations"** está ativo
3. **Clear cache** (primeira vez)
4. Navegar /en/ várias vezes
5. Verificar tempo carregamento (deve ser rápido após 2ª visita)

**LiteSpeed Cache + Transposh:**

1. **LiteSpeed Cache → Settings → Cache**
2. Verificar **"Cache Logged-in Users"** desativado (conflito Transposh editor)
3. **"Separate Cache by Cookies"** → adicionar: `transposh_lc` (cookie idioma)

---

## FASE 8: DOCUMENTAÇÃO CLIENTE (30 min)

### 8.1 Manual Rápido (1 página)

**Criar documento:** `MANUAL_BILINGUE_CLIENTE.pdf`

**Conteúdo:**

1. **Como traduzir nova página:**
   - Criar página em PT
   - Abrir /en/nome-pagina/
   - Clicar bandeira editor (Alt+Shift+E)
   - Traduzir inline
   - Salvar (Ctrl+S)

2. **Como traduzir novo produto:**
   - Criar produto em PT
   - Transposh traduz automaticamente ao abrir /en/product/nome/
   - Se precisar melhorar: Alt+Shift+E → editar → Salvar

3. **Como editar strings WooCommerce:**
   - WordPress Admin → Loco Translate → Plugins → WooCommerce
   - Editar tradução EN
   - Salvar .po file

4. **Troubleshooting:**
   - Language switcher não aparece → verificar Widget ativo
   - URLs /en/ não funcionam → Configurações → Permalinks → Salvar
   - Tradução não salva → verificar permissões database

---

### 8.2 Vídeo Tutorial (Opcional)

**Gravar screencast 5-10 min:**

1. Demonstrar tradução de página inline
2. Demonstrar adição de novo produto (auto-tradução)
3. Mostrar onde editar strings WooCommerce (Loco Translate)

**Ferramenta:** QuickTime (Mac) ou OBS Studio

---

## FASE 9: DEPLOY PRODUÇÃO (Futuro)

**Quando o site for para produção:**

### 9.1 Exportar Traduções (Local → Produção)

```bash
# Exportar database Transposh
docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web \
  --tables lx_options lx_postmeta lx_termmeta \
  --where="option_name LIKE '%transposh%' OR meta_key LIKE '%transposh%'" \
  > transposh_translations_export.sql

# Importar em produção
mysql -u username -p database_producao < transposh_translations_export.sql
```

---

### 9.2 Atualizar URLs Produção

```sql
-- Atualizar siteurl e home
UPDATE lx_options
SET option_value = 'https://chapeuslisboetas.com'
WHERE option_name IN ('siteurl', 'home');

-- Flush rewrite rules
-- Via WP-CLI: wp rewrite flush --allow-root
```

---

### 9.3 Verificar hreflang Produção

```bash
# Trocar localhost por domínio real
curl -s https://chapeuslisboetas.com/ | grep hreflang

# Resultado esperado:
# <link rel="alternate" hreflang="pt" href="https://chapeuslisboetas.com/" />
# <link rel="alternate" hreflang="en" href="https://chapeuslisboetas.com/en/" />
```

---

## RESUMO TIMELINE

| Fase | Tarefa | Tempo | Responsável |
|------|--------|-------|-------------|
| 1 | Backup database + arquivos | 15 min | Dev |
| 2 | Limpar WPML database | 30 min | Dev |
| 3 | Configurar Transposh PT/EN | 30 min | Dev |
| 4 | Language switcher header | 1h | Dev |
| 5 | Traduzir páginas críticas (4) | 1h | Cliente/Dev |
| 5 | Traduzir outras páginas (7) | 2h | Cliente/Dev |
| 5 | Revisar top 20 produtos | 2h | Cliente |
| 6 | Strings Loco Translate (WC + Flatsome) | 2h | Dev |
| 7 | Testes e validação | 1h | Dev |
| 8 | Documentação cliente | 30 min | Dev |
| **TOTAL** | | **10.5h** | |

**Prazo:** 2-3 dias úteis (~4h/dia)

---

## COMANDOS RÁPIDOS

### Backup
```bash
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"
docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web > backup_$(date +%Y%m%d).sql
```

### Limpar WPML
```bash
docker exec -i chapeus_mysql mysql -u root -prootpassword lisboetas_web < scripts/cleanup_wpml_database.sql
```

### Configurar Transposh
```bash
docker exec -i chapeus_mysql mysql -u root -prootpassword lisboetas_web < scripts/configure_transposh_pt_en.sql
docker exec chapeus_wordpress php -r "require '/var/www/html/wp-load.php'; flush_rewrite_rules();"
```

### Verificar configuração
```bash
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "SELECT option_value FROM lx_options WHERE option_name = 'WPLANG';"
```

### Restaurar backup (se necessário)
```bash
docker exec -i chapeus_mysql mysql -u root -prootpassword lisboetas_web < backup_pre_cleanup_YYYYMMDD.sql
```

---

## NOTAS FINAIS

### O que ESTÁ incluído

✅ Sistema bilingue PT/EN funcional
✅ Language switcher no header
✅ Transposh configurado (auto-tradução Google)
✅ URLs /en/ estruturados (permalinks)
✅ Hreflang SEO tags
✅ Database limpa (sem WPML antigo)
✅ Loco Translate para strings WC/Flatsome
✅ Manual cliente

### O que NÃO está incluído

❌ Tradução 100% manual profissional (usamos Google Translate + revisão)
❌ Terceiro idioma (ES, FR, DE)
❌ Descrições longas 131 produtos (pode fazer depois)
❌ Templates email customizados por idioma
❌ Localização preços/moedas (EUR único)

---

**Preparado por:** Bilal Machraa / AiParaTi
**Para:** Chapéus Lisboeta (Tiago Andrade)
**Versão:** 1.0
**Data:** 23 Outubro 2025
**Status:** Pronto para execução
