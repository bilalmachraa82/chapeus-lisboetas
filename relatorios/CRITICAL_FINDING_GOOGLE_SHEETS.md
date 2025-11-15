# 🔥 CRITICAL FINDING: Google Sheets Structure Mismatch

**Data:** 15 Novembro 2025
**Descoberta durante:** Individual agent testing (SheetSync-Agent)
**Impacto:** BLOCKER para execução do orchestrator

---

## PROBLEMA IDENTIFICADO

### O que esperávamos (CLAUDE.md spec):
Worksheet "Catalogo" com colunas:
- SKU
- Nome
- Preço
- Descrição curta
- Descrição longa
- Tags
- Cor, Tamanho, Composição
- URL fornecedor
- URLs extra
- Imagens
- etc.

### O que realmente existe:
17 worksheets de categoria (BOINAS INVERNO, BOINAS VERÃO, etc.) com estrutura MÍNIMA:
```
Col 0: (vazio) - números de linha (1, 2, 3...)
Col 1: MARCA - marca do produto (HOLOGRAMME, VELEN, etc.)
Col 2: NOME - nome do produto
Col 3: INFORMAÇÕES - info curta
Col 4: (sem header) - URL fornecedor
```

**Sem colunas:** SKU, Preço, Descrição longa, Imagens, Tags, Specs

---

## PORQUÊ O SHEETSYNC-AGENT FALHOU

O agent estava tentando ler colunas que NÃO EXISTEM:

```python
# SheetSync-Agent tentou fazer:
product['sku'] = row[0]      # ❌ Col 0 = números (1, 2, 3...) não SKUs!
product['name'] = row[1]     # ❌ Col 1 = MARCA não nome!
product['price'] = row[2]    # ❌ Col 2 = NOME não preço!
```

**Resultado:** Produtos criados com dados completamente errados:
- SKU = "1", "2", "€27.50" (números de linha e preços!)
- Nome = "HOLOGRAMME" (marca, não nome)
- Preço = nomes de produtos (não preços)

---

## WORKFLOW REAL (descoberto)

O workflow correto JÁ IMPLEMENTADO foi:

```
1. Google Sheets (estrutura simples)
   - 17 worksheets de categoria
   - MARCA, NOME, INFORMAÇÕES, URL

2. scripts/sync_google_sheet.py
   - Lê Google Sheets simples
   - SCRAPE cada URL fornecedor (hologrammeparis.com)
   - Extrai: preço, specs, imagens, descrições
   - Salva: output_catalogo/catalogo.json (ENRIQUECIDO)

3. catalogo.json (62 produtos enriquecidos)
   - Tem TUDO: SKU (gerado), preço, specs, imagens, etc.
   - Pronto para import WordPress

4. WordPress import (manual ou via API)
   - Usa catalogo.json como fonte
```

**Conclusão:** O sistema já funcionava! Mas o SheetSync-Agent foi implementado com base na spec CLAUDE.md que descreve um estado FUTURO (após beautify_google_sheet.py criar aba "Catalogo").

---

## ONDE ESTAMOS AGORA

### ✅ O que já funciona:
1. **scripts/sync_google_sheet.py** - ✅ Lê Google Sheets → catalogo.json
2. **scripts/catalog_scraper.py** - ✅ Scrape URLs fornecedor → enriquece dados
3. **output_catalogo/catalogo.json** - ✅ 62 produtos com preços, specs, imagens
4. **scripts/validate_and_enrich.py** - ✅ Valida URLs, download imagens
5. **scripts/beautify_google_sheet.py** - ⚠️ Cria abas Dashboard/Clean/Pendentes (mas NÃO aba "Catalogo" ainda)

### ❌ O que NÃO funciona:
1. **SheetSync-Agent** - ❌ Tenta ler estrutura que não existe
2. **Resto do orchestrator** - ⏸️ Bloqueado pelo SheetSync

---

## SOLUÇÕES POSSÍVEIS

### Opção A: Adaptar SheetSync-Agent à realidade 🎯 RECOMENDADO
**Tempo:** 1-2 horas
**Complexidade:** Baixa

