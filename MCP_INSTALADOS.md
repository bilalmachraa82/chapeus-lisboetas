# 🤖 MCPs Instalados e Disponíveis no Sistema

## ✅ MCPs INSTALADOS (Factory/Droid)

### 1. **Playwright** ⭐⭐⭐⭐⭐
**Status:** ✅ INSTALADO (v1191 - Chromium 141.0.7390.16)  
**Localização:** `/Users/bilal/Library/Caches/ms-playwright/chromium-1191`

**Capacidades:**
```bash
# Screenshot simples
npx playwright screenshot http://localhost:8080 screenshot.png

# Screenshot com timeout
npx playwright screenshot http://localhost:8080/teste-html site.png --wait-for-timeout 3000

# Screenshot full page
npx playwright screenshot http://localhost:8080 --full-page full.png

# Screenshot com viewport específico
npx playwright screenshot http://localhost:8080 mobile.png --viewport-size 375x667
```

**✅ JÁ TESTADO:** Screenshot tirado com sucesso (82KB)

---

### 2. **Chrome DevTools MCP** ⭐⭐⭐⭐⭐
**Status:** ✅ INSTALADO (v0.6.0)  
**Comando:** `chrome-devtools-mcp`

**Capacidades:**
- Screenshots + Performance metrics (LCP, FCP)
- DOM access e CSS inspection
- Console logs e network requests
- Real-time debugging
- Proxy server support

**Como Usar:**
```bash
# Headless mode
npx chrome-devtools-mcp --headless

# Com viewport específico
npx chrome-devtools-mcp --viewport 1920x1080

# Com logs de debug
DEBUG=* npx chrome-devtools-mcp --logFile /tmp/chrome-debug.log

# Conectar a Chrome existente
npx chrome-devtools-mcp --browserUrl http://127.0.0.1:9222

# Modo isolado (temporary profile)
npx chrome-devtools-mcp --isolated
```

**Canais Disponíveis:**
- `--channel stable` (default)
- `--channel beta`
- `--channel canary`
- `--channel dev`

---

## ⚠️ LIMITAÇÃO ATUAL

**PROBLEMA:** Não tenho acesso direto a MCP Protocol dentro da Factory/Droid!

- ❌ Não consigo usar MCPs como "sub-agents" automáticos
- ❌ Não consigo conectar via stdio/SSE do MCP
- ✅ **MAS:** Posso executar comandos CLI destes MCPs!

---

## 💡 O QUE POSSO FAZER AGORA

### Opção A: Executar Screenshots Automaticamente
```bash
# Screenshot homepage
npx playwright screenshot http://localhost:8080 home.png --wait-for-timeout 3000

# Screenshot shop page
npx playwright screenshot http://localhost:8080/teste-html shop.png --wait-for-timeout 3000

# Screenshot mobile
npx playwright screenshot http://localhost:8080 mobile.png --viewport-size 375x667
```

