# Sistema Bilingue PT/EN - Chapéus Lisboetas
## Documentação Completa

**Data:** 23 Outubro 2025
**Versão:** 1.0
**Status:** Pronto para implementação

---

## ÍNDICE DE DOCUMENTOS

### 1. RESUMO EXECUTIVO (Começar aqui)
**Arquivo:** [`RESUMO_EXECUTIVO_BILINGUE.md`](RESUMO_EXECUTIVO_BILINGUE.md)

**Conteúdo:**
- Decisão técnica (Transposh vs WPML)
- Estrutura do sistema (URLs, language switcher)
- Timeline e custos
- Próximos passos
- Aprovação necessária

**Para quem:** Cliente (Tiago), gestores de projeto

---

### 2. RELATÓRIO TÉCNICO COMPLETO
**Arquivo:** [`RELATORIO_STATUS_MULTILINGUE.md`](RELATORIO_STATUS_MULTILINGUE.md)

**Conteúdo:**
- Descobertas database (WPML antigo, Transposh ativo)
- Análise 127 traduções vazias
- Comparação detalhada OPÇÃO 1/2/3
- Queries SQL de auditoria
- Perguntas para cliente
- Recomendação técnica fundamentada

**Para quem:** Dev, tech leads

---

### 3. PLANO DE IMPLEMENTAÇÃO
**Arquivo:** [`IMPLEMENTACAO_BILINGUE_PT_EN.md`](IMPLEMENTACAO_BILINGUE_PT_EN.md)

**Conteúdo:**
- Situação atual detalhada
- Plano 6 fases (reconfigurar, switcher, traduzir, SEO, testar, documentar)
- Escopo tradução (páginas, produtos, strings)
- Timeline 12.5h
- Recursos necessários
- Alternativas avaliadas
- Métricas de sucesso

**Para quem:** Gestores de projeto, cliente

---

### 4. GUIA PASSO A PASSO (Operacional)
**Arquivo:** [`GUIA_IMPLEMENTACAO_BILINGUE.md`](GUIA_IMPLEMENTACAO_BILINGUE.md)

**Conteúdo:**
- 9 fases práticas com comandos
- Backup e preparação
- Limpeza WPML
- Configuração Transposh
- Language switcher (3 métodos)
- Tradução conteúdo (inline tutorial)
- Strings Loco Translate
- Testes completos (navegação, WooCommerce, SEO, performance)
- Deploy produção

**Para quem:** Dev executando implementação

---

### 5. CHECKLIST DE ACOMPANHAMENTO
**Arquivo:** [`CHECKLIST_BILINGUE.md`](CHECKLIST_BILINGUE.md)

**Conteúdo:**
- Checklist visual 9 fases
- Tabela top 20 produtos para preencher
- Tracking de tempo gasto
- Aprovação cliente
- Métricas pós-lançamento

**Para quem:** Dev, cliente, tracking progresso

---

## SCRIPTS AUTOMATIZADOS

### 1. Script de Limpeza WPML
**Arquivo:** [`scripts/cleanup_wpml_database.sql`](scripts/cleanup_wpml_database.sql)

**Função:**
- Remove 15+ tabelas WPML (lx_icl_*)
- Limpa opções WPML
- Limpa postmeta/usermeta/termmeta WPML
- Queries de validação

**Executar:**
```bash
docker exec -i chapeus_mysql mysql -u root -prootpassword lisboetas_web < scripts/cleanup_wpml_database.sql
```

---

### 2. Script de Configuração Transposh
**Arquivo:** [`scripts/configure_transposh_pt_en.sql`](scripts/configure_transposh_pt_en.sql)

**Função:**
- Altera default language para PT
- Define viewable languages: pt,en
- Ativa permalinks /en/
- Configura WordPress locale pt_PT
- Timezone Europe/Lisbon
- Formatos PT (data, hora)

**Executar:**
```bash
docker exec -i chapeus_mysql mysql -u root -prootpassword lisboetas_web < scripts/configure_transposh_pt_en.sql
```

---

### 3. Script Bash Completo (RECOMENDADO)
**Arquivo:** [`scripts/setup_bilingue_pt_en.sh`](scripts/setup_bilingue_pt_en.sh)

**Função:**
- Executa tudo automaticamente (fases 1-6)
- Verificações iniciais
- Backup automático
- Limpeza WPML
- Configuração Transposh
- Flush rewrite rules
- Testes URLs PT/EN
- Relatório final

**Executar:**
```bash
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"
./scripts/setup_bilingue_pt_en.sh
```

**Tempo:** ~5 minutos
**Resultado:** Sistema configurado e testado

---

## QUICK START (COMEÇAR AGORA)

### Opção A: Script Automático (Recomendado)

```bash
# 1. Navegar para diretório
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

# 2. Executar script (tudo automático)
./scripts/setup_bilingue_pt_en.sh

# 3. Aguardar ~5 min

# 4. Verificar resultado
# - WPML removido ✓
# - Transposh configurado ✓
# - URLs /en/ funcionando ✓
# - Backup criado ✓
```

