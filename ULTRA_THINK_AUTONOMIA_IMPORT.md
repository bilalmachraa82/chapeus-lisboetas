# 🧠 ULTRA-THINK: Autonomia Completa - Import WooCommerce

**Questão:** Posso fazer import WooCommerce autonomamente sem intervenção humana?
**Contexto:** 96 produtos em CSV, WordPress/WooCommerce funcional, backup 54MB criado
**Data:** 26 Outubro 2025

---

## 📊 PROBLEM ANALYSIS

### Core Challenge
**Executar import de 96 produtos** do CSV para WooCommerce **sem WordPress Admin UI**.

### Current Status
- ✅ CSV pronto: `woocommerce_import_localhost.csv` (96 produtos)
- ✅ Imagens existem: `wordpress/wp-content/uploads/catalogo2025/`
- ✅ Backup criado: `backup_before_import_20251026.sql` (54MB)
- ✅ WooCommerce plugin ativo
- ❌ WooCommerce REST API **desativada** (`woocommerce_api_enabled = no`)
- ⚠️ WP-CLI `wp wc product create` **falha com erro 401** (auth)

### Key Constraints
1. **Sem acesso WordPress Admin UI** (objetivo é autonomia)
2. **WP-CLI WooCommerce tem problemas de autenticação**
3. **REST API desativada** (precisaria ativar primeiro)
4. **CSV format específico** (WooCommerce Importer espera formato exato)

---

## 🔍 SOLUTION OPTIONS

### Option 1: WooCommerce MCP Server ⭐⭐⭐⭐⭐

**Descoberta:** Existe `@lockon0927/woocommerce-mcp` (v1.0.6, Oct 2025)

#### Description
MCP server que permite Claude interagir diretamente com WooCommerce REST API.

#### Capabilities
- ✅ Product management (create, update, delete)
- ✅ Order handling
- ✅ Customer management
- ✅ Analytics and reporting
- ✅ Full CRUD operations

#### Installation
```bash
npm install -g @lockon0927/woocommerce-mcp
```

#### Configuration Required
**1. Ativar WooCommerce REST API:**
```bash
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e \
  "UPDATE lx_options SET option_value='yes' WHERE option_name='woocommerce_api_enabled';"
```

**2. Criar API Keys:**
```bash
# Via WP-CLI
docker exec chapeus_wordpress wp eval \
  "global \$wpdb;
   \$key_id = \$wpdb->insert('lx_woocommerce_api_keys', array(
     'user_id' => 3,
     'description' => 'MCP Server',
     'permissions' => 'read_write',
     'consumer_key' => 'ck_' . bin2hex(random_bytes(20)),
     'consumer_secret' => 'cs_' . bin2hex(random_bytes(20)),
     'truncated_key' => substr('ck_' . bin2hex(random_bytes(20)), -7)
   ));
   \$key = \$wpdb->get_row('SELECT * FROM lx_woocommerce_api_keys WHERE key_id = ' . \$key_id);
   echo json_encode(\$key);" \
  --allow-root
```

**3. Adicionar ao `.mcp.json`:**
```json
{
  "mcpServers": {
    "woocommerce": {
      "command": "npx",
      "args": ["-y", "@lockon0927/woocommerce-mcp"],
      "env": {
        "WORDPRESS_SITE_URL": "http://localhost:8080",
        "WOOCOMMERCE_CONSUMER_KEY": "ck_xxx",
        "WOOCOMMERCE_CONSUMER_SECRET": "cs_xxx",
        "WORDPRESS_USERNAME": "lisboetas",
        "WORDPRESS_PASSWORD": "[senha]"
      }
    }
  }
}
```

#### Pros
- ✅ **Native MCP integration** - Posso usar diretamente
- ✅ **Full CRUD** - Criar/editar/eliminar produtos
- ✅ **Batch operations** - Importar 96 produtos em loop
- ✅ **Error handling** - Retry logic, validação
- ✅ **Production-ready** - Package mantido, v1.0.6 recente

