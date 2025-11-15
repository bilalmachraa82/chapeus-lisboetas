# 🔍 PLANO FORENSE - 16 PASTAS NÃO MATCHADAS

## 📊 SITUAÇÃO ATUAL

**✅ SUCESSO:**
- 24 produtos matchados
- 216 fotos AI linkadas
- 0 erros

**⚠️ POR RESOLVER:**
- **16 pastas** sem match (135 imagens)
- **4 pastas** sem SKU extraído
- **12 SKUs** sem produto correspondente

---

## 🎯 ESTRATÉGIA DE RECUPERAÇÃO

### FASE 1: Análise Forense Database (5 min)

**Objetivo:** Encontrar produtos com SKUs similares na base de dados

```sql
-- Buscar SKUs com sufixos (18220mi → 18220)
SELECT ID, post_title, meta_value as sku
FROM lx_posts p
INNER JOIN lx_postmeta pm ON p.ID = pm.post_id
WHERE p.post_type = 'product'
AND pm.meta_key = '_sku'
AND (
   meta_value LIKE '18220%' OR
   meta_value LIKE '15266%' OR
   meta_value LIKE '18106%' OR
   meta_value LIKE '18110%' OR
   meta_value LIKE '18161%' OR
   meta_value LIKE '18500%' OR
   meta_value LIKE '18521%' OR
   meta_value LIKE '22195%' OR
   meta_value LIKE '181054%' OR
   meta_value LIKE '181056%' OR
   meta_value LIKE '344974%' OR
   meta_value LIKE '22100%'
);
```

**Pastas a investigar:**
1. `18220mi` → Buscar SKU 18220*
2. `15266f/15266c` → Buscar SKU 15266* (provavelmente variações de cor)
3. `18106mi/k/g/ma` → Buscar SKU 18106* (4 variações)
4. `18110ec/ol` → Buscar SKU 18110*
5. `18161n/m` → Buscar SKU 18161*
6. `18500mi` → Buscar SKU 18500*
7. `18521a` → Buscar SKU 18521*
8. `22195` → Verificar se existe na base
9. `181054` → Pack 12 (pode não estar no e-commerce)
10. `181056` → Chapéu impermeável
11. `344974` → Gorro Docker
12. `22100` → Gorro Miki Docker

---

### FASE 2: Análise Visual dos Logs (10 min)

**Objetivo:** Rastrear a origem das fotos AI nos logs de geração

**Comando:**
```bash
# Verificar logs de geração AI
grep -r "18220mi\|15266\|18106\|18110\|18161\|18500\|18521\|22195\|181054\|181056\|344974\|22100" \
  relatorios/*.log output_catalogo/*.json 2>/dev/null

# Procurar pastas originais
find wordpress/wp-content/uploads/catalogo2025 -type d -name "*18220*" -o -name "*15266*"
```

**Ficheiros a verificar:**
- `relatorios/ai_processing_*.log` → Registos de geração
- `output_catalogo/catalogo.json` → Catálogo mestre
- `scripts/gemini_image_pro.py` → Lógica de nomeação de pastas

---

### FASE 3: Match Manual por Categoria (15 min)

**Pastas SEM SKU extraído (4 pastas):**

| Pasta | Imagens | Análise | Ação Proposta |
|-------|---------|---------|---------------|
| `bonnet-pierre-cardin` | 3 | Pierre Cardin brand → Boina sextavada | Buscar "Pierre Cardin" no título |
| `chapeu-art-970-pack-12` | 6 | Pack atacado | Provavelmente não e-commerce |
| `hologramme` | 8 | Marca fornecedor | Fotos genéricas? Eliminar ou usar como "sobre nós" |
| `tags-fabricado-na-italia-la-pura` | 8 | Tags de produto | Não são fotos de produto |

**SQL Match por Título:**
```sql
-- Bonnet Pierre Cardin
SELECT ID, post_title FROM lx_posts
WHERE post_type = 'product'
AND post_title LIKE '%Pierre Cardin%';

-- Art 970
SELECT ID, post_title FROM lx_posts
WHERE post_type = 'product'
AND (post_title LIKE '%970%' OR post_title LIKE '%pack%');
```

