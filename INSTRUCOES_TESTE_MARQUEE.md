# Instruções de Teste: Header Ticker Animado

**Para:** Tiago Andrade (Chapéus Lisboeta)
**De:** Bilal Machraa / AiParaTi
**Data:** 27 Outubro 2025

---

## Como Testar o Novo Header Animado

### 1. Abrir o Site Local

```
http://localhost:8080
```

### 2. O Que Deve Ver

No topo do site (barra castanha), deve ver o texto:

**"Envios grátis acima de 50€ · Loja física: Praça da Figueira, Lisboa"**

A **passar suavemente** da direita para a esquerda, continuamente.

### 3. Verificações Rápidas

#### ✓ Movimento Suave
- [ ] O texto move-se horizontalmente?
- [ ] O movimento é contínuo (sem pausas)?
- [ ] Não há "saltos" ou "cortes" no loop?

#### ✓ Velocidade
- [ ] A velocidade é moderada (não muito rápido)?
- [ ] Consegue ler o texto confortavelmente?

#### ✓ Interactividade
- [ ] Ao passar o rato por cima, a animação pausa?
- [ ] Ao tirar o rato, a animação retoma?

#### ✓ Mobile (Testar no Telemóvel)
- [ ] Abra no telemóvel: http://localhost:8080
- [ ] O texto passa mais rápido que no desktop?
- [ ] O texto é legível no ecrã pequeno?

### 4. Teste Visual Standalone

Se quiser ver a animação isoladamente (sem o resto do site):

```
Abra o ficheiro: test-marquee.html
(Basta fazer duplo-click no ficheiro)
```

Este ficheiro mostra apenas a animação do header, para verificar se está tudo correcto.

### 5. Problemas Conhecidos (e Soluções)

#### Se não ver animação (texto está parado):

1. **Limpar cache do browser:**
   - Mac: `Command + Shift + R`
   - Windows: `Ctrl + Shift + R`

2. **Verificar se JavaScript está activado:**
   - Deve estar activado por padrão
   - Se não funcionar, avisar

3. **Hard refresh:**
   - Fechar e abrir o browser novamente
   - Ir a http://localhost:8080 novamente

#### Se o texto estiver "cortado" ou "colado":

1. Fazer hard refresh (Command + Shift + R)
2. Verificar se o site está a carregar completamente
3. Avisar se persistir

### 6. Feedback Esperado

Por favor, verificar e responder:

#### A. Velocidade da Animação
- [ ] **Perfeita** - não mexer
- [ ] **Muito rápida** - precisa desacelerar
- [ ] **Muito lenta** - precisa acelerar

#### B. Aspeto Visual
- [ ] **Profissional** - gostei
- [ ] **Precisa ajustes** - especificar: ___________

#### C. Espaçamento entre Textos
- [ ] **Bom** - não mexer
- [ ] **Muito junto** - precisa mais espaço
- [ ] **Muito espaçado** - precisa menos espaço

#### D. Tamanho do Texto
- [ ] **Bom** - não mexer
- [ ] **Muito pequeno** - aumentar
- [ ] **Muito grande** - diminuir

#### E. Mensagem
- [ ] **Correcta** - manter assim
- [ ] **Alterar para:** ___________________________

### 7. Testes Opcionais (Avançado)

Se quiser testar mais a fundo:

#### Teste de Performance (Chrome DevTools)

1. Abrir o site: http://localhost:8080
2. Pressionar `F12` (abrir DevTools)
3. Ir ao separador **Performance**
4. Clicar em "Record" (botão redondo)
5. Esperar 5 segundos
6. Clicar em "Stop"
7. Verificar linha de FPS (deve estar verde/60fps)

#### Teste de Acessibilidade (WAVE)

1. Instalar extensão: https://wave.webaim.org/extension/
2. Abrir http://localhost:8080
3. Clicar no ícone WAVE
4. Verificar se não há erros críticos

### 8. Screenshots para Referência

#### ANTES (Problema Original)
```
╔════════════════════════════════════════════════════╗
║  Envios grátis acima de 50€ · Loja física: Praça  ║
║  da Figueira, LisboaEnvios grátis acima de 50€    ║
║  [TEXTO ESTÁTICO E COLADO]                         ║
╚════════════════════════════════════════════════════╝
```

#### DEPOIS (Solução Implementada)
```
╔════════════════════════════════════════════════════╗
║  ←←← Envios grátis acima de 50€ · Loja física:   ║
║      Praça da Figueira, Lisboa                    ║
║  [ANIMAÇÃO SUAVE E CONTÍNUA]                       ║
╚════════════════════════════════════════════════════╝
```

### 9. Comparação com Sites de Referência

Esta animação é similar a:

- **Rothys.com** - Header promotions
- **American Apparel** - Top bar announcements
- **Zara** - Seasonal offers bar
- **H&M** - Free shipping messages

Todos usam ticker animado para mensagens promocionais.

### 10. Próximos Passos

Após aprovar:

1. ✅ Implementação está completa no código
2. ✅ Pode fazer commit para Git
3. ✅ Pronto para deploy em staging
4. ✅ Depois pode ir para produção

### 11. Alterações Futuras

Se quiser mudar a mensagem no futuro:

**Ficheiro a editar:**
```
wordpress/wp-content/themes/flatsome-child/assets/js/custom.js
```

**Linha a modificar:**
```javascript
// Linha 9
const message = 'Envios grátis acima de 50€ · Loja física: Praça da Figueira, Lisboa';
```

Ou contactar Bilal/AiParaTi para fazer a alteração.

### 12. Contactos de Suporte

**Durante 3 meses (incluído):**
- WhatsApp: +351 918 911 308
- Email: (adicionar email aqui)
- Resposta: <24h dias úteis

**Para bugs críticos:**
- Contactar imediatamente
- Suporte incluído sem custos

---

## Checklist Final para Aprovação

Por favor preencher:

- [ ] Testei no site local (http://localhost:8080)
- [ ] Testei no mobile (ou DevTools mobile view)
- [ ] A animação está suave e profissional
- [ ] A velocidade está correcta
- [ ] O texto pausa ao passar o rato
- [ ] Li a mensagem e está correcta
- [ ] Aprovado para deploy em produção

**Assinatura de Aprovação:**

Nome: ___________________________
Data: ___________________________
Observações: ____________________
____________________________________
____________________________________

---

**Obrigado pela confiança!**
Bilal Machraa / AiParaTi
Desenvolvimento Web & AI para PMEs Portuguesas

---

## Anexos

### A. URLs Úteis
- Site local: http://localhost:8080
- Admin: http://localhost:8080/wp-admin
- Teste standalone: test-marquee.html (duplo-click)

### B. Ficheiros Técnicos
- Relatório completo: `RELATORIO_IMPLEMENTACAO_MARQUEE.md`
- Resumo visual: `RESUMO_VISUAL_MARQUEE.md`
- Script de teste: `test-console.js`

### C. Backup
Todos os ficheiros originais foram preservados.
Se algo correr mal, pode reverter sem problemas.

**Localização do backup:**
```
wordpress/wp-content/themes/flatsome-child/
```

Git mantém histórico completo de alterações.