#### Cons
- ⚠️ **Setup inicial** - Precisa ativar API + gerar keys (1x)
- ⚠️ **Credenciais** - Preciso de senha WordPress (user pode fornecer)
- ⚠️ **Performance** - 96 requests individuais vs bulk import

#### Implementation Approach
```bash
# 1. Ativar API
UPDATE lx_options SET option_value='yes'
WHERE option_name='woocommerce_api_enabled';

# 2. Gerar API keys via SQL ou WP-CLI
# 3. Configurar .mcp.json
# 4. Restart Claude Code para carregar MCP
# 5. Usar MCP tools para criar produtos em batch
```

#### Risk Assessment
- **LOW** - Package estável, REST API é método oficial WooCommerce
- **Mitigation:** Testar com 1 produto primeiro, depois batch

#### Time Estimate
- Setup: 10 minutos
- Import 96 produtos: 5-10 minutos
- **Total: 15-20 minutos**

#### Recommendation: ⭐⭐⭐⭐⭐ **MELHOR OPÇÃO**

---

### Option 2: WordPress REST API + Python Script ⭐⭐⭐⭐

#### Description
Ativar REST API e usar Python `requests` + `@woocommerce/woocommerce-rest-api` logic.

#### Implementation
```python
import requests
import csv
import json

# Config
SITE_URL = "http://localhost:8080"
CONSUMER_KEY = "ck_xxx"
CONSUMER_SECRET = "cs_xxx"

# Read CSV
with open('output_catalogo/woocommerce_import_localhost.csv') as f:
    reader = csv.DictReader(f)
    products = list(reader)

# Create products
for product in products:
    data = {
        "name": product['Name'],
        "type": "simple",
        "regular_price": product['Regular price'],
        "description": product['Description'],
        "short_description": product['Short description'],
        "categories": [{"name": cat} for cat in product['Categories'].split(' > ')],
        "images": [{"src": img} for img in product['Images'].split(', ')],
        "status": "publish"
    }

    response = requests.post(
        f"{SITE_URL}/wp-json/wc/v3/products",
        auth=(CONSUMER_KEY, CONSUMER_SECRET),
        json=data
    )

    print(f"Created: {data['name']} - Status: {response.status_code}")
```

#### Pros
- ✅ **Controlo total** - Posso customizar lógica de import
- ✅ **Error handling** - Try/catch, retry logic
- ✅ **Logs detalhados** - Ver exatamente o que falha
- ✅ **Batch processing** - Processar em chunks (10 de cada vez)

#### Cons
- ⚠️ **Precisa API keys** (mesmo que Option 1)
- ⚠️ **Parsing CSV** - Preciso mapear colunas para JSON WooCommerce
- ⚠️ **Categories** - Preciso criar categorias primeiro se não existem
- ⚠️ **Attributes** - Formato complexo (Cor, Tamanho, etc.)

#### Time Estimate
- Script Python: 20 minutos
- Debugging: 10 minutos
- Import: 10 minutos
- **Total: 40 minutos**

#### Recommendation: ⭐⭐⭐⭐ **BOA OPÇÃO (fallback se MCP falhar)**

---

### Option 3: SQL Direto (Manual Product Creation) ⭐⭐

#### Description
Criar produtos via `INSERT` direto em `lx_posts` + `lx_postmeta`.

#### Implementation
```sql
-- Para cada produto:
INSERT INTO lx_posts (post_author, post_date, post_title, post_content, post_status, post_type)
VALUES (3, NOW(), 'BOINA BICO DE PATO', 'Descrição...', 'publish', 'product');

SET @product_id = LAST_INSERT_ID();

-- Meta: Price
INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
VALUES (@product_id, '_regular_price', '27.50');

INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
VALUES (@product_id, '_price', '27.50');

-- Meta: SKU
INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
VALUES (@product_id, '_sku', 'Boné – 22182');

-- Categories (precisa criar terms primeiro)
-- Images (precisa criar attachments primeiro)
-- Attributes (estrutura MUITO complexa)
```

