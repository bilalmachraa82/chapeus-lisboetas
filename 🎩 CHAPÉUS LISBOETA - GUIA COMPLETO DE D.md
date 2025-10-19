🎩 CHAPÉUS LISBOETA - GUIA COMPLETO DE DESENVOLVIMENTO
Documentação Técnica para Implementação com Codex

📋 CONTEXTO DO PROJETO
Cliente: Chapéus Lisboeta (Tiago Andrade & Sr. Andrade)
Situação: Reconstrução total após perda do site anterior
Urgência: Lançamento antes da Black Friday (época alta e-commerce)
Objetivo: Site profissional, autónomo, com proteção total de dados
Histórico crítico:

Perderam site anterior, dados, backups, e vendas por falha de fornecedor
Prejuízo estimado: 6-12 meses reconstrução = €2.000-€5.000 em vendas perdidas (sector moda/acessórios 2024)
Prioridade absoluta: autonomia, backups, e garantias anti-perda


🎯 ESPECIFICAÇÕES TÉCNICAS BASE
Stack Tecnológico Confirmado
yamlCMS: WordPress (última versão estável)
E-commerce: WooCommerce
Theme: Flatsome Premium (licença incluída)
Hosting: PTisp Premium (1 ano incluído)
  - Datacenter: Lisboa (3ms latência)
  - NVMe: 40 GB (3.500 MB/s)
  - RAM: 3 GB dedicada
  - Backups: Diários 30 dias (JetBackup)
  - Segurança: Imunify360 + Anti-DDoS 40 Gbps
  - Restauro: 1-click (cliente pode fazer)
  - Suporte: 24/7 telefone direto (<15 min)

Domínio: .pt (1 ano incluído)
SSL: Certificado incluído
CDN: Cloudflare (incluído)
Integrações de Pagamento Obrigatórias
yamlGateway: IfthenPay (método preferido por 70% portugueses)
Métodos ativos:
  - MB Way (taxa 0,8-1%)
  - Multibanco (taxa 0,8-1%)
  - Sem custos mensais fixos
  - Confirmação automática WooCommerce
Envios & Logística
yamlTransportadora: CTT Expresso
Plugin: CTT Expresso integrado
Funcionalidades:
  - Cálculo automático portes (zona/peso)
  - Rastreio encomendas
  - Etiquetas envio automáticas
  - Cobertura Portugal Continental + Ilhas
```

---

## 📊 GESTÃO DE CATÁLOGO - ESPECIFICAÇÕES CRÍTICAS

### Fonte de Dados Principal
**Ficheiro Excel Google Sheets:**  
`https://docs.google.com/spreadsheets/d/1m5ObJBG3CXetWNN9BoXwE69EVA5RH-xMqozhY3d7ptw/edit?usp=sharing`

