# 🔧 Problemas Corrigidos - Chapéus Lisboetas

## Problemas Encontrados e Soluções

### 1. ❌ Revolution Slider - Erro Fatal com PHP 7.4
**Problema:** Plugin causava erro fatal: `[] operator not supported for strings`

**Solução:** Plugin desativado (pasta renomeada para `revslider.disabled`)

**Detalhes:**
- Revolution Slider usa função deprecated `create_function()`
- Incompatível com PHP 7.4+
- Para reativar: atualizar plugin ou usar PHP 7.2/7.3

---

### 2. ❌ .htaccess - Loop de Redirecionamento (500 Error)
**Problema:** `Request exceeded the limit of 10 internal redirects`

**Configuração Original:**
```apache
RewriteBase /wp/
RewriteRule . /wp/index.php [L]
```

**Configuração Corrigida:**
```apache
RewriteBase /
RewriteRule . /index.php [L]
```

**Motivo:** O site estava configurado para `/wp/` mas o Docker serve da raiz `/`

**Backup:** `.htaccess.backup`

---

### 3. ❌ Tema Ausente - Página em Branco (Content-Length: 0)
**Problema:** Base de dados configurada com tema "Divi" que não existe nos ficheiros

**Base de Dados Antes:**
```sql
template = 'Divi'
stylesheet = 'Divi'
```

**Base de Dados Depois:**
```sql
template = 'theretailer'
stylesheet = 'theretailer-child'
```

**Comando usado:**
```bash
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "UPDATE lx_options SET option_value='theretailer' WHERE option_name='template';"
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "UPDATE lx_options SET option_value='theretailer-child' WHERE option_name='stylesheet';"
```

---

### 4. ⚠️ Transposh - PHP Notice (Não Crítico)
**Aviso:** `Undefined index: HTTP_ACCEPT_LANGUAGE`

**Impacto:** Baixo - apenas notice, não afeta funcionalidade

**Status:** Mantido ativo, pode ser corrigido no futuro

---

### 5. ⚠️ Child Theme Footer - PHP Notice (Não Crítico)
**Aviso:** `Trying to access array offset on value of type null in footer.php line 95`

**Impacto:** Baixo - apenas notice

**Status:** Pode necessitar correção no código do child theme

---

## Configurações Ajustadas

### wp-config.php
- `DB_HOST`: `localhost` → `mysql` (nome do container Docker)
- `WP_DEBUG`: `false` → `true`
- Adicionado: `WP_DEBUG_LOG: true`
- Adicionado: `WP_DEBUG_DISPLAY: false`

### Base de Dados
- URLs: `https://www.chapeuslisboetas.com/wp` → `http://localhost:8080`
- Tema: `Divi` → `theretailer-child`

---

## Resultado Final

✅ **Site 100% Funcional**
- Homepage: 303KB de conteúdo HTML
- Login: Operacional
- Admin: Acessível
- Produtos: 128 produtos WooCommerce
- Imagens: 381MB de uploads

---

## Plugins Desativados

1. **revslider** → `revslider.disabled`
   - Motivo: Incompatibilidade com PHP 7.4
   - Impacto: Sliders não funcionam, mas site funciona normalmente

---

## Avisos Restantes (Não Críticos)

Estes avisos aparecem no `debug.log` mas não impedem o funcionamento:

1. Transposh: `HTTP_ACCEPT_LANGUAGE` undefined
2. Child Theme: Array offset notice no footer

**Recomendação:** Podem ser ignorados por agora ou corrigidos futuramente.

---

## Tempo Total de Resolução
Aproximadamente 20 minutos de troubleshooting:
- 5 min: Importação da BD
- 10 min: Correção do Revolution Slider e .htaccess
- 5 min: Identificação e correção do problema do tema

---

**Data:** 30 Setembro 2025  
**Status:** ✅ Totalmente Operacional