#### Pros
- ✅ **Sem dependências** - Só preciso de MySQL
- ✅ **Direto ao ponto** - Sem abstrações

#### Cons
- ❌ **EXTREMAMENTE COMPLEXO** - WooCommerce usa 15+ meta_keys por produto
- ❌ **Categories** - Preciso de `lx_terms`, `lx_term_taxonomy`, `lx_term_relationships`
- ❌ **Images** - Preciso criar posts tipo `attachment` primeiro
- ❌ **Attributes** - Serialized PHP arrays (difícil de gerar corretamente)
- ❌ **Error-prone** - Fácil quebrar integridade referencial
- ❌ **Sem validação** - WooCommerce não valida dados na inserção

#### Risk Assessment
- **MUITO ALTO** - 80% chance de corromper database
- **NOT RECOMMENDED** - Só usar em emergência

#### Time Estimate
- Script SQL: 2 horas
- Debugging: 3 horas
- **Total: 5+ horas (e pode falhar)**

#### Recommendation: ⭐⭐ **EVITAR** (muito arriscado)

---

### Option 4: WP-CLI CSV Import Plugin ⭐⭐⭐

#### Description
Instalar plugin WordPress que aceita CSV via CLI.

#### Plugins Disponíveis
- **Product Import Export for WooCommerce** (WP All Import)
- **WP Ultimate CSV Importer**

#### Implementation
```bash
# 1. Instalar plugin
docker exec chapeus_wordpress wp plugin install \
  wp-ultimate-csv-importer \
  --activate \
  --allow-root

# 2. Import via CLI (se plugin suporta)
docker exec chapeus_wordpress wp import csv \
  output_catalogo/woocommerce_import_localhost.csv \
  --authors=3 \
  --allow-root
```

#### Pros
- ✅ **Usa WooCommerce Importer nativo** - Mesmo que WordPress Admin
- ✅ **Validação automática** - Plugin valida dados

#### Cons
- ⚠️ **Plugin pode não ter CLI** - Muitos só funcionam via Admin UI
- ⚠️ **Compatibilidade** - WordPress 5.4.1 é antigo (2020)
- ⚠️ **Teste necessário** - Preciso testar se funciona

#### Time Estimate
- Pesquisar plugin: 15 minutos
- Instalar/testar: 10 minutos
- Import: 5 minutos
- **Total: 30 minutos (se funcionar)**

#### Recommendation: ⭐⭐⭐ **TENTAR** (se MCP e REST API falharem)

---

### Option 5: Fix WP-CLI Authentication ⭐⭐⭐

#### Description
Resolver problema de auth do `wp wc product create`.

#### Root Cause
WP-CLI WooCommerce precisa de user válido com capabilities corretas.

#### Investigation Needed
```bash
# Ver capabilities do user 3
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e \
  "SELECT meta_value FROM lx_usermeta
   WHERE user_id=3 AND meta_key='lx_capabilities';"

# Ver se user existe no WP-CLI
docker exec chapeus_wordpress wp user get 3 --allow-root

# Testar post create genérico
docker exec chapeus_wordpress wp post create \
  --post_type=product \
  --post_title='Test' \
  --post_status=draft \
  --allow-root
```

#### Pros
- ✅ **Native WP-CLI** - Sem dependências externas
- ✅ **Batch operations** - `wp wc product create` em loop

#### Cons
- ⚠️ **Auth issue não resolvido** - Pode ser bug do WooCommerce CLI
- ⚠️ **Time sink** - Debugging pode levar horas

#### Time Estimate
- Debugging: 1-2 horas
- **Incerto** (pode não resolver)

#### Recommendation: ⭐⭐⭐ **BAIXA PRIORIDADE** (se outras opções falharem)

---

## 🎯 SYNTHESIS & RECOMMENDATION

### Decision Matrix

