# Livro de Reclamações - Image TODO

**ISSUE-009:** Missing Livro de Reclamações link

## Current Status: ⚠️ PARTIALLY COMPLETE

### ✅ What's Done:
- PHP function added to functions.php
- Link to https://www.livroreclamacoes.pt/ configured
- Fallback text emoji "📖 Livro de Reclamações" if image missing
- Hook into footer: `flatsome_footer_bottom`

### ❌ What's Missing:
**Download official badge image:**

1. Visit: https://www.livroreclamacoes.pt/Inicio/
2. Scroll to bottom → "Livro de Reclamações Eletrónico"
3. Download official badge PNG
4. Save to: `/wordpress/wp-content/themes/flatsome-child/assets/images/livro-reclamacoes.png`
5. Recommended size: 200×60px or similar

**Alternative:** Use text-only fallback (already configured)

## Legal Requirement

**Decreto-Lei n.º 156/2005, de 15 de Setembro**
- Obrigatório para todos os estabelecimentos comerciais em Portugal
- Inclui e-commerce
- Multas: €250 - €3,740 por incumprimento

## Testing

1. Go to: http://localhost:8080
2. Scroll to footer
3. Look for "Livro de Reclamações" link
4. Click → Should open https://www.livroreclamacoes.pt/ in new tab

---

**Created:** 2025-10-30 02:05
**Status:** Functional (text fallback), needs official badge image
