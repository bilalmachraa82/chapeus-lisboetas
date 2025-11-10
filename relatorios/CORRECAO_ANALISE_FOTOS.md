# CORREÇÃO - ANÁLISE DE FOTOS (NÚMEROS REAIS)

**Data:** 2025-11-10 08:30
**Erro Identificado:** Script anterior não validava caminhos relativos corretamente

---

## ❌ ERRO NO RELATÓRIO ANTERIOR

### O que foi reportado (ERRADO):
- ✅ Com fotos: **28/86** produtos (32%)
- ❌ Sem fotos: **58/86** produtos (68%)

### Por que estava errado:
O script `analyze_product_images.py` procurava ficheiros em `./images/...` quando os caminhos no catalog.json são relativos a `output_catalogo/images/...`

```python
# ANTES (errado):
img_path = Path(local_img['path'])  # ex: images/boinas inverno/bone-22182/img_01.jpg
if img_path.exists():  # procura em ./images/... → NÃO EXISTE!
    valid_local.append(...)

# DEPOIS (correto):
candidates = [
    img_path,
    Path('output_catalogo') / img_path,  # ← CORRIGE AQUI!
    Path('wordpress') / img_path
]
for candidate in candidates:
    if candidate.exists():
        valid_local.append(...)
        break
```

---

## ✅ NÚMEROS REAIS (CORRETOS)

### Após correção do script:
- ✅ **Com fotos: 73/86 produtos (84.9%)**
- ❌ **Sem fotos: 13/86 produtos (15.1%)**

### Distribuição de Fotos:
- **Com 1 foto:** 2 produtos
- **Com 2+ fotos:** 71 produtos (82%)
- **Máximo fotos:** 34 fotos (bone-15266f-bone-15266c)
- **Média:** 7.3 fotos/produto

### Tipo de Fotos:
- **Fotos locais:** 73 produtos (ficheiros em `output_catalogo/images/...`)
- **Fotos URLs:** Alguns produtos também têm URLs externas (Google Photos)
- **Fotos scraped:** 0 (scraping hologrammeparis.com retorna 403/404)

---

## 📋 13 PRODUTOS SEM FOTOS

| # | SKU | Preço | Nome | Ação |
|---|-----|-------|------|------|
| 1 | `bone-22174` | €29.90 | BOINA OITAVADA HARRINGBONE | Cliente fornecer |
| 2 | `casquette-18534n` | €37.50 | Boina verão Itália | Cliente fornecer |
| 3 | `chapeu-australiano` | €67.50 | CHAPEU AUSTRALIANO | **ALTO VALOR** - Cliente fornecer |
| 4 | `chapeu-colonial-pith-helmet` | €45.00 | CHAPEU COLONIAL | Cliente fornecer |
| 5 | `palha-12403` | €3.00 | CHAPÉUS DE PALHA FEMININOS | Remover (valor baixo) |
| 6 | `bone-2018016` | **INVÁLIDO** | BONÉS VERÃO MULHERES | **REMOVER** (preço inválido) |
| 7 | `chapeu-cloche` | €35.00 | CHAPEU CLOCHE | Cliente fornecer |
| 8 | `casquete` | €1.00 | CASQUETE | Remover (valor baixo) |
| 9 | `chapeu-cerimonia-perolas` | €2.00 | CHAPÉU CERIMÓNIA PERÓLAS | Remover (valor baixo) |
| 10 | `chapeu-cerimonia-flores` | €3.00 | CHAPÉU CERIMÓNIA FLORES | Remover (valor baixo) |
| 11 | `solid` | €19.90 | CHAPÉU UV | Cliente fornecer (preço médio) |
| 12 | `bucket-hat-reversivel` | €19.90 | BUCKET HAT REVERSIVEL | Cliente fornecer (popular) |
| 13 | `chapeu-cowboy` | €2.00 | CHAPÉU COWBOY | Remover (valor baixo) |

---

## 🎯 DECISÃO IMPORTAÇÃO

### Cenário A: Import Máximo (67 produtos)
**Incluir:** 73 com fotos - 6 sem fotos de valor baixo = **67 produtos**

**Excluir apenas:**
- 6 produtos valor baixo/inválido: palha-12403, bone-2018016, casquete, chapeu-cerimonia-perolas, chapeu-cerimonia-flores, chapeu-cowboy
- Total valor excluído: ~€14 (desprezível)

**Pedir fotos ao cliente:**
- 7 produtos valor médio/alto (€29.90 - €67.50)
- Total valor bloqueado: ~€270
- Prazo sugerido: 3-5 dias úteis