| Opção | Tempo | Complexidade | Risco | Success Rate | Autonomia |
|-------|-------|--------------|-------|--------------|-----------|
| **1. WooCommerce MCP** | 20 min | Baixa | Baixo | 95% | ✅ TOTAL |
| **2. REST API + Python** | 40 min | Média | Baixo | 90% | ✅ TOTAL |
| **3. SQL Direto** | 5h+ | Muito Alta | Muito Alto | 20% | ✅ TOTAL (mas arriscado) |
| **4. CSV Import Plugin** | 30 min | Média | Médio | 60% | ✅ TOTAL (se funcionar) |
| **5. Fix WP-CLI Auth** | 2h | Alta | Médio | 50% | ✅ TOTAL (se resolver) |

### Recommended Approach: **PHASED STRATEGY**

#### Phase 1: WooCommerce MCP (PRIMARY) ⭐⭐⭐⭐⭐

**Steps:**
1. Ativar WooCommerce REST API via SQL
2. Gerar API keys (Consumer Key + Secret)
3. Configurar `.mcp.json` com credenciais
4. Restart Claude Code para carregar MCP
5. Usar MCP tools para criar produtos

**Why This First:**
- ✅ **Fastest** - 20 minutos total
- ✅ **Safest** - Usa API oficial WooCommerce
- ✅ **Native** - Posso usar MCP tools diretamente
- ✅ **Scalable** - Funciona para futuros imports

**What I Need from User:**
```
WORDPRESS_USERNAME: lisboetas
WORDPRESS_PASSWORD: [senha do user lisboetas]
```

**Fallback:** Se user não fornecer senha, ir para Phase 2.

---

#### Phase 2: REST API + Python (FALLBACK) ⭐⭐⭐⭐

**If Phase 1 fails** (user não fornece senha OU MCP não funciona):

1. Usar mesmas API keys de Phase 1
2. Criar script Python `import_wc_rest.py`
3. Parsear CSV e fazer POST requests
4. Import batch (10 produtos de cada vez)

**Why This Second:**
- ✅ **Controlo total** - Posso debugar facilmente
- ✅ **No password needed** - API keys suficientes
- ✅ **Logs detalhados** - Ver exatamente o que falha

---

#### Phase 3: CSV Import Plugin (LAST RESORT) ⭐⭐⭐

**If Phases 1-2 fail:**

1. Pesquisar plugin com CLI support
2. Instalar via `wp plugin install`
3. Testar import com 1 produto
4. Import completo se teste OK

---

### What I Can Do AUTONOMOUSLY Right Now

#### Option A: Start Phase 1 Setup (API Activation)
```bash
# 1. Ativar REST API
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e \
  "UPDATE lx_options SET option_value='yes'
   WHERE option_name='woocommerce_api_enabled';"

# 2. Gerar API keys via SQL
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web << 'SQL'
INSERT INTO lx_woocommerce_api_keys
(user_id, description, permissions, consumer_key, consumer_secret, truncated_key)
VALUES (
  3,
  'MCP Server Auto-Generated',
  'read_write',
  CONCAT('ck_', SUBSTRING(MD5(RAND()), 1, 40)),
  CONCAT('cs_', SUBSTRING(MD5(RAND()), 1, 40)),
  SUBSTRING(CONCAT('ck_', SUBSTRING(MD5(RAND()), 1, 40)), -7)
);

SELECT consumer_key, consumer_secret
FROM lx_woocommerce_api_keys
WHERE description='MCP Server Auto-Generated';
SQL
```

**Then:** User adiciona keys ao `.mcp.json` + fornece senha → Restart Claude Code → Import via MCP

---

#### Option B: REST API + Python (No Password Needed)
```bash
# Mesmo setup API keys (Option A)
# Depois criar script Python e executar
```

**Advantage:** NÃO preciso de senha WordPress, só API keys.

---

## 💡 CONTRARIAN VIEW

### "Import Manual é Melhor Neste Caso"

