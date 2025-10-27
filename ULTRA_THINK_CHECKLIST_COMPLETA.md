# 🧠 ULTRA-THINK: CHECKLIST COMPLETA - Google Sheets → WooCommerce

**Data:** 26 Outubro 2025
**Contexto:** Alinhar scripts existentes (Oct 19) com novo plano (5 fases) e novo Google Sheets ID
**Objetivo:** Pipeline completo de sincronização sem perder nenhum passo

---

## 📊 ANÁLISE DO HISTÓRICO (O que JÁ FOI FEITO)

### ✅ Scripts Python Existentes (criados Oct 19)

| Script | Função | Status | Última execução |
|--------|--------|--------|-----------------|
| **sync_google_sheet.py** | Puxa dados do Google Sheet → `catalogo.json` | ✅ Funcional | Oct 19 21:54 |
| **validate_and_enrich.py** | Valida URLs, scrape dados, gera clean/pending CSVs | ✅ Funcional | Oct 19 21:00 |
| **beautify_google_sheet.py** | Formata Google Sheet, cria abas Dashboard/Faltas/Clean & Ready | ✅ Funcional | Oct 19 22:56 |
| **generate_wc_catalog.py** | Gera CSV para WooCommerce import | ✅ Funcional | Oct 19 21:55 |
| **catalog_scraper.py** | Scrape hologrammeparis.com para descrições | ✅ Funcional | Oct 19 16:38 |

### 📁 Outputs Existentes (output_catalogo/)

| Ficheiro | Tamanho | Data | Descrição |
|----------|---------|------|-----------|
| `catalogo.json` | 574 KB | Oct 19 21:54 | Master catalog sincronizado do Google Sheet |
| `catalogo_clean_ready.csv` | 310 KB | Oct 19 21:00 | Produtos validados prontos para WooCommerce |
| `catalogo_pending.csv` | 17 KB | Oct 19 21:00 | Produtos com problemas para revisão manual |
| `catalogo_master_with_price.csv` | 23 KB | Oct 19 20:42 | Produtos com preços (apenas e-commerce) |
| `woocommerce_import_localhost.csv` | 133 KB | Oct 19 23:03 | CSV pronto para import no WooCommerce |

**Status:** Pipeline completo foi executado há **7 dias** (Oct 19 → Oct 26)

---

## 🔄 MUDANÇAS NECESSÁRIAS

### ⚠️ Google Sheets ID Atualizado

**ANTIGO (Oct 19):**
```
1m5ObJBG3CXetWNN9BoXwE69EVA5RH-xMqozhY3d7ptw
```

**NOVO (Oct 26):**
```
18Sj_LNokkZZYNSseaPScCSWJ_iann7sbbgiwzva3VzA
```

**Link:** https://docs.google.com/spreadsheets/d/18Sj_LNokkZZYNSseaPScCSWJ_iann7sbbgiwzva3VzA/edit

### 🔧 Variáveis de Ambiente

Todos os scripts usam variáveis de ambiente (não hardcoded):

```bash
export GOOGLE_SHEETS_ID="18Sj_LNokkZZYNSseaPScCSWJ_iann7sbbgiwzva3VzA"
export GOOGLE_SERVICE_ACCOUNT_FILE="config/google-service-account.json"
export GOOGLE_SHEETS_TAB="Catalogo"  # opcional, padrão é "Catalogo"
```

**Service Account:** `sheets-api-reader@corded-smithy-453023-b7.iam.gserviceaccount.com`
**Status:** ✅ Credenciais válidas em `config/google-service-account.json`

---

## 🎯 PLANO COMPLETO: 5 FASES ALINHADAS

### FASE 0: Preparação (AGORA - 5 min)

**Objetivo:** Configurar ambiente e verificar acesso ao novo Google Sheet

**Tarefas:**
- [ ] 1. Exportar novo GOOGLE_SHEETS_ID
- [ ] 2. Testar conexão ao Google Sheet
- [ ] 3. Verificar estrutura (17 abas de categorias?)
- [ ] 4. Confirmar que service account tem acesso