### Cenário B: Import Imediato (73 produtos)
**Incluir:** Todos os 73 com fotos (mesmo os de valor baixo)
**Excluir:** Apenas 13 sem fotos
**Vantagem:** Deploy mais rápido, catálogo completo

### Cenário C: Import Conservador (66 produtos)
**Incluir:** Apenas produtos com 2+ fotos (71) - 5 problemáticos = 66
**Excluir:** 20 produtos (13 sem fotos + 7 duvidosos)
**Vantagem:** Qualidade máxima garantida

---

## 📊 COMPARAÇÃO COM GOOGLE SHEET

### O que o utilizador reportou:
- **88 linhas** com valores no campo "Imagens" (caminhos relativos)
- **26 linhas** vazias

### O que o script deteta (catalog.json):
- **73 produtos** com fotos (após deduplicação de 28 duplicados)
- **13 produtos** sem fotos

### Reconciliação:
```
Google Sheet original: 114 produtos
  - 28 duplicados removidos (FASE 3)
  = 86 produtos únicos

Campo "Imagens" original: 88 preenchidos, 26 vazios
  - Após dedup: 73 preenchidos, 13 vazios
  ✅ NÚMEROS BATEM!
```

---

## 🔧 CORREÇÕES APLICADAS

### 1. Script `analyze_product_images.py`
```python
# Linha 177-201 (corrigido)
candidates = [
    img_path,
    Path('output_catalogo') / img_path,  # ← ADICIONADO
    Path('wordpress') / img_path
]
for candidate in candidates:
    if candidate.exists():
        valid_local.append({...})
        found = True
        break
```

### 2. Relatórios Re-gerados
- `relatorios/product_images_analysis.json` (atualizado)
- `relatorios/product_images_summary.md` (atualizado)
- `relatorios/CORRECAO_ANALISE_FOTOS.md` (este ficheiro)

---

## 🚀 IMPACTO NO PLANO

### ANTES (com erro):
- ❌ 28 produtos importáveis
- ❌ 58 produtos bloqueados
- ❌ Catálogo muito limitado

### AGORA (correto):
- ✅ **73 produtos prontos para import** (84.9%)
- ✅ Apenas 13 bloqueados (15.1%)
- ✅ **Catálogo quase completo!**

### Próximos Passos Atualizados:

#### OPÇÃO RECOMENDADA: Cenário B (Import Imediato)
```bash
# 1. Corrigir preços inválidos (5 min)
python3 scripts/fix_invalid_prices.py

# 2. Gerar WooCommerce CSV (2 min)
python3 scripts/generate_wc_catalog.py
# Output: output_catalogo/catalogo_woocommerce_ready.csv (73 produtos)

# 3. Upload imagens para WordPress (10 min)
# Via Media Library ou rsync:
rsync -av output_catalogo/images/ wordpress/wp-content/uploads/products/

# 4. Import produtos via WooCommerce (5 min)
# WooCommerce → Products → Import CSV

# 5. Opcional: Fotoshoot Gemini para os 13 restantes
# Se cliente fornecer fotos caseiras, transformar em profissionais
```

#### Timeline Atualizado:
```
Fase 1: Preparação (30 min)     → HOJ E
Fase 2: Upgrade Stack (2-3 dias) → Dom-Ter
Fase 3: GA4 Install (2h)         → Qua
Fase 4: Import (1h)              → Qua
Fase 5: Testing (1 dia)          → Qui
Fase 6: Deploy (0.5 dia)         → Sex

Go-Live: 15 Nov (9 dias até Black Friday) ✅ VIÁVEL
```

---

## ✅ CONCLUSÃO

### Estado Real do Projeto:
- ✅ **86/86 descrições completas** (100%)
- ✅ **73/86 com fotos** (84.9%) - PRONTOS PARA IMPORT
- ⚠️  **13/86 sem fotos** (15.1%) - 7 valor médio/alto, 6 valor baixo

### Recomendação:
**Import imediato dos 73 produtos com fotos.**

Para os 13 restantes:
- Remover 6 de valor baixo/inválido (não compensam)
- Solicitar fotos dos 7 de valor médio/alto ao cliente (€270 bloqueados)
- Adicionar depois quando tiverem fotos

### Valor do Catálogo:
```
73 produtos com fotos:  ~€2,100 (estimativa)
13 produtos sem fotos:  ~€270 (12.8% do valor)

Import Rate: 84.9% produtos, 88.7% valor ✅
```

---

**Lição Aprendida:** Sempre validar caminhos relativos com múltiplos prefixos (output_catalogo/, wordpress/, ./).

**Próxima Ação:** Aguardando aprovação para import dos 73 produtos ou decisão sobre os 13 restantes.
