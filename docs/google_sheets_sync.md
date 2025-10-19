# Sincronização de Catálogo com Google Sheets

## 1. Preparar o documento
1. Execute `scripts/export_master_catalog.py`.
2. Importe o ficheiro `output_catalogo/catalogo_master.csv` para uma folha Google (sugestão: aba `Catalogo`).
3. Garanta que as colunas obrigatórias estão presentes e com estes nomes exatamente:
   - `Sheet`
   - `SKU`
   - `Nome`
   - `Preço`
4. Colunas opcionais suportadas pelo pipeline: `Descrição curta`, `Descrição longa`, `Tags`, `Cor`, `Tamanho`, `Composição`, `Pack`, `URL fornecedor`, `URLs extra`, `Imagens`, `Prioridade`, `Destaque homepage?`, `Notas internas`.
5. Para pré-visualizar imagens no Google Sheets pode usar `=IMAGE("https://dominio/catalogo2025/.../img_01.jpg")`.

## 2. Criar a Service Account
1. No [Google Cloud Console](https://console.cloud.google.com/) crie um projeto (ou reutilize um existente).
2. Ative as APIs **Google Sheets** e **Google Drive**.
3. Em IAM & Admin → Service Accounts → `Create Service Account`:
   - Nome: `chapéus-sync`
   - Role: `Editor` (não é necessário mais do que isto).
4. Na conta criada, gere uma chave (`Add Key → JSON`) e guarde o ficheiro como `config/google-service-account.json` (adicione ao `.gitignore`).
5. Partilhe o documento Google Sheets com o e-mail da Service Account (permissão `Editor`).

## 3. Configurar o ambiente local
```bash
pip install gspread google-auth

export GOOGLE_SHEETS_ID="<ID do documento>"
export GOOGLE_SERVICE_ACCOUNT_FILE="config/google-service-account.json"
# opcional (usa sheet1 por defeito)
export GOOGLE_SHEETS_TAB="Catalogo"
```

## 4. Sincronizar alterações
```bash
python scripts/sync_google_sheet.py
scripts/generate_wc_catalog.py
```
- O script cria `output_catalogo/catalogo_backup.json` antes de atualizar `catalogo.json`.
- Se o cliente adicionar novos produtos, os campos `Imagens` podem ser preenchidos com os caminhos relativos (ex.: `catalogo2025/boinas inverno/...`).
- Produtos sem imagens continuarão sinalizados em `relatorios/produtos_sem_imagem.{csv,md}`.

## 5. Guia de resumo/pivots
- Execute `scripts/export_catalog_summary.py` para gerar `catalogo_summary_sheet.csv` (total por coleção) e `catalogo_summary_sheet_tipo.csv` (total por coleção e tipo). Pode importar estes CSVs como abas adicionais no Google Sheets para referência.
- Alternativamente, crie uma aba `Resumo` no Google Sheets com as fórmulas:
  ```
  =QUERY(Catalogo!A:Q,"select A, count(A) where A<>'' group by A label count(A) 'Total produtos'")
  =QUERY(Catalogo!A:Q,"select A, C, count(C) where A<>'' group by A, C label count(C) 'Total por tipo'")
  ```
  Ajuste os intervalos conforme as colunas da sua folha. Estas tabelas atualizam-se automaticamente à medida que o cliente edita a aba principal.

## 5. Fluxo recomendado
1. Cliente atualiza a folha.
2. Equipa corre `sync_google_sheet.py` e `generate_wc_catalog.py`.
3. Importar o novo CSV no WooCommerce (staging ou produção).
4. Executar `util/qa_catalogo.py` e `relatorios/produtos_sem_imagem.csv` para confirmar que não faltam dados críticos.

> Em caso de erro (`Invalid credentials` / `403`), confirme que o documento foi partilhado com a service account e que as APIs foram ativadas.