### Estrutura de Dados Excel
```
Tabs (ordem de prioridade):
1. Winter (prioridade máxima)
2. Summer (prioridade alta)
3. Panama (prioridade média)
4. Leather, Fur, Outros (prioridade normal)

Campos por produto:
- Brand/Marca (ex: "Hologramme")
- SKU/Código (ex: "18456-A", "18456-B" = variações tecido)
- Nome/Modelo
- Preço (€) - SE VAZIO = NÃO PUBLICAR
- Link para pasta Google Photos com imagens
- Categoria/Tipo

Regras de importação:
✅ Produto TEM preço → publicar no site
❌ Produto SEM preço → ignorar (venda física apenas)
🔄 Mesmo SKU base + letras diferentes = variações do mesmo modelo
Script de Extração (JÁ CRIADO)
Status: Codex já desenvolveu script para extração de fotos
Âmbito: Não limitar a 20-30 produtos iniciais - extrair catálogo completo se viável
Fornecedor principal: hologrammeparis.com
Autorização: Cliente tem permissão para usar imagens e copiar informações
Regras de Importação de Imagens
python# Prioridade de sources:
1. Pasta Google Photos do cliente (links no Excel)
2. Site do fornecedor hologrammeparis.com (via script)

# Requisitos técnicos:
- Formato: JPG/PNG
- Tamanho mínimo: 1500x1500px
- Qualidade: Alta resolução
- Múltiplos ângulos por produto (quando disponível)
- Vista frontal OBRIGATÓRIA como imagem principal

### Cockpit Premium Google Sheets (implementado)

- **Setup CLI**
  - `python3 -m pip install --user gspread google-auth gspread-formatting`
  - Definir variáveis antes de correr scripts (`export GOOGLE_SHEETS_ID=...` e, se necessário, `GOOGLE_SERVICE_ACCOUNT_FILE=config/google-service-account.json`).
  - Executar `python3 scripts/beautify_google_sheet.py` para aplicar formatação, criar abas auxiliares e sincronizar dados locais (usa credenciais da service account já criada).

- **Melhorias na aba `Catalogo`**
  - Colunas reordenadas e cabeçalho com paleta da marca (#EECAC9 / #A8DADF) + tipografia Montserrat.
  - `Preview` agora usa `IMAGE()` com thumb 120×120px; linhas formatadas com altura 140px.
  - `Status` automático com lógica `OK / Sem foto / Sem preço / Rever link / Sem descrição` + cores condicionais (verde, âmbar, vermelho) para triagem rápida.
  - Novas colunas: `Última atualização`, `Responsável`, `Notas internas` preparadas para Apps Script `onEdit` (timestamp + editor).
  - Validação extra: `Destaque homepage?` (checkbox), `Prioridade` (1–5), filtros básicos ativos e congelamento das 3 primeiras colunas.

- **Abas geradas automaticamente**
  - `Dashboard`: cartões com KPIs (total, pendências, destaques), sparkline de cobertura fotográfica, links diretos para `Faltas`, resumos e guia. Fórmulas prontas para refletir os dados do sheet.
  - `Faltas`: importa `relatorios/produtos_sem_imagem.csv`, preserva notas/URLs inseridas pelo cliente e mantém colunas “Nova URL/Foto” + “Notas”. Ideal para controlar correções.
  - `Resumo Coleções` e `Resumo Tipos`: carregam `output_catalogo/catalogo_summary_sheet*.csv`, calculam percentagens/ranking e já vêm com filtros/formatos percentuais.
- `Histórico`: cabeçalho protegido para receber logs `onEdit` (timestamp, autor, valor antigo/novo) — Apps Script segue como próximo passo.
  - `Guia`: mini playbook com passos 1-2-3, lembrete para correr `sync_google_sheet.py` + `generate_wc_catalog.py` e apontadores de suporte.

- **Estado atual (Out 2025)**
  - Base inicial consolidada com **62 produtos** (preço preenchido + URL único) → `output_catalogo/catalogo_master_with_price.csv`.
  - Excel limpo (`catalogo_original_full.csv`) e dump da aba `Catalogo` (`catalogo_google_sheet.csv`) disponíveis para auditoria.
  - Relatórios de reconciliação gerados: `catalogo_comparison_detail.csv`, `catalogo_comparison_summary.csv`, `sheet_only_skus.csv` e `link_duplicate_summary.csv`.
  - `beautify_google_sheet.py` corrido com sucesso — Dashboard/Faltas/Resumos/Guia atualizados com layout premium.

- **Script `validate_and_enrich.py` (NOVO)**
  - Lê o `catalogo_master_with_price.csv`, valida cada URL de fornecedor e faz scraping (descrição longa, composição, excertos).
  - Output automático (ultima execução: 54 clean / 8 pendentes):
    - `output_catalogo/catalogo_clean_ready.csv` (produtos prontos para import) → publicados na aba **Clean & Ready**.
    - `output_catalogo/catalogo_pending.csv` (produtos com lacunas / falhas de scrape) → listados na aba **Pendentes** com observações (HTTP status, “descrição/composição não encontrada”, etc.).
    - HTML bruto guardado em `output_catalogo/scrape_raw/` (debug/manual QA).
  - Reexecutar sempre que novos produtos forem adicionados ao catálogo ou links forem corrigidos.

  **Checklist Clean/Pending (cliente ou operação diária)**
  1. Atualizar a aba `Catalogo` (preço + URL obrigatório).
  2. Executar `python3 scripts/validate_and_enrich.py` → revê abas `Clean & Ready` / `Pendentes`.
  3. Corrigir/validar manualmente os produtos marcados como pendentes (ou usar menu “Chapéus Premium → Enviar linha ...”).
  4. Rerun `validate_and_enrich.py` até que todos os produtos pretendidos estejam em “Clean & Ready”.
  5. Executar `python3 scripts/beautify_google_sheet.py` (dashboard actualizado) e `python3 scripts/sync_google_sheet.py` (actualiza `catalogo.json` + `catalogo_backup.json`).
  6. Gerar CSV WooCommerce: `python3 scripts/generate_wc_catalog.py` → `output_catalogo/woocommerce_import.csv` (última execução: 96 produtos exportados; 18 sem imagens foram reportados no log).
  7. Importar no site apenas os produtos validados com preço + URL (Clean & Ready) e guardar log em `catalogo_clean_ready.csv` + `woocommerce_import.csv`.


- **Próximos passos (em curso)**
  1. ✅ `validate_and_enrich.py` criado/executado — repetir sempre que existam novos produtos ou correções de link.
  2. ✅ `beautify_google_sheet.py` ajustado (cards “Produtos validados / Pendentes”, progress = Clean & Ready ÷ total). Script executado com sleeps extra para evitar erro 429.
     ✅ `sync_google_sheet.py` atualizado para concatenar notas de “Observações” e manter “Notas internas”; garantir que o catálogo local reflete as novas abas Clean/Pending. (Rever fluxos finais antes da próxima importação.)
  3. Reescrever `apps_script/catalogo.gs` com menu “Chapéus Premium”, validações adicionais, tooltips premium e histórico detalhado.
  4. Atualizar este guia com checklist final e instruções para o cliente completar os SKUs pendentes.

- **Boas práticas aplicadas**
  - Layout segue recomendações recentes do Google Workspace (“Edit & format a spreadsheet”, 2024) para uso de temas, filtros e sparklines.
  - Estrutura pensada para workflows via CLI/MCP: todas as alterações são repetíveis com um único comando e mantêm compatibilidade com `sync_google_sheet.py` e o pipeline WooCommerce.
  - Apps Script (`apps_script/catalogo.gs`) agora com menu “Chapéus Premium” reforçado:
    - Reaplicar fórmulas e actualizar carimbos.
    - Atalhos para abrir “Clean & Ready” / “Pendentes”.
    - Ação rápida para enviar a linha seleccionada para as abas Clean/Pending (gera registo manual compatível com o output do scraper).

### Apps Script (onEdit + menu)

- Copiar o conteúdo de `apps_script/catalogo.gs` para o editor Apps Script da folha (`Extensões → Apps Script`).
- Guardar e publicar; autorizar a execução na primeira edição.
- Funcionalidades:
  - `onEdit`: carimba “Última atualização” e “Responsável”, regista alterações na aba `Histórico` com valor antigo/novo e valida SKU duplicado + URLs inválidos.
  - Aba `Faltas`: validação de URLs em “Nova URL/Foto” com destaque visual.
  - Menu “Chapéus Premium”: opção para reaplicar fórmulas de preview/status ou forçar timestamp manual na linha selecionada.

### Sincronização enriquecida (`scripts/sync_google_sheet.py`)

- Se “Descrição longa” estiver vazia no sheet, o script tenta reutilizar dados já raspados (`catalogo.json`).
- Na ausência de texto, aciona `catalog_scraper.scrape_product_page` para re-scrape do link do fornecedor, preenchendo automaticamente a descrição e anotando em “Notas internas”.
- Cache de scraping em memória para evitar requisições duplicadas na mesma execução.
- Log de avisos `print` caso a página falhe (HTTP 404, etc.), permitindo diagnóstico rápido no terminal.

### MCP Chrome DevTools (para automação total via Codex)

1. **Pré-requisitos**
   - Node.js ≥ 18 (`node --version`).
   - npm/npx atualizados (`npm install -g npm`).
2. **Arrancar o servidor MCP**
   ```bash
   npx -y chrome-devtools-mcp@latest
   ```
   - Mantém esta janela aberta; o comando lança um Chrome controlável e imprime o endereço WebSocket (`ws://...`).
3. **Partilhar acesso**
   - Copia o URL/porta/token exibidos no terminal para que o Codex possa ligar-se e operar o browser.
   - (Opcional) adiciona ao `~/.codex/config.json`:
     ```json
     {
       "mcpServers": {
         "chrome-devtools": {
           "command": "npx",
           "args": ["-y", "chrome-devtools-mcp@latest"]
         }
       }
     }
     ```
4. **Manter sessão**
   - Não fechar o terminal nem o Chrome enquanto a automação estiver em curso.
   - Conceder manualmente quaisquer permissões (ex.: popups, login Google).

> Próxima prompt sugerida (depois de iniciares o MCP e reiniciares o Codex):
> 
> ```
> MCP chrome-devtools pronto em ws://localhost:PORT. Continua a automatizar Google Sheets + Apps Script.
> ```

🎨 DESIGN & EXPERIÊNCIA VISUAL
Referências de Inspiração (Google Keep)
yamlReferência 1 - Rothys.com:
  Destaques:
    - Combinação elegante imagem + texto/lettering
    - Proporções e tamanhos equilibrados
    - Dropdown menus limpos
  Aplicar:
    - Hero sections com produtos + copy sobreposto
    - Hierarquia tipográfica clara
    - Menus categorizados (dropdown)

