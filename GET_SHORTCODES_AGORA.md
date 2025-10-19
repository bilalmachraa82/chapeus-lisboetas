# 🚨 AÇÃO IMEDIATA: Copiar Shortcodes

**Instagram bloqueou TODOS os métodos automáticos. Preciso que VOCÊ faça isto (2 minutos!):**

---

## 📋 **PASSO A PASSO (COPIAR E COLAR):**

### **1. Abrir Instagram**
```
https://www.instagram.com/chapeuslisboetas/
```

### **2. Fazer Scroll**
- Scroll para baixo até carregar **TODAS** as 372 fotos
- Demoram ~1-2 minutos scrolling
- Até não carregar mais fotos novas

### **3. Abrir Console (F12)**
- Windows/Linux: `F12`
- Mac: `Cmd + Option + J`

### **4. Ir para tab "Console"**

### **5. COPIAR E COLAR este código:**

```javascript
// Extrair e copiar TODOS os shortcodes automaticamente
let shortcodes = [];
document.querySelectorAll('a[href*="/p/"]').forEach(a => {
  const match = a.href.match(/\/p\/([A-Za-z0-9_-]+)\//);
  if(match && !shortcodes.includes(match[1])) {
    shortcodes.push(match[1]);
  }
});

// Mostrar quantidade
console.log(`✅ ${shortcodes.length} shortcodes encontrados!`);

// Copiar para clipboard AUTOMATICAMENTE
const text = shortcodes.join('\n');
navigator.clipboard.writeText(text).then(() => {
  console.log('📋 COPIADO PARA CLIPBOARD!');
  alert(`✅ ${shortcodes.length} shortcodes copiados!\n\nAgora:\n1. Criar arquivo shortcodes.txt\n2. Colar (Ctrl+V)\n3. Salvar`);
});

// Mostrar primeiros 5
console.log('\n📝 Primeiros 5:');
shortcodes.slice(0, 5).forEach(s => console.log(s));
```

### **6. Pressionar ENTER**

### **7. Vai aparecer alerta:**
```
✅ XXX shortcodes copiados!

Agora:
1. Criar arquivo shortcodes.txt
2. Colar (Ctrl+V)
3. Salvar
```

### **8. Criar arquivo:**
```bash
# No Mac:
open -e shortcodes.txt

# OU usar qualquer editor
```

### **9. Colar (Cmd+V ou Ctrl+V)**

### **10. Salvar arquivo**

Deve ficar assim:
```
DO8jxFKiJko
DO53ge6COrf
DO1YuMVCHCU
DOwDq6WjcUR
DN5--uojSLW
DN5lICAirxp
DNyTzUT2gf7
...
(total ~372 linhas)
```

---

## 🚀 **DEPOIS DE SALVAR shortcodes.txt:**

```bash
# Rodar download
python3 download_from_shortcodes.py

# Vai baixar TODAS as 372 fotos automaticamente!
# Tempo estimado: 15-20 minutos
```

---

## ⚡ **ALTERNATIVA MAIS RÁPIDA:**

Se preferir não usar console, posso criar uma **lista parcial** agora:

Os 12 shortcodes que já temos:
```
DO8jxFKiJko
DO53ge6COrf
DO1YuMVCHCU
DOwDq6WjcUR
DN5--uojSLW
DN5lICAirxp
DNyTzUT2gf7
DNn-LYdtJAa
DNVyxfvt489
DNQ1eR1s0LE
DND36SVML27
DL-Xt9oNI6H
```

Posso processar estas 12 com Seedream AGORA enquanto você obtém os outros 360!

---

## 🎯 **O QUE PREFERE?**

**OPÇÃO 1:** Você faz método console (2 min) → Download automático 372 fotos (20 min)

**OPÇÃO 2:** Processar 12 agora → Obter 360 depois

**Qual prefere?** 🚀