---

### FASE 4: Análise de Imagens Originais (20 min)

**Objetivo:** Comparar fotos AI com originais para identificar produto

**Método:**
1. Abrir cada pasta de fotos AI não matchadas
2. Ver a primeira imagem (img_01_pro.jpg)
3. Comparar visualmente com produtos no site
4. Identificar por:
   - Cor do chapéu
   - Formato (boina, panamá, gorro)
   - Padrão (liso, quadrados, herringbone)

**Comando para ver imagens:**
```bash
# Ver primeira imagem de cada pasta não matchada
open "wordpress/wp-content/uploads/products/boinas inverno/18220mi/img_01_pro.jpg"
open "wordpress/wp-content/uploads/products/boinas inverno/bone-15266f-bone-15266c/img_01_pro.jpg"
# ... etc
```

---

### FASE 5: Script de Match Semi-Automático (30 min)

**Criar `match_remaining_folders.py`:**

```python
# Mapeamento manual baseado na análise forense
MANUAL_MAPPINGS = {
    # Pastas onde o SKU existe mas com sufixo diferente
    '18220mi': '18220',  # Tentar match parcial
    '18106mi': '18106',
    '18106k': '18106',
    '18106g': '18106',
    '18106ma': '18106',

    # Variações de cor (F=feminino, C=cinza?)
    '15266f': '15266',
    '15266c': '15266',

    # Pack 12 → Ignorar (atacado, não e-commerce)
    'chapeu-art-970-pack-12': None,
    '181054': None,

    # Tags → Usar para "Sobre Nós" ou eliminar
    'tags-fabricado-na-italia-la-pura': None,
    'hologramme': None,

    # Pierre Cardin → Match por título
    'bonnet-pierre-cardin': 'FIND_BY_TITLE:Pierre Cardin'
}

def find_product_by_partial_sku(sku_prefix):
    """Buscar produto com SKU que começa com prefixo"""
    query = """
        SELECT ID, post_title, meta_value as sku
        FROM lx_posts p
        INNER JOIN lx_postmeta pm ON p.ID = pm.post_id
        WHERE p.post_type = 'product'
        AND pm.meta_key = '_sku'
        AND meta_value LIKE %s
        LIMIT 1
    """
    return execute_query(query, (f'{sku_prefix}%',))
```

---

## 📋 TIMELINE & EXECUÇÃO

### Prioridade 1: Quick Wins (30 min)
1. ✅ Executar SQL para buscar SKUs parciais
2. ✅ Match Pierre Cardin por título
3. ✅ Eliminar pastas de pack/tags

**Resultado esperado:** +5-8 produtos matchados

### Prioridade 2: Análise Visual (30 min)
1. Abrir imagens não matchadas
2. Comparar com catálogo atual
3. Criar mapeamento manual

**Resultado esperado:** +4-6 produtos matchados

### Prioridade 3: Decisão Final (10 min)
- Pastas que não têm correspondência: **eliminar ou arquivar?**
- Pastas de "pack": **não usar em e-commerce**
- Tags/genéricas: **usar em "Sobre Nós" ou descartar**

---

## 🎯 META FINAL

**Objetivo realista:**
- 28-32 produtos com fotos AI (de 40 pastas)
- 70-80% de cobertura
- Pastas restantes: arquivadas ou eliminadas

**Se não conseguirmos match:**
- Opção A: Deixar produtos com fotos originais
- Opção B: Usar fotos AI genéricas na homepage/banner
- Opção C: Batch 2 completo pode resolver (415 fotos adicionais)

---

## 🚀 PRÓXIMOS PASSOS IMEDIATOS

```bash
# 1. Executar análise SQL
python3 scripts/analyze_unmatched_skus.py

# 2. Ver relatório
cat relatorios/unmatched_analysis.txt

# 3. Match manual assistido
python3 scripts/match_remaining_folders.py --interactive

# 4. Verificar site
open http://localhost:8080/loja
```

---

**Status:** Plano criado
**Data:** 2025-11-13
**Progresso atual:** 24/40 produtos (60%) → Meta: 28-32/40 (70-80%)
