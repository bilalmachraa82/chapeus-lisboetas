# Implementação Sistema Bilingue PT/EN - Chapéus Lisboetas

**Data:** 23 Outubro 2025
**Status:** Em implementação
**Sistema:** Transposh Translation Filter (já instalado)

---

## 1. SITUAÇÃO ATUAL

### Plugins Instalados e Ativos
- **Transposh Translation Filter** (ativo) - Sistema de tradução free
- **Loco Translate** (ativo) - Tradução de strings de temas/plugins
- **Yoast SEO** (ativo) - Com suporte WPML/multilíngue integrado
- **WooCommerce** (ativo) - 131 produtos publicados

### Configuração Transposh Atual
```
Idioma default: EN (inglês) ⚠️ PRECISA TROCAR PARA PT
Idiomas visíveis: EN, PT, ES
Autotradução: Ativada (Google Translate API)
Detecção automática: Ativada
Widget: Disponível ("Translation")
```

### Conteúdo Existente
- **17 páginas** publicadas
- **131 produtos** WooCommerce
- **Tema:** Flatsome (com suporte multilíngue)

---

## 2. PLANO DE IMPLEMENTAÇÃO

### FASE 1: Reconfigurar Transposh (PT como default)

**Objetivo:** Inverter PT como idioma principal, EN como secundário

**Ações:**
1. WordPress Admin → Configurações → Transposh
2. Alterar configurações:
   - **Default language:** pt (Português)
   - **Viewable languages:** pt, en (remover ES por enquanto)
   - **Auto-translate:** Manter ativado
   - **Enable permalinks:** Ativar (URLs tipo /en/about/)
   - **Widget:** Configurar no header

**Query SQL alternativa (backup):**
```sql
-- Alterar idioma default para PT
UPDATE lx_options
SET option_value = REPLACE(option_value, 's:16:"default_language";s:2:"en"', 's:16:"default_language";s:2:"pt"')
WHERE option_name = 'transposh_options';

-- Alterar idiomas visíveis para pt,en apenas
UPDATE lx_options
SET option_value = REPLACE(option_value, 's:18:"viewable_languages";s:8:"en,pt,es"', 's:18:"viewable_languages";s:5:"pt,en"')
WHERE option_name = 'transposh_options';

-- Ativar permalinks para URLs /en/
UPDATE lx_options
SET option_value = REPLACE(option_value, 's:17:"enable_permalinks";i:0', 's:17:"enable_permalinks";i:1')
WHERE option_name = 'transposh_options';
```

---

### FASE 2: Adicionar Language Switcher no Header

**Opção A: Widget Transposh no Header (Flatsome)**
1. Aparência → Widgets
2. Encontrar widget "Translation" (Transposh)
3. Adicionar ao "Header" widget area
4. Configurar:
   - Título: vazio ou "Language / Idioma"
   - Theme: ui-lightness (clean dropdown)

**Opção B: Shortcode no Menu (mais elegante)**
1. Aparência → Menus
2. Menu principal (Header Menu)
3. Adicionar item personalizado com shortcode: `[tp_translate]`
4. CSS customizado para estilizar bandeiras

**Opção C: Flatsome Theme Builder (Premium)**
1. Flatsome → Theme Options → Header Builder
2. Adicionar elemento "HTML/Text"
3. Inserir: `<?php do_action('transposh_widget'); ?>`
4. Posicionar: Top right (ao lado carrinho)

---

### FASE 3: Traduzir Conteúdo Essencial (Prioridade)

#### 3.1 Páginas Institucionais (Manual via Transposh)

**Método:** Acessar cada página em /en/ e usar editor inline do Transposh

**Lista de páginas a traduzir:**
- [ ] Homepage / Início → /en/
- [ ] Sobre / About → /en/sobre/
- [ ] Contactos / Contact → /en/contactos/
- [ ] Envios / Shipping → /en/envios/
- [ ] Devoluções / Returns → /en/devolucoes/
- [ ] FAQ → /en/faq/
- [ ] Guia de Tamanhos / Size Guide → /en/guia-tamanhos/
- [ ] Política Privacidade / Privacy Policy → /en/politica-privacidade/
- [ ] Termos e Condições / Terms → /en/termos/
- [ ] Sobre Nós / About Us → /en/sobre-nos/
- [ ] Loja / Shop → /en/loja/

