# Checklist Sistema Bilingue PT/EN
## Chapéus Lisboetas - Acompanhamento de Implementação

**Data início:** _____________
**Responsável:** Bilal Machraa / AiParaTi
**Cliente:** Tiago Andrade

---

## FASE 1: SETUP TÉCNICO (Dev)

### 1.1 Preparação
- [ ] Docker containers rodando (MySQL + WordPress)
- [ ] Acesso WordPress Admin confirmado
- [ ] Backup database criado (54MB)
- [ ] Scripts SQL verificados

**Data conclusão:** _____________

---

### 1.2 Execução Script Automático
```bash
./scripts/setup_bilingue_pt_en.sh
```

- [ ] Script executado sem erros
- [ ] WPML removido (0 tabelas lx_icl_*)
- [ ] Transposh configurado (PT default)
- [ ] Permalinks /en/ ativados
- [ ] URLs PT testados (200 OK)
- [ ] URLs EN testados (200 OK)

**Data conclusão:** _____________
**Tempo gasto:** _______ min

---

## FASE 2: LANGUAGE SWITCHER (Dev)

### 2.1 Adicionar Widget Header
- [ ] WordPress Admin → Aparência → Widgets
- [ ] Widget "Translation" encontrado
- [ ] Arrastado para área "Header"
- [ ] Configurado (título vazio, theme ui-lightness)
- [ ] Salvo

**OU Método alternativo:**
- [ ] Flatsome Header Builder usado
- [ ] Shortcode/HTML adicionado
- [ ] Posicionado top right

---

### 2.2 Testes Switcher
- [ ] Dropdown aparece no header
- [ ] Bandeiras PT/EN visíveis
- [ ] Clique EN → redireciona /en/
- [ ] Clique PT → volta /
- [ ] Navegação mantém idioma

**Data conclusão:** _____________
**Screenshot:** [ ] Anexado

---

## FASE 3: TRADUÇÃO PÁGINAS (Cliente/Dev)

### 3.1 Páginas Críticas (Prioridade Máxima)

**Homepage (/):**
- [ ] Aberto /en/
- [ ] Editor ativado (Alt+Shift+E)
- [ ] Título traduzido
- [ ] Textos principais traduzidos
- [ ] Botões CTAs traduzidos
- [ ] Salvo e testado

**Responsável:** _____________
**Data:** _____________

---

**About Lisboetas (/about-lisboetas/):**
- [ ] Traduzido inline
- [ ] História marca em inglês
- [ ] Valores/missão traduzidos
- [ ] Salvo e testado

**Responsável:** _____________
**Data:** _____________

---

**Contact (/contact/):**
- [ ] Formulário traduzido
- [ ] Informações contato
- [ ] Horários/morada
- [ ] Mapa (se aplicável)
- [ ] Salvo e testado

**Responsável:** _____________
**Data:** _____________

---

**Shop (/shop/):**
- [ ] Categorias traduzidas
- [ ] Filtros traduzidos
- [ ] Breadcrumbs traduzidos
- [ ] Salvo e testado

**Responsável:** _____________
**Data:** _____________

---

### 3.2 Páginas Importantes

- [ ] Shipping and Handling (/delivery/)
- [ ] Return Policy (/return-policy/)
- [ ] FAQs (/frequently-asked-questions/)
- [ ] Sizing Guide (/sizing-guide/)

**Tempo total:** _______ h
**Data conclusão:** _____________

---

### 3.3 Páginas Secundárias (Opcional agora)

- [ ] Privacy Policy (/privacy-policy/)
- [ ] Terms of use (/terms-of-use/)
- [ ] Track Order (/track-order/)
- [ ] Blog (/blog/)

**Status:** [ ] Feito agora  [ ] Fazer depois

---

## FASE 4: PRODUTOS (Cliente)

### 4.1 Auto-Tradução (Automática)
- [ ] Verificado que Transposh auto-traduz ao abrir /en/product/
- [ ] Testado com 3-5 produtos aleatórios
- [ ] Qualidade tradução aceitável

