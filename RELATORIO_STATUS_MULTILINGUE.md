# Relatório Status Sistema Multilíngue - Chapéus Lisboetas

**Data:** 23 Outubro 2025
**Preparado por:** Bilal Machraa / AiParaTi

---

## DESCOBERTAS CRÍTICAS

### 1. WPML Já Esteve Instalado (Agora Inativo)

**Evidências na database:**
```sql
-- Tabelas WPML existentes
lx_icl_languages (2 idiomas ativos: EN, PT-PT)
lx_icl_translations (127 traduções)
lx_icl_content_status
lx_icl_languages_translations
... (15+ tabelas WPML)

-- Configuração WPML
icl_sitepress_version: 3.1.9.4 (versão antiga, 2015)
Idioma principal: EN (English)
Idioma secundário: PT-PT (Portuguese, Portugal)
```

**Status atual:**
- ✅ Database com estrutura WPML completa
- ✅ 127 traduções armazenadas
- ❌ Plugins WPML **NÃO instalados** no wp-content/plugins/
- ❌ WPML **inativo** (não aparece em active_plugins)

**Conclusão:**
Site foi configurado com WPML no passado, mas:
1. Licença expirou ou foi removida
2. Plugins foram deletados manualmente
3. Database manteve as tabelas (limpar requer plugin ativo)
4. Conteúdo atual está em EN (páginas em inglês)

---

### 2. Transposh Também Instalado (Ativo)

**Configuração atual:**
```
Plugin: Transposh Translation Filter (ativo)
Default language: EN (precisa trocar para PT)
Viewable languages: EN, PT, ES
Auto-translate: Ativado (Google Translate)
Widget: Disponível
```

**Problema:** Conflito potencial com restos WPML na database

---

### 3. Situação Atual do Conteúdo

**Idioma predominante:** Inglês (EN)

**Páginas publicadas (17 total):**
- About Lisboetas
- Account (My Account)
- Blog
- Cart
- Checkout
- Contact
- FAQs (Frequently Asked Questions)
- Home
- Privacy Policy
- Request a Quote
- Return Policy
- Shipping and Handling
- Shop
- Sizing Guide
- Terms of use
- Track Order
- Wishlist

**Produtos:** 131 produtos (títulos em inglês, alguns podem ter tradução PT nas tabelas WPML)

---

## OPÇÕES DE IMPLEMENTAÇÃO

### OPÇÃO 1: Limpar WPML e Usar Apenas Transposh (RECOMENDADO)

**Vantagens:**
✅ Solução gratuita
✅ Sistema mais simples (1 plugin só)
✅ Elimina conflitos database
✅ Tradução inline (mais rápido)
✅ Auto-tradução Google (economiza tempo)

**Desvantagens:**
⚠️ Perde 127 traduções existentes WPML (se houver conteúdo útil)
⚠️ Precisa retrabalho manual (revisar auto-traduções)

**Passos:**
1. **Exportar traduções WPML** (se houver conteúdo valioso)
   ```sql
   -- Ver traduções PT existentes
   SELECT t.element_id, p.post_title, t.language_code
   FROM lx_icl_translations t
   LEFT JOIN lx_posts p ON t.element_id = p.ID
   WHERE t.language_code = 'pt-pt';
   ```

2. **Limpar tabelas WPML**
   ```sql
   DROP TABLE IF EXISTS lx_icl_languages;
   DROP TABLE IF EXISTS lx_icl_translations;
   DROP TABLE IF EXISTS lx_icl_content_status;
   -- (todas as 15+ tabelas lx_icl_*)
   ```

3. **Reconfigurar Transposh**
   - Default language: PT (Português)
   - Viewable languages: PT, EN
   - Enable permalinks: /en/
   - Widget: Header

4. **Traduzir conteúdo PT → EN**
   - Auto-tradução: 100% produtos via Google Translate
   - Revisão manual: 11 páginas críticas + top 20 produtos

**Timeline:** 2-3 dias
**Custo:** €0 (free)

---

### OPÇÃO 2: Reativar WPML (Comprar Licença)

**Vantagens:**
✅ Aproveita 127 traduções existentes
✅ Sistema profissional robusto
✅ Suporte oficial
✅ Editor visual avançado