Referência 2 - American Apparel:
  Destaques:
    - Praticidade máxima
    - Textos óbvios e diretos
    - Rapidez de navegação
    - Dropdown menus eficientes
  Aplicar:
    - CTAs claros ("Comprar", "Ver Produto")
    - Navegação intuitiva (≤3 cliques para qualquer produto)
    - Checkout simplificado
    - Menus dropdown por categoria
Diretrizes de Design Flatsome
css/* Paleta de Cores - Definir com Cliente */
--primary: #[TBD] /* Cor marca principal */
--secondary: #[TBD] /* Cor secundária/CTAs */
--neutral-light: #F5F5F5
--neutral-dark: #1A1A1A
--accent: #[TBD] /* Destaques/promoções */

/* Tipografia */
--heading-font: [TBD] /* Elegante, legível */
--body-font: [TBD] /* Clean, sans-serif */
--size-base: 16px
--line-height: 1.6

/* Espaçamento */
--spacing-unit: 8px /* Base para todos os espaçamentos */
Estrutura de Páginas Essenciais
Homepage
markdown[HERO SECTION]
- Imagem impactante (chapéu icónico)
- Headline: "Chapéus Lisboeta - Tradição & Elegância"
- Subheadline: "Desde [ano] / Artesanato Português"
- CTA: "Ver Coleção" → /colecao ou /produtos

[CATEGORIAS DESTACADAS]
Grid 3 colunas (desktop) / 1 coluna (mobile):
- Inverno | Verão | Panamá
- Imagem + Nome + "Explorar" (link)

[PRODUTOS DESTAQUE]
Carrossel/Grid 4 produtos:
- Novidades / Mais Vendidos / Escolha da Semana

[SOBRE / HISTÓRIA]
- Bloco texto + imagem loja física
- "Há [X] anos no Chiado..."
- CTA: "Conheça a Nossa História"

[NEWSLETTER / CONTACTO]
- Formulário simples email
- WhatsApp button fixo canto inferior direito

[FOOTER]
- Links rápidos | Políticas | Redes sociais | Contactos
Página Produto
markdownLayout 2 colunas (60/40):

[COLUNA ESQUERDA - Imagens]
- Galeria imagens (4-8 fotos)
- Zoom ao hover
- Thumbnails navegáveis

[COLUNA DIREITA - Info]
- Nome produto (H1)
- Preço (destaque)
- SKU / Referência
- Descrição curta (2-3 linhas)
- Variações (tamanho/cor/tecido) - SE APLICÁVEL
- Seletor quantidade
- Botão "Adicionar ao Carrinho" (destaque)
- Ícones: Envio Grátis (se >€X) | Devoluções | Garantia

[TABS INFERIORES]
- Descrição completa
- Materiais / Especificações
- Envios / Devoluções
- Cuidados / Manutenção
Páginas Institucionais (Cliente Fornecerá Textos)
markdown/sobre - História da marca, valores, equipa
/contactos - Morada loja, telefone, email, mapa, horário
/envios - Políticas CTT, prazos, custos
/devolucoes - Processo devolução, prazos (14 dias lei)
/garantias - Garantia legal, cuidados produto
/privacidade - Política RGPD completa
/termos - Termos e condições venda
/cookies - Banner + página explicativa
/faq - 10+ perguntas frequentes

🔧 FUNCIONALIDADES FASE 1 (ESSENCIAL)
1. Configuração WordPress Base
bash# Plugins OBRIGATÓRIOS (instalar/ativar):
- WooCommerce (última stable)
- Flatsome Theme + Child Theme
- IfthenPay for WooCommerce
- CTT Expresso
- WPML (tradução PT/EN - BÓNUS ATÉ 11/10)
- Yoast SEO
- WP Rocket Cache (€59 - incluído licenças)
- CookieYes RGPD (€75 - incluído)
- Google Analytics 4 + GTM
- UpdraftPlus (backups adicionais - redundância)

# Configurações críticas:
- Permalinks: /%postname%/
- Timezone: Europe/Lisbon
- Language: PT (primary) + EN (WPML)
- Currency: EUR (€)
- Date format: d/m/Y
2. WooCommerce - Configurações Essenciais
yamlGeral:
  Base localização: Portugal
  Moeda: EUR (€)
  Vender para: Portugal + [outros países se cliente quiser]
  Enviar para: Portugal Continental + Ilhas

Produtos:
  Unidade peso: kg
  Unidade dimensões: cm
  Avaliações: Ativar (moderação manual)
  Stock: Gerir inventário ativado
  Notificações stock baixo: <5 unidades

Impostos:
  IVA Portugal: 23%
  Preços já incluem IVA: SIM
  Mostrar preços na loja: Com IVA
  
Checkout:
  Criar conta: Opcional
  Checkout como convidado: Permitir
  Campos obrigatórios: Nome, Email, Morada, NIF (opcional), Telefone
  
Emails:
  Templates: Personalizar com branding Chapéus Lisboeta
  Remetente: [email cliente]
  Nome remetente: "Chapéus Lisboeta"
3. Configuração Flatsome Theme
yamlTheme Options:
  Performance:
    - Lazy load: Ativar
    - Minify CSS/JS: Ativar
    - Preload fonts: Ativar
  
  Header:
    - Layout: [Escolher com cliente - referências Rothys]
    - Sticky header: Ativar
    - Mobile menu: Hamburger
    - Elements:
      * Logo (receber do cliente)
      * Menu categorias (dropdown)
      * Pesquisa
      * Ícone conta
      * Carrinho com contador
      * Botão WhatsApp

  Footer:
    - Columns: 4 (Desktop) / 1 (Mobile)
    - Widgets: Menus, Contactos, Newsletter, Social
    
  Colors:
    - Primary: [Cliente definirá]
    - Secondary: [Cliente definirá]
    - Text: #333
    - Background: #FFF
    
  Typography:
    - Headings: [Cliente definirá]
    - Body: Sans-serif legível
    - Sizes: Responsive scaling
4. Menus & Navegação
yamlMenu Principal (Header):
  - Início
  - Loja (dropdown)
    └─ Inverno
    └─ Verão
    └─ Panamá
    └─ Pele/Couro
    └─ Todos os Produtos
  - Coleções (dropdown - SE APLICÁVEL)
  - Sobre
  - Contactos

Menu Secundário (Footer):
  Coluna 1 - Informações:
    - Sobre Nós
    - Envios
    - Devoluções
    - Garantias
  
  Coluna 2 - Ajuda:
    - FAQ
    - Guia Tamanhos
    - Cuidados Produto
    - Contactos
  
  Coluna 3 - Legal:
    - Termos e Condições
    - Política Privacidade
    - Política Cookies
    - Livro Reclamações Online
  
  Coluna 4 - Contacto:
    - Morada loja
    - Telefone
    - Email
    - Horário
    - Redes Sociais (ícones)
