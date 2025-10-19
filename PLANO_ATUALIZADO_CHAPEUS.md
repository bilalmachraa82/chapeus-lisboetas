# Plano Atualizado – Chapéus Lisboetas (Outubro 2025)

## 📌 Estado Atual
- [x] Ambiente local WordPress + WooCommerce funcional (`docker-compose`).
- [x] Catálogo Excel centralizado (`WEBSITE Produtos Catálogo.xlsx`).
- [x] Extrator `scripts/catalog_scraper.py` revisto:
  - Salva _todos_ os campos do Excel (marca, preço, specs, etc.).
  - Faz scraping automático de cada URL de fornecedor.
  - Descarrega apenas imagens ≥ 800 px com metadados (alt/origem/ordem).
  - Gera `catalogo.json`, `catalogo.csv`, `catalogo.db` + pasta `output_catalogo/images/`.
- [x] QA manual e automático (`util/qa_catalogo.py`) cobrindo 114 produtos.
- [x] Banco de imagens existente substituído por nova extração (backup `backups/uploads_legacy_20251019.tar.gz`).

## 🎯 Objetivo de Curto Prazo
Publicar o catálogo completo (≈180 produtos) no novo site WooCommerce mantendo ordem lógica das imagens, atributos detalhados e autonomia total para futuras atualizações.

---

## Fase 1 – Dados & Imagens ✅
1. **Extrair catálogo completo** – _concluído_ (`scripts/catalog_scraper.py` sem limite → 114 produtos).
2. **Verificação automática** – _concluído_ (`util/qa_catalogo.py` lista avisos de preço/imagem para tratamento manual).
3. **Upload assets** – _concluído_ (imagens novas copiadas para `wp-content/uploads/catalogo2025/`).
4. **Backup** – _concluído_ (`backups/uploads_legacy_20251019.tar.gz`).

### TODO rápido
- [ ] Sincronizar pasta de imagens com storage permanente (git LFS, S3, etc.).
- [ ] Tratar avisos do QA (produtos sem preço/imagem HD → decidir excluir ou complementar).

---

## Fase 2 – Modelagem WooCommerce
1. **Mapeamento de atributos** – _concluído_
   - `specs` → atributos WooCommerce (Cor, Tamanho, Composição, Pack).
   - `tags` → etiquetas WooCommerce (lista do Excel).
   - `sheet` → categorias (`Chapéus > …`).
2. **Gerar CSV WooCommerce definitivo** – _concluído_
   - `scripts/export_master_catalog.py` gera `catalogo_master.csv` (fonte para Google Sheets).
   - `scripts/generate_wc_catalog.py` gera `output_catalogo/woocommerce_import.csv` (88 produtos válidos).
   - Produtos sem imagem HD listados em `relatorios/produtos_sem_imagem.{md,csv}` para revisão com o cliente.
3. **Preparar importação**
   - [x] Copiar `output_catalogo/images` → `wp-content/uploads/catalogo2025/` (estrutura final).
   - [x] CSV já referencia `catalogo2025/...` (compatível com uploads atuais).
   - [ ] Validar com cliente a exclusão temporária dos 34 produtos sem dados completos (preço/imagem) antes da importação.
4. **Sincronização Google Sheets** – _em progresso_
   - `catalogo_master.csv` pronto para importar.
   - `scripts/sync_google_sheet.py` sincroniza alterações do Sheet → `catalogo.json` (requer Service Account + `gspread`).
   - Falta configurar credenciais/API e automatizar execução.

### TODO rápido
- [ ] Definir hierarquia de categorias (seguir doc “GUIA COMPLETO DE D.md”).
- [ ] Normalizar nomenclatura de atributos (PT/EN) pensando no WPML.

---

## Fase 3 – WooCommerce & Conteúdo
1. **Importação staging**
   - Usar ambiente Docker local / PTisp staging.
   - Importar CSV completo (WooCommerce > Produtos > Importar).
   - Validar: preços, variações, galeria ordenada.
2. **Conteúdos institucionais**
   - Páginas: Sobre, Contactos, Envios, Devoluções, Garantias, FAQ, Privacidade, Termos, Cookies.
   - Traduções PT/EN (WPML) conforme doc do Claude.
3. **Menus e navegação**
   - Menu principal (Início, Loja dropdown, Coleções, Sobre, Contactos).
   - Footer com 4 colunas (Informações, Ajuda, Legal, Contacto).

### TODO rápido
- [ ] Recolher copy final do cliente para páginas institucionais.
- [ ] Definir coleções destacadas (Novidades, Mais vendidos, etc.).

---

## Fase 4 – UX/UI & Integrações
1. **Tema Flatsome**
   - Aplicar identidade (cores/tipografia) guardada em `brand_identity.json`.
   - Configurar cabeçalho, hero, carrosséis, hero sections (referências Rothys + American Apparel).
2. **Plugins obrigatórios**
   - IfthenPay (MB Way + Multibanco).
   - CTT Expresso (envios automáticos).
   - WP Rocket, Yoast, CookieYes, GA4/GTM, WPML.
3. **Componentes customizados**
   - Botão WhatsApp flutuante e CTA telefone.
   - Blocos de confiança (serviço ao cliente, devoluções, etc.).
   - Tabs adicionais nas páginas de produto (especificações, cuidados, envios).

### TODO rápido
- [ ] Receber logótipo final e paleta oficial.
- [ ] Criar layout hero (imagem + copy).

---

## Fase 5 – QA & Publicação
1. **Checklist funcional** (staging e produção)
   - Fluxo completo compra MB Way/Multibanco.
   - Emails transacionais personalizados.
   - Testes mobile/tablet.
   - Tempo de carregamento (WP Rocket + Cloudflare caching).
2. **Backups & redundância**
   - Confirmar JetBackup no PTisp + UpdraftPlus para storage externo.
   - Exportar CSV final de produtos após importação (snapshot).
3. **Lançamento**
   - Trocar DNS para PTisp.
   - Monitorizar GA4/GTM + conversões.
   - Plano de contingência: rollback via backup + reimportação CSV.

---

## Fase 6 – Autonomia & Documentação
- [ ] Criar guia interno para o cliente (atualização de produtos, reposição de stock, reposição backup).
- [x] Documentar pipeline ETL (`scripts/catalog_scraper.py`, QA, import WooCommerce) neste plano.
- [ ] Configurar automação mensal (cron ou GitHub Actions) para reextrair catálogo caso fornecedor atualize dados.

---

## Referências e Artefactos
- `🎩 CHAPÉUS LISBOETA - GUIA COMPLETO DE D.md` (requisitos macro).
- `output_catalogo/` (dataset completo + imagens).
- `brand_identity.json` (cores + tipografia).
- `generate_woocommerce_complete.py` (base para CSV final).
- `setup-wordpress-complete.sh`, `import-db.sh` (infra local).

---

## Próximos Passos Imediatos
1. Tratar avisos do QA (imagens em falta) com o cliente via Google Sheets.
2. Configurar Service Account + sincronização (`sync_google_sheet.py`).
3. Importar catálogo completo em staging e revisar com o cliente.
4. Aplicar identidade visual + conteúdos institucionais.
5. Executar checklist de QA e preparar go-live.

> **Nota**: este plano substitui qualquer limitação anterior (20/30 produtos). O objetivo é importar a totalidade do catálogo com qualidade e autonomia máximas, conforme instruções recentes do cliente e alinhado com o plano do Claude.