**Comandos:**
```bash
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

# Configurar variáveis
export GOOGLE_SHEETS_ID="18Sj_LNokkZZYNSseaPScCSWJ_iann7sbbgiwzva3VzA"
export GOOGLE_SERVICE_ACCOUNT_FILE="config/google-service-account.json"

# Testar conexão (script de teste rápido)
python3 -c "
import gspread
from google.oauth2.service_account import Credentials
import os

creds = Credentials.from_service_account_file(
    os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE'),
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(os.getenv('GOOGLE_SHEETS_ID'))
print(f'✅ Conectado a: {sheet.title}')
print(f'📊 Total de abas: {len(sheet.worksheets())}')
for ws in sheet.worksheets():
    print(f'  - {ws.title} ({ws.row_count} linhas)')
"
```

**Output esperado:**
```
✅ Conectado a: [nome do sheet]
📊 Total de abas: [número]
  - [lista de abas]
```

**Decisão após Fase 0:**
- ✅ Se estrutura é igual (17 abas de categorias) → continuar para Fase 1
- ❌ Se estrutura diferente → PARAR e reportar diferenças

---

### FASE 1: Auditoria (READ-ONLY - 15 min)

**Objetivo:** Ler Google Sheet e validar dados SEM modificar nada

**Script:** `sync_google_sheet.py` (modo leitura)

**Tarefas:**
- [ ] 1. Ler todas as 17 abas de produtos
- [ ] 2. Validar estrutura (colunas obrigatórias: SKU, Nome, Preço)
- [ ] 3. Contar produtos totais vs com preço vs sem preço
- [ ] 4. Detectar problemas conhecidos:
  - [ ] "Tags: Verão 2023" na coluna Preço (linha 110, Boné 15125)
  - [ ] "Fabricado na Chinanna" (typo)
  - [ ] SKUs duplicados
  - [ ] Preços inválidos (>€500 ou <€1)
- [ ] 5. Gerar snapshot: `output_catalogo/google_sheet_snapshot_[timestamp].json`
- [ ] 6. Comparar com catalogo.json existente (Oct 19)

**Comandos:**
```bash
# Sync (cria backup automático de catalogo.json antes de sobrescrever)
python3 scripts/sync_google_sheet.py

# Verificar output
ls -lh output_catalogo/catalogo*.json

# Ver estatísticas
python3 -c "
import json
data = json.load(open('output_catalogo/catalogo.json'))
total = len(data)
with_price = len([p for p in data if p.get('price')])
print(f'Total produtos: {total}')
print(f'Com preço (e-commerce): {with_price}')
print(f'Sem preço (loja física): {total - with_price}')
"
```

**Output esperado:**
```
✅ Conectado ao Google Sheet
📊 Lendo [N] abas...
  BOINAS INVERNO: X produtos
  BOINAS VERÃO: Y produtos
  ...
💾 Backup criado: catalogo_backup.json
✅ catalogo.json atualizado
```

**Relatórios gerados:**
- `output_catalogo/catalogo.json` (atualizado)
- `output_catalogo/catalogo_backup.json` (backup do anterior)

**Checkpoint Humano:**
- Rever totais (esperado: ~62 produtos com preço, ~300+ total)
- Confirmar se números fazem sentido
- ✅ Aprovar Fase 2 / ❌ Corrigir Google Sheet manualmente

---

### FASE 2: Validação e Enriquecimento (20 min)

**Objetivo:** Validar URLs, scrape dados faltantes, separar clean vs pending

**Script:** `validate_and_enrich.py`

**Tarefas:**
- [ ] 1. Validar URLs de fornecedor (hologrammeparis.com)
- [ ] 2. Validar URLs de imagens (Google Photos)
- [ ] 3. Scrape descrições/composições de URLs válidas
- [ ] 4. Aplicar templates de descrição para produtos sem conteúdo
- [ ] 5. Separar produtos:
  - [ ] **Clean & Ready:** Preço + Descrição + Imagem OK
  - [ ] **Pendentes:** Falta dados ou scrape falhou
- [ ] 6. Gerar relatórios CSV

**Comandos:**
```bash
# Executar validação
python3 scripts/validate_and_enrich.py

# Verificar outputs
ls -lh output_catalogo/catalogo_clean_ready.csv
ls -lh output_catalogo/catalogo_pending.csv

# Ver estatísticas
wc -l output_catalogo/catalogo_clean_ready.csv
wc -l output_catalogo/catalogo_pending.csv
```

**Output esperado:**
```
🔍 Validando catalogo_master_with_price.csv...
📊 Total produtos: 62

🌐 Validando URLs...
  ✅ URLs válidas: X
  ❌ URLs inválidas: Y

🔎 Scraping descrições faltantes...
  ✅ Scrape bem sucedido: A
  ⚠️ Scrape parcial: B
  ❌ Scrape falhou: C

📄 Gerando relatórios...
  ✅ Clean & Ready: N produtos
  ⚠️ Pendentes: M produtos
```