5. Integrações Técnicas
WhatsApp & Telefone
html<!-- Button fixo canto inferior direito -->
<div class="floating-contact">
  <a href="https://wa.me/351918911308?text=Olá,%20tenho%20uma%20questão%20sobre..."
     class="whatsapp-button"
     target="_blank"
     rel="noopener">
    <img src="/whatsapp-icon.svg" alt="WhatsApp">
    <span>Falar Connosco</span>
  </a>
  
  <a href="tel:+351918911308" class="phone-button">
    <img src="/phone-icon.svg" alt="Telefone">
  </a>
</div>

<!-- Incluir no rodapé de páginas produto -->
<div class="product-contact-cta">
  <p>Dúvidas sobre este produto?</p>
  <a href="https://wa.me/351918911308" class="button">
    💬 WhatsApp
  </a>
  <a href="tel:+351918911308" class="button secondary">
    📞 Ligar Agora
  </a>
</div>
Google Analytics 4 + GTM
javascript// Eventos e-commerce a trackear:
- view_item (página produto)
- add_to_cart
- begin_checkout
- add_payment_info
- purchase (conversão)
- view_item_list (categorias)

// Configurar Enhanced E-commerce
// Incluir tracking code no <head>
// GTM container: GTM-XXXXXX (criar com cliente)
SEO On-Page (Yoast)
yamlHomepage:
  Title: "Chapéus Lisboeta | Chapéus Artesanais Portugueses"
  Meta: "Descubra chapéus de qualidade superior. Tradição artesanal portuguesa desde [ano]. Inverno, verão, panamá. Loja no Chiado, Lisboa."
  
Produtos:
  Title: "[Nome Produto] | Chapéus Lisboeta"
  Meta: "[Descrição produto 120-150 chars] Compre online com envio rápido."
  
Categorias:
  Title: "Chapéus [Categoria] | Chapéus Lisboeta"
  Meta: "Explore a nossa coleção de chapéus [categoria]. Qualidade artesanal portuguesa."

Schema Markup:
  - Organization
  - LocalBusiness (loja física)
  - Product (todos os produtos)
  - BreadcrumbList
  - Review/Rating (quando houver)
RGPD & Cookies
yamlCookieYes:
  Banner:
    - Posição: Bottom center
    - Idioma: PT (principal) + EN
    - Categorias:
      * Necessários (sempre ativos)
      * Funcionais (opt-in)
      * Analytics (opt-in)
      * Marketing (opt-in)
  
  Páginas legais:
    - Política Privacidade (template RGPD-compliant)
    - Política Cookies (gerada automática)
    - Termos e Condições
  
  Formulários:
    - Checkbox RGPD em newsletter
    - Checkbox RGPD em checkout (opcional)
    - Link para políticas sempre visível

🚀 PLANO DE IMPLEMENTAÇÃO FASE 1
SEMANA 1: Setup & Design Foundation
markdown## Dia 1-2: Infraestrutura
[X] Contratar hosting PTisp + domínio
[X] Instalar WordPress + SSL
[X] Configurar backups diários
[X] Instalar plugins essenciais
[X] Ativar tema Flatsome + child theme
[X] Configurar RGPD básico (CookieYes)

## Dia 3-4: Design & Branding
[ ] RECEBER DO CLIENTE:
    - Logótipo (SVG + PNG alta resolução)
    - Paleta cores marca (códigos HEX)
    - Fontes preferidas (ou escolher)
    - Fotos loja física (se tiverem)
    
[ ] CONFIGURAR:
    - Cores tema (primary, secondary, accent)
    - Tipografia (headings + body)
    - Layout header/footer
    - Homepage mockup inicial
    
[ ] CHECKPOINT: Reunião validação design (Sexta 14h)
    - Mostrar homepage mockup
    - Ajustar cores/fontes se necessário
    - Aprovar estrutura geral
SEMANA 2: Catálogo & WooCommerce
markdown## Dia 5-6: Estrutura Catálogo
[ ] Criar categorias WooCommerce:
    - Inverno
    - Verão
    - Panamá
    - Pele/Couro
    - [Outras conforme Excel]

[ ] Criar atributos produto:
    - Tamanho (se aplicável)
    - Cor/Tecido (variações SKU com letras)
    - Material (filtro)

[ ] Processar Excel + Script extração:
    - Limpar linhas sem preço
    - Validar links Google Photos
    - Executar script download imagens
    - Organizar por categoria/prioridade

## Dia 7-9: Importação Produtos
[ ] FASE PRIORIDADE ALTA (Inverno):
    - Importar todos produtos Winter com preço
    - Associar imagens (mínimo 1, ideal 4-6 por produto)
    - Configurar variações (se SKU com letras diferentes)
    - Preencher descrições (curta + longa)
    - Definir preços + IVA
    - Configurar stock inicial
    
[ ] FASE PRIORIDADE MÉDIA (Verão + Panamá):
    - Repetir processo acima
    
[ ] FASE PRIORIDADE NORMAL (Restantes):
    - Importar catálogo completo conforme disponibilidade
    
[ ] CHECKPOINT: Validação catálogo (Segunda 11h)
    - Cliente revê produtos importados
    - Corrigir preços/nomes/descrições
    - Aprovar para continuar
SEMANA 3: Integrações & Conteúdos
markdown## Dia 10-11: Pagamentos & Envios
[ ] IfthenPay:
    - Criar conta IfthenPay (com cliente)
    - Configurar plugin MB Way + Multibanco
    - Testar pagamento sandbox
    - Ativar produção
    
[ ] CTT Expresso:
    - Criar conta CTT empresas (com cliente)
    - Configurar plugin
    - Definir zonas/tarifas envio
    - Testar cálculo portes carrinho

## Dia 12-13: Páginas Institucionais
[ ] RECEBER TEXTOS CLIENTE:
    - Sobre / História marca (200-400 palavras)
    - Contactos (morada, telefone, email, horário)
    - FAQ inicial (10 perguntas/respostas)
    
[ ] CRIAR PÁGINAS:
    - Sobre (texto + imagens)
    - Contactos (formulário + mapa + info loja)
    - Envios (políticas CTT, prazos, custos)
    - Devoluções (14 dias lei, condições)
    - Garantias (legal + cuidados)
    - Privacidade (template RGPD)
    - Termos (template e-commerce)
    - FAQ (accordion)

## Dia 14: SEO & Analytics
[ ] Yoast SEO:
    - Configurar títulos/metas todas as páginas
    - Schema markup
    - Sitemap XML
    - Robots.txt
    