**Desvantagens:**
❌ Custo: €99/ano (Multilingual CMS) + €159/ano (WooCommerce Multilingual) = **€258/ano**
❌ Complexidade (3+ plugins)
❌ Lock-in (dificulta migração futura)
❌ Performance (queries extras)

**Passos:**
1. **Comprar licença WPML** (wpml.org)
2. **Baixar plugins:**
   - WPML Multilingual CMS
   - WPML String Translation
   - WPML Translation Management
   - WooCommerce Multilingual & Multicurrency

3. **Instalar e ativar**
   - Upload via WordPress Admin → Plugins
   - Ativar licença

4. **Verificar traduções existentes**
   - WPML → Translation Management
   - Ver se traduções PT estão intactas

5. **Completar traduções faltantes**
   - Páginas sem PT: traduzir manual
   - Produtos: revisar PT existente

**Timeline:** 1-2 dias (se traduções estiverem boas)
**Custo:** €258/ano (recorrente)

---

### OPÇÃO 3: Híbrido (Transposh + Recuperar Traduções WPML)

**Conceito:** Extrair traduções WPML úteis, limpar database, usar Transposh

**Vantagens:**
✅ Aproveita trabalho passado (traduções PT)
✅ Sistema free (Transposh)
✅ Database limpa
✅ Sem lock-in

**Desvantagens:**
⚠️ Trabalhoso (export/import manual)
⚠️ Risco perder formatação
⚠️ Requer script customizado

**Passos:**
1. **Exportar traduções WPML para CSV**
   ```sql
   SELECT
     p_en.ID as id_en,
     p_en.post_title as title_en,
     p_en.post_content as content_en,
     p_pt.post_title as title_pt,
     p_pt.post_content as content_pt
   FROM lx_icl_translations t_en
   LEFT JOIN lx_icl_translations t_pt ON t_en.trid = t_pt.trid
   LEFT JOIN lx_posts p_en ON t_en.element_id = p_en.ID
   LEFT JOIN lx_posts p_pt ON t_pt.element_id = p_pt.ID
   WHERE t_en.language_code = 'en' AND t_pt.language_code = 'pt-pt'
   INTO OUTFILE '/tmp/wpml_translations.csv';
   ```

2. **Importar para Transposh**
   - Não há ferramenta nativa
   - Requer script PHP customizado
   - Ou: copiar/colar manual via editor Transposh

3. **Limpar WPML**
4. **Configurar Transposh**

**Timeline:** 3-5 dias (desenvolvimento script)
**Custo:** €0 (mas horas dev)

---

## RECOMENDAÇÃO FINAL

### OPÇÃO 1: Limpar WPML + Transposh

**Rationale:**
1. **Budget:** Projeto tem orçamento apertado, WPML €258/ano é alto
2. **WPML antigo:** Versão 3.1.9.4 (2015) vs atual 4.6+ (incompatibilidades prováveis)
3. **Traduções duvidosas:** 127 traduções de database antiga, qualidade desconhecida
4. **Site em EN:** Conteúdo principal está em inglês, PT é secundário (turistas)
5. **Transposh suficiente:** Auto-tradução + revisão manual cobre 95% necessidades
6. **Autonomia cliente:** Transposh inline editing é mais simples que WPML

**Plano de ação:**
1. ✅ **Backup completo** (já feito: backup_pre_transposh_20251023_full.sql)
2. 🔍 **Auditar traduções WPML** (verificar se há conteúdo PT valioso)
3. 📥 **Exportar traduções úteis** (manual ou query SQL)
4. 🗑️ **Limpar tabelas WPML** (script SQL)
5. ⚙️ **Configurar Transposh PT/EN**
6. 🌐 **Traduzir conteúdo crítico** (11 páginas + top 20 produtos)
7. ✅ **Testar e validar**

---

## PRÓXIMOS PASSOS IMEDIATOS

### 1. Auditar Traduções WPML Existentes

**Objetivo:** Verificar se há traduções PT que valem a pena salvar