```python
class SheetSyncAgent(BaseAgent):
    def run(self):
        # 1. Lê catalogo.json (fonte da verdade)
        with open('output_catalogo/catalogo.json') as f:
            enriched_products = json.load(f)

        # 2. Cria/atualiza produtos WordPress
        for product in enriched_products:
            if product.get('price') and product['price'] > 0:
                self.create_or_update_product(product)
            else:
                self.logger.info(f"Skip {product['name']} - NO PRICE")

        # 3. Opcional: Sync back SKU/status para Google Sheets
        self.update_google_sheet_status()
```

**Vantagens:**
- ✅ Usa dados já enriquecidos (scrape feito)
- ✅ Rápido de implementar
- ✅ Não quebra workflow existente
- ✅ Pode executar orchestrator HOJE

**Desvantagens:**
- ⚠️ catalogo.json tem apenas 62 produtos (não todos os 200+)
- ⚠️ Precisa rodar scripts/sync_google_sheet.py primeiro

---

### Opção B: Criar aba "Catalogo" no Google Sheets
**Tempo:** 4-8 horas
**Complexidade:** Média

Usar beautify_google_sheet.py para:
1. Ler todas as 17 worksheets
2. Merge com catalogo.json (preços, specs)
3. Criar nova aba "Catalogo" com estrutura completa
4. Populate com TODOS os dados (200+ produtos)

**Vantagens:**
- ✅ Alinha com spec CLAUDE.md
- ✅ Google Sheet vira fonte única da verdade
- ✅ SheetSync-Agent funciona conforme spec

**Desvantagens:**
- ⚠️ Demora mais
- ⚠️ Precisa scrape dos produtos restantes (200 - 62 = 138)
- ⚠️ Workflow mais complexo

---

### Opção C: Hybrid (Opção A + B gradual) ⭐ MELHOR LONGO PRAZO
**Tempo:** 2 horas imediato + 1 semana gradual
**Complexidade:** Média

**Fase 1 (HOJE):**
- Implementar Opção A (SheetSync lê catalogo.json)
- Executar orchestrator com 62 produtos
- Deploy emergency (photos + produtos básicos)

**Fase 2 (Esta semana):**
- Scrape dos 138 produtos restantes
- Merge tudo em catalogo.json (200+ produtos)
- Re-executar SheetSync

**Fase 3 (Próxima semana):**
- Criar aba "Catalogo" no Google Sheets
- Migrar SheetSync para ler Google Sheets diretamente
- Google Sheets vira master source

**Vantagens:**
- ✅ Desbloqueia orchestrator HOJE
- ✅ Progressivo (não all-or-nothing)
- ✅ Chega ao estado ideal gradualmente

---

## RECOMENDAÇÃO

**Implementar Opção C (Hybrid)** 🎯

### IMEDIATO (próximas 2 horas):
1. ✅ Testar todos os agents - **CONCLUÍDO**
2. ✅ Identificar gaps - **CONCLUÍDO**
3. 🔧 Adaptar SheetSync-Agent para ler catalogo.json
4. ▶️ Executar orchestrator Phases 1-6 (com 62 produtos)
5. 📊 Gerar relatório para cliente

### ESTA SEMANA:
6. Scrape 138 produtos restantes (hologrammeparis.com)
7. Re-executar SheetSync (200+ produtos)
8. Implementar 4 agents críticos:
   - IfthenPay-Agent (pagamentos)
   - CTT-Agent (envios)
   - CookieYes-Agent (RGPD)
   - Flatsome-Agent (tema)

### PRÓXIMA SEMANA:
9. Criar aba "Catalogo" em Google Sheets
10. Migrar SheetSync para fonte Google Sheets
11. Deploy production

---

## IMPACTO NOS OUTROS AGENTS

### Agents afetados pela descoberta:
1. **SheetSync-Agent** - ❌ Bloqueado (fix prioritário)
2. **SheetSanitizer-Agent** - ⚠️ Também lê estrutura errada
3. **DataDiff-Agent** - ⚠️ Placeholder, mas precisará catalogo.json

