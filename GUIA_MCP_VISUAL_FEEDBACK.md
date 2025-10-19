# 🤖 GUIA COMPLETO - MCPs para Visual Feedback de Sites Localhost

## 📋 MELHOR MCPs para Ver Site e Dar Feedback (2025)

### 🥇 TOP 5 MCPs RECOMENDADOS

#### 1. **Chrome DevTools MCP** ⭐⭐⭐⭐⭐
**Melhor para: Análise visual completa + Performance**

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "@executeautomation/chrome-devtools-mcp"]
    }
  }
}
```

**Funcionalidades:**
- ✅ Captura screenshots do localhost
- ✅ Lê DOM e CSS em real-time
- ✅ Métricas de performance (LCP, FCP, etc)
- ✅ Console logs e network requests
- ✅ Debugging visual interativo

**Documentação:** https://addyosmani.com/blog/devtools-mcp/

---

#### 2. **Playwright MCP** ⭐⭐⭐⭐⭐
**Melhor para: Automação + Testing visual**

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/mcp-playwright"]
    }
  }
}
```

**Funcionalidades:**
- ✅ Screenshots em múltiplos viewports
- ✅ Navegação completa do site
- ✅ Testes E2E automatizados
- ✅ Acessa accessibility tree
- ✅ Modo snapshot para análise

**GitHub:** https://github.com/executeautomation/mcp-playwright

---

#### 3. **Puppeteer Vision MCP** ⭐⭐⭐⭐
**Melhor para: Scraping visual + AI interactions**

```json
{
  "mcpServers": {
    "puppeteer-vision": {
      "command": "npx",
      "args": ["-y", "puppeteer-vision-mcp-server"],
      "env": {
        "OPENAI_API_KEY": "your-api-key",
        "DISABLE_HEADLESS": "true"
      }
    }
  }
}
```

**Funcionalidades:**
- ✅ AI-driven interactions (auto-click, auto-fill)
- ✅ Handle cookie banners, CAPTCHAs
- ✅ Convert páginas para markdown
- ✅ Screenshots com annotations
- ✅ Browser visível (headless opcional)

**GitHub:** https://github.com/djannot/puppeteer-vision-mcp

---

#### 4. **Screenshot MCP Server** ⭐⭐⭐⭐
**Melhor para: Screenshots rápidos de localhost**

```bash
# Instalação
git clone https://github.com/bradydouthit/screenshot-mcp.git
cd screenshot-mcp
npm install
npm run build
```

**Configuração Claude:**
```json
{
  "mcpServers": {
    "screenshot": {
      "command": "node",
      "args": ["/path/to/screenshot-mcp/dist/index.js"]
    }
  }
}
```

**Funcionalidades:**
- ✅ Localhost-only (seguro)
- ✅ Viewport configurável
- ✅ Full-page screenshots
- ✅ Playwright-powered
- ✅ Integração direta Claude

**URL:** https://lobehub.com/mcp/bradydouthit-screenshot-mcp

---

#### 5. **Browserbase MCP** ⭐⭐⭐⭐
**Melhor para: Cloud browser + Session management**

```json
{
  "mcpServers": {
    "browserbase": {
      "command": "npx",
      "args": ["-y", "@browserbasehq/mcp-server-browserbase"],
      "env": {
        "BROWSERBASE_API_KEY": "your-api-key",
        "BROWSERBASE_PROJECT_ID": "your-project-id"
      }
    }
  }
}
```

**Funcionalidades:**
- ✅ Cloud browser (não precisa Chrome local)
- ✅ Session persistence
- ✅ JavaScript execution
- ✅ Dynamic content handling
- ✅ Screenshots + logs

---

## 🎯 MELHORES PARA SITE WORDPRESS/WOOCOMMERCE

### Recomendação Específica:

**OPÇÃO 1: Chrome DevTools MCP** (Mais completo)
- Ver performance do WooCommerce
- Analisar CSS do Flatsome
- Debug de imagens não carregadas
- Network requests (ver se imagens 404)

