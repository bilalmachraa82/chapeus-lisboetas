# 🔄 COMO ATIVAR OS MCPs INSTALADOS

**Situação:** Acabaste de instalar 9 MCPs novos
**Problema:** Claude Code ainda não os "vê"
**Solução:** Recarregar o ambiente

---

## ✅ OPÇÃO 1: RELOAD RÁPIDO (RECOMENDADO)

### Se estás no Claude Desktop / Cursor / Cline:

```bash
# Método 1: Comando interno
/reload

# Método 2: Keyboard shortcut
Cmd + Shift + P (Mac) ou Ctrl + Shift + P (Windows)
→ Digite: "Reload Window"
→ Enter
```

### Se estás no Terminal (Codex CLI):

```bash
# Sai do ambiente atual
exit

# Reinicia
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"
claude  # ou codex, dependendo do teu setup
```

---

## ✅ OPÇÃO 2: RESTART COMPLETO

### Claude Desktop:
```
1. Fecha a aplicação completamente (Cmd+Q no Mac)
2. Reabre Claude Desktop
3. Vai para Settings → Developer → MCP Servers
4. Deverás ver os 9 novos MCPs listados
```

### Cursor IDE:
```
1. Fecha Cursor
2. Reabre Cursor
3. Abre a pasta do projeto
4. Os MCPs carregam automaticamente
```

---

## 🔍 COMO VERIFICAR SE OS MCPs ESTÃO ATIVOS

### Método 1: Ver ícone de ferramentas
```
Olha para o input box do Claude Code
→ Deverás ver um ícone de 🔨 (hammer) ou 🛠️ (tools)
→ Clica nele
→ Deverás ver lista de 9+ tools disponíveis
```

### Método 2: Testar um MCP
```
Escreve no chat:
"List all available MCP servers"

Ou tenta um comando específico:
"Take a screenshot of http://localhost:8080"
```

### Método 3: Verificar configuração
```bash
# No terminal, verifica se o ficheiro está correto:
cat mcp_config.json | jq '.mcpServers | keys'

# Deve mostrar:
[
  "google-sheets",
  "beautify-google-sheet",
  "chrome-devtools",
  "playwright",
  "wp-cli",
  "mysql",
  "woocommerce",
  "supabase",
  "github"
]
```

---

## ⚠️ TROUBLESHOOTING

### Problema: "MCPs não aparecem após reload"

**Causa 1:** Erro no `mcp_config.json`
```bash
# Verifica syntax:
cat mcp_config.json | jq .

# Se der erro, corrige o JSON
```

**Causa 2:** `.env.mcp` não é lido
```bash
# Verifica se existe:
ls -la .env.mcp

# Verifica permissões:
chmod 600 .env.mcp
```

**Causa 3:** Executáveis não encontrados
```bash
# Verifica instalações globais:
npm list -g | grep -E "playwright|supabase|chrome"

# Se faltarem, reinstala:
npm install -g playwright-mcp @supabase/mcp-server-supabase
```

### Problema: "MCP server failed to start"

**Solução:** Ver logs
```bash
# Claude Desktop logs:
# Mac: ~/Library/Logs/Claude/
# Windows: %APPDATA%\Claude\logs\

# Cursor logs:
# Mac: ~/Library/Application Support/Cursor/logs/
```

### Problema: "Docker containers not found"

**Solução:** Containers precisam estar running
```bash
# Verifica:
docker ps | grep chapeus

# Se não estiverem UP:
docker-compose up -d

# Aguarda 10s e testa novamente
```

---

## 🎯 TESTES RÁPIDOS APÓS ATIVAÇÃO

### Teste 1: Chrome DevTools
```
Prompt: "Take a screenshot of http://localhost:8080/sobre-nos/"
Esperado: Screenshot saved + analysis
```

### Teste 2: Playwright
```
Prompt: "Navigate to http://localhost:8080/shop/ and tell me how many products are visible"
Esperado: "Found X products on the page"
```

### Teste 3: WP-CLI
```
Prompt: "List all active WordPress plugins using WP-CLI"
Esperado: Lista de plugins com status
```

### Teste 4: MySQL
```
Prompt: "Query the database to show me the active WordPress theme"
Esperado: "flatsome-child"
```

---

## 📊 COMO SABER SE FUNCIONOU

### ✅ SINAIS DE SUCESSO:

1. **Ícone de ferramentas visível** 🔨
2. **MCPs listados quando clicas no ícone**
3. **Comandos executam sem "tool not found"**
4. **Respostas incluem dados reais (não "I don't have access to...")**

### ❌ SINAIS DE PROBLEMA:

1. **Erro: "MCP server not found"**
2. **Resposta: "I don't have the ability to..."**
3. **Timeout ao executar comandos**
4. **Nenhum ícone de ferramentas aparece**

---

## 🚀 PRÓXIMO PASSO APÓS ATIVAÇÃO

Uma vez que os MCPs estejam ativos:

### 1. Gerar Tokens (OBRIGATÓRIO)
```
- WooCommerce API keys
- GitHub Personal Access Token
- (Opcional) Supabase credentials
```

### 2. Testar cada MCP
```
Segue a lista de testes em PHASE1_INSTALLATION_COMPLETE.md
```

### 3. (Opcional) Instalar Fase 2
```
Figma, Storybook, Notion, Slack, Filesystem
+60% productivity boost
```

---

## 💡 DICA PRO

**Atalho para reload rápido no Claude Desktop:**

```
Settings → Keyboard Shortcuts
→ Adiciona: "Reload MCP Servers" → Cmd+Shift+R
```

Assim não precisas sair e voltar sempre!

---

## 📞 SE AINDA NÃO FUNCIONAR

1. **Verifica Docker containers:**
   ```bash
   docker ps
   # Devem estar UP: chapeus_wordpress, chapeus_mysql
   ```

2. **Verifica Node.js global packages:**
   ```bash
   npm list -g --depth=0
   # Devem aparecer: playwright-mcp, chrome-devtools-mcp, etc
   ```

3. **Verifica mcp_config.json syntax:**
   ```bash
   cat mcp_config.json | jq .
   # Não deve dar erro de syntax
   ```

4. **Reinicia TUDO:**
   ```bash
   docker-compose restart
   # Aguarda 10s
   # Fecha e reabre Claude Code
   ```

---

**Resumo:**
✅ **Sai e volta a entrar** → MCPs ativam automaticamente!

🤖 Generated with [Claude Code](https://claude.com/claude-code)
