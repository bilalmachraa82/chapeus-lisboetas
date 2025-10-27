# 🔧 INSTRUÇÕES PLACEHOLDERS - WordPress Admin

**Tempo estimado:** 10 minutos
**Método:** WordPress Admin (não pode ser feito via SQL)

---

## ⚠️ POR QUÊ WORDPRESS ADMIN?

Estes placeholders estão em **Flatsome Theme Customizer**, que usa serialized PHP arrays.
**NÃO PODE ser editado via SQL** sem risco de corromper dados.

---

## 📋 PLACEHOLDER 1: TOP BAR HEADER

**Atual:** "Add anything here or just remove it..."

**Target:** "Envios grátis acima de 50€ | Loja física: Praça da Figueira, Lisboa | ☎ +351 918 911 308"

**Como corrigir:**
1. Login: http://localhost:8080/wp-admin
2. Aparência → Personalizar
3. **Header → Top Bar**
4. Encontrar campo "Text Content" ou "HTML Content"
5. Substituir texto
6. **Publicar**

---

## 📋 PLACEHOLDER 2: SOCIAL LINKS

**Atual:**
- Facebook: http://url
- Instagram: http://url
- Twitter: http://url
- Email: mailto:your@email

**Target:**
- Instagram: https://www.instagram.com/chapeuslisboetas
- Facebook: https://www.facebook.com/chapeuslisboetas (a confirmar)
- Email: mailto:mail@chapeuslisboetas.com
- **REMOVER:** Twitter

**Como corrigir:**
1. Aparência → Personalizar
2. **Header → Social Links**
3. Para cada link:
   - Instagram → URL real
   - Facebook → URL real (confirmar com cliente)
   - Email → mail@chapeuslisboetas.com
   - Twitter → **DELETE**
4. **Publicar**

---

## 📋 PLACEHOLDER 3: FOOTER COPYRIGHT

**Atual:** "Copyright 2025 © Flatsome Theme"

**Target:** "Copyright 2025 © Chapéus Lisboetas | Praça da Figueira, Lisboa"

**Como corrigir:**
1. Aparência → Personalizar
2. **Footer → Footer Copyright**
3. Substituir texto
4. Adicionar link (opcional): `<a href="/">Chapéus Lisboetas</a> | Praça da Figueira, Lisboa`
5. **Publicar**

---

## ✅ VERIFICAÇÃO PÓS-CORREÇÃO

Após publicar, abrir:
- http://localhost:8080/
- Ctrl+Shift+R (hard refresh - limpar cache browser)
- Verificar:
  - [ ] Top bar sem "Add anything"
  - [ ] Social links funcionam
  - [ ] Footer sem "Flatsome Theme"

---

## 🚨 SE APARECER ERRO

**Erro:** "Cannot modify header information"
**Solução:** Recarregar página WordPress Admin

**Erro:** "Changes não salvam"
**Solução:**
1. Desativar todos os plugins
2. Tentar novamente
3. Reativar plugins

---

## 📊 IMPACTO

**Antes:** Site com 3 placeholders visíveis (não profissional)
**Depois:** Site 100% branded (launch-ready)

**Grade:** B- → A+

---

**Tempo:** 10 minutos
**Dificuldade:** Fácil (sem código, só Customizer)