**Processo:**
1. Navegar para http://localhost:8080/en/nome-da-pagina/
2. Transposh mostrará bandeira de tradução
3. Clicar em "Edit Translation" (lápis)
4. Traduzir manualmente cada parágrafo
5. Salvar (Transposh armazena em lx_postmeta)

**Estimativa:** ~2h para 11 páginas (10-15 min cada)

---

#### 3.2 Produtos WooCommerce (131 produtos)

**Estratégia:** Tradução seletiva (apenas campos essenciais)

**Campos a traduzir:**
✅ Nome do produto (Title)
✅ Descrição curta (Short description) - aparece na página de produto
❌ Descrição longa (Long description) - opcional, fazer depois
✅ Categorias (via Loco Translate)
✅ Atributos (Tamanho, Cor, Material)

**Método automatizado com Transposh:**
1. Transposh já traduz automaticamente via Google Translate
2. Revisão manual apenas dos 10-20 produtos principais (bestsellers)
3. Produtos menos vendidos: tradução automática suficiente

**Query para identificar produtos prioritários:**
```sql
-- Top 20 produtos mais vendidos (se houver histórico)
SELECT p.ID, p.post_title, pm.meta_value as total_sales
FROM lx_posts p
LEFT JOIN lx_postmeta pm ON p.ID = pm.post_id AND pm.meta_key = 'total_sales'
WHERE p.post_type = 'product' AND p.post_status = 'publish'
ORDER BY CAST(pm.meta_value AS UNSIGNED) DESC
LIMIT 20;
```

**Estimativa:**
- Automático: 131 produtos traduzidos em segundos (Transposh)
- Revisão manual top 20: ~3h

---

#### 3.3 Strings WooCommerce e Flatsome (Loco Translate)

**Método:** Traduzir strings de interface via Loco Translate

**Passos:**
1. WordPress Admin → Loco Translate → Plugins
2. Selecionar "WooCommerce"
3. Criar nova tradução: English (en_US) ou English (en_GB)
4. Traduzir strings essenciais:

**Strings críticas WooCommerce:**
```
PT → EN
"Adicionar ao carrinho" → "Add to cart"
"Finalizar compra" → "Checkout"
"Carrinho" → "Cart"
"A Minha Conta" → "My Account"
"Produtos" → "Products"
"Categorias" → "Categories"
"Preço" → "Price"
"Em stock" → "In stock"
"Esgotado" → "Out of stock"
"Procurar produtos" → "Search products"
"Entrar" → "Login"
"Sair" → "Logout"
"Encomendas" → "Orders"
"Endereços" → "Addresses"
"Métodos de pagamento" → "Payment methods"
"Envio" → "Shipping"
"Subtotal" → "Subtotal"
"Total" → "Total"
"Continuar a comprar" → "Continue shopping"
```

**Strings Flatsome Theme:**
1. Loco Translate → Themes → Flatsome
2. Criar tradução EN
3. Traduzir:
   - Menu labels
   - Footer text
   - Botões CTA
   - Breadcrumbs

**Estimativa:** ~2h para WooCommerce + Flatsome

---

### FASE 4: Configuração URLs e SEO

#### 4.1 Estrutura de URLs

**Transposh com permalinks ativados:**
```
PT (default):
http://localhost:8080/
http://localhost:8080/sobre/
http://localhost:8080/loja/
http://localhost:8080/produto/boina-inverno/

EN (traduzido):
http://localhost:8080/en/
http://localhost:8080/en/sobre/  (ou /en/about/ se slug traduzido)
http://localhost:8080/en/loja/   (ou /en/shop/)
http://localhost:8080/en/produto/boina-inverno/
```

**Nota:** Transposh NÃO traduz slugs de URL automaticamente (mantém originais PT)

---

#### 4.2 SEO Multilíngue (Yoast + Transposh)

**Hreflang tags automáticos:**
Transposh adiciona automaticamente:
```html
<link rel="alternate" hreflang="pt" href="http://localhost:8080/" />
<link rel="alternate" hreflang="en" href="http://localhost:8080/en/" />
<link rel="alternate" hreflang="x-default" href="http://localhost:8080/" />
```

**Sitemap XML multilíngue:**
- Yoast SEO detecta Transposh automaticamente
- Gera sitemap separado por idioma:
  - sitemap.xml (PT)
  - en/sitemap.xml (EN)

**Meta tags por idioma:**
- Yoast permite editar title/description por idioma
- Aceder página em /en/ e editar meta Yoast normalmente

---

### FASE 5: Testes e Validação

#### 5.1 Checklist Funcional