**Próximo passo:** Adicionar language switcher no header (manual, 30 min)

---

### Opção B: Passo a Passo Manual

```bash
# 1. Backup
docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web > backup_$(date +%Y%m%d).sql

# 2. Limpar WPML
docker exec -i chapeus_mysql mysql -u root -prootpassword lisboetas_web < scripts/cleanup_wpml_database.sql

# 3. Configurar Transposh
docker exec -i chapeus_mysql mysql -u root -prootpassword lisboetas_web < scripts/configure_transposh_pt_en.sql

# 4. Flush permalinks
docker exec chapeus_wordpress php -r "require '/var/www/html/wp-load.php'; flush_rewrite_rules();"

# 5. Testar
curl -I http://localhost:8080/
curl -I http://localhost:8080/en/
```

**Próximo passo:** Consultar [`GUIA_IMPLEMENTACAO_BILINGUE.md`](GUIA_IMPLEMENTACAO_BILINGUE.md) Fase 4

---

## ESTRUTURA FINAL DO SISTEMA

### URLs

**Português (idioma principal):**
```
http://localhost:8080/
http://localhost:8080/sobre/
http://localhost:8080/loja/
http://localhost:8080/produto/boina-inverno/
```

**Inglês (versão traduzida):**
```
http://localhost:8080/en/
http://localhost:8080/en/sobre/
http://localhost:8080/en/loja/
http://localhost:8080/en/produto/boina-inverno/
```

---

### Plugins Usados

**Multilíngue:**
- ✅ Transposh Translation Filter (free)
- ✅ Loco Translate (free, strings tema/plugins)

**Removidos:**
- ❌ WPML (tabelas limpas)

**Mantidos:**
- ✅ Yoast SEO (hreflang automático)
- ✅ WooCommerce (compatível Transposh)
- ✅ Flatsome theme (suporte multilíngue)
- ✅ LiteSpeed Cache (cache por idioma)

---

## ESCOPO DE TRADUÇÃO

### Páginas Institucionais (11 total)

**Críticas (fazer primeiro):**
1. Homepage (/)
2. Shop (/shop/)
3. About Lisboetas (/about-lisboetas/)
4. Contact (/contact/)

**Importantes:**
5. Shipping and Handling (/delivery/)
6. Return Policy (/return-policy/)
7. FAQs (/frequently-asked-questions/)
8. Sizing Guide (/sizing-guide/)

**Secundárias:**
9. Privacy Policy (/privacy-policy/)
10. Terms of use (/terms-of-use/)
11. Track Order (/track-order/)

**Método:** Transposh inline (Alt+Shift+E)
**Tempo:** 15-20 min/página

---

### Produtos (131 total)

**Auto-tradução:** 100% (Google Translate via Transposh)
**Revisão manual:** Top 20 bestsellers
**Tempo:** 5-10 min/produto (revisão)

---

### Strings Interface

**WooCommerce:** ~150 strings (Loco Translate)
**Flatsome:** ~50 strings (Loco Translate)
**Tempo:** 2h total

---

## TIMELINE COMPLETA

| Fase | Tarefa | Tempo | Ferramenta |
|------|--------|-------|------------|
| **Setup Técnico** | | | |
| 1.1 | Backup + verificações | 15 min | Bash script |
| 1.2 | Limpar WPML | 5 min | SQL script |
| 1.3 | Configurar Transposh | 5 min | SQL script |
| 1.4 | Flush permalinks | 2 min | WP-CLI |
| **Interface** | | | |
| 2.1 | Language switcher header | 30 min | WordPress Admin |
| **Conteúdo** | | | |
| 3.1 | Traduzir 4 páginas críticas | 1h | Transposh inline |
| 3.2 | Traduzir 7 páginas restantes | 2h | Transposh inline |
| 3.3 | Revisar top 20 produtos | 2h | Transposh inline |
| **Strings** | | | |
| 4.1 | WooCommerce (~150 strings) | 1.5h | Loco Translate |
| 4.2 | Flatsome (~50 strings) | 30 min | Loco Translate |
| **Testes** | | | |
| 5.1 | Navegação + WooCommerce | 30 min | Manual |
| 5.2 | SEO (hreflang, sitemap) | 15 min | Curl + browser |
| 5.3 | Performance + cache | 15 min | PageSpeed |
| **TOTAL** | | **8.5h** | |

**Prazo:** 2 dias úteis (~4h/dia)

---

## CUSTOS

| Item | Anual | Único | Total |
|------|-------|-------|-------|
| Transposh (plugin) | €0 | - | €0 |
| Loco Translate (plugin) | €0 | - | €0 |
| Google Translate API (free tier) | €0 | - | €0 |
| Dev time (8.5h × €0) | - | €0 | €0 |
| **TOTAL** | **€0/ano** | **€0** | **€0** |

**Economia vs WPML:** €258/ano

