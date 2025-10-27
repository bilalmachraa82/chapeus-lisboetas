# 🎯 RELATÓRIO FINAL - Sincronização Google Sheets → WooCommerce

**Data:** 26 Outubro 2025, 09:30
**Status:** ✅ **PRONTO PARA IMPORTAR**
**Tempo total:** ~30 minutos

---

## 📊 RESUMO EXECUTIVO

### ✅ Pipeline Completo Executado

| Fase | Status | Resultado |
|------|--------|-----------|
| **FASE 0** | ✅ Completa | Conexão ao Google Sheet estabelecida |
| **FASE 1** | ✅ Completa | 114 produtos sincronizados do Google Sheet |
| **FASE 2** | ⏭️ Pulada | Dados já enriquecidos (scraping prévio OK) |
| **FASE 3** | ⏭️ Pulada | Abas Dashboard já existem no Google Sheet |
| **FASE 4** | ✅ Completa | 96 produtos exportados para CSV WooCommerce |
| **FASE 5** | ⏸️ Aguardando | Backup 54MB criado, pronto para importar |

---

## 📈 ESTATÍSTICAS

### Google Sheet → Local

```
✅ Conectado a: "WEBSITE Produtos Catálogo"
📊 26 abas totais (17 categorias + 8 auxiliares + 1 master)

Produtos sincronizados:
  - Total: 114 produtos
  - Com preço válido: 79 produtos (69.3%)
  - Sem preço (loja física): 35 produtos (30.7%)
```

### Catalogo → WooCommerce CSV

```
✅ Processados: 114 produtos
✅ Exportados: 96 produtos (com imagens)
⚠️  Excluídos: 18 produtos (sem imagens - precisam atenção)

Ficheiro gerado: woocommerce_import_localhost.csv (96 produtos)
Tamanho: ~1.5 MB
Imagens: Paths completos para http://localhost:8080
```

### Backup Segurança

```
💾 Ficheiro: backup_before_import_20251026.sql
📏 Tamanho: 54 MB
⏰ Data: 26 Out 2025, 09:30
✅ Status: Pronto para restore se necessário
```

---

## 📋 PRÓXIMOS PASSOS - IMPORT MANUAL

### Opção A: Import via WordPress Admin (RECOMENDADO)

**Passo 1:** Abrir WordPress Admin
```bash
open http://localhost:8080/wp-admin
# Login: lisboetas / [senha do cliente]
```

**Passo 2:** Navegar para WooCommerce Import
```
WooCommerce → Products → Import
```

**Passo 3:** Upload CSV
```
1. Click "Choose File"
2. Selecionar: output_catalogo/woocommerce_import_localhost.csv
3. Click "Continue"
```

**Passo 4:** Mapear Colunas (automático)
```
WooCommerce reconhece automaticamente as colunas.
Verificar se tudo está mapeado corretamente:
  ✅ SKU → SKU
  ✅ Name → Name
  ✅ Regular price → Regular price
  ✅ Categories → Categories
  ✅ Images → Images
  ✅ Attributes → Attributes

Click "Run the importer"
```

**Passo 5:** Aguardar Import
```
⏳ Progresso: WooCommerce mostra barra de progresso
⏱️ Tempo estimado: 3-5 minutos para 96 produtos
✅ Conclusão: "Import complete!"
```

**Passo 6:** Verificar Resultados
```bash
# Ver total importado
open http://localhost:8080/wp-admin/edit.php?post_type=product

# Ver loja frontend
open http://localhost:8080/shop/
```

---

### Opção B: Import via WP-CLI (automático)

```bash
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

# Import via CLI
docker exec chapeus_wordpress wp import csv \
  /var/www/html/output_catalogo/woocommerce_import_localhost.csv \
  --authors=1 \
  --allow-root

# OU usar WooCommerce CLI diretamente
docker exec chapeus_wordpress wp wc product import \
  output_catalogo/woocommerce_import_localhost.csv \
  --user=1 \
  --allow-root
```

**Nota:** WP-CLI pode falhar se CSV tiver formato específico WooCommerce.
**Recomendação:** Usar Opção A (WordPress Admin) para primeira importação.

---

## 🔍 VERIFICAÇÃO PÓS-IMPORT

### 1. Totais no Database

```bash
# Total produtos WooCommerce
docker exec chapeus_wordpress wp post list --post_type=product --format=count --allow-root

# Esperado: ~96 novos produtos (pode haver produtos antigos também)

# Produtos publicados (com preço)
docker exec chapeus_wordpress wp post list \
  --post_type=product \
  --post_status=publish \
  --format=count \
  --allow-root

# Produtos rascunho (sem preço)
docker exec chapeus_wordpress wp post list \
  --post_type=product \
  --post_status=draft \
  --format=count \
  --allow-root
```

### 2. Verificação Visual

**Abrir site:**
```bash
open http://localhost:8080/shop/
```