**Navegação:**
- [ ] Language switcher aparece no header
- [ ] Clique em EN redireciona para /en/
- [ ] Clique em PT volta para /
- [ ] Navegação entre páginas mantém idioma (se em /en/, links apontam /en/*)

**Conteúdo:**
- [ ] Homepage em PT e EN com textos corretos
- [ ] Páginas institucionais traduzidas (11 páginas)
- [ ] Produtos mostram nome/descrição em inglês na versão /en/
- [ ] Categorias de produtos traduzidas
- [ ] Menu de navegação em inglês

**WooCommerce:**
- [ ] Botões "Add to cart" em inglês
- [ ] Página de carrinho em inglês
- [ ] Checkout em inglês
- [ ] Emails transacionais respeitam idioma do pedido
- [ ] My Account em inglês

**SEO:**
- [ ] Tags hreflang presentes no HTML
- [ ] Sitemap XML para EN gerado
- [ ] Meta descriptions em inglês (Yoast)
- [ ] Breadcrumbs em inglês

---

#### 5.2 Testes de URLs

**Comandos de verificação:**
```bash
# Testar URLs PT
curl -I http://localhost:8080/ | grep HTTP
curl -I http://localhost:8080/sobre/ | grep HTTP
curl -I http://localhost:8080/loja/ | grep HTTP

# Testar URLs EN
curl -I http://localhost:8080/en/ | grep HTTP
curl -I http://localhost:8080/en/sobre/ | grep HTTP
curl -I http://localhost:8080/en/loja/ | grep HTTP

# Verificar hreflang
curl -s http://localhost:8080/ | grep hreflang
curl -s http://localhost:8080/en/ | grep hreflang
```

---

#### 5.3 Testes de Performance

**PageSpeed por idioma:**
```bash
# PT
https://pagespeed.web.dev/analysis?url=http://localhost:8080/

# EN
https://pagespeed.web.dev/analysis?url=http://localhost:8080/en/
```

**Cache e otimização:**
- Transposh tem cache interno de traduções
- LiteSpeed Cache já instalado (compatível com Transposh)
- Verificar se cache respeita variação de idioma

---

### FASE 6: Documentação Cliente

#### Manual de Uso do Sistema Bilingue

**Como adicionar/editar tradução de página:**
1. Aceder http://localhost:8080/en/nome-da-pagina/
2. No topo, clicar na bandeira com lápis (Edit Translation)
3. Editar texto diretamente inline
4. Salvar (Ctrl+S ou botão Save)

**Como traduzir novo produto:**
1. Criar produto normalmente em PT
2. Publicar
3. Aceder /en/produto/nome-produto/
4. Transposh traduz automaticamente via Google
5. Se precisar melhorar: clicar Edit Translation e corrigir

**Como traduzir strings de tema/plugin:**
1. WordPress Admin → Loco Translate
2. Selecionar plugin/tema
3. Editar tradução EN
4. Salvar .po file
5. Sync (Loco gera .mo automaticamente)

---

## 3. ALTERNATIVAS AVALIADAS

### Por que NÃO WPML?

**Motivos:**
- **Custo:** €99/ano (licença básica) + €159/ano (WooCommerce Multilingual addon)
- **Complexidade:** Requer instalação manual de 3+ plugins
- **Lock-in:** Dificulta migração futura (traduções em estrutura proprietária)
- **Performance:** 2x queries por página (tabela separada de traduções)

**Transposh vantagens:**
- **Grátis** e open-source
- **Já instalado** e configurado
- **Tradução inline** (mais rápido editar)
- **Google Translate API** integrada (auto-tradução gratuita)
- **Compatível** com WooCommerce e Yoast SEO

---

### Por que NÃO Polylang?

**Motivos:**
- Requer criar duplicata manual de cada página/produto
- 131 produtos = 131 cópias manuais
- Sem auto-tradução (precisa plugin pago "Lingotek")
- Interface mais complexa

---

### Por que SIM Transposh?

**Vantagens para este projeto:**
✅ Já instalado e ativo
✅ Auto-tradução via Google Translate (economiza 80% trabalho manual)
✅ Tradução inline (edit in place)
✅ WooCommerce compatível
✅ Widget pronto para header
✅ Permalalkins /en/ estruturados
✅ Hreflang automático (SEO)
✅ Cache interno (performance)
✅ Free e sem lock-in

**Desvantagens (aceitáveis):**
⚠️ Tradução automática precisa revisão manual (mas rápida)
⚠️ Não traduz slugs de URL (mantém PT em /en/sobre/)
⚠️ Menos features que WPML (mas suficiente para o escopo)

---

## 4. TIMELINE E RECURSOS

### Estimativa de Tempo

| Fase | Tarefa | Tempo | Responsável |
|------|--------|-------|-------------|
| 1 | Reconfigurar Transposh (PT default) | 30 min | Dev |
| 2 | Language switcher no header | 1h | Dev |
| 3.1 | Traduzir 11 páginas institucionais | 2h | Cliente/Dev |
| 3.2 | Revisar top 20 produtos | 3h | Cliente |
| 3.3 | Strings Loco Translate (WooCommerce + Flatsome) | 2h | Dev |
| 4 | SEO e URLs | 1h | Dev |
| 5 | Testes e validação | 2h | Dev |
| 6 | Documentação cliente | 1h | Dev |
| **TOTAL** | | **12.5h** | |

**Prazo:** 2-3 dias úteis (com aprovações cliente)

---

### Recursos Necessários

**Técnicos:**
- Acesso WordPress Admin (lisboetas / mail@chapeuslisboetas.com)
- Acesso SSH/Docker (já disponível)
- Acesso banco de dados (lx_ prefix)

**Conteúdo:**
- Textos institucionais em PT (já existem)
- Revisão traduções automáticas (cliente)
- Aprovação final textos EN (cliente)

**Ferramentas:**
- Transposh Translation Filter (instalado)
- Loco Translate (instalado)
- Google Translate API (free tier - 500k chars/mês)

---

## 5. PRÓXIMOS PASSOS

### Ações Imediatas (Dev)

1. **Reconfigurar Transposh:**
   ```bash
   # Backup database primeiro
   docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web > backup_pre_transposh_$(date +%Y%m%d).sql

   # Aplicar mudanças via Admin ou SQL
   # WordPress Admin → Configurações → Transposh
   ```

2. **Testar language switcher:**
   - Adicionar widget no header
   - Verificar URLs /en/
   - Capturar screenshot

3. **Preparar lista páginas para tradução:**
   ```sql
   SELECT ID, post_title, post_name, post_status, post_modified
   FROM lx_posts
   WHERE post_type = 'page' AND post_status = 'publish'
   ORDER BY post_modified DESC;
   ```

4. **Criar relatório inicial:**
   - Status atual (screenshots)
   - Próximas ações
   - Aguardar aprovação cliente para tradução manual

---

### Aprovações Cliente (Tiago Andrade)

**Perguntas para decidir:**

1. **Tradução automática vs manual:**
   - Top 20 produtos: revisão manual obrigatória?
   - Outros 111 produtos: aceita Google Translate com revisão posterior?

2. **Prioridade páginas:**
   - Quais 5 páginas mais importantes para traduzir primeiro?
   - FAQ precisa estar 100% traduzido no lançamento?

3. **Emails transacionais:**
   - WooCommerce envia emails em PT e EN automaticamente (Transposh)
   - Precisa templates personalizados EN? (extra work)

4. **Conteúdo extra:**
   - Blog posts precisam tradução? (se existirem)
   - Descrições longas de produtos: prioridade ou fazer depois?

---

## 6. MÉTRICAS DE SUCESSO

### KPIs Técnicos (Lançamento)

- [ ] Language switcher visível e funcional
- [ ] 100% páginas institucionais traduzidas
- [ ] 100% produtos com nome/descrição curta EN
- [ ] 0 erros 404 em URLs /en/
- [ ] Hreflang tags presentes
- [ ] Sitemap XML multilíngue gerado

### KPIs Negócio (30 dias)

- **Tráfego EN:** >15% visitantes em inglês
- **Conversão EN:** Similar ou superior a PT
- **Bounce rate EN:** <65% (turistas navegam mais)
- **Tempo sessão EN:** >2min (conteúdo relevante)
- **Pageviews EN:** >2.5 páginas/sessão

### Feedback Cliente

- Facilidade edição traduções (1-5): objetivo >4
- Qualidade traduções automáticas (1-5): objetivo >3
- Tempo para traduzir novo produto: <5min
- Satisfação overall sistema: >4/5

---

## 7. MANUTENÇÃO E SUPORTE

### Incluído (3 meses)

- Correções traduções automáticas
- Ajustes layout language switcher
- Otimização cache multilíngue
- Troubleshooting URLs /en/
- Atualizações Transposh/Loco

### Rotina Cliente (Pós-lançamento)

**Ao adicionar novo produto:**
1. Criar em PT normalmente
2. Acessar /en/produto/nome/
3. Transposh traduz automaticamente
4. Revisar e corrigir se necessário (2-3 min)

**Ao editar página existente:**
1. Editar versão PT
2. Acessar /en/nome-pagina/
3. Transposh atualiza automaticamente
4. Revisar tradução EN (1-2 min)

**Não requer:**
- Criação manual de duplicatas
- Sincronização complexa
- Gestão de categorias separadas
- Manutenção de 2 inventários

---

## 8. RISCOS E MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Tradução automática de baixa qualidade | Alta | Médio | Revisão manual top 20 produtos + páginas críticas |
| Language switcher conflito com tema | Média | Alto | Testar 3 posições alternativas (widget/menu/shortcode) |
| Performance degradada (2 idiomas) | Baixa | Médio | LiteSpeed Cache + Transposh cache ativado |
| URLs /en/ não funcionam (permalinks) | Baixa | Alto | Backup database + teste antes produção |
| Cliente não consegue editar traduções | Média | Médio | Manual passo-a-passo + vídeo tutorial |
| Google Translate API limite atingido | Muito baixa | Baixo | Free tier 500k/mês suficiente + fallback manual |

---

## 9. RECURSOS E REFERÊNCIAS

### Documentação Oficial

- **Transposh:** https://transposh.org/documentation/
- **Loco Translate:** https://localise.biz/wordpress/plugin
- **WooCommerce Multilingual:** https://woocommerce.com/document/woocommerce-multilingual/
- **Yoast SEO Multilingual:** https://yoast.com/help/multilingual-seo/

### Tutoriais Relevantes

- Transposh WooCommerce setup: https://transposh.org/transposh-and-woocommerce/
- Flatsome multilingual: https://flatsome.uxthemes.com/documentation/multilingual/
- Hreflang best practices: https://developers.google.com/search/docs/advanced/crawling/localized-versions

### Comandos Úteis

```bash
# Backup database antes de mudanças
docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web > backup_$(date +%Y%m%d_%H%M%S).sql

# Ver configuração Transposh
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "SELECT option_value FROM lx_options WHERE option_name = 'transposh_options'\\G"

# Listar páginas para traduzir
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "SELECT ID, post_title, post_name FROM lx_posts WHERE post_type='page' AND post_status='publish' ORDER BY post_modified DESC;"

# Listar produtos para traduzir
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "SELECT ID, post_title, post_name FROM lx_posts WHERE post_type='product' AND post_status='publish' LIMIT 20;"

# Flush rewrite rules após mudança permalinks
docker exec chapeus_wordpress php -r "require '/var/www/html/wp-load.php'; flush_rewrite_rules();"

# Rebuild Transposh cache
# WordPress Admin → Transposh → Advanced → Clear Cache
```

---

## 10. NOTAS FINAIS

### Decisão Final: Transposh (não WPML)

**Rationale:**
- Projeto tem budget apertado (WPML = €258/ano extra)
- Transposh já instalado e funcional
- Cliente precisa autonomia (tradução inline é mais simples)
- 80% traduções automáticas aceitáveis (produtos técnicos)
- Foco em turistas (qualidade EN suficiente, não nativo)
- Timeline curta (Black Friday chegando)

### Escopo Claro: O que ESTÁ incluído

✅ Sistema bilingue PT/EN funcional
✅ Language switcher no header
✅ 11 páginas institucionais traduzidas
✅ 131 produtos com nome/descrição curta EN
✅ Interface WooCommerce em inglês
✅ Emails transacionais bilingues
✅ SEO multilíngue (hreflang + sitemap)
✅ Manual cliente para manutenção

### Escopo Claro: O que NÃO está incluído

❌ Terceiro idioma (ES, FR, DE)
❌ Traduções profissionais humanas
❌ Descrições longas 131 produtos (pode fazer depois)
❌ Blog posts multilíngue (se existir blog)
❌ Templates email customizados por idioma
❌ Localização preços/moedas (EUR único)
❌ Atendimento cliente bilingue (chatbot)

---

**Preparado por:** Bilal Machraa / AiParaTi
**Para:** Chapéus Lisboeta (Tiago Andrade)
**Versão:** 1.0
**Status:** Aguardando início implementação
**Próximo passo:** Reconfigurar Transposh via WordPress Admin