### Agents NÃO afetados:
- ✅ PhotoTriage-Agent (usa filesystem)
- ✅ ImageInventory-Agent (usa filesystem)
- ✅ GalleryLinker-Agent (usa WordPress DB)
- ✅ PriceGate-Agent (usa WordPress DB)
- ✅ DescriptionBuilder, VariationBuilder, etc. (WordPress DB)
- ✅ WooPagesFixer, MenuUXFix, VisualQA (WordPress)
- ✅ Security&SEO, ImportVerifier (WordPress)

**Conclusão:** Apenas Phase 1 afetada (Data Foundation). Resto do orchestrator pode executar normalmente após fix.

---

## CATALOGO.JSON STATUS

**Ficheiro:** `output_catalogo/catalogo.json`
**Produtos:** 62
**Status:** ✅ Enriquecido com scrape

**Campos disponíveis:**
```json
{
  "sheet": "BOINAS INVERNO",
  "brand": "HOLOGRAMME",
  "name": "BOINA BICO DE PATO AJUSTÁVEL",
  "info_short": "Tamanho ajustável",
  "supplier_url": "https://hologrammeparis.com/...",
  "price": 27.5,  // ✅ Preço real
  "supplier_code": "Boné – 22182",  // Pode virar SKU
  "tags": ["Inverno", "Tamanho ajustável"],
  "specs": {
    "COR": "Sortido",
    "TAMANHO": "Tamanho único ajustável",
    "VENDIDO POR": "Pacote 12",
    "COMPOSIÇÃO": "100% Poliéster"
  },
  "variations": "4*preto, 3*marrom...",
  "downloaded_images": [...]  // ✅ Imagens prontas
}
```

**Produtos por worksheet:**
- BOINAS INVERNO: ~15 produtos
- BOINAS VERÃO: ~12 produtos
- PANAMÁ: ~8 produtos
- Outros: ~27 produtos
- **Total:** 62 produtos com dados completos

**Faltam:** ~138 produtos (200 total esperado)

---

## PRÓXIMOS PASSOS

### 1. Adaptar SheetSync-Agent (2 horas)
```python
def run(self) -> int:
    # Load enriched catalog
    catalogo_path = BASE_DIR / 'output_catalogo/catalogo.json'
    with open(catalogo_path) as f:
        products = json.load(f)

    self.metrics.items_total = len(products)

    for product in products:
        # Extract SKU from supplier_code or generate
        sku = self.extract_or_generate_sku(product)

        # NO PRICE = NO PUBLISH
        if not product.get('price') or product['price'] <= 0:
            self.add_warning(f"Skip {product['name']} - NO PRICE")
            self.record_skip()
            continue

        # Create/update WordPress product
        success = self.create_or_update_product(
            sku=sku,
            name=product['name'],
            price=product['price'],
            description=product.get('info_short', ''),
            specs=product.get('specs', {}),
            images=product.get('downloaded_images', []),
            category=product['sheet']
        )

        if success:
            self.record_success()
        else:
            self.record_failure()
```

### 2. Executar orchestrator
```bash
python3 orchestrator/orchestrator_3_1.py
```

### 3. Validar resultado
- 62 produtos importados
- Preços corretos
- Imagens linkadas
- Categorias mapeadas

---

## CONCLUSÃO

**Descoberta crítica:** Google Sheets tem estrutura simples (MARCA, NOME, URL), não estrutura completa esperada.

**Causa raiz:** SheetSync-Agent baseado em spec futura (aba "Catalogo" ainda não criada).

**Solução imediata:** Adaptar SheetSync para ler catalogo.json (dados já enriquecidos).

**Timeline:**
- ✅ Testing concluído (1 hora)
- 🔧 Fix SheetSync (2 horas) → NEXT
- ▶️ Executar orchestrator (30 min)
- 📊 Relatório para cliente (30 min)

**Impacto:** Desbloqueia orchestrator execution HOJE com 62 produtos.

---

**Próxima ação:** Adaptar SheetSync-Agent para ler catalogo.json

**Generated by:** Claude Code
**For:** Bilal / AiParaTi
**Cliente:** Chapéus Lisboeta (Tiago Andrade)