**OPÇÃO 2: Playwright MCP** (Mais prático)
- Tirar screenshots de todas páginas
- Testar responsivo mobile/tablet/desktop
- Verificar se produtos aparecem
- Automatizar testes de checkout

---

## 📦 INSTALAÇÃO PASSO-A-PASSO

### Para Chrome DevTools MCP:

**1. Instalar via NPM:**
```bash
npm install -g @executeautomation/chrome-devtools-mcp
```

**2. Configurar em Claude Desktop:**

**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `C:\Users\{username}\AppData\Roaming\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "@executeautomation/chrome-devtools-mcp"]
    }
  }
}
```

**3. Reiniciar Claude Desktop**

**4. Testar:**
```
Prompt: "Tire um screenshot de http://localhost:8080 
e analise o design, cores e layout"
```

---

### Para Playwright MCP:

**1. Clonar Repositório:**
```bash
git clone https://github.com/executeautomation/mcp-playwright.git
cd mcp-playwright
npm install
npm run build
npm link
```

**2. Configurar:**
```json
{
  "mcpServers": {
    "playwright": {
      "command": "node",
      "args": ["/path/to/mcp-playwright/dist/index.js"]
    }
  }
}
```

**3. Usar:**
```
"Navega para http://localhost:8080/teste-html 
e tira screenshots em mobile, tablet e desktop"
```

---

## 🔧 CONFIGURAÇÃO PARA O TEU SITE

### Script Automático de Análise Visual:

```javascript
// analyze_site.js
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  const pages = [
    'http://localhost:8080',
    'http://localhost:8080/teste-html',
    'http://localhost:8080/sobre',
    'http://localhost:8080/product-category/boinas'
  ];
  
  for (const url of pages) {
    console.log(`📸 Analisando: ${url}`);
    await page.goto(url, { waitUntil: 'networkidle' });
    
    // Screenshot
    await page.screenshot({ 
      path: `screenshots/${url.split('/').pop() || 'homepage'}.png`,
      fullPage: true 
    });
    
    // Verificar imagens
    const brokenImages = await page.$$eval('img', imgs => 
      imgs.filter(img => !img.complete || img.naturalWidth === 0)
        .map(img => img.src)
    );
    
    if (brokenImages.length > 0) {
      console.log(`❌ Imagens quebradas: ${brokenImages.length}`);
      brokenImages.forEach(src => console.log(`   • ${src}`));
    }
    
    // Performance metrics
    const metrics = await page.evaluate(() => ({
      lcp: performance.getEntriesByType('largest-contentful-paint')[0]?.renderTime,
      fcp: performance.getEntriesByType('paint').find(p => p.name === 'first-contentful-paint')?.startTime
    }));
    
    console.log(`⚡ Performance:`, metrics);
  }
  
  await browser.close();
})();
```

**Executar:**
```bash
mkdir screenshots
node analyze_site.js
```

---

## 🎨 PROMPTS PARA USAR COM MCPs

### Análise Visual Completa:
```
"Usando Chrome DevTools MCP, analisa http://localhost:8080 e dá-me:
1. Screenshot da homepage
2. Lista de todas imagens que não carregam
3. Problemas de CSS (overflow, alignment)
4. Performance score
5. Sugestões de melhorias visuais"
```

### Teste Responsivo:
```
"Usando Playwright, tira screenshots de http://localhost:8080/teste-html 
em 3 viewports:
- Mobile: 375x667
- Tablet: 768x1024  
- Desktop: 1920x1080

Depois compara e diz quais problemas encontras em cada um"
```

### Auditoria de Imagens:
```
"Navega para http://localhost:8080/shop e:
1. Lista todos produtos visíveis
2. Identifica quais NÃO têm imagem
3. Verifica tamanho das imagens (devem ser >400px)
4. Diz se imagens estão centradas"
```