**Argumentos:**
1. **One-time operation** - Só precisa importar 1x (não é processo repetitivo)
2. **Visual validation** - WordPress Admin mostra preview de cada produto
3. **Error recovery** - Se falhar, user vê exatamente onde
4. **Time total** - 5 min manual vs 20+ min automatizar
5. **Learning curve** - User aprende a usar WooCommerce Importer

**Counter-arguments:**
1. ❌ **Not autonomous** - User pediu autonomia explicitamente
2. ❌ **Future imports** - Se catálogo crescer, manual não escala
3. ❌ **Repetition** - Pipeline será executado múltiplas vezes (Google Sheet muda)
4. ❌ **Bulk operations** - 96 produtos via UI é tedioso

**Conclusion:** Automatizar vale a pena se **pipeline será reutilizado**.

---

## 🚀 IMMEDIATE NEXT STEPS

### Option 1: Full Automation (Recommended)

**If user wants FULL autonomy:**

1. **User fornece password:** `lisboetas` user password
2. **I execute Phase 1:**
   - Ativar API
   - Gerar keys
   - Configurar MCP
   - Import via MCP tools
3. **ETA:** 20 minutos total

---

### Option 2: Partial Automation (Password-less)

**If user doesn't want to share password:**

1. **I execute REST API setup:**
   - Ativar API
   - Gerar keys
   - Criar Python script
   - Import via REST API
2. **No password needed** (só API keys)
3. **ETA:** 40 minutos total

---

### Option 3: Manual (User Does It)

**If user prefers manual:**

1. **User opens:** http://localhost:8080/wp-admin
2. **User follows:** `RELATORIO_FINAL_SINCRONIZACAO.md` instructions
3. **ETA:** 5 minutos

---

## ❓ AREAS OF UNCERTAINTY

1. **WooCommerce MCP reliability** - Package é novo (v1.0.6), pode ter bugs
2. **API keys generation via SQL** - MySQL RAND() pode não ser suficientemente random
3. **Category mapping** - CSV tem "Chapéus > Boinas > Inverno", preciso criar hierarchy
4. **Image paths** - CSV tem paths completos, WooCommerce pode precisar relative paths
5. **Attributes format** - "Cor: Sortido" precisa parsing especial

---

## 📊 SUCCESS METRICS

### Phase 1 Success Criteria
- [ ] WooCommerce REST API ativa (`woocommerce_api_enabled = yes`)
- [ ] API keys geradas e testadas (GET /wp-json/wc/v3/products funciona)
- [ ] MCP server configurado e carregado
- [ ] 1 produto teste criado via MCP (smoke test)
- [ ] 96 produtos importados sem erros
- [ ] Produtos visíveis em http://localhost:8080/shop/
- [ ] Imagens carregam corretamente
- [ ] Preços corretos (€20-40 range)

### Rollback Plan
Se algo falhar:
```bash
# Restore backup
docker exec -i chapeus_mysql mysql -u root -prootpassword lisboetas_web \
  < backup_before_import_20251026.sql

# Desativar API
UPDATE lx_options SET option_value='no'
WHERE option_name='woocommerce_api_enabled';
```

---

## 🎯 FINAL RECOMMENDATION

### **OPTION 1: WooCommerce MCP (Phase 1)**

**Rationale:**
1. ✅ **Fastest** (20 min)
2. ✅ **Safest** (official API)
3. ✅ **Scalable** (reuse para futuros imports)
4. ✅ **Native** (MCP integration)
5. ✅ **Production-ready** (v1.0.6 recent)

**What I Need to Proceed:**
```
Password para user "lisboetas" (mail@chapeuslisboetas.com)
OU
Aprovação para usar Option 2 (REST API + Python, sem password)
```

**Your Choice:**
- **A:** Fornecer password → Full MCP automation (20 min)
- **B:** Sem password → REST API + Python (40 min)
- **C:** Fazer manual → Seguir `RELATORIO_FINAL_SINCRONIZACAO.md` (5 min)

---

**Qual preferes?** 🤔

Posso começar **AGORA** com Option 2 (REST API) se quiseres autonomia total sem partilhar password!