[ ] Google Analytics 4:
    - Criar propriedade GA4
    - Instalar tracking code
    - Configurar e-commerce events
    - Testar eventos carrinho/checkout
    
[ ] Google Tag Manager:
    - Criar container
    - Configurar tags básicas
    - Testar disparo eventos
SEMANA 4: QA & Lançamento
markdown## Dia 15-16: Testes Completos
[ ] FUNCIONALIDADES:
    - Adicionar produto ao carrinho
    - Alterar quantidades
    - Aplicar cupom desconto (criar teste)
    - Calcular portes diferentes zonas
    - Processo checkout completo
    - Pagamento MB Way (teste real €1)
    - Pagamento Multibanco (gerar referência)
    - Recepção email confirmação
    - Backoffice: ver encomenda
    
[ ] RESPONSIVE:
    - Testar mobile (iOS + Android)
    - Testar tablet
    - Testar desktop (Chrome, Firefox, Safari)
    - Corrigir bugs layout
    
[ ] PERFORMANCE:
    - PageSpeed Insights (target >85 mobile, >90 desktop)
    - Otimizar imagens se necessário
    - Cache configurado
    - CDN ativo
    
[ ] SEO:
    - Todos os produtos com meta description
    - Imagens com alt text
    - Links internos funcionais
    - Sitemap submetido Google Search Console

## Dia 17: Formação Cliente
[ ] SESSÃO 1H PRESENCIAL/ZOOM:
    - Acesso backoffice WordPress
    - Tour interface WooCommerce
    - Adicionar novo produto (prática)
    - Editar produto existente
    - Gerir encomendas
    - Processar envio CTT
    - Ver relatórios vendas
    - Criar cupom desconto
    - Gerir stock
    - Restaurar backup (demonstração)
    
[ ] ENTREGAR:
    - Manual PDF operações básicas
    - Vídeo screencast 15min (opcional)
    - Contactos suporte 24/7

## Dia 18: GO LIVE 🚀
[ ] PRÉ-LANÇAMENTO:
    - Backup completo final
    - Remover "Em Construção"
    - Verificar DNS apontado
    - SSL ativo e funcionando
    - Robots.txt permitir indexação
    
[ ] LANÇAMENTO:
    - Site ao vivo!
    - Submeter sitemap Google
    - Partilhar redes sociais cliente
    - Enviar email base clientes (se tiverem)
    
[ ] MONITORIZAÇÃO 48H:
    - Verificar Analytics a receber dados
    - Acompanhar primeiros pedidos
    - Resolver bugs críticos se surgirem
    - Suporte direto cliente
SEMANA 5-6: Buffer & Otimização
markdown## Margem Segurança
[ ] Ajustes pós-lançamento
[ ] Correções feedback cliente
[ ] Otimizações performance
[ ] Início preparação Fase 2 (se aprovado)

## RELATÓRIO 30 DIAS (incluído bónus)
[ ] Core Web Vitals report
[ ] Traffic Analytics (visitantes, origens)
[ ] E-commerce metrics (conversão, AOV, produtos mais vistos)
[ ] Recomendações otimização

🤖 FASE 2: AUTOMAÇÃO & IA (Pós-Lançamento)
Objetivo
Reduzir trabalho manual de gestão catálogo através de:

Chatbot IA para atendimento 24/7
Importação automática produtos fornecedor

1. Chatbot IA - Especificações
Funcionalidades Mínimas
yamlRespostas automáticas:
  - Horário loja física
  - Prazos/custos envio
  - Política devoluções
  - Guia tamanhos chapéus
  - Métodos pagamento
  - Rastreio encomenda (pedir nº)
  - Cuidados produto
  - Disponibilidade stock (integrar WooCommerce)

Idiomas:
  - Português (primary)
  - Inglês (turistas)

Canais:
  - Widget site (canto inferior direito)
  - WhatsApp (integração API Business)
  - Email (respostas sugestões)

Fallback:
  - "Não entendi. Quer falar com humano?"
  - Botão transferir WhatsApp direto
  - Horário atendimento humano: 10h-18h
Plugins Recomendados
markdownOpção A - Tidio (€29/mês):
  ✅ Chatbot visual builder
  ✅ Integração WhatsApp
  ✅ Multi-idioma
  ✅ Analytics conversas
  ❌ IA limitada (regras básicas)

Opção B - Elfsight AI Chatbot (€49/mês):
  ✅ GPT-powered (respostas inteligentes)
  ✅ Treino custom base conhecimento
  ✅ Multi-idioma avançado
  ❌ Não integra WhatsApp direto

Opção C - Custom ChatGPT API:
  ✅ Controlo total
  ✅ Custo variável uso (~€20-30/mês)
  ✅ Integração profunda WooCommerce
  ❌ Requer desenvolvimento (€800-€1200)

RECOMENDAÇÃO: Testar Tidio 1 mês (trial grátis) → avaliar necessidade IA avançada
Base Conhecimento (FAQ para treinar bot)
markdownCLIENTE DEVE FORNECER:
- 20-30 perguntas frequentes + respostas
- Informações específicas produtos
- Políticas loja detalhadas
- Tom de voz marca (formal/casual/elegante)

Exemplos perguntas:
- "Qual o prazo de entrega?"
- "Como sei o meu tamanho de chapéu?"
- "Posso devolver se não servir?"
- "Fazem envios para as ilhas?"
- "Este chapéu é lavável?"
- "Têm loja física? Onde?"
- etc.
2. Importador Automático - Análise Técnica
Diagnóstico Situação
yamlFornecedor: hologrammeparis.com
API disponível: ❌ NÃO
XML/CSV feed: ❌ NÃO (confirmado conversa)
Autorização uso conteúdo: ✅ SIM

Solução: Web Scraping Automatizado
Arquitectura Proposta
Componente 1: Scraper
python# Tecnologias
- Linguagem: Python 3.11+
- Frameworks:
  * Scrapy (scraping)
  * BeautifulSoup (parsing HTML)
  * Selenium (se JavaScript necessário)
  * Requests (HTTP)
  * Pillow (processamento imagens)

# Funcionalidades
1. Navegação categorias site fornecedor
2. Extração dados produtos:
   - Nome
   - SKU/Referência
   - Preço (converter para EUR se necessário)
   - Descrição
   - Especificações (material, tamanho, peso)
   - URLs imagens (todas disponíveis)
   
3. Download imagens:
   - Resolução máxima
   - Renomear padrão: SKU-001.jpg, SKU-002.jpg
   - Otimizar (compressão sem perda qualidade)
   
4. Estruturação dados:
   - Export JSON/CSV
   - Compatível importação WooCommerce
Componente 2: Importador WooCommerce
python# Integração
- WooCommerce REST API v3
- Autenticação: Consumer Key + Secret

