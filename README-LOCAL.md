# Chapéus Lisboetas - Ambiente Local

## ✅ Site WordPress Configurado com Sucesso!

### 🌐 URLs de Acesso

- **Site Frontend**: http://localhost:8080
- **Painel Admin**: http://localhost:8080/wp-admin
- **phpMyAdmin**: http://localhost:8081

### 🔑 Credenciais

**Base de Dados:**
- Host: localhost:3306 (ou `mysql` dentro do Docker)
- Database: `lisboetas_web`
- Username: `lisboetas`
- Password: `e$4rU9h8`
- Root Password: `rootpassword`

**WordPress Admin:**
- URL: http://localhost:8080/wp-admin
- Utilizadores disponíveis:
  - `vm` (pb@virtualmente.pt)
  - `lisboetas` (mail@chapeuslisboetas.com)
  - `well` (wellcardoso.pt@gmail.com)
- ⚠️ Passwords são as mesmas do site de produção

### 🐳 Comandos Docker Úteis

```bash
# Iniciar os containers
docker-compose up -d

# Parar os containers
docker-compose stop

# Parar e remover os containers
docker-compose down

# Ver logs do WordPress
docker logs chapeus_wordpress -f

# Ver logs do MySQL
docker logs chapeus_mysql -f

# Ver status dos containers
docker-compose ps

# Reiniciar containers
docker-compose restart

# Aceder ao shell do WordPress
docker exec -it chapeus_wordpress bash

# Aceder ao MySQL
docker exec -it chapeus_mysql mysql -u root -prootpassword lisboetas_web
```

### 📊 Informações do Site

**WordPress:** v5.4.1 (Maio 2020)
**PHP:** 7.4.33
**MySQL:** MariaDB 10.6
**Tema:** The Retailer v3.1.6 (Child Theme ativo)

### 🔌 Plugins Principais Instalados

- WooCommerce (loja online)
- Multibanco Gateway (pagamentos PT)
- Moloni (faturação PT)
- Revolution Slider
- Visual Composer (JS Composer)
- WPML / Transposh (multilíngua)
- Wordfence (segurança)
- MailChimp, Contact Form 7, YITH Wishlist

### ⚠️ Problemas Corrigidos

1. ✅ **Revolution Slider DESATIVADO**: Plugin incompatível com PHP 7.4 (erro fatal)
   - Pasta renomeada para `revslider.disabled`
   - Para reativar: atualizar plugin ou usar PHP 7.2/7.3

2. ✅ **.htaccess**: Corrigido loop de redirecionamento
   - Alterado `RewriteBase /wp/` para `RewriteBase /`
   - Backup: `.htaccess.backup`

3. ✅ **Tema**: Base de dados tinha "Divi" que não existia
   - Corrigido para `theretailer-child`
   - Era a causa da página em branco

4. ⚠️ **Transposh**: Warning de `HTTP_ACCEPT_LANGUAGE` (não crítico)

**Ver detalhes:** [PROBLEMAS-CORRIGIDOS.md](PROBLEMAS-CORRIGIDOS.md)

### 📊 Estatísticas do Site

- **128 produtos WooCommerce** publicados
- **3 utilizadores** WordPress
- **381MB** de media/uploads

### 📝 Estrutura de Ficheiros

```
full-chapeus-lisboetas (2)/
├── docker-compose.yml       # Configuração Docker
├── php-config.ini          # Configurações PHP personalizadas
├── database-backup.sql     # Backup da BD (78MB)
├── import-db.sh           # Script de importação (opcional)
└── backup/wp/             # Ficheiros WordPress
    ├── wp-config.php      # Configuração WP (ajustado para local)
    ├── wp-config.php.backup # Backup da config original
    ├── wp-content/
    │   ├── plugins/       # 30+ plugins
    │   ├── themes/        # theretailer + theretailer-child
    │   └── uploads/       # 381MB de media
    └── ...
```

### 🔧 Resolução de Problemas

**Site não carrega?**
```bash
# Verificar se containers estão a correr
docker-compose ps

# Reiniciar containers
docker-compose restart

# Ver logs de erros
docker logs chapeus_wordpress --tail 50
```

**Erro de ligação à BD?**
```bash
# Verificar se MySQL está a responder
docker exec chapeus_mysql mysql -u root -prootpassword -e "SELECT 1;"

# Ver logs do MySQL
docker logs chapeus_mysql --tail 50
```

**Imagens não aparecem?**
- As imagens estão em `/wp-content/uploads/` (381MB)
- Podem ter URLs antigos do site de produção
- Considere usar plugin "Better Search Replace" para atualizar URLs

### 🚀 Próximos Passos Recomendados

1. ✅ Testar login no wp-admin
2. ✅ Verificar produtos WooCommerce
3. ✅ Testar funcionalidades principais
4. ⚠️ Atualizar WordPress e plugins (cuidado com compatibilidade!)
5. ⚠️ Verificar e corrigir plugins com deprecated functions
6. 📦 Fazer backup regular dos dados
7. 🔒 Quando voltar online, atualizar credenciais de segurança

### 📌 Notas Importantes

- **NUNCA** comitar ficheiros com credenciais para repositórios públicos
- O ambiente local usa emulação x86_64 no Mac Apple Silicon (pode ser mais lento)

### 🔄 Sincronização de Catálogo via Google Sheets

1. Gere a exportação base com `scripts/export_master_catalog.py` (cria `output_catalogo/catalogo_master.csv`).
2. Importe o CSV para uma folha Google (ex.: aba "Catalogo") e partilhe com a Service Account.
3. Crie a Service Account no Google Cloud, guarde o JSON em `config/google-service-account.json` (fora do git) e defina:
   ```bash
   export GOOGLE_SHEETS_ID="<ID do documento>"
   export GOOGLE_SERVICE_ACCOUNT_FILE="config/google-service-account.json"
   export GOOGLE_SHEETS_TAB="Catalogo"
   ```
4. Instale `pip install gspread google-auth` e execute `python scripts/sync_google_sheet.py` para sincronizar as alterações do sheet para `output_catalogo/catalogo.json`.
5. Corra `scripts/generate_wc_catalog.py` para gerar o CSV de importação WooCommerce atualizado e carregue-o no WordPress.
6. (Opcional) `scripts/export_catalog_summary.py` gera resumos (`catalogo_summary_sheet*.csv`) úteis para validar quantidades por coleção/tipo e importar como abas de referência no Google Sheets.

> As colunas obrigatórias do sheet são: `Sheet`, `SKU`, `Nome`, `Preço`. Campos opcionais como `Prioridade` e `Destaque homepage?` são mapeados automaticamente na importação.
- A versão do WordPress é antiga (2020) - considere atualizar com cuidado
- Alguns plugins premium podem precisar de reativação de licença
- O site original era https://www.chapeuslisboetas.com/wp

---

**Data de Configuração:** 30 Setembro 2025
**Configurado por:** Droid (Factory AI)
