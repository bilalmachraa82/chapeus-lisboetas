# 🎯 PRÓXIMO PASSO: Restart Claude Code

**Status:** ✅ **WooCommerce MCP 95% CONFIGURADO**
**Falta:** 1 passo manual - Restart Claude Code

---

## 📊 O QUE FOI FEITO (Automático)

### ✅ FASE 1-4 COMPLETAS

1. ✅ **REST API ativada**
   ```sql
   woocommerce_api_enabled = 'yes'
   ```

2. ✅ **API Keys geradas e inseridas na database**
   ```
   Consumer Key:    ck_c03beed029fe06a9d38004a9e279ef953cc26402
   Consumer Secret: cs_efec5750e1e4f3413e7199e78b5de3ef031b3d62
   User ID: 3 (lisboetas)
   Permissions: read_write
   ```

3. ✅ **WooCommerce MCP package instalado**
   ```bash
   npm install -g @lockon0927/woocommerce-mcp
   # ✅ 38 packages instalados
   ```

4. ✅ **.mcp.json atualizado**
   ```json
   {
     "woocommerce": {
       "command": "npx",
       "args": ["-y", "@lockon0927/woocommerce-mcp"],
       "env": {
         "WORDPRESS_SITE_URL": "http://localhost:8080",
         "WOOCOMMERCE_CONSUMER_KEY": "ck_...",
         "WOOCOMMERCE_CONSUMER_SECRET": "cs_...",
         "WORDPRESS_USERNAME": "lisboetas",
         "WORDPRESS_PASSWORD": "EUsourico82!"
       }
     }
   }
   ```

---

## ⏸️ PASSO MANUAL NECESSÁRIO

### PRECISAS FAZER: Restart Claude Code

**Porquê?**
Claude Code só carrega MCP servers ao iniciar. Preciso que reinicies para carregar o WooCommerce MCP.

**Como fazer:**

#### Opção A: Via VS Code (se usas Claude Code no VS Code)
```
1. Cmd+Shift+P (Mac) ou Ctrl+Shift+P (Windows/Linux)
2. Escrever: "Developer: Reload Window"
3. Enter
```

#### Opção B: Via Claude Desktop App
```
1. Fechar completamente o Claude Code
2. Reabrir Claude Code
3. Navegar de volta a este projeto
```

#### Opção C: Via Terminal
```bash
# Fechar sessão atual
# Reabrir terminal
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"
claude
```

---

## ✅ APÓS RESTART

### O que vai acontecer automaticamente:

1. **Claude Code carrega WooCommerce MCP**
   - Vou ter acesso a novos tools MCP para WooCommerce
   - Tools disponíveis: `woocommerce-create-product`, `woocommerce-list-products`, etc.

2. **Vou testar conexão** (smoke test)
   - Criar 1 produto teste via MCP
   - Verificar se aparece no WordPress

3. **Import batch completo** (96 produtos)
   - Ler CSV: `output_catalogo/woocommerce_import_localhost.csv`
   - Criar cada produto via MCP tools
   - Progress bar: "Produto 1/96... 2/96... etc."

4. **Verificação final**
   - Contar produtos no database
   - Testar 5 produtos aleatórios no site
   - Confirmar imagens, preços, categorias

**ETA após restart:** 10-15 minutos para import completo

---

## 🔍 COMO SABER SE MCP ESTÁ CARREGADO?

Depois de restart, **escreve qualquer mensagem** (ex: "está pronto?").

**Se MCP funcionar**, vou responder:
```
✅ WooCommerce MCP carregado!
📊 Tools disponíveis: [lista de tools]
🚀 Pronto para importar 96 produtos
```

**Se MCP NÃO funcionar**, vou dizer:
```
❌ WooCommerce MCP não encontrado
⚠️ Preciso de debug do .mcp.json
```

---

## 🚨 TROUBLESHOOTING (se MCP não carregar)

### Problema 1: "MCP server not found"

**Solução:**
```bash
# Verificar se package está instalado
npm list -g @lockon0927/woocommerce-mcp

# Se não estiver, reinstalar
npm install -g @lockon0927/woocommerce-mcp
```

### Problema 2: "Authentication failed"

**Causa:** Password ou username errado

**Solução:**
```bash
# Testar login manualmente
docker exec chapeus_wordpress wp user list --allow-root | grep lisboetas

# Se user não existir ou password estiver errada, corrigir .mcp.json
```

### Problema 3: ".mcp.json não carrega"

**Solução:**
```bash
# Validar JSON syntax
cat .mcp.json | python3 -m json.tool

# Se houver erro de syntax, corrigir e restart novamente
```

---

## 📋 CHECKLIST FINAL

### Antes de restart:
- [✅] REST API ativada
- [✅] API keys criadas
- [✅] WooCommerce MCP instalado
- [✅] .mcp.json configurado
- [✅] Docker containers running
- [✅] Backup database existe (54MB)

### Depois de restart:
- [ ] Claude Code reiniciado
- [ ] WooCommerce MCP carregado (verificar com mensagem teste)
- [ ] Smoke test: 1 produto criado via MCP
- [ ] Import batch: 96 produtos
- [ ] Verificação: produtos visíveis no site
- [ ] Confirmação final: tudo OK ✅

---

## 📊 FILES & CREDENTIALS (Referência)

### Ficheiros Importantes
```
✅ .mcp.json (configurado)
✅ output_catalogo/woocommerce_import_localhost.csv (96 produtos)
✅ backup_before_import_20251026.sql (54MB backup)
```

### Credenciais (já configuradas em .mcp.json)
```
Site: http://localhost:8080
Username: lisboetas
Password: EUsourico82!
Consumer Key: ck_c03beed029fe06a9d38004a9e279ef953cc26402
Consumer Secret: cs_efec5750e1e4f3413e7199e78b5de3ef031b3d62
```

### Database
```
Host: localhost:3306
Database: lisboetas_web
User: lisboetas
Password: e$$4rU9h8
Prefix: lx_
```

---

## 🎯 RESUMO

**O QUE FALTA:**
1. ⏸️ **TU:** Restart Claude Code
2. 🤖 **EU:** Import automático 96 produtos via MCP

**ETA TOTAL:** 15-20 minutos após restart

**PRÓXIMO PASSO:**
👉 **RESTART CLAUDE CODE AGORA** 👈

Depois de restart, escreve qualquer coisa (ex: "pronto") e eu continuo automaticamente! 🚀

---

**Preparado por:** Claude (Autonomia Fase 1-4)
**Data:** 26 Outubro 2025, 09:45
**Status:** ✅ 95% completo - aguarda restart para 100%