# Processo
1. Ler ficheiro output scraper
2. Para cada produto:
   a) Verificar se SKU existe (update vs create)
   b) Upload imagens WordPress Media Library
   c) Criar/atualizar produto WooCommerce
   d) Associar categorias corretas
   e) Configurar preço + stock
   f) Publicar (ou rascunho se cliente quer revisar)
   
3. Log operações:
   - Produtos novos
   - Produtos atualizados
   - Erros/falhas
   - Estatísticas (tempo, total, sucesso%)
Componente 3: Agendador
bash# Cron Job Linux (hosting PTisp)
# Executar scraper + import automaticamente

# Frequência sugerida:
0 3 * * 1   /usr/bin/python3 /home/user/scraper/run.py
# = Toda segunda-feira às 3h da manhã

# Notificações:
- Email cliente com sumário operação
- Alerta se >10% produtos falharam
- Dashboard web ver última execução
Desafios & Mitigações
yamlDesafio 1: Site fornecedor muda estrutura HTML
  Risco: Alto
  Mitigação:
    - Scraper com seletores flexíveis
    - Fallbacks múltiplos por campo
    - Monitorização semanal (manual inicial)
    - Sistema alertas se scrape falha

Desafio 2: Bloqueio IP / Rate Limiting
  Risco: Médio
  Mitigação:
    - Delays entre requests (2-5s)
    - User-Agent rotation
    - Respeitar robots.txt
    - Scraping horário baixo tráfego (3h-6h)
    
Desafio 3: Imagens grandes (bandwidth)
  Risco: Baixo
  Mitigação:
    - Download incremental (só novas)
    - Compressão automática 80% quality
    - CDN serve imagens produção
    
Desafio 4: Produtos descontinuados fornecedor
  Risco: Médio
  Mitigação:
    - Scraper detecta produtos removidos
    - Automaticamente coloca "Fora de Stock"
    - Cliente decide se remove ou mantém
Fluxo Completo Automação
mermaidgraph TD
    A[Cron Trigger 3h Segunda] --> B[Scraper inicia]
    B --> C{Scrape bem-sucedido?}
    C -->|Sim| D[Processar dados]
    C -->|Não| E[Email erro admin]
    D --> F[Download imagens novas]
    F --> G[Optimizar imagens]
    G --> H[Importar WooCommerce API]
    H --> I{Produtos importados?}
    I -->|Sim| J[Atualizar stock/preços]
    I -->|Não| K[Log erros]
    J --> L[Email sumário cliente]
    K --> L
    E --> M[Retry ou alerta manual]
Orçamento Detalhado Fase 2
yamlChatbot IA:
  Setup inicial: €150
    - Configuração Tidio/Elfsight
    - Treino base conhecimento
    - Testes multi-idioma
    - Integração WhatsApp
  
  Licença anual: €29-49/mês × 12 = €348-€588
  Total Ano 1: €498-€738

Importador Automático:
  Desenvolvimento scraper: €400-€600
    - Análise estrutura site fornecedor
    - Scraper Scrapy/BeautifulSoup
    - Testes robustez
    - Documentação
  
  Integração WooCommerce: €200-€300
    - API REST implementation
    - Upload/associação imagens
    - Gestão stock/preços
    - Sistema notificações
  
  Agendador + Dashboard: €100-€150
    - Cron job configuração
    - Interface web ver status
    - Logs execuções
    - Alertas email
  
  Total desenvolvimento: €700-€1.050

Custos recorrentes:
  - Servidor execução (se necessário): €0 (usa hosting atual)
  - Manutenção anual: €150 (updates, ajustes)

TOTAL FASE 2 ANO 1: €1.348 - €1.938
TOTAL FASE 2 Anos seguintes: ~€500/ano
Alternativa Low-Code (se orçamento reduzido)
yamlFerramenta: n8n.io (automação visual)
  Vantagens:
    - Interface drag-and-drop
    - Integrações pre-built
    - Sem código complexo
    - Self-hosted (grátis)
  
  Limitações:
    - Scraping menos robusto
    - Requer servidor dedicado (~€15/mês)
    - Menos customização
  
  Custo:
    - Setup: €300-€400 (mais simples)
    - Hosting: €180/ano
    - Total Ano 1: €480-€580

📞 REQUISITOS DO CLIENTE
Até Dia 2 do Projeto (CRÍTICO)
markdown[ ] Logótipos:
    - SVG (vetor)
    - PNG alta resolução (min 2000px largura)
    - Variações: cor + branco + preto

[ ] Paleta Cores Marca:
    - Cor primária (HEX code)
    - Cor secundária (HEX code)
    - Cores acento (1-2 HEX codes)
    
[ ] Textos Institucionais:
    - História marca (200-400 palavras)
    - Sobre a equipa (100-200 palavras)
    - Morada loja + coordenadas GPS
    - Telefone + email + horário
    
[ ] Políticas Loja:
    - Prazo devolução (sugestão: 14 dias)
    - Condições devolução (produto intacto, etiquetas, etc.)
    - Garantias oferecidas
    - Informações CTT (conta empresas)

[ ] Credenciais IfthenPay:
    - Criar conta em ifthenpay.com
    - Fornecer chave API
    - Confirmar métodos ativos (MB Way + Multibanco)

[ ] Acesso Google Sheets:
    - Confirmar permissões edição
    - Limpar produtos sem preço
    - Validar links fotos funcionais
Disponibilidade Reuniões
markdownAgendado cliente: 10h-16h dias úteis
Reuniões semanais: Sextas 15h (60min)

Agenda fixa:
- Semana 1: Sexta 15h - Aprovação design
- Semana 2: Segunda 11h - Validação catálogo
- Semana 3: Sexta 15h - Review páginas conteúdo
- Semana 4: Terça 11h - Formação backoffice
- Semana 4: Sexta 15h - GO LIVE (acompanhamento)

🎁 BÓNUS LIMITADO (ATÉ 11 OUTUBRO 2025)
Tradução Bilingue PT/EN - WPML
yamlIncluído se aceitar proposta até 11/10:
  Valor normal: €600
  Valor oferta: GRÁTIS

Âmbito tradução:
  - Homepage completa
  - Páginas institucionais (Sobre, Contactos, etc.)
  - Menu navegação
  - Footer
  - Produtos: Nomes + descrições curtas
  - Checkout: Interface completa
  - Emails transacionais

Não incluído (manual cliente depois):
  - Descrições longas produtos (centenas)
  - Conteúdo blog (se criarem)
  - FAQs extensas
  
Instalação WPML:
  - Plugin WPML Multilingual CMS
  - WPML String Translation
  - WPML Translation Management
  - Configuração PT (default) + EN
  - Switcher idioma header
Relatório Performance 30 Dias
yamlIncluído:
  Entrega: 30 dias pós-lançamento
  