**Query de auditoria:**
```sql
-- Contar traduções por tipo
SELECT element_type, COUNT(*) as total
FROM lx_icl_translations
WHERE language_code = 'pt-pt'
GROUP BY element_type;

-- Ver páginas com tradução PT
SELECT
  p_en.post_title as "Título EN",
  p_pt.post_title as "Título PT",
  p_en.post_type as "Tipo"
FROM lx_icl_translations t_en
LEFT JOIN lx_icl_translations t_pt ON t_en.trid = t_pt.trid AND t_pt.language_code = 'pt-pt'
LEFT JOIN lx_posts p_en ON t_en.element_id = p_en.ID
LEFT JOIN lx_posts p_pt ON t_pt.element_id = p_pt.ID
WHERE t_en.language_code = 'en'
  AND p_en.post_status = 'publish'
  AND p_en.post_type IN ('page', 'product')
ORDER BY p_en.post_type, p_en.post_title;
```

**Decisão:**
- Se >50% traduções PT estão OK → considerar OPÇÃO 3 (híbrido)
- Se <50% traduções PT ou vazias → OPÇÃO 1 (limpar tudo)

---

### 2. Preparar Script Limpeza WPML

**Arquivo:** `scripts/cleanup_wpml_tables.sql`

```sql
-- BACKUP OBRIGATÓRIO ANTES DE EXECUTAR!
-- docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web > backup_pre_cleanup.sql

-- Remover todas as tabelas WPML
DROP TABLE IF EXISTS lx_icl_languages;
DROP TABLE IF EXISTS lx_icl_translations;
DROP TABLE IF EXISTS lx_icl_translation_status;
DROP TABLE IF EXISTS lx_icl_content_status;
DROP TABLE IF EXISTS lx_icl_core_status;
DROP TABLE IF EXISTS lx_icl_flags;
DROP TABLE IF EXISTS lx_icl_languages_translations;
DROP TABLE IF EXISTS lx_icl_locale_map;
DROP TABLE IF EXISTS lx_icl_message_status;
DROP TABLE IF EXISTS lx_icl_node;
DROP TABLE IF EXISTS lx_icl_reminders;
DROP TABLE IF EXISTS lx_icl_strings;
DROP TABLE IF EXISTS lx_icl_string_batches;
DROP TABLE IF EXISTS lx_icl_string_packages;
DROP TABLE IF EXISTS lx_icl_string_pages;
DROP TABLE IF EXISTS lx_icl_string_positions;
DROP TABLE IF EXISTS lx_icl_string_status;
DROP TABLE IF EXISTS lx_icl_string_translations;
DROP TABLE IF EXISTS lx_icl_string_urls;
DROP TABLE IF EXISTS lx_icl_translate;
DROP TABLE IF EXISTS lx_icl_translate_job;
DROP TABLE IF EXISTS lx_icl_translations;

-- Remover opções WPML
DELETE FROM lx_options WHERE option_name LIKE '%wpml%';
DELETE FROM lx_options WHERE option_name LIKE '%icl%';
DELETE FROM lx_options WHERE option_name LIKE '%sitepress%';

-- Limpar postmeta WPML
DELETE FROM lx_postmeta WHERE meta_key LIKE '%wpml%';
DELETE FROM lx_postmeta WHERE meta_key LIKE '%icl%';

-- Limpar usermeta WPML
DELETE FROM lx_usermeta WHERE meta_key LIKE '%wpml%';
DELETE FROM lx_usermeta WHERE meta_key LIKE '%icl%';
```

---

### 3. Configurar Transposh (Pós-Limpeza)

**Query SQL para ajustes rápidos:**
```sql
-- Trocar default language para PT
UPDATE lx_options
SET option_value = REPLACE(
  REPLACE(option_value,
    's:16:"default_language";s:2:"en"',
    's:16:"default_language";s:2:"pt"'
  ),
  's:18:"viewable_languages";s:8:"en,pt,es"',
  's:18:"viewable_languages";s:5:"pt,en"'
)
WHERE option_name = 'transposh_options';

-- Ativar permalinks /en/
UPDATE lx_options
SET option_value = REPLACE(option_value,
  's:17:"enable_permalinks";i:0',
  's:17:"enable_permalinks";i:1'
)
WHERE option_name = 'transposh_options';
```

**Ou via WordPress Admin (preferível):**
1. Login: http://localhost:8080/wp-admin
2. Settings → Transposh
3. Alterar:
   - Default language: pt
   - Viewable languages: pt, en
   - Enable permalinks: checked
   - Save