**Relatórios gerados:**
- `output_catalogo/catalogo_clean_ready.csv` - prontos para WooCommerce
- `output_catalogo/catalogo_pending.csv` - precisam revisão manual
- (Opcional) Abas no Google Sheet atualizadas

**Checkpoint Humano:**
- Rever `catalogo_pending.csv` - quantos produtos precisam atenção?
- Decisão:
  - ✅ <10 produtos pendentes → continuar
  - ⚠️ 10-30 pendentes → rever casos críticos, depois continuar
  - ❌ >30 pendentes → PARAR, há problema estrutural no Google Sheet

---

### FASE 3: Formatação Google Sheet (10 min)

**Objetivo:** Criar abas visuais no Google Sheet (Dashboard, Faltas, etc.)

**Script:** `beautify_google_sheet.py`

**Tarefas:**
- [ ] 1. Criar aba "Dashboard" com KPIs
- [ ] 2. Criar aba "Faltas" (produtos sem imagem de `relatorios/produtos_sem_imagem.csv`)
- [ ] 3. Criar aba "Clean & Ready" (produtos validados)
- [ ] 4. Criar aba "Pendentes" (produtos com gaps)
- [ ] 5. Aplicar formatação:
  - [ ] Cores da marca (#EECAC9, #A8DADF)
  - [ ] Conditional formatting (verde/amarelo/vermelho)
  - [ ] Colunas Status e Preview
- [ ] 6. Criar aba "Histórico" (changelog via Apps Script - opcional)

**Comandos:**
```bash
# Executar beautify
python3 scripts/beautify_google_sheet.py

# Verificar no browser
open "https://docs.google.com/spreadsheets/d/18Sj_LNokkZZYNSseaPScCSWJ_iann7sbbgiwzva3VzA/edit"
```

**Output esperado:**
```
📊 Conectado ao Google Sheet: [nome]

✨ Criando abas...
  ✅ Dashboard criado
  ✅ Faltas criado
  ✅ Clean & Ready criado (N produtos)
  ✅ Pendentes criado (M produtos)

🎨 Aplicando formatação...
  ✅ Brand colors aplicados
  ✅ Conditional formatting aplicado
  ✅ Colunas Status/Preview adicionadas

✅ Google Sheet beautified!
```

**Checkpoint Humano:**
- Abrir Google Sheet no browser
- Verificar visualmente:
  - Dashboard mostra KPIs corretos?
  - Abas Clean & Ready / Pendentes estão populadas?
  - Formatação está bonita?
- ✅ Aprovar Fase 4

---

### FASE 4: Geração WooCommerce CSV (10 min)

**Objetivo:** Gerar CSV final para import no WooCommerce

**Script:** `generate_wc_catalog.py`

**Tarefas:**
- [ ] 1. Ler `catalogo_clean_ready.csv`
- [ ] 2. Mapear categorias:
  - BOINAS INVERNO → Chapéus > Boinas > Inverno
  - PANAMÁ → Chapéus > Panamá
  - etc.
- [ ] 3. Formatar preços (€XX.XX)
- [ ] 4. Preparar URLs de imagens:
  - [ ] Imagens principais
  - [ ] Imagens secundárias (galeria)
- [ ] 5. Aplicar regras:
  - [ ] Produtos SEM preço → status: draft
  - [ ] Produtos COM preço → status: publish
- [ ] 6. Gerar CSV WooCommerce-ready

**Comandos:**
```bash
# Gerar CSV
python3 scripts/generate_wc_catalog.py

# Verificar output
ls -lh output_catalogo/woocommerce_import*.csv
head -3 output_catalogo/woocommerce_import_localhost.csv
```

**Output esperado:**
```
📖 Lendo catalogo_clean_ready.csv...
  Total produtos: N

🗂️ Mapeando categorias...
  ✅ BOINAS INVERNO → Chapéus > Boinas > Inverno
  ✅ PANAMÁ → Chapéus > Panamá
  ...

💰 Formatando preços...
  ✅ Com preço (publish): X
  ⚠️ Sem preço (draft): Y

📄 Gerando CSV WooCommerce...
  ✅ woocommerce_import_localhost.csv (N produtos)
```

**Relatórios gerados:**
- `output_catalogo/woocommerce_import_localhost.csv` - CSV pronto para import

**Checkpoint Humano:**
- Abrir CSV no Excel/Numbers
- Verificar colunas:
  - SKU, Name, Price, Categories, Images, Description
- Spot-check 3-5 produtos aleatórios
- ✅ Aprovar Fase 5 (import final)

---

### FASE 5: Sincronização WooCommerce (15 min)

**Objetivo:** Importar produtos para WooCommerce e verificar

**Método:** WordPress Admin ou WP-CLI

**Tarefas:**
- [ ] 1. **BACKUP DATABASE PRIMEIRO!**
- [ ] 2. Importar CSV via WooCommerce
- [ ] 3. Verificar produtos importados
- [ ] 4. Comparar totais (Google Sheet vs WooCommerce)
- [ ] 5. Identificar órfãos (produtos no WooCommerce mas não no Sheet)
- [ ] 6. Decisão sobre órfãos:
  - [ ] Manter como rascunho?
  - [ ] Eliminar?

**Comandos:**

**Opção A: Via WordPress Admin**
```bash
# 1. Backup primeiro
docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web \
  > backup_before_import_$(date +%Y%m%d_%H%M).sql

# 2. Abrir admin
open http://localhost:8080/wp-admin

# 3. WooCommerce → Products → Import
# 4. Upload: output_catalogo/woocommerce_import_localhost.csv
# 5. Mapear colunas (WooCommerce faz automaticamente)
# 6. Run import
```

**Opção B: Via WP-CLI** (mais rápido)
```bash
# 1. Backup
docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web \
  > backup_before_import_$(date +%Y%m%d_%H%M).sql

# 2. Import
docker exec chapeus_wordpress wp wc product import \
  output_catalogo/woocommerce_import_localhost.csv \
  --allow-root

# 3. Verificar totais
docker exec chapeus_wordpress wp wc product list --format=count --allow-root
```

**Verificação pós-import:**
```bash
# Total produtos WooCommerce
docker exec chapeus_wordpress wp wc product list --format=count --allow-root

# Produtos publicados
docker exec chapeus_wordpress wp wc product list --status=publish --format=count --allow-root

# Produtos rascunho
docker exec chapeus_wordpress wp wc product list --status=draft --format=count --allow-root

# Produtos sem preço
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "
SELECT COUNT(*) as 'Produtos SEM preço'
FROM lx_posts p
LEFT JOIN lx_postmeta pm ON p.ID = pm.post_id AND pm.meta_key = '_price'
WHERE p.post_type = 'product'
AND (pm.meta_value IS NULL OR pm.meta_value = '' OR pm.meta_value = '0');
"
```

**Output esperado:**
```
✅ Importados: N produtos
  - Publicados (com preço): X
  - Rascunho (sem preço): Y

⚠️ Produtos órfãos (em WooCommerce mas não no Sheet): Z
```

**Relatório de comparação:**
- Criar CSV com produtos órfãos para decisão humana
- `relatorios/sincronizacao_delta.csv`

**Checkpoint Final:**
- Abrir site: http://localhost:8080/shop/
- Verificar:
  - Produtos aparecem?
  - Preços corretos?
  - Imagens carregam?
  - Categorias certas?
- ✅ CONCLUÍDO / ⚠️ Ajustes necessários

---

## 📋 CHECKLIST EXECUTIVA (Resumo)

### Preparação
- [ ] Exportar GOOGLE_SHEETS_ID novo
- [ ] Testar conexão ao Google Sheet
- [ ] Verificar estrutura (17 abas?)

### Execução (ordem exata)
1. [ ] **sync_google_sheet.py** → catalogo.json atualizado
2. [ ] **validate_and_enrich.py** → clean_ready.csv + pending.csv
3. [ ] **beautify_google_sheet.py** → Dashboard + abas no Google Sheet
4. [ ] **generate_wc_catalog.py** → woocommerce_import.csv
5. [ ] **BACKUP DATABASE** → dump SQL
6. [ ] **WooCommerce Import** → produtos sincronizados
7. [ ] **Verificação final** → comparar totais, testar site

### Relatórios Gerados (total: 8 ficheiros)
- [ ] `catalogo.json` (master)
- [ ] `catalogo_backup.json` (backup Oct 19)
- [ ] `catalogo_clean_ready.csv` (prontos)
- [ ] `catalogo_pending.csv` (pendentes)
- [ ] `woocommerce_import_localhost.csv` (para import)
- [ ] `backup_before_import_[timestamp].sql` (segurança)
- [ ] `relatorios/sincronizacao_delta.csv` (órfãos)
- [ ] Google Sheet com abas: Dashboard, Faltas, Clean & Ready, Pendentes

---

## ⚡ COMANDOS RÁPIDOS (Copiar/Colar)

### Setup Completo (5 fases em sequência)

```bash
#!/bin/bash
# Pipeline completo Google Sheets → WooCommerce

cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

# Setup vars
export GOOGLE_SHEETS_ID="18Sj_LNokkZZYNSseaPScCSWJ_iann7sbbgiwzva3VzA"
export GOOGLE_SERVICE_ACCOUNT_FILE="config/google-service-account.json"
export GOOGLE_SHEETS_TAB="Catalogo"

echo "🔍 FASE 0: Teste de conexão..."
python3 -c "
import gspread
from google.oauth2.service_account import Credentials
import os
creds = Credentials.from_service_account_file(
    os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE'),
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(os.getenv('GOOGLE_SHEETS_ID'))
print(f'✅ Conectado: {sheet.title}')
print(f'📊 Abas: {len(sheet.worksheets())}')
"

echo ""
echo "📥 FASE 1: Sync Google Sheet → catalogo.json..."
python3 scripts/sync_google_sheet.py

echo ""
echo "🔍 FASE 2: Validação e enriquecimento..."
python3 scripts/validate_and_enrich.py

echo ""
echo "✨ FASE 3: Beautify Google Sheet..."
python3 scripts/beautify_google_sheet.py

echo ""
echo "📦 FASE 4: Gerar WooCommerce CSV..."
python3 scripts/generate_wc_catalog.py

echo ""
echo "💾 Backup database..."
docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web \
  > backup_before_import_$(date +%Y%m%d_%H%M).sql

echo ""
echo "✅ PIPELINE COMPLETO!"
echo ""
echo "📊 Próximos passos:"
echo "1. Rever catalogo_pending.csv (produtos com problemas)"
echo "2. Importar woocommerce_import_localhost.csv via WP Admin"
echo "3. Verificar site: http://localhost:8080/shop/"
```

### Estatísticas Rápidas

```bash
# Ver totais
python3 -c "
import json, csv
catalogo = json.load(open('output_catalogo/catalogo.json'))
clean = len(list(csv.DictReader(open('output_catalogo/catalogo_clean_ready.csv'))))
pending = len(list(csv.DictReader(open('output_catalogo/catalogo_pending.csv'))))

print(f'📊 Estatísticas:')
print(f'  Total Google Sheet: {len(catalogo)}')
print(f'  Clean & Ready: {clean} ({clean/len(catalogo)*100:.1f}%)')
print(f'  Pendentes: {pending} ({pending/len(catalogo)*100:.1f}%)')
"
```

---

## 🚨 TROUBLESHOOTING

### Erro: "Worksheet 'Catalogo' not found"

**Causa:** Aba "Catalogo" não existe no novo Google Sheet
**Solução:**
1. Verificar nome exato da aba principal
2. Atualizar `export GOOGLE_SHEETS_TAB="[nome correto]"`
3. OU: O script deve ler das 17 abas de categorias (BOINAS INVERNO, etc.)

### Erro: "Permission denied" ao acessar Google Sheet

**Causa:** Service account não tem acesso ao novo sheet
**Solução:**
```
1. Abrir: https://docs.google.com/spreadsheets/d/18Sj_LNokkZZYNSseaPScCSWJ_iann7sbbgiwzva3VzA/edit
2. Share → Add people
3. Email: sheets-api-reader@corded-smithy-453023-b7.iam.gserviceaccount.com
4. Permissão: Editor (ou Viewer se só leitura)
```

### Erro: WooCommerce import falha

**Causa:** CSV mal formatado ou colunas erradas
**Solução:**
1. Abrir `woocommerce_import_localhost.csv` no Excel
2. Verificar header (linha 1): deve ter SKU, Name, Regular price, Categories, Images
3. Verificar se há células com aspas ou vírgulas a mais
4. Re-gerar: `python3 scripts/generate_wc_catalog.py`

### Produtos importados mas sem imagens

**Causa:** URLs de imagens inválidas ou Google Photos sem permissão pública
**Solução:**
1. Verificar `catalogo_pending.csv` - coluna "Observações"
2. Corrigir URLs no Google Sheet
3. Re-executar pipeline a partir da Fase 1

---

## 📈 MÉTRICAS DE SUCESSO

### Fase 1 - Sync
- ✅ catalogo.json criado sem erros
- ✅ Total produtos >= 60
- ✅ Produtos com preço >= 50

### Fase 2 - Validação
- ✅ Clean & Ready >= 80% do total
- ✅ Pendentes < 20%
- ✅ Sem erros críticos de scraping

### Fase 3 - Beautify
- ✅ Google Sheet tem 4+ abas novas (Dashboard, Faltas, Clean, Pendentes)
- ✅ Formatação visual aplicada
- ✅ KPIs no Dashboard corretos

### Fase 4 - WooCommerce CSV
- ✅ woocommerce_import.csv criado
- ✅ Tamanho > 100 KB
- ✅ Header WooCommerce válido

### Fase 5 - Import
- ✅ Produtos importados = Clean & Ready count
- ✅ 0 produtos com preço >€500
- ✅ Site abre sem erros (http://localhost:8080/shop/)

---

## 🎯 DECISÕES CHAVE

### Quando PARAR e pedir aprovação humana?

1. **Fase 0:** Se estrutura do Google Sheet for diferente (não tem 17 abas)
2. **Fase 1:** Se total de produtos for <50 ou >500 (muito diferente do esperado)
3. **Fase 2:** Se Clean & Ready <50% (maioria tem problemas)
4. **Fase 4:** Se woocommerce_import.csv <50 produtos (pipeline falhou)
5. **Fase 5:** Se import falhar (erro WooCommerce)

### Quando CONTINUAR automaticamente?

1. Fase 0 → Fase 1: Se conexão OK e estrutura similar
2. Fase 1 → Fase 2: Se sync OK e totais razoáveis (50-400 produtos)
3. Fase 2 → Fase 3: Se Clean & Ready >= 50%
4. Fase 3 → Fase 4: Sempre (beautify não bloqueia)
5. Fase 4 → Fase 5: Apenas APÓS aprovação humana do CSV

---

## 📝 NOTAS IMPORTANTES

### Service Account vs MCP

**Não há MCP para Google Sheets!**
Apenas ferramenta disponível: Python `gspread` library com service account.

**Por isso:**
- ✅ Usar scripts Python existentes (já testados Oct 19)
- ✅ Configurar vars de ambiente antes de executar
- ❌ Não tentar usar MCP (não existe para Sheets)

### Dados Antigos (Oct 19 vs Oct 26)

**Ficheiros output têm 7 dias:**
- `catalogo.json` (Oct 19) pode estar desatualizado
- Google Sheet pode ter sido editado entretanto
- **SOLUÇÃO:** Re-executar pipeline completo (Fases 1-5)

### Produtos sem Preço

**REGRA:** Sem preço = não publicar (apenas loja física)

**Implementação:**
- `validate_and_enrich.py` separa com preço vs sem preço
- `generate_wc_catalog.py` marca sem preço como `status: draft`
- WooCommerce import cria mas não publica

**Verificação:**
```sql
SELECT COUNT(*) FROM lx_posts
WHERE post_type='product' AND post_status='draft';
```

---

## ✅ CHECKLIST FINAL PARA EXECUÇÃO

### Antes de começar:
- [ ] Docker containers running (chapeus_wordpress, chapeus_mysql)
- [ ] Python deps instalados (gspread, google-auth, pandas, requests, bs4)
- [ ] Service account tem acesso ao novo Google Sheet
- [ ] Backup de catalogo.json existente (opcional)

### Execução (copiar/colar commands):
- [ ] 1. Exportar GOOGLE_SHEETS_ID novo
- [ ] 2. Testar conexão
- [ ] 3. sync_google_sheet.py
- [ ] 4. validate_and_enrich.py
- [ ] 5. beautify_google_sheet.py
- [ ] 6. generate_wc_catalog.py
- [ ] 7. Backup database
- [ ] 8. Import WooCommerce
- [ ] 9. Verificar site

### Após conclusão:
- [ ] Abrir Google Sheet: verificar Dashboard
- [ ] Rever catalogo_pending.csv: corrigir problemas
- [ ] Abrir site: testar 5 produtos aleatórios
- [ ] Documentar quaisquer issues encontrados
- [ ] Marcar esta checklist como ✅ COMPLETO

---

**FIM DA CHECKLIST**
**Versão:** 1.0
**Data:** 26 Outubro 2025
**Status:** Pronto para execução