### Comparação com Best Practices:
```
"Analisa http://localhost:8080 e compara com sites e-commerce 
premium como:
- farfetch.com
- mrporter.com
- endclothing.com

Diz o que falta para ser premium e dá sugestões específicas"
```

---

## 📊 BENCHMARK - Qual MCP Escolher?

| MCP | Screenshots | DOM Access | Performance | AI Vision | Localhost | Dificuldade |
|-----|-------------|------------|-------------|-----------|-----------|-------------|
| **Chrome DevTools** | ✅ | ✅ | ✅✅✅ | ⚠️ | ✅ | Fácil |
| **Playwright** | ✅✅✅ | ✅ | ✅✅ | ⚠️ | ✅ | Média |
| **Puppeteer Vision** | ✅✅ | ✅ | ✅ | ✅✅✅ | ✅ | Média |
| **Screenshot MCP** | ✅✅ | ❌ | ⚠️ | ❌ | ✅✅✅ | Fácil |
| **Browserbase** | ✅✅ | ✅ | ✅✅ | ⚠️ | ⚠️ | Difícil |

**Legenda:**
- ✅✅✅ = Excelente
- ✅✅ = Bom
- ✅ = Básico
- ⚠️ = Limitado
- ❌ = Não suporta

---

## 🚀 MINHA RECOMENDAÇÃO PARA O TEU CASO

### MELHOR OPÇÃO: **Playwright MCP**

**Porquê:**
1. ✅ Open-source e bem mantido (Microsoft)
2. ✅ Funciona perfeitamente com localhost
3. ✅ Screenshots em múltiplos viewports
4. ✅ Pode verificar se produtos aparecem
5. ✅ Integração fácil com Claude
6. ✅ Boa documentação

### SETUP RÁPIDO (5 minutos):

```bash
# 1. Instalar
npx playwright install chromium

# 2. Testar manualmente
npx playwright codegen http://localhost:8080

# 3. Configurar MCP
# Editar claude_desktop_config.json:
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/mcp-playwright"]
    }
  }
}

# 4. Reiniciar Claude

# 5. Prompt de teste:
"Tira um screenshot de http://localhost:8080/teste-html 
e diz-me quantos produtos consegues ver"
```

---

## 🎯 ALTERNATIVA SIMPLES (SEM MCP)

Se MCPs forem complicados, podes usar:

### Screenshot Manual + Análise:

```bash
# 1. Tirar screenshot com Playwright
npx playwright screenshot http://localhost:8080 homepage.png

# 2. Upload para Claude/ChatGPT Vision
# 3. Prompt: "Analisa este site e diz problemas"
```

### Ou Script Python:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('http://localhost:8080')
    page.screenshot(path='site.png', full_page=True)
    browser.close()

print("Screenshot salvo! Abre e analisa.")
```

---

## 📝 RESUMO EXECUTIVO

**Para o teu caso (site WordPress localhost):**

1. **INSTALAR:** Playwright MCP
2. **CONFIGURAR:** claude_desktop_config.json
3. **USAR PROMPT:** "Analisa http://localhost:8080/teste-html visualmente"
4. **BENEFÍCIO:** AI vê o site e dá feedback automático

**Tempo:** 10 minutos setup  
**Resultado:** Feedback visual automático de AI

---

## 🔗 LINKS ÚTEIS

- **Playwright MCP:** https://github.com/executeautomation/mcp-playwright
- **Chrome DevTools MCP:** https://addyosmani.com/blog/devtools-mcp/
- **Puppeteer Vision:** https://github.com/djannot/puppeteer-vision-mcp
- **MCP Servers List:** https://github.com/punkpeye/awesome-mcp-servers
- **Documentação MCP:** https://modelcontextprotocol.info/

---

**PRÓXIMO PASSO:** Escolhe um MCP (recomendo Playwright) e configura. Depois podes pedir para AI auditar o site visualmente!