Conteúdo:
  1. Core Web Vitals:
     - LCP (Largest Contentful Paint)
     - FID (First Input Delay)
     - CLS (Cumulative Layout Shift)
     - Comparação com concorrentes
  
  2. Analytics:
     - Total visitantes
     - Origem tráfego (orgânico/direto/social)
     - Taxa rejeição
     - Páginas mais vistas
     - Produtos mais vistos
  
  3. E-commerce:
     - Total encomendas
     - Taxa conversão
     - Valor médio encomenda (AOV)
     - Produtos mais vendidos
     - Taxa abandono carrinho
  
  4. SEO:
     - Posicionamento palavras-chave target
     - Impressões Google
     - CTR médio
     - Páginas indexadas
  
  5. Recomendações:
     - 5-10 otimizações prioritárias
     - Estimativa impacto cada uma
     - Esforço implementação

  Formato: PDF profissional (15-20 páginas)

⚠️ REGRAS IMPORTANTES PARA CODEX
Flexibilidade vs Rigor
markdownFLEXÍVEL (ajustar à realidade):
- Organização ficheiros/estrutura (Codex decide melhor caminho)
- Ferramentas específicas (se alternativas melhores disponíveis)
- Ordem de implementação (se lógica diferente mais eficiente)
- Design visual detalhes (dentro das referências fornecidas)
- Nomes técnicos componentes (desde que documentado)

RÍGIDO (não negociável):
- Funcionalidades prometidas cliente (todas devem ser entregues)
- Stack tecnológico base (WordPress, WooCommerce, Flatsome)
- Integrações obrigatórias (IfthenPay, CTT, RGPD)
- Prazos comunicados (4-6 semanas Fase 1)
- Orçamento fechado (€1.887 Fase 1)
- Segurança e backups (garantias anti-perda)
- RGPD compliance (obrigatório legal)
- Estrutura catálogo Excel fornecida (importar conforme)
Tomada Decisões Técnicas
markdownSE precisar decidir sobre algo não especificado:
1. Priorizar: Simplicidade + Manutenção fácil cliente
2. Preferir: Soluções nativas WordPress quando possível
3. Evitar: Over-engineering / dependências desnecessárias
4. Documentar: Todas as decisões não-óbvias no código
5. Perguntar: Se impactar experiência utilizador ou custos futuros

SEMPRE PERGUNTAR ANTES:
- Escolhas que afetam orçamento (plugins pagos extra)
- Decisões design impactantes (layout, cores, UX)
- Alterações escopo acordado
- Remoção funcionalidades prometidas
- Mudanças stack tecnológico core
Gestão Catálogo - Autonomia Total
markdownCodex tem AUTONOMIA COMPLETA para:
✅ Decidir melhor método importação dados Excel
✅ Estruturar categorias/taxonomias WooCommerce
✅ Organizar imagens (nomenclatura, estrutura pastas)
✅ Escolher abordagem script extração (Scrapy/Beautiful/outro)
✅ Optimizar performance importação (batch size, etc.)
✅ Criar variações produtos (se SKU indica)

Codex deve SEMPRE:
✅ Importar TODOS os produtos com preço (não limitar 20-30)
✅ Priorizar ordem: Winter > Summer > Panama > Outros
✅ Manter integridade dados (SKU, preços, nomes do Excel)
✅ Associar múltiplas imagens quando disponível
✅ Validar qualidade imagens (reportar problemas)
✅ Documentar processo para cliente replicar futuramente
Qualidade & Best Practices
markdownCÓDIGO:
- Comentários claros (PT ou EN)
- Nomenclatura descritiva variáveis
- Child theme para customizações Flatsome
- Version control (Git) se aplicável
- Sem hardcoded credentials (usar wp-config.php)

PERFORMANCE:
- Lazy load imagens
- CSS/JS minificados
- Cache ativo (WP Rocket)
- CDN configurado
- Optimização database (queries eficientes)

SEGURANÇA:
- Updates plugins regulares (documentar processo)
- Passwords fortes (gerados automaticamente)
- 2FA acesso admin (recomendar cliente)
- Backups testados (fazer restore teste)
- SSL forçado (HTTPS redirect)

ACESSIBILIDADE:
- Alt text todas as imagens
- Contraste cores adequado (WCAG AA mínimo)
- Navegação teclado funcional
- Formulários labels corretos
- Hierarquia headings semântica

📋 CHECKLIST FINAL PRÉ-ENTREGA
Funcionalidades Essenciais
markdown[ ] Homepage carrega <3s (PageSpeed >85 mobile)
[ ] Catálogo completo importado e organizado
[ ] Adicionar produto ao carrinho funciona
[ ] Checkout completo funcional
[ ] Pagamento MB Way testa OK (€1 real)
[ ] Pagamento Multibanco gera referência
[ ] CTT calcula portes corretamente
[ ] Emails transacionais enviam (pedido, confirmação, envio)
[ ] Backoffice WooCommerce acessível cliente
[ ] WPML PT/EN funciona (se aplicável)
[ ] SEO básico configurado (meta tags, sitemap)
[ ] Google Analytics 4 a trackear
[ ] RGPD cookie banner funciona
[ ] Políticas legais publicadas
[ ] WhatsApp button fixo visível
[ ] Menu categorias dropdown funciona
[ ] Pesquisa interna retorna resultados
[ ] Filtros produtos funcionam
[ ] Mobile responsive todas páginas
[ ] SSL ativo (candado verde)
[ ] Backups diários confirmados (testar restore)
Conteúdo & Dados
markdown[ ] Todos os produtos têm:
    [ ] Nome correto
    [ ] SKU/Referência
    [ ] Preço com IVA
    [ ] Pelo menos 1 imagem qualidade
    [ ] Descrição curta
    [ ] Categoria associada
    [ ] Stock inicial definido

[ ] Páginas institucionais preenchidas:
    [ ] Sobre
    [ ] Contactos
    [ ] Envios
    [ ] Devoluções
    [ ] Garantias
    [ ] FAQ
    [ ] Privacidade
    [ ] Termos
    [ ] Cookies

[ ] Menus configurados:
    [ ] Header principal
    [ ] Footer (4 colunas)
    [ ] Legal
    [ ] Mobile hamburger

[ ] Imagens otimizadas:
    [ ] Alt text preenchido
    [ ] Tamanho adequado (<500KB each)
    [ ] Formato correto (JPG/PNG)
Integrações & Plugins
markdown[ ] IfthenPay:
    [ ] MB Way ativo
    [ ] Multibanco ativo
    [ ] Teste pagamento confirmado
    [ ] Emails notificação funcionam

[ ] CTT Expresso:
    [ ] Conta configurada
    [ ] Zonas/tarifas corretas
    [ ] Etiquetas geram
    [ ] Rastreio funciona