**Checklist:**
- [ ] Produtos aparecem na loja?
- [ ] Imagens carregam corretamente?
- [ ] Preços estão corretos? (€20-40 faixa esperada)
- [ ] Categorias mapeadas? (Chapéus > Boinas > Inverno)
- [ ] Atributos visíveis? (Cor, Tamanho, Composição)
- [ ] Descrições completas?

**Testar 3-5 produtos aleatórios:**
1. BOINA BICO DE PATO AJUSTÁVEL (SKU: Boné – 22182) - €27.50
2. BOINA OITAVA INVERNO (SKU: Boné – 25025) - €29.90
3. [Escolher mais 3 aleatórios]

---

## 📊 PRODUTOS EXCLUÍDOS (18 sem imagens)

**⚠️ Estes 18 produtos NÃO foram exportados** porque não têm imagens.

**Próximo passo (opcional):**
1. Verificar quais são os 18 produtos
2. Adicionar imagens no Google Sheet
3. Re-executar pipeline (só FASE 1 → FASE 4)
4. Import incremental

**Como ver os 18 produtos sem imagens:**
```bash
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

python3 -c "
import json

data = json.load(open('output_catalogo/catalogo.json'))
sem_imagens = []

for p in data:
    # Check if product has valid price
    price_str = str(p.get('price', '')).strip()
    try:
        price_float = float(str(price_str).replace('€','').replace(',','.'))
        if price_float > 0:
            # Has price, check images
            images = p.get('downloaded_images', []) or p.get('filtered_images', [])
            if not images or len(images) == 0:
                sem_imagens.append({
                    'name': p.get('name', 'N/A'),
                    'sku': p.get('sku') or p.get('supplier_code', 'N/A'),
                    'price': price_float,
                    'sheet': p.get('sheet', 'N/A')
                })
    except:
        pass

print(f'📦 Produtos COM preço MAS SEM imagens: {len(sem_imagens)}')
print('')
for i, p in enumerate(sem_imagens, 1):
    print(f\"{i}. {p['name']} (SKU: {p['sku']}) - €{p['price']:.2f} [{p['sheet']}]\")
"
```

---

## 🗂️ FICHEIROS GERADOS

### Principais (para usar)

| Ficheiro | Descrição | Uso |
|----------|-----------|-----|
| `output_catalogo/catalogo.json` | Master catalog (114 produtos) | Fonte de dados completa |
| `output_catalogo/woocommerce_import_localhost.csv` | CSV para WooCommerce (96 produtos) | **IMPORTAR ESTE** |
| `backup_before_import_20251026.sql` | Backup database (54MB) | Restore se algo falhar |

### Auxiliares (referência)

| Ficheiro | Descrição |
|----------|-----------|
| `output_catalogo/catalogo_backup.json` | Backup do catalogo.json anterior (Oct 19) |
| `output_catalogo/catalogo_master_with_price.csv` | Produtos com preço (79 produtos) |
| `output_catalogo/woocommerce_import.csv` | CSV com paths relativos (não usar) |
| `ULTRA_THINK_CHECKLIST_COMPLETA.md` | Checklist detalhada do pipeline |

---

## 🔄 RE-EXECUTAR PIPELINE (se necessário)

Se precisar re-sincronizar no futuro (Google Sheet foi editado):

```bash
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

# Setup vars
export GOOGLE_SHEETS_ID="18Sj_LNokkZZYNSseaPScCSWJ_iann7sbbgiwzva3VzA"
export GOOGLE_SERVICE_ACCOUNT_FILE="config/google-service-account.json"

# Pipeline completo (5 minutos)
echo "📥 FASE 1: Sync Google Sheet..."
python3 scripts/sync_google_sheet.py

echo ""
echo "🔧 Gerar catalogo_master_with_price.csv..."
python3 -c "
import json, csv
data = json.load(open('output_catalogo/catalogo.json'))
with_price = [p for p in data if str(p.get('price','')).strip() and float(str(p.get('price','')).replace('€','').replace(',','.').replace(' ','') or 0) > 0]
with open('output_catalogo/catalogo_master_with_price.csv', 'w', newline='', encoding='utf-8') as f:
    if with_price:
        writer = csv.DictWriter(f, fieldnames=with_price[0].keys())
        writer.writeheader()
        writer.writerows(with_price)
print(f'✅ {len(with_price)} produtos com preço')
"

echo ""
echo "📦 FASE 4: Gerar WooCommerce CSV..."
python3 scripts/generate_wc_catalog.py

echo ""
echo "🌐 Criar versão localhost..."
python3 -c "
import csv
with open('output_catalogo/woocommerce_import.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fieldnames = reader.fieldnames

for row in rows:
    if row.get('Images'):
        images = row['Images'].split(', ')
        images_full = [f'http://localhost:8080/wp-content/uploads/{img.strip()}' for img in images]
        row['Images'] = ', '.join(images_full)

with open('output_catalogo/woocommerce_import_localhost.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
print(f'✅ {len(rows)} produtos no CSV localhost')
"

echo ""
echo "💾 Backup database..."
TIMESTAMP=$(python3 -c "from datetime import datetime; print(datetime.now().strftime('%Y%m%d_%H%M'))")
docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web > backup_reimport_${TIMESTAMP}.sql

echo ""
echo "✅ PIPELINE COMPLETO! Pronto para importar:"
echo "   output_catalogo/woocommerce_import_localhost.csv"
```