---

## SUPORTE

### Durante Implementação (Incluído)
- Troubleshooting scripts
- Ajustes configuração
- Suporte tradução inline
- Otimização performance

### Pós-Implementação (3 meses incluídos)
- Correções traduções automáticas
- Ajustes language switcher
- Atualizações Transposh/Loco
- Suporte cliente (manual uso)

### Manutenção Rotina (Cliente)
- Adicionar novo produto → auto-traduz
- Editar página → revisar tradução EN (2-3 min)
- Editar string tema → Loco Translate (1 min)

---

## MÉTRICAS DE SUCESSO

### Técnicas (Lançamento)
- [ ] Language switcher visível e funcional
- [ ] 100% páginas institucionais traduzidas (11)
- [ ] 100% produtos com nome/descrição EN (131)
- [ ] 0 erros 404 em URLs /en/
- [ ] Hreflang tags presentes
- [ ] Sitemap XML multilíngue

### Negócio (30 dias)
- Tráfego EN: >15% total visitantes
- Conversão EN: ≥ Conversão PT
- Bounce rate EN: <65%
- Tempo sessão EN: >2 min
- Pageviews EN: >2.5/sessão

---

## TROUBLESHOOTING

### Language switcher não aparece
**Solução:**
1. WordPress Admin → Aparência → Widgets
2. Verificar widget "Translation" está em área "Header"
3. Se não estiver: arrastar e salvar
4. Limpar cache (LiteSpeed Cache)

---

### URLs /en/ retornam 404
**Solução:**
```bash
# Flush rewrite rules
docker exec chapeus_wordpress php -r "require '/var/www/html/wp-load.php'; flush_rewrite_rules();"

# OU via WordPress Admin
# Configurações → Permalinks → Salvar (sem mudar nada)
```

---

### Tradução não salva (Transposh inline)
**Solução:**
1. Verificar permissões database (lx_postmeta write)
2. Desativar cache temporariamente
3. Limpar cookies navegador
4. Tentar em janela anônima

---

### Hreflang tags não aparecem
**Solução:**
1. Transposh → Settings → Advanced
2. Verificar "Don't add rel alternate" está DESMARCADO
3. Limpar cache
4. Testar: `curl -s http://localhost:8080/ | grep hreflang`

---

## CONTATOS

**Dev responsável:** Bilal Machraa / AiParaTi
**Cliente:** Tiago Andrade (Chapéus Lisboetas)
**Email:** mail@chapeuslisboetas.com
**WhatsApp:** +351 918 911 308

---

## CHANGELOG

### v1.0 - 23 Outubro 2025
- Criação documentação completa
- Scripts SQL (cleanup + configure)
- Script Bash automatizado
- Guias passo a passo
- Checklist acompanhamento
- README índice

---

## PRÓXIMOS PASSOS IMEDIATOS

### 1. DECISÃO CLIENTE (Urgente)

**Perguntas:**
- [ ] Aprovação solução Transposh (free) vs WPML (€258/ano)?
- [ ] Quem traduz páginas? (Dev, Cliente, 50/50)
- [ ] Quantos produtos revisar manualmente? (Top 10, 20, 50?)
- [ ] Prazo lançamento EN? (Com PT, 1-2 semanas após, pós-Black Friday)

**Enviar:** [`RESUMO_EXECUTIVO_BILINGUE.md`](RESUMO_EXECUTIVO_BILINGUE.md)

---

### 2. EXECUÇÃO (Após aprovação)

**Dia 1 (2h):**
```bash
# Setup automático
./scripts/setup_bilingue_pt_en.sh

# Language switcher manual
# WordPress Admin → Widgets → Translation → Header
```

**Dia 2 (4h):**
- Traduzir 4 páginas críticas
- Traduzir 7 páginas restantes
- Strings WooCommerce (Loco)

**Dia 3 (2.5h):**
- Revisar top 20 produtos
- Strings Flatsome (Loco)
- Testes finais

**TOTAL:** 8.5h em 3 dias

---

### 3. ENTREGA

**Deliverables:**
- [ ] Sistema bilingue PT/EN funcional
- [ ] Language switcher header
- [ ] 11 páginas traduzidas
- [ ] 131 produtos traduzidos (20 revisados)
- [ ] Strings WC/Flatsome traduzidas
- [ ] Manual cliente
- [ ] Testes validados

---

## RECURSOS ADICIONAIS

**Documentação oficial:**
- Transposh: https://transposh.org/documentation/
- Loco Translate: https://localise.biz/wordpress/plugin
- WooCommerce multilingual: https://woocommerce.com/document/woocommerce-multilingual/

**Referências projeto:**
- CLAUDE.md (contexto geral)
- Guia Claude+Z.AI (setup dev)
- Docker compose (ambiente local)

---

**Última atualização:** 23 Outubro 2025
**Status:** ✅ Documentação completa e scripts prontos
**Ação:** Aguardando aprovação cliente para execução