### Opção B: Script de Análise Visual Completo
```javascript
// visual_qa.js
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  const page = await context.newPage();
  
  console.log('🔍 Analisando http://localhost:8080/teste-html...\n');
  
  // Navegar
  await page.goto('http://localhost:8080/teste-html', { 
    waitUntil: 'networkidle' 
  });
  
  // Screenshot
  await page.screenshot({ 
    path: 'analysis/homepage.png', 
    fullPage: true 
  });
  console.log('✅ Screenshot salvo');
  
  // Verificar imagens quebradas
  const brokenImages = await page.$$eval('img', imgs => 
    imgs.filter(img => !img.complete || img.naturalWidth === 0)
      .map(img => ({ src: img.src, alt: img.alt }))
  );
  
  console.log(`\n📸 Imagens: Total ${await page.$$eval('img', imgs => imgs.length)}`);
  if (brokenImages.length > 0) {
    console.log(`❌ Quebradas: ${brokenImages.length}`);
    brokenImages.forEach(img => console.log(`   • ${img.src}`));
  } else {
    console.log('✅ Todas as imagens carregaram!');
  }
  
  // Contar produtos
  const products = await page.$$eval('.product-card', cards => cards.length);
  console.log(`\n🛍️ Produtos visíveis: ${products}`);
  
  // Performance metrics
  const metrics = await page.evaluate(() => {
    const paint = performance.getEntriesByType('paint');
    const fcp = paint.find(p => p.name === 'first-contentful-paint');
    const lcp = performance.getEntriesByType('largest-contentful-paint')[0];
    
    return {
      fcp: fcp ? Math.round(fcp.startTime) : null,
      lcp: lcp ? Math.round(lcp.renderTime) : null,
      loadTime: Math.round(performance.timing.loadEventEnd - performance.timing.navigationStart)
    };
  });
  
  console.log(`\n⚡ Performance:`);
  console.log(`   • FCP: ${metrics.fcp}ms`);
  console.log(`   • LCP: ${metrics.lcp}ms`);
  console.log(`   • Load: ${metrics.loadTime}ms`);
  
  // Console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log(`\n❌ Console Error: ${msg.text()}`);
    }
  });
  
  // Testar responsivo
  console.log('\n📱 Testando mobile...');
  await page.setViewportSize({ width: 375, height: 667 });
  await page.screenshot({ path: 'analysis/mobile.png' });
  
  console.log('\n📱 Testando tablet...');
  await page.setViewportSize({ width: 768, height: 1024 });
  await page.screenshot({ path: 'analysis/tablet.png' });
  
  console.log('\n✅ Análise completa!');
  
  await browser.close();
})();
```

**Executar:**
```bash
mkdir -p analysis
node visual_qa.js
```

---

## 🎯 PARA TU USARES MCPs COM AI

### Para Claude Desktop (Recomendado):

**Ficheiro:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/mcp-playwright"]
    },
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest"]
    },
    "screenshot": {
      "command": "npx",
      "args": ["-y", "puppeteer-vision-mcp-server"],
      "env": {
        "OPENAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Depois podes perguntar ao Claude Desktop:**
```
"Tira um screenshot de http://localhost:8080/teste-html 
e analisa visualmente o design, cores e layout"
```

---

## 📊 RESUMO - O QUE ESTÁ DISPONÍVEL

| Tool | Status | Uso Direto (CLI) | Uso MCP (Claude Desktop) |
|------|--------|------------------|--------------------------|
| **Playwright** | ✅ Instalado | ✅ Sim | ✅ Sim (precisa config) |
| **Chrome DevTools MCP** | ✅ Instalado | ✅ Sim | ✅ Sim (precisa config) |
| **Puppeteer Vision** | ❌ Não instalado | ⚠️ Possível | ✅ Sim (precisa config) |

---

## 🚀 PRÓXIMOS PASSOS

### 1. Posso Fazer AGORA (Factory/Droid):
- ✅ Tirar screenshots via CLI
- ✅ Executar scripts Playwright/Puppeteer
- ✅ Analisar imagens depois de tiradas
- ✅ Gerar relatórios de QA

### 2. Tu Podes Fazer (Claude Desktop):
- ✅ Configurar MCPs no Claude Desktop
- ✅ Pedir análises visuais diretas
- ✅ AI vê screenshots automaticamente
- ✅ Feedback em real-time

---

## 💬 EXEMPLO DE USO ATUAL

**TU PEDES:**
"Tira screenshot do /teste-html e analisa"

**EU FAÇO:**
```bash
# 1. Tirar screenshot
npx playwright screenshot http://localhost:8080/teste-html site.png

# 2. Ler imagem
[Read tool para ver site.png]

# 3. Analisar visualmente
"Vejo 48 produtos em grid 3 colunas, 
imagens 400px altura, cores amarelo/azul navy,
design premium com shadows..."
```

**COM MCP NO CLAUDE DESKTOP:**
AI faz tudo automaticamente sem comandos manuais!

---

## 📝 CONCLUSÃO

✅ **Tenho instalado:** Playwright + Chrome DevTools MCP  
⚠️ **Limitação:** Não tenho protocolo MCP ativo (sou CLI-based)  
✅ **Solução:** Posso executar comandos e analisar resultados  
🎯 **Melhor opção:** Tu configuras MCPs no Claude Desktop para análise automática!