**Observações:**
_________________________________________________________
_________________________________________________________

---

### 4.2 Identificar Top 20 Produtos

**Query executada:**
```sql
SELECT p.ID, p.post_title, pm.meta_value as total_sales
FROM lx_posts p
LEFT JOIN lx_postmeta pm ON p.ID = pm.post_id AND pm.meta_key = 'total_sales'
WHERE p.post_type = 'product' AND p.post_status = 'publish'
ORDER BY CAST(IFNULL(pm.meta_value, 0) AS UNSIGNED) DESC
LIMIT 20;
```

**Top 20 identificados:**
- [ ] Lista exportada para CSV
- [ ] Prioridade definida

---

### 4.3 Revisão Manual Top 20

| # | Produto | EN URL | Traduzido? | Revisado? | Data |
|---|---------|--------|------------|-----------|------|
| 1 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 2 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 3 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 4 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 5 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 6 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 7 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 8 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 9 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 10 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 11 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 12 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 13 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 14 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 15 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 16 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 17 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 18 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 19 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |
| 20 | _________________ | /en/product/______ | [ ] | [ ] | __/__/__ |

**Tempo total:** _______ h
**Data conclusão:** _____________

---

## FASE 5: STRINGS WOOCOMMERCE (Dev)

### 5.1 Loco Translate - WooCommerce

**Acesso:**
- [ ] WordPress Admin → Loco Translate → Plugins
- [ ] WooCommerce selecionado
- [ ] Nova tradução EN criada

---

**Strings Interface Loja (15 strings):**
- [ ] "Adicionar ao carrinho" → "Add to cart"
- [ ] "Carrinho" → "Cart"
- [ ] "Finalizar compra" → "Checkout"
- [ ] "A Minha Conta" → "My Account"
- [ ] "Produtos" → "Products"
- [ ] "Categorias" → "Categories"
- [ ] "Preço" → "Price"
- [ ] "Em stock" → "In stock"
- [ ] "Esgotado" → "Out of stock"
- [ ] "Procurar produtos" → "Search products"
- [ ] "Entrar" → "Login"
- [ ] "Sair" → "Logout"
- [ ] "Encomendas" → "Orders"
- [ ] "Endereços" → "Addresses"
- [ ] "Ver encomenda" → "View order"

---

**Strings Checkout (10 strings):**
- [ ] "Detalhes de faturação" → "Billing details"
- [ ] "Informações adicionais" → "Additional information"
- [ ] "A sua encomenda" → "Your order"
- [ ] "Métodos de pagamento" → "Payment methods"
- [ ] "Efetuar encomenda" → "Place order"
- [ ] "Cupão" → "Coupon"
- [ ] "Aplicar cupão" → "Apply coupon"
- [ ] "Subtotal" → "Subtotal"
- [ ] "Envio" → "Shipping"
- [ ] "Total" → "Total"

---

**Strings My Account (8 strings):**
- [ ] "Encomendas" → "Orders"
- [ ] "Downloads" → "Downloads"
- [ ] "Endereços" → "Addresses"
- [ ] "Detalhes da conta" → "Account details"
- [ ] "Terminar sessão" → "Logout"
- [ ] "Detalhes de envio" → "Shipping address"
- [ ] "Detalhes de faturação" → "Billing address"
- [ ] "Guardar alterações" → "Save changes"

---

**Strings Emails (5 strings):**
- [ ] "Olá" → "Hello"
- [ ] "Obrigado pela sua compra" → "Thank you for your purchase"
- [ ] "Encomenda nº" → "Order #"
- [ ] "Data" → "Date"
- [ ] "Estado" → "Status"

---

**Arquivo .po salvo:**
- [ ] Sim, localização: _________________________________

**Tempo gasto:** _______ min
**Data conclusão:** _____________

---

### 5.2 Loco Translate - Flatsome Theme

**Acesso:**
- [ ] WordPress Admin → Loco Translate → Themes
- [ ] Flatsome selecionado
- [ ] Nova tradução EN criada

---