[ ] WPML (se bónus aplicável):
    [ ] PT (default) completo
    [ ] EN traduzido essenciais
    [ ] Switcher header visível
    [ ] URLs /en/ funcionam

[ ] SEO (Yoast):
    [ ] Sitemap XML gerado
    [ ] Submetido Google Search Console
    [ ] Meta descriptions produtos
    [ ] Schema markup ativo

[ ] Analytics:
    [ ] GA4 property criada
    [ ] Tracking code instalado
    [ ] E-commerce events testados
    [ ] GTM configurado (se aplicável)

[ ] RGPD:
    [ ] CookieYes ativo
    [ ] Banner conformidade
    [ ] Políticas páginas
    [ ] Checkboxes formulários
Documentação Cliente
markdown[ ] Manual Backoffice PDF:
    [ ] Login WordPress
    [ ] Adicionar produto
    [ ] Editar produto
    [ ] Gerir encomendas
    [ ] Processar envio CTT
    [ ] Ver relatórios
    [ ] Criar cupom
    [ ] Restaurar backup

[ ] Credenciais entregues (seguro):
    [ ] WordPress admin
    [ ] Hosting PTisp
    [ ] IfthenPay
    [ ] CTT
    [ ] Google Analytics
    [ ] Google Search Console
    [ ] Email profissional

[ ] Contactos suporte:
    [ ] PTisp: 24/7 telefone
    [ ] Bilal/AiParaTi: 3 meses incluído
    [ ] Emergências: procedimento claro

🎯 MÉTRICAS DE SUCESSO
KPIs Técnicos (Launch)
yamlPerformance:
  PageSpeed Mobile: >85
  PageSpeed Desktop: >90
  Time to First Byte: <600ms
  Largest Contentful Paint: <2.5s
  First Input Delay: <100ms
  Cumulative Layout Shift: <0.1

SEO:
  Sitemap indexado: ✓
  Meta descriptions: 100% páginas
  Alt text imagens: >95%
  Schema markup: ✓ (Organization, Product, Local)
  Links internos: sem 404s

Security:
  SSL: A+ rating (SSLLabs)
  Backups: diários automáticos últimos 30 dias
  Updates: plugins/theme/core latest stable
  2FA admin: configurado

RGPD:
  Cookie banner: ✓ conforme
  Políticas: publicadas e acessíveis
  Opt-ins: formulários com checkboxes
  Data handling: documented
KPIs Negócio (30 dias)
yamlTráfego:
  Visitantes únicos: [baseline] → target +20% mês-a-mês
  Taxa rejeição: <60%
  Páginas/sessão: >2.5
  Duração média: >2min

Conversão:
  Taxa conversão: >1% (e-commerce fashion média)
  Valor médio encomenda: €[TBD baseado preços médios]
  Taxa abandono carrinho: <70%
  
Engajamento:
  Produtos vistos/sessão: >3
  Add-to-cart rate: >5%
  Newsletter sign-ups: >2% visitantes

SEO (orgânico):
  Impressões Google: >1000/mês
  Clicks orgânico: >50/mês
  Palavras-chave top 10: >5 (branded + generic)

📞 PRÓXIMOS PASSOS IMEDIATOS
Se Cliente Aceitar Proposta (€1.887)
markdown1. Responder email: "Aceito proposta €1.887"
   OU ligar: +351 918 911 308

2. Bilal envia:
   - Contrato formal
   - Fatura 50% (€943,50)
   - Dados pagamento
   
3. Cliente paga 50% → Projeto inicia imediatamente

4. Agendar Kick-off Meeting (2h):
   - Sexta ou Segunda próxima
   - Definir acessos
   - Recolher materiais (logo, textos, etc.)
   - Alinhar expectativas
   - Confirmar cronograma

5. Codex recebe:
   - Acesso hosting PTisp
   - Google Sheet catálogo
   - Materiais branding cliente
   - Briefing design final
   
6. Desenvolvimento arranca Semana 1
Timeline Recordar Cliente
markdown📅 Agora - 11 Outubro: Janela bónus tradução EN (€600 grátis)
📅 Semana 1-4: Desenvolvimento Fase 1
📅 Semana 4: Lançamento site + formação
📅 Dia 30 pós-launch: Relatório performance
📅 Mês 2-3: Decidir Fase 2 (chatbot + automação)
📅 Antes Black Friday: Site 100% operacional vendas

🔐 GARANTIAS & SUPORTE
Incluído nos €1.887
yamlSuporte 3 meses:
  - Email: resposta <24h úteis
  - WhatsApp: resposta <2h úteis (9h-18h)
  - Telefone: emergências <15min
  - Reunião mensal: 30min review
  
Coberto sem custos:
  - Bugs correcção
  - Ajustes design minor
  - Dúvidas uso backoffice
  - Updates core/plugins
  - Restauro backup (se necessário)
  - Configurações adicionais pequenas
  
Não coberto (orçamento à parte):
  - Novos desenvolvimentos (Fase 2)
  - Integrações adicionais
  - Design changes major
  - Conteúdo novo massivo
  - Formação adicional avançada
  - Migrações/mudanças servidor
Pós 3 Meses
yamlOpções:
  A) Autonomia total cliente (grátis)
     - Manual completo fornecido
     - Suporte PTisp 24/7 infraestrutura
     
  B) Plano manutenção mensal (€150/mês):
     - Updates mensais garantidos
     - Suporte prioritário
     - 2h desenvolvimento incluídas
     - Backup check semanal
     - Monitorização uptime
     
  C) Pay-as-you-go (€75/h):
     - Sem compromisso
     - Faturação posterior
     - Mínimo 1h por intervenção

🎓 NOTAS FINAIS PARA CODEX
Este documento é VIVO - ajustar conforme descobertas durante implementação.
Princípios guia:

Qualidade > Velocidade (mas dentro prazo acordado)
Documentar decisões (cliente precisa autonomia futura)
Comunicar cedo (problemas/bloqueios reportar imediato)
Testar exaustivamente (site DEVE funcionar 100% launch)
Pensar longo prazo (soluções escaláveis, não hacks)

Em caso de dúvida:

Referir este documento
Consultar referências visuais (Rothys, American Apparel)
Priorizar experiência utilizador
Seguir best practices WordPress/WooCommerce
Perguntar antes de decidir (se impactar cliente)

Objetivo final:

Site profissional, autónomo, protegido, que gere vendas e dê total controlo ao cliente. Nunca mais perdem dados. Nunca mais dependem de terceiros. SEMPRE têm controlo total.


Preparado por: Bilal Machraa / AiParaTi
Para: Chapéus Lisboeta (Tiago Andrade)
Data: Outubro 2025
Versão: 1.0
Status: Aguarda aprovação cliente

"Desta vez, com proteção total e tecnologia portuguesa premium."
🎩 Vamos fazer história juntos!
