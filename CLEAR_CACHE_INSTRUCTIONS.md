# 🔄 INSTRUÇÕES: LIMPAR CACHE DO BROWSER

**PROBLEMA:** Site parece igual mesmo depois das alterações aplicadas.

**CAUSA:** Cache do browser está a mostrar versões antigas do CSS/JavaScript.

---

## ✅ PASSO A PASSO (OBRIGATÓRIO!)

### 1️⃣ **CHROME / EDGE / BRAVE**

**Método 1: Hard Refresh (MAIS RÁPIDO)**
```
Mac: Cmd + Shift + R
Windows/Linux: Ctrl + Shift + R
```

**Método 2: Limpar cache manualmente**
1. Abre Chrome
2. Carrega em: **Cmd+Shift+Delete** (Mac) ou **Ctrl+Shift+Delete** (Windows)
3. Seleciona:
   - ✅ Cached images and files
   - ✅ Últimas 24 horas
4. Clica "Clear data"
5. Recarrega página: http://localhost:8080

---

### 2️⃣ **FIREFOX**

**Hard Refresh:**
```
Mac: Cmd + Shift + R
Windows/Linux: Ctrl + Shift + R
```

**OU:**
```
Mac: Cmd + Shift + Delete
Windows/Linux: Ctrl + Shift + Delete
```
→ Seleciona "Cache" → Limpar agora

---

### 3️⃣ **SAFARI**

**Hard Refresh:**
```
Mac: Option + Cmd + E (limpa cache)
Depois: Cmd + R (recarrega)
```

**OU via Menu:**
1. Safari → Preferences → Advanced
2. ✅ Ativa "Show Develop menu"
3. Menu Develop → Empty Caches
4. Recarrega: http://localhost:8080

---

## 🧪 VERIFICAR SE FUNCIONOU

Depois de limpar cache, verifica:

### ✅ Checklist Rápido:

1. **Menu Dropdown**
   - Passa o rato sobre "Loja" no menu
   - O dropdown DEVE aparecer POR CIMA das imagens
   - ❌ Se aparecer ATRÁS das imagens → Ainda em cache

2. **Cor dos Links**
   - Links no site devem ser **castanho/brown** (#8B4513)
   - ❌ Se forem **azul slate** (#5B7B8F) → Ainda em cache

3. **Cookie Banner** (Modo Incógnito)
   - Abre janela incógnita: Cmd+Shift+N (Chrome) ou Cmd+Shift+P (Firefox)
   - Vai para: http://localhost:8080
   - Botões do cookie banner devem ser **terracotta/laranja** (#E07A31)
   - ❌ Se forem **azul brilhante** (#1863DC) → Problema persiste

4. **Footer - Livro de Reclamações**
   - Scroll até ao fundo da página
   - DEVE aparecer link "📖 Livro de Reclamações"
   - ❌ Se não aparecer → functions.php não carregou

5. **Admin Bar** (se estiveres logged in)
   - Admin bar no topo deve ser **terracotta** (#E07A31)
   - ❌ Se for **azul WordPress** (#007cba) → Cache

---

## 🚨 SE AINDA NÃO FUNCIONAR

### Opção A: Modo Incógnito (Teste Limpo)
```
Chrome: Cmd+Shift+N (Mac) ou Ctrl+Shift+N (Windows)
Firefox: Cmd+Shift+P (Mac) ou Ctrl+Shift+P (Windows)
Safari: File → New Private Window
```
→ Vai para http://localhost:8080
→ Se funcionar aqui = é problema de cache
→ Limpa cache do browser normal

### Opção B: Desabilitar Cache (Chrome DevTools)
1. Abre http://localhost:8080
2. **F12** ou **Cmd+Option+I** (abre DevTools)
3. Tab "Network"
4. ✅ Ativa checkbox "Disable cache"
5. Mantém DevTools aberto
6. Recarrega página (**Cmd+R**)

### Opção C: Força Reload CSS Específico
No browser, abre Console (F12) e corre:
```javascript
// Força reload do CSS do child theme
var link = document.querySelector('link[href*="flatsome-child/style.css"]');
if (link) {
    link.href = link.href.split('?')[0] + '?v=' + Date.now();
}
```

### Opção D: Verificar se Container Está Running
```bash
docker ps | grep chapeus
```
Deve mostrar:
- chapeus_wordpress (UP)
- chapeus_mysql (UP)

Se não estiver:
```bash
docker-compose up -d
```

---

## 📸 SCREENSHOTS PARA COMPARAR

### ANTES (com bugs):
- Menu dropdown atrás das imagens ❌
- Links azul slate ❌
- Cookie banner azul brilhante ❌

### DEPOIS (fixes aplicados):
- Menu dropdown por cima (z-index 10001) ✅
- Links castanho (#8B4513) ✅
- Cookie banner terracotta (#E07A31) ✅
- Footer com Livro Reclamações ✅

---

## 🆘 ÚLTIMA OPÇÃO: REBUILD COMPLETO

Se NADA funcionar:

```bash
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

# Stop containers
docker-compose down

# Clear Docker cache
docker system prune -f

# Restart
docker-compose up -d

# Wait 10 seconds
sleep 10

# Test
curl -I http://localhost:8080/
```

Depois:
1. Fecha TODOS os browsers
2. Reabre browser
3. Vai para http://localhost:8080
4. Verifica mudanças

---

## ✅ CONFIRMAÇÃO FINAL

Quando vires estas mudanças, está OK:

- ✅ Menu "Loja" hover → Dropdown visível
- ✅ Links castanho (não azul)
- ✅ Cookie banner terracotta (modo incógnito)
- ✅ Footer: "📖 Livro de Reclamações"
- ✅ Add to cart → Mensagem terracotta

**Se não vires NENHUMA destas mudanças:**
→ Reporta qual browser estás a usar (Chrome/Firefox/Safari)
→ Screenshot do que vês
→ Output de: `docker ps`

---

**Criado:** 2025-10-30 02:15
**Tempo estimado:** 2-5 minutos para limpar cache
**Sucesso esperado:** 95%