**Strings Tema (12 strings):**
- [ ] "Início" → "Home"
- [ ] "Loja" → "Shop"
- [ ] "Sobre" → "About"
- [ ] "Contacto" → "Contact"
- [ ] "Pesquisar..." → "Search..."
- [ ] "Menu" → "Menu"
- [ ] "Filtros" → "Filters"
- [ ] "Ordenar por" → "Sort by"
- [ ] "Mais recentes" → "Newest"
- [ ] "Preço: baixo a alto" → "Price: low to high"
- [ ] "Preço: alto a baixo" → "Price: high to low"
- [ ] "Popularidade" → "Popularity"

---

**Arquivo .po salvo:**
- [ ] Sim, localização: _________________________________

**Tempo gasto:** _______ min
**Data conclusão:** _____________

---

## FASE 6: TESTES E VALIDAÇÃO (Dev)

### 6.1 Testes Navegação

**URLs Português:**
- [ ] http://localhost:8080/ (200 OK)
- [ ] http://localhost:8080/shop/ (200 OK)
- [ ] http://localhost:8080/about-lisboetas/ (200 OK)
- [ ] http://localhost:8080/contact/ (200 OK)

**URLs Inglês:**
- [ ] http://localhost:8080/en/ (200 OK)
- [ ] http://localhost:8080/en/shop/ (200 OK)
- [ ] http://localhost:8080/en/about-lisboetas/ (200 OK)
- [ ] http://localhost:8080/en/contact/ (200 OK)

---

### 6.2 Testes Language Switcher

- [ ] Dropdown aparece em todas páginas PT
- [ ] Dropdown aparece em todas páginas EN
- [ ] Clique PT → EN funciona
- [ ] Clique EN → PT funciona
- [ ] URL mantém estrutura (/en/nome/ equivalente a /nome/)

---

### 6.3 Testes WooCommerce EN

**Processo de compra completo:**
1. [ ] Abrir /en/shop/
2. [ ] Navegar categoria (textos EN)
3. [ ] Abrir produto (nome/descrição EN)
4. [ ] "Add to cart" → adiciona ao carrinho
5. [ ] /en/cart/ → interface em inglês
6. [ ] /en/checkout/ → formulário em inglês
7. [ ] /en/my-account/ → painel em inglês

**Funcionalidades:**
- [ ] Filtros produtos EN
- [ ] Ordenação produtos EN
- [ ] Breadcrumbs EN
- [ ] Paginação EN
- [ ] Mensagens erro EN
- [ ] Mensagens sucesso EN

---

### 6.4 Testes SEO

**Hreflang tags:**
```bash
curl -s http://localhost:8080/ | grep hreflang
```

- [ ] Tag hreflang="pt" presente
- [ ] Tag hreflang="en" presente
- [ ] Tag hreflang="x-default" presente
- [ ] URLs corretas em cada tag

---

**Sitemap XML:**
- [ ] http://localhost:8080/sitemap_index.xml acessível
- [ ] Sitemap PT presente
- [ ] Sitemap EN presente (/en/sitemap.xml)
- [ ] Yoast SEO configurado para multilíngue

---

### 6.5 Testes Performance

**Tempo carregamento:**
- [ ] Homepage PT: _______ s (objetivo: <3s)
- [ ] Homepage EN: _______ s (objetivo: <3s)
- [ ] Shop PT: _______ s
- [ ] Shop EN: _______ s

**Cache Transposh:**
- [ ] Transposh → Advanced → Cache ativo
- [ ] 2ª visita /en/ mais rápida que 1ª

**LiteSpeed Cache:**
- [ ] Configurado para respeitar cookie idioma
- [ ] Separate cache PT/EN funcionando

---

### 6.6 Testes Mobile

**Dispositivos testados:**
- [ ] iPhone Safari (/  + /en/)
- [ ] Android Chrome (/ + /en/)
- [ ] iPad Safari
- [ ] Desktop Chrome
- [ ] Desktop Firefox
- [ ] Desktop Safari

**Verificar:**
- [ ] Language switcher responsivo
- [ ] Layout EN não quebra
- [ ] Textos legíveis
- [ ] Botões clicáveis