---

### 4. Adicionar Language Switcher

**Método rápido via Widget:**
```php
// Aparência → Widgets
// Widget "Translation" (Transposh)
// Arrastar para "Header" ou "Footer"
```

**Método avançado via Flatsome Header Builder:**
```php
// Flatsome → Theme Options → Header Builder
// Add Element → HTML
// Code:
<?php if (function_exists('transposh_widget')) { transposh_widget(); } ?>
```

---

## TIMELINE COMPLETA

| Dia | Tarefa | Duração | Status |
|-----|--------|---------|--------|
| D1 | Auditar traduções WPML existentes | 2h | ⏳ Pendente |
| D1 | Decidir OPÇÃO 1/2/3 (com cliente) | 1h | ⏳ Aguardando |
| D2 | Backup + Limpar WPML (se OPÇÃO 1) | 1h | ⏳ Pendente |
| D2 | Configurar Transposh PT/EN | 1h | ⏳ Pendente |
| D2 | Language switcher header | 1h | ⏳ Pendente |
| D3 | Traduzir páginas institucionais (11) | 3h | ⏳ Pendente |
| D3 | Traduzir top 20 produtos (manual) | 2h | ⏳ Pendente |
| D4 | Auto-tradução 111 produtos restantes | 1h | ⏳ Pendente |
| D4 | Strings Loco Translate (WooCommerce) | 2h | ⏳ Pendente |
| D5 | Testes e validação | 2h | ⏳ Pendente |
| D5 | Documentação cliente | 1h | ⏳ Pendente |
| **TOTAL** | | **17h** | |

**Prazo:** 5 dias úteis (~3.5h/dia)

---

## PERGUNTAS PARA O CLIENTE (Tiago Andrade)

### Decisão Crítica: WPML vs Transposh

**Contexto:**
- Site antigo tinha WPML (pago, €258/ano)
- Plugins foram removidos, mas database tem 127 traduções PT
- Transposh (free) já está instalado e funcionando

**Perguntas:**

1. **Budget multilíngue:**
   - Aceita pagar €258/ano pelo WPML profissional?
   - Ou prefere solução free (Transposh)?

2. **Traduções existentes:**
   - As 127 traduções PT do WPML antigo são valiosas?
   - Vale a pena auditá-las ou começar do zero?

3. **Qualidade vs velocidade:**
   - Prioriza tradução 100% manual (WPML, lento)?
   - Ou aceita 80% auto-tradução Google + 20% revisão (Transposh, rápido)?

4. **Idioma principal:**
   - Site deve ser PT com versão EN (turistas)?
   - Ou EN com versão PT (mercado internacional)?

5. **Escopo tradução:**
   - 131 produtos: todos com descrição longa traduzida?
   - Ou apenas nome + descrição curta (suficiente para lançamento)?

6. **Timeline:**
   - Precisa bilingue antes Black Friday (nov)?
   - Ou pode lançar PT primeiro, EN depois?

---

## RECOMENDAÇÃO EXECUTIVA

**Para Tiago Andrade:**

> "Sugiro **OPÇÃO 1**: Limpar WPML antigo e usar apenas Transposh (free).
>
> **Razões:**
> - Economiza €258/ano (orçamento apertado)
> - WPML versão antiga (2015) provavelmente incompatível com WordPress atual
> - Transposh cobre 95% das necessidades (turistas PT/EN)
> - Auto-tradução Google acelera lançamento (Black Friday chegando)
> - Cliente ganha autonomia (edição inline simples)
>
> **Trade-off:**
> - Perde 127 traduções antigas (qualidade desconhecida)
> - Precisa 2-3 dias para retrabalho manual (páginas críticas)
>
> **Garantia:**
> - Backup completo antes de qualquer mudança
> - Se não funcionar, posso reverter em 30min
> - Se cliente precisar WPML depois, migramos (mas perde traduções Transposh)
>
> **Decisão:** Preciso OK do cliente para prosseguir."

---

**Preparado por:** Bilal Machraa / AiParaTi
**Data:** 23 Outubro 2025
**Próxima ação:** Aguardando decisão cliente sobre OPÇÃO 1/2/3