---

## ⚠️ TROUBLESHOOTING

### Import falha: "Invalid file"

**Causa:** CSV mal formatado ou encoding errado
**Solução:**
1. Abrir CSV no Excel/Numbers
2. Verificar se header (linha 1) está intacto
3. Salvar como UTF-8 CSV
4. Tentar import novamente

### Produtos importados sem imagens

**Causa:** Paths de imagens inválidos ou ficheiros faltando
**Solução:**
```bash
# Verificar se imagens existem
ls wordpress/wp-content/uploads/catalogo2025/boinas\ inverno/

# Se faltam imagens, copiar do backup
cp -r backup/wp-content/uploads/catalogo2025/* \
   wordpress/wp-content/uploads/catalogo2025/
```

### Preços aparecem errados (€2,023 em vez de €20.23)

**Causa:** Cache do WooCommerce
**Solução:**
```bash
# Limpar cache WooCommerce
docker exec chapeus_wordpress wp cache flush --allow-root
docker exec chapeus_wordpress wp wc product list --format=ids --allow-root | head -10 | \
while read id; do
    docker exec chapeus_wordpress wp post meta delete $id _price_hash --allow-root
done
```

### Produtos duplicados

**Causa:** Import executado 2x
**Solução:**
```bash
# Ver produtos duplicados por SKU
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "
SELECT pm.meta_value as SKU, COUNT(*) as count
FROM lx_posts p
JOIN lx_postmeta pm ON p.ID = pm.post_id
WHERE p.post_type = 'product'
AND pm.meta_key = '_sku'
GROUP BY pm.meta_value
HAVING count > 1;
"

# Eliminar produtos duplicados (CUIDADO!)
# Fazer backup primeiro!
# docker exec chapeus_wordpress wp post delete [ID] --force --allow-root
```

---

## 🎯 PRÓXIMOS PASSOS RECOMENDADOS

### Imediato (hoje)
- [ ] Importar CSV via WordPress Admin
- [ ] Verificar 10 produtos aleatórios
- [ ] Testar checkout (adicionar ao carrinho, ver preços)
- [ ] Documentar quaisquer problemas encontrados

### Curto prazo (esta semana)
- [ ] Adicionar imagens aos 18 produtos faltantes
- [ ] Re-executar pipeline e import incremental
- [ ] Configurar categorias destacadas na homepage
- [ ] Testar fluxo de compra completo (não processar pagamento real)

### Médio prazo (próximas 2 semanas)
- [ ] Otimizar imagens (converter para WebP)
- [ ] Configurar variações de produtos (cores/tamanhos)
- [ ] Adicionar reviews/avaliações (prova social)
- [ ] SEO: meta descriptions para produtos principais

---

## 📞 SUPORTE

Se encontrar problemas durante o import:

1. **Verificar logs do WooCommerce:**
   ```
   http://localhost:8080/wp-admin/admin.php?page=wc-status&tab=logs
   ```

2. **Verificar logs do WordPress:**
   ```bash
   docker logs chapeus_wordpress -f
   ```

3. **Restore backup se necessário:**
   ```bash
   docker exec -i chapeus_mysql mysql -u root -prootpassword lisboetas_web \
     < backup_before_import_20251026.sql
   ```

4. **Contactar:**
   - Bilal / AiParaTi (desenvolvimento)
   - Documentação: `ULTRA_THINK_CHECKLIST_COMPLETA.md`

---

## ✅ CHECKLIST FINAL

### Antes de importar:
- [✅] Backup database criado (54MB)
- [✅] CSV gerado (96 produtos)
- [✅] Imagens existem no servidor (catalogo2025/)
- [✅] WordPress funcionando (http://localhost:8080)

### Durante import:
- [ ] WordPress Admin aberto
- [ ] WooCommerce → Products → Import
- [ ] CSV selecionado corretamente
- [ ] Colunas mapeadas automaticamente
- [ ] Import iniciado ("Run the importer")
- [ ] Aguardar conclusão (~3-5 min)

### Após import:
- [ ] Ver produtos no admin (edit.php?post_type=product)
- [ ] Ver loja frontend (/shop/)
- [ ] Testar 3-5 produtos aleatórios
- [ ] Verificar preços, imagens, descrições
- [ ] Documentar problemas (se houver)
- [ ] Marcar como ✅ COMPLETO

---

**FIM DO RELATÓRIO**
**Status:** ✅ Pronto para importar manualmente via WordPress Admin
**Próximo:** Abrir http://localhost:8080/wp-admin → WooCommerce → Products → Import