---

## FASE 7: DOCUMENTAÇÃO (Dev)

### 7.1 Manual Cliente

**Documento criado:**
- [ ] MANUAL_BILINGUE_CLIENTE.pdf
- [ ] Incluí: como traduzir páginas
- [ ] Incluí: como traduzir produtos
- [ ] Incluí: como editar strings Loco
- [ ] Incluí: troubleshooting básico

**Data entrega:** _____________

---

### 7.2 Vídeo Tutorial (Opcional)

- [ ] Screencast gravado (5-10 min)
- [ ] Demonstra tradução inline
- [ ] Demonstra revisão produto
- [ ] Demonstra Loco Translate
- [ ] Enviado para cliente

**Link:** _________________________________

---

## FASE 8: APROVAÇÃO CLIENTE

### 8.1 Review Geral

**Cliente testou:**
- [ ] Language switcher (PT ↔ EN)
- [ ] Navegação páginas EN
- [ ] Qualidade traduções páginas
- [ ] Qualidade traduções produtos
- [ ] Processo checkout EN
- [ ] Mobile PT + EN

---

### 8.2 Feedback Cliente

**Páginas que precisam ajuste:**
_________________________________________________________
_________________________________________________________
_________________________________________________________

**Produtos que precisam revisão:**
_________________________________________________________
_________________________________________________________
_________________________________________________________

**Strings WooCommerce a corrigir:**
_________________________________________________________
_________________________________________________________
_________________________________________________________

**Outros:**
_________________________________________________________
_________________________________________________________
_________________________________________________________

---

### 8.3 Aprovação Final

- [ ] Cliente aprovou sistema bilingue
- [ ] Nenhum ajuste necessário
- [ ] OU: Ajustes solicitados listados acima

**Assinatura cliente:** _________________________________
**Data aprovação:** _____________

---

## FASE 9: DEPLOY PRODUÇÃO (Futuro)

### 9.1 Preparação

- [ ] Backup produção criado
- [ ] Database local exportada (Transposh tables)
- [ ] Arquivos .po/.mo Loco exportados
- [ ] Checklist pré-deploy revisado

---

### 9.2 Migração

- [ ] Transposh configuração importada
- [ ] Traduções páginas importadas
- [ ] Strings Loco importadas
- [ ] URLs produção atualizadas
- [ ] Rewrite rules flushed

---

### 9.3 Testes Produção

- [ ] https://chapeuslisboetas.com/ (PT) OK
- [ ] https://chapeuslisboetas.com/en/ (EN) OK
- [ ] Language switcher funciona
- [ ] Hreflang tags com domínio produção
- [ ] Sitemap XML atualizado
- [ ] Google Search Console atualizado

---

### 9.4 Monitoramento

**Métricas 7 dias pós-lançamento:**
- Tráfego EN: _______ % (objetivo >15%)
- Bounce rate EN: _______ % (objetivo <65%)
- Conversões EN: _______ (comparar com PT)

**Métricas 30 dias:**
- Tráfego EN: _______ %
- Conversão EN: _______ %
- Tempo sessão EN: _______ min (objetivo >2min)
- Pageviews EN: _______ (objetivo >2.5/sessão)

---

## RESUMO FINAL

**Data início:** _____________
**Data conclusão:** _____________
**Tempo total gasto:** _______ horas

**Páginas traduzidas:** _______ / 17
**Produtos revisados:** _______ / 131
**Strings WooCommerce:** _______ / ~150
**Strings Flatsome:** _______ / ~50

**Custo total:** €0 (Transposh free)

**Status final:**
- [ ] ✅ Sistema bilingue 100% funcional
- [ ] ⚠️ Funcional com pequenos ajustes pendentes
- [ ] ❌ Problemas detectados (descrever):

_________________________________________________________
_________________________________________________________
_________________________________________________________

---

**Responsável implementação:** Bilal Machraa / AiParaTi
**Cliente:** Tiago Andrade (Chapéus Lisboetas)
**Assinatura:** _________________________________
**Data:** _____________
