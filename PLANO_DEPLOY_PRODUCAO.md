# Plano de Deploy para Produção
## Chapéus Lisboetas - WordPress E-commerce

---

## 📋 Índice

1. [Resumo Executivo](#resumo-executivo)
2. [Pré-Requisitos](#pré-requisitos)
3. [Fase 1: Preparação Local](#fase-1-preparação-local)
4. [Fase 2: Setup Alojamento PTisp](#fase-2-setup-alojamento-ptisp)
5. [Fase 3: Migração de Base de Dados](#fase-3-migração-de-base-de-dados)
6. [Fase 4: Migração de Ficheiros](#fase-4-migração-de-ficheiros)
7. [Fase 5: Configuração DNS e SSL](#fase-5-configuração-dns-e-ssl)
8. [Fase 6: Testes e Validação](#fase-6-testes-e-validação)
9. [Fase 7: Go-Live](#fase-7-go-live)
10. [Plano de Rollback](#plano-de-rollback)
11. [Checklist Final](#checklist-final)

---

## Resumo Executivo

**Objetivo:** Migrar site WordPress Chapéus Lisboetas de ambiente local (Docker) para produção online.

**Timeline Estimada:** 3-5 dias (dependendo de aprovação DNS)

**Fases:**
1. ✅ Desenvolvimento Local (COMPLETO)
2. 🔄 Preparação para Deploy (1 dia)
3. 🔄 Compra e Setup Alojamento (1 dia)
4. 🔄 Migração (1-2 dias)
5. 🔄 Testes e Ajustes (1 dia)
6. 🚀 Go-Live (algumas horas)

**Downtime Esperado:** Zero (novo site, não há site antigo para substituir)

---

## Pré-Requisitos

### Decisões de Negócio Necessárias

- [ ] **Domínio definitivo:** chapeuslisboetas.pt ou chapeuslisboeta.pt?
  - Verificar disponibilidade em https://www.dns.pt
  - Custo: ~€10/ano (.pt) ou ~€15/ano (.com)
  - Recomendação: `.pt` para credibilidade local

- [ ] **Email do domínio:** mail@chapeuslisboetas.pt
  - Incluído no PTisp Premium? Verificar
  - Alternativa: Google Workspace (€6/mês) ou Zoho Mail (€1/mês)

- [ ] **Data de Go-Live target:**
  - Antes Black Friday? (29 Novembro 2025)
  - Antes Natal? (Dezembro 2025)
  - Recomendação: 2 semanas antes de evento comercial importante

### Ferramentas Necessárias

**Instaladas Localmente:**
- [x] Docker Desktop (para backup final)
- [x] MySQL Workbench ou DBeaver (gestão BD)
- [ ] FileZilla ou Cyberduck (FTP/SFTP)
- [ ] WP-CLI (opcional, facilita migração)

**Online:**
- [ ] Acesso cPanel PTisp
- [ ] Acesso Cloudflare (DNS management)
- [ ] Google Search Console account
- [ ] Google Analytics 4 account

### Credenciais a Preparar

```
LOCALHOST (origem):
- Database: lisboetas_web
- User: lisboetas
- Password: e$4rU9h8
- WP Admin: [verificar em wp_users]

PRODUÇÃO (destino):
- Database: [a criar no PTisp]
- User: [a criar no PTisp]
- Password: [a criar no PTisp]
- WP Admin: [manter do localhost]

FTP/SFTP:
- Host: [fornecido por PTisp]
- User: [fornecido por PTisp]
- Password: [definir no cPanel]
```

---

## Fase 1: Preparação Local

### 1.1 Backup Completo do Localhost

**Database Backup:**
```bash
# Entrar na pasta do projeto
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

# Criar pasta de backups
mkdir -p backups/pre-deploy-$(date +%Y%m%d)

# Backup completo da base de dados
docker exec chapeus_mysql mysqldump -u root -prootpassword \
  --single-transaction \
  --routines \
  --triggers \
  --events \
  lisboetas_web > backups/pre-deploy-$(date +%Y%m%d)/database.sql

# Verificar tamanho do backup
ls -lh backups/pre-deploy-$(date +%Y%m%d)/database.sql
```

**Ficheiros Backup:**
```bash
# Backup do wp-content (themes, plugins, uploads)
tar -czf backups/pre-deploy-$(date +%Y%m%d)/wp-content.tar.gz \
  wordpress/wp-content/

# Backup específico de uploads (fotos produtos/blog)
tar -czf backups/pre-deploy-$(date +%Y%m%d)/uploads.tar.gz \
  wordpress/wp-content/uploads/

# Backup do tema child (customizações)
tar -czf backups/pre-deploy-$(date +%Y%m%d)/flatsome-child.tar.gz \
  wordpress/wp-content/themes/flatsome-child/

# Verificar backups criados
ls -lh backups/pre-deploy-$(date +%Y%m%d)/
```

**Expected Output:**
```
database.sql          ~15-20 MB
wp-content.tar.gz     ~400-450 MB
uploads.tar.gz        ~380-400 MB
flatsome-child.tar.gz ~1-2 MB
```

### 1.2 Limpeza de Base de Dados

**Remover dados de desenvolvimento/teste:**
```sql
-- Conectar ao MySQL
docker exec -it chapeus_mysql mysql -u root -prootpassword lisboetas_web

-- Limpar transients (cache temporário)
DELETE FROM wp_options WHERE option_name LIKE '_transient_%';
DELETE FROM wp_options WHERE option_name LIKE '_site_transient_%';

-- Limpar spam e comentários não aprovados (se houver)
DELETE FROM wp_comments WHERE comment_approved = 'spam';
DELETE FROM wp_comments WHERE comment_approved = '0' AND comment_type = '';

-- Limpar revisões de posts (manter só última versão)
DELETE FROM wp_posts WHERE post_type = 'revision';

-- Limpar auto-drafts
DELETE FROM wp_posts WHERE post_status = 'auto-draft';

-- Otimizar tabelas
OPTIMIZE TABLE wp_posts, wp_postmeta, wp_options, wp_comments, wp_commentmeta;

-- Sair
EXIT;
```

**Novo backup após limpeza:**
```bash
docker exec chapeus_mysql mysqldump -u root -prootpassword \
  --single-transaction \
  lisboetas_web > backups/pre-deploy-$(date +%Y%m%d)/database-clean.sql
```

### 1.3 Verificar URLs Hardcoded

**Search & Replace URLs:**
```bash
# Procurar referências a localhost no database backup
grep -i "localhost:8080" backups/pre-deploy-*/database-clean.sql | head -n 20

# Contar ocorrências
grep -c "localhost:8080" backups/pre-deploy-*/database-clean.sql
```

**Preparar Search-Replace (executar APÓS definir domínio final):**
```sql
-- Não executar agora, só após deploy!
-- Substituir localhost:8080 por domínio real

UPDATE wp_options
SET option_value = REPLACE(option_value, 'http://localhost:8080', 'https://chapeuslisboetas.pt')
WHERE option_value LIKE '%localhost:8080%';

UPDATE wp_posts
SET post_content = REPLACE(post_content, 'http://localhost:8080', 'https://chapeuslisboetas.pt')
WHERE post_content LIKE '%localhost:8080%';

UPDATE wp_postmeta
SET meta_value = REPLACE(meta_value, 'http://localhost:8080', 'https://chapeuslisboetas.pt')
WHERE meta_value LIKE '%localhost:8080%';

-- Atualizar URLs principais
UPDATE wp_options SET option_value = 'https://chapeuslisboetas.pt'
WHERE option_name IN ('siteurl', 'home');
```

### 1.4 Validar Plugins e Temas

**Verificar compatibilidade PHP 7.4+ (versão PTisp):**
```bash
# Listar plugins ativos
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web \
  -e "SELECT option_value FROM wp_options WHERE option_name = 'active_plugins';"

# Verificar versão WordPress
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web \
  -e "SELECT option_value FROM wp_options WHERE option_name = 'db_version';"
```

**Plugins Críticos a Verificar:**
- WooCommerce (versão atualizada?)
- IfthenPay Gateway
- Flatsome Theme (licença válida?)
- WPML/Transposh (se multilíngue)
- WP Rocket (licença válida?)
- UpdraftPlus (configurar backups automáticos)

### 1.5 Criar wp-config.php para Produção

**Backup do wp-config.php local:**
```bash
cp wordpress/wp-config.php wordpress/wp-config-local-backup.php
```

**Preparar wp-config.php template para produção:**
```php
<?php
/**
 * wp-config.php para PRODUÇÃO
 * Chapéus Lisboetas - PTisp Hosting
 */

// ** Database settings - ATUALIZAR COM DADOS PTISP ** //
define( 'DB_NAME', 'chapeuslisboetas_db' );
define( 'DB_USER', 'chapeuslisboetas_user' );
define( 'DB_PASSWORD', 'SENHA_SEGURA_AQUI' );
define( 'DB_HOST', 'localhost' ); // PTisp usa localhost
define( 'DB_CHARSET', 'utf8mb4' );
define( 'DB_COLLATE', '' );

// ** Security Keys - GERAR NOVOS EM https://api.wordpress.org/secret-key/1.1/salt/ ** //
define('AUTH_KEY',         'SUBSTITUIR_POR_CHAVE_GERADA');
define('SECURE_AUTH_KEY',  'SUBSTITUIR_POR_CHAVE_GERADA');
define('LOGGED_IN_KEY',    'SUBSTITUIR_POR_CHAVE_GERADA');
define('NONCE_KEY',        'SUBSTITUIR_POR_CHAVE_GERADA');
define('AUTH_SALT',        'SUBSTITUIR_POR_CHAVE_GERADA');
define('SECURE_AUTH_SALT', 'SUBSTITUIR_POR_CHAVE_GERADA');
define('LOGGED_IN_SALT',   'SUBSTITUIR_POR_CHAVE_GERADA');
define('NONCE_SALT',       'SUBSTITUIR_POR_CHAVE_GERADA');

// ** WordPress table prefix ** //
$table_prefix = 'wp_'; // Manter wp_ (não lx_)

// ** SSL / HTTPS ** //
define('FORCE_SSL_ADMIN', true);
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] = 'on';
}

// ** WordPress URLs - ATUALIZAR COM DOMÍNIO FINAL ** //
define('WP_HOME', 'https://chapeuslisboetas.pt');
define('WP_SITEURL', 'https://chapeuslisboetas.pt');

// ** Debug (DESATIVAR EM PRODUÇÃO) ** //
define('WP_DEBUG', false);
define('WP_DEBUG_LOG', false);
define('WP_DEBUG_DISPLAY', false);
@ini_set('display_errors', 0);

// ** Performance ** //
define('WP_MEMORY_LIMIT', '256M');
define('WP_MAX_MEMORY_LIMIT', '512M');
define('DISABLE_WP_CRON', false); // PTisp suporta cron

// ** File Permissions ** //
define('FS_METHOD', 'direct');
define('FS_CHMOD_DIR', (0755 & ~umask()));
define('FS_CHMOD_FILE', (0644 & ~umask()));

// ** Automatic Updates ** //
define('AUTOMATIC_UPDATER_DISABLED', false);
define('WP_AUTO_UPDATE_CORE', 'minor'); // Só security updates automáticos

// ** Backups - UpdraftPlus ** //
define('UPDRAFTPLUS_NOGARBAGE', true);

/* That's all, stop editing! Happy publishing. */
if ( ! defined( 'ABSPATH' ) ) {
    define( 'ABSPATH', __DIR__ . '/' );
}
require_once ABSPATH . 'wp-settings.php';
```

---

## Fase 2: Setup Alojamento PTisp

### 2.1 Compra do Alojamento

**Plano Recomendado:** PTisp Premium (já mencionado no CLAUDE.md)

**Especificações:**
- NVMe: 40GB a 3,500 MB/s
- RAM: 3GB dedicada
- Datacenter: Lisboa (3ms latency)
- Backups: Daily JetBackup (30 dias)
- SSL: Let's Encrypt incluído
- Email: Contas ilimitadas
- Suporte: 24/7 telefone

**Custo:** ~€120-150/ano (1 ano incluído no orçamento projeto)

**Link:** https://www.ptisp.pt/alojamento-web

### 2.2 Compra do Domínio

**Opções:**

**Opção A: Registar .pt na DNS.pt**
- Custo: €10/ano
- Link: https://www.dns.pt
- Vantagem: Domínio português, credibilidade local
- Prazo: 24-48h para aprovação

**Opção B: Registar .com na PTisp/GoDaddy**
- Custo: €15/ano
- Link: Incluído no cPanel PTisp
- Vantagem: Instantâneo, gestão centralizada
- Prazo: Imediato

**Domínios a verificar:**
1. `chapeuslisboetas.pt` (preferencial)
2. `chapeuslisboeta.pt` (singular, alternativa)
3. `chapeuslisboetas.com` (backup internacional)

**Recomendação:** Comprar `.pt` + `.com` e redirecionar `.com` → `.pt`

### 2.3 Configuração Inicial cPanel

**Após receber email de ativação PTisp:**

1. **Aceder cPanel:**
   - URL: https://cpanel.ptisp.pt
   - User: [fornecido por email]
   - Password: [definida no registo]

2. **Criar Base de Dados MySQL:**
   ```
   cPanel → MySQL Databases → Create New Database

   Database Name: chapeuslisboetas_db
   Database User: chapeuslisboetas_user
   Password: [GERAR SENHA FORTE - 20+ caracteres]

   Assign User to Database:
   Privileges: ALL PRIVILEGES ✓
   ```

3. **Anotar Credenciais:**
   ```
   Database Name: chapeuslisboetas_db (ou [prefix]_chapeuslisboetas_db)
   Database User: [prefix]_chapeuslisboetas_user
   Database Password: [senha gerada]
   Database Host: localhost
   ```

4. **Criar Conta FTP/SFTP:**
   ```
   cPanel → FTP Accounts → Add FTP Account

   Login: deploy
   Password: [SENHA FORTE]
   Directory: /public_html
   Quota: Unlimited
   ```

5. **Ativar SSL (Let's Encrypt):**
   ```
   cPanel → SSL/TLS Status
   → Selecionar domínio
   → Run AutoSSL

   Aguardar 2-5 minutos para certificado
   ```

6. **Configurar PHP:**
   ```
   cPanel → Select PHP Version

   PHP Version: 7.4 ou 8.0 (testar compatibilidade)
   Extensions (ativar):
   ✓ mysqli
   ✓ gd
   ✓ curl
   ✓ zip
   ✓ mbstring
   ✓ xml
   ✓ opcache

   Settings:
   memory_limit: 256M
   max_execution_time: 300
   post_max_size: 64M
   upload_max_filesize: 64M
   ```

---

## Fase 3: Migração de Base de Dados

### 3.1 Preparar SQL para Importação

**Editar database-clean.sql:**
```bash
cd backups/pre-deploy-*/

# Criar versão editada
cp database-clean.sql database-production.sql

# Search & Replace para domínio produção
# SUBSTITUIR chapeuslisboetas.pt pelo domínio REAL escolhido
sed -i '' 's|http://localhost:8080|https://chapeuslisboetas.pt|g' database-production.sql
sed -i '' 's|localhost:8080|chapeuslisboetas.pt|g' database-production.sql

# Verificar substituições
grep -c "localhost" database-production.sql  # Deve ser 0
grep -c "chapeuslisboetas.pt" database-production.sql  # Deve ser >100
```

### 3.2 Importar para PTisp

**Método A: phpMyAdmin (se BD < 50MB)**
```
1. Aceder cPanel → phpMyAdmin
2. Selecionar database: chapeuslisboetas_db
3. Tab "Import"
4. Choose File: database-production.sql
5. Format: SQL
6. Encoding: utf-8
7. Click "Go"
8. Aguardar (pode demorar 5-10 min)
```

**Método B: SSH/Command Line (se BD > 50MB - PREFERENCIAL)**
```bash
# Conectar via SSH (se PTisp fornece acesso SSH)
ssh deploy@chapeuslisboetas.pt

# Ou via FTP, fazer upload do database-production.sql para pasta temporária
# Depois executar via cPanel → Terminal

# Importar
mysql -u chapeuslisboetas_user -p chapeuslisboetas_db < database-production.sql

# Verificar importação
mysql -u chapeuslisboetas_user -p chapeuslisboetas_db -e "SHOW TABLES;"
mysql -u chapeuslisboetas_user -p chapeuslisboetas_db -e "SELECT COUNT(*) FROM wp_posts;"
```

**Expected Output:**
```sql
Tables_in_chapeuslisboetas_db
------------------------------
wp_commentmeta
wp_comments
wp_links
wp_options
wp_postmeta
wp_posts
wp_term_relationships
wp_term_taxonomy
wp_terms
wp_usermeta
wp_users
[...WooCommerce tables...]

COUNT(*): ~150-200 posts (produtos + blog posts)
```

### 3.3 Atualizar URLs na Produção

**Executar via phpMyAdmin ou SSH:**
```sql
USE chapeuslisboetas_db;

-- Verificar URLs atuais
SELECT option_value FROM wp_options WHERE option_name IN ('siteurl', 'home');

-- Atualizar URLs principais
UPDATE wp_options SET option_value = 'https://chapeuslisboetas.pt'
WHERE option_name IN ('siteurl', 'home');

-- Verificar se há URLs antigos restantes
SELECT COUNT(*) FROM wp_posts WHERE post_content LIKE '%localhost%';
SELECT COUNT(*) FROM wp_postmeta WHERE meta_value LIKE '%localhost%';

-- Se encontrar, executar replace global (já feito no sed, mas double-check)
UPDATE wp_posts
SET post_content = REPLACE(post_content, 'http://localhost:8080', 'https://chapeuslisboetas.pt');

UPDATE wp_postmeta
SET meta_value = REPLACE(meta_value, 'http://localhost:8080', 'https://chapeuslisboetas.pt');
```

---

## Fase 4: Migração de Ficheiros

### 4.1 Preparar Ficheiros WordPress

**Estrutura a migrar:**
```
wordpress/
├── wp-admin/ (core WP - pode re-download)
├── wp-includes/ (core WP - pode re-download)
├── wp-content/
│   ├── themes/
│   │   ├── flatsome/
│   │   └── flatsome-child/ ← CRÍTICO (customizações)
│   ├── plugins/ ← CRÍTICO (WooCommerce, IfthenPay, etc)
│   └── uploads/ ← CRÍTICO (381MB de imagens produtos/blog)
├── wp-config.php ← Criar novo (preparado na Fase 1.5)
└── index.php (core WP)
```

**Opção A: Upload via FTP (SIMPLES, LENTO)**
```bash
# Instalar FileZilla: https://filezilla-project.org

# Conectar:
Host: ftp.chapeuslisboetas.pt (ou SFTP: sftp.chapeuslisboetas.pt)
Username: deploy (criado na Fase 2.3)
Password: [senha FTP]
Port: 21 (FTP) ou 22 (SFTP - preferencial)

# Upload:
Local: /Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress/
Remote: /public_html/

# Arrastar pastas:
1. wp-content/themes/flatsome-child/ → /public_html/wp-content/themes/
2. wp-content/plugins/ → /public_html/wp-content/plugins/
3. wp-content/uploads/ → /public_html/wp-content/uploads/ (DEMORADO: 381MB)

Tempo estimado: 2-4 horas (depende de velocidade upload)
```

**Opção B: Compressão + Upload + Extração (RÁPIDO, RECOMENDADO)**
```bash
# 1. LOCALHOST: Comprimir ficheiros
cd wordpress/

# Comprimir só wp-content (core WP baixar depois)
tar -czf wp-content-production.tar.gz wp-content/

# Verificar tamanho
ls -lh wp-content-production.tar.gz  # ~200-250 MB comprimido

# 2. Upload via FTP/SFTP
# FileZilla ou comando scp:
scp wp-content-production.tar.gz deploy@chapeuslisboetas.pt:/home/deploy/

# 3. SERVIDOR: Extrair
ssh deploy@chapeuslisboetas.pt
cd /home/deploy/public_html/
tar -xzf ../wp-content-production.tar.gz
rm ../wp-content-production.tar.gz

# Ajustar permissões
chown -R deploy:deploy wp-content/
find wp-content/ -type d -exec chmod 755 {} \;
find wp-content/ -type f -exec chmod 644 {} \;
chmod 640 wp-config.php

Tempo estimado: 30-60 minutos
```

**Opção C: WordPress Core Fresh Install (RECOMENDADO PARA PRODUÇÃO)**
```bash
# 1. Download WordPress PT no servidor
ssh deploy@chapeuslisboetas.pt
cd /home/deploy/public_html/
wget https://pt.wordpress.org/latest-pt_PT.tar.gz
tar -xzf latest-pt_PT.tar.gz --strip-components=1
rm latest-pt_PT.tar.gz

# 2. Upload só customizações via FTP
# - wp-content/themes/flatsome-child/
# - wp-content/plugins/ (se plugins personalizados)
# - wp-content/uploads/

# 3. Upload wp-config.php preparado (Fase 1.5)

# 4. Re-instalar plugins comerciais:
# - Flatsome Theme (upload .zip via Appearence → Themes)
# - WooCommerce (pode instalar direto do WordPress.org)
# - IfthenPay (upload .zip se não estiver no repo)
```

### 4.2 Upload wp-config.php

**CRÍTICO: Usar versão PRODUÇÃO preparada**
```bash
# Editar wp-config.php com dados PTisp reais
nano wp-config-production.php

# Verificar:
# 1. DB_NAME, DB_USER, DB_PASSWORD (Fase 2.3)
# 2. Security Keys (gerar em https://api.wordpress.org/secret-key/1.1/salt/)
# 3. WP_HOME e WP_SITEURL (https://chapeuslisboetas.pt)
# 4. WP_DEBUG = false

# Upload via FTP para /public_html/wp-config.php
# Ou via SSH:
scp wp-config-production.php deploy@chapeuslisboetas.pt:/home/deploy/public_html/wp-config.php

# Ajustar permissões (SEGURANÇA)
ssh deploy@chapeuslisboetas.pt
chmod 640 /home/deploy/public_html/wp-config.php
```

### 4.3 Verificar Estrutura

**SSH no servidor:**
```bash
ssh deploy@chapeuslisboetas.pt
cd /home/deploy/public_html/

# Verificar estrutura
ls -la

# Expected output:
# drwxr-xr-x  wp-admin/
# drwxr-xr-x  wp-content/
# drwxr-xr-x  wp-includes/
# -rw-r--r--  index.php
# -rw-r-----  wp-config.php
# -rw-r--r--  wp-activate.php
# [...]

# Verificar uploads
ls -lh wp-content/uploads/2025/10/
# Deve mostrar pastas blog/, produtos/, etc.

# Verificar tema child
ls -la wp-content/themes/flatsome-child/
# Deve mostrar style.css, functions.php, assets/
```

---

## Fase 5: Configuração DNS e SSL

### 5.1 Apontar Domínio para PTisp

**Se domínio registado na DNS.pt:**
```
1. Login: https://online.dns.pt
2. Domínios → chapeuslisboetas.pt → Gerir
3. DNS Records:

A Record:
Name: @
Type: A
Value: [IP do servidor PTisp - fornecido no email ativação]
TTL: 3600

A Record:
Name: www
Type: A
Value: [mesmo IP]
TTL: 3600

CNAME (opcional, para subdomínios):
Name: blog
Type: CNAME
Value: chapeuslisboetas.pt
TTL: 3600

MX Records (email - se usar PTisp):
Priority: 10
Value: mail.chapeuslisboetas.pt
TTL: 3600

4. Guardar alterações
5. Aguardar propagação: 2-48h (geralmente <6h)
```

**Se domínio registado no PTisp:**
```
cPanel → Zone Editor → Manage
(DNS já está automaticamente configurado)
```

**Verificar Propagação DNS:**
```bash
# Mac/Linux terminal
nslookup chapeuslisboetas.pt
dig chapeuslisboetas.pt

# Online:
https://www.whatsmydns.net/#A/chapeuslisboetas.pt
```

### 5.2 Configurar SSL (HTTPS)

**Método A: Let's Encrypt via cPanel (AUTOMÁTICO)**
```
cPanel → SSL/TLS Status
→ Domain: chapeuslisboetas.pt
→ Run AutoSSL
→ Aguardar 2-5 minutos

Status esperado:
✓ SSL certificate successfully installed
Valid until: [90 dias depois]
Auto-renew: Enabled
```

**Método B: Cloudflare SSL (RECOMENDADO - GRÁTIS + CDN)**
```
1. Criar conta: https://dash.cloudflare.com/sign-up

2. Add Site → chapeuslisboetas.pt

3. Cloudflare vai detectar DNS records automaticamente
   → Confirmar/ajustar

4. Cloudflare fornece 2 nameservers:
   Example:
   ns1.cloudflare.com
   ns2.cloudflare.com

5. Voltar a DNS.pt → Alterar nameservers para os da Cloudflare

6. Aguardar ativação (1-24h)

7. Cloudflare Dashboard → SSL/TLS:
   Encryption mode: Full (strict)
   Always Use HTTPS: ON
   Automatic HTTPS Rewrites: ON
   Minimum TLS Version: 1.2

8. Cloudflare Dashboard → Speed:
   Auto Minify: CSS + JS + HTML
   Brotli: ON
   Rocket Loader: OFF (pode quebrar WooCommerce)

9. Cloudflare Dashboard → Caching:
   Caching Level: Standard
   Browser Cache TTL: 4 hours

Vantagens Cloudflare:
- SSL grátis
- CDN global (site mais rápido)
- Proteção DDoS
- Analytics
- Minificação automática
```

### 5.3 Forçar HTTPS

**Adicionar a wp-config.php (já incluído em Fase 1.5):**
```php
define('FORCE_SSL_ADMIN', true);
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] = 'on';
}
```

**Adicionar .htaccess redirect:**
```bash
# SSH ou FTP editar: /public_html/.htaccess
nano /home/deploy/public_html/.htaccess
```

**Conteúdo .htaccess:**
```apache
# BEGIN WordPress
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteBase /

# Force HTTPS
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Force WWW (opcional - decidir se www.chapeuslisboetas.pt ou só chapeuslisboetas.pt)
# RewriteCond %{HTTP_HOST} !^www\. [NC]
# RewriteRule ^(.*)$ https://www.%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# WordPress rules
RewriteRule ^index\.php$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.php [L]
</IfModule>
# END WordPress

# Security Headers
<IfModule mod_headers.c>
Header set X-Content-Type-Options "nosniff"
Header set X-Frame-Options "SAMEORIGIN"
Header set X-XSS-Protection "1; mode=block"
Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>

# Disable directory browsing
Options -Indexes

# Protect wp-config.php
<files wp-config.php>
order allow,deny
deny from all
</files>
```

---

## Fase 6: Testes e Validação

### 6.1 Checklist de Testes Funcionais

**Homepage:**
- [ ] Carrega sem erros (HTTP 200)
- [ ] SSL ativo (cadeado verde)
- [ ] Header ticker/marquee animado funciona
- [ ] Imagens Instagram visíveis
- [ ] Menu navegação funciona
- [ ] Footer completo

**Blog:**
- [ ] Lista de posts visível: https://chapeuslisboetas.pt/blog/
- [ ] 15 posts visíveis (5 originais + 10 novos)
- [ ] Hero images aparecem em todos
- [ ] Categorias no sidebar
- [ ] Click em post abre corretamente
- [ ] Imagens carregam
- [ ] CTAs funcionam

**Loja (WooCommerce):**
- [ ] Produtos aparecem: https://chapeuslisboetas.pt/loja/
- [ ] Imagens produtos carregam
- [ ] Filtros funcionam (categoria, preço)
- [ ] Página produto individual abre
- [ ] Adicionar ao carrinho funciona
- [ ] Carrinho atualiza
- [ ] Checkout carrega

**Pagamentos:**
- [ ] IfthenPay aparece no checkout
- [ ] MB Way disponível
- [ ] Multibanco disponível
- [ ] Teste de compra (€1 produto teste)

**Performance:**
- [ ] Google PageSpeed: https://pagespeed.web.dev/
  - Target: >85 mobile, >90 desktop
- [ ] GTmetrix: https://gtmetrix.com/
  - Target: Grade A, <3s load time
- [ ] WebPageTest: https://www.webpagetest.org/

**SEO:**
- [ ] Google Search Console: https://search.google.com/search-console
  - Submeter sitemap: https://chapeuslisboetas.pt/sitemap_index.xml
- [ ] Meta descriptions presentes (view source)
- [ ] Schema.org markup (Yoast)
- [ ] robots.txt: https://chapeuslisboetas.pt/robots.txt
- [ ] XML sitemap acessível

### 6.2 Testes de Email

**Criar conta teste:**
```
WP Admin → Users → Add New
Username: teste-cliente
Email: [email pessoal para teste]
Role: Customer

Complete registration via email
```

**Testar emails transacionais:**
- [ ] Registo de cliente (welcome email)
- [ ] Password reset
- [ ] Confirmação de encomenda (ordem de teste)
- [ ] Emails vêm de mail@chapeuslisboetas.pt (não noreply@ptisp.pt)

**Se emails não funcionam:**
```
Instalar plugin: WP Mail SMTP
Settings:
Mailer: SendGrid (grátis 100 emails/dia) ou Mailgun
Configure API keys
Test email
```

### 6.3 Testes Cross-Browser

**Desktop:**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

**Mobile:**
- [ ] iPhone Safari
- [ ] Android Chrome
- [ ] iPad

**Ferramentas online:**
- BrowserStack: https://www.browserstack.com (trial grátis)
- LambdaTest: https://www.lambdatest.com

### 6.4 Teste de Carga (Load Testing)

**Simular tráfego Black Friday:**
```bash
# Instalar Apache Bench (Mac já tem)
ab -n 1000 -c 10 https://chapeuslisboetas.pt/

# -n 1000: 1000 requests total
# -c 10: 10 concurrent users

# Expected output:
# Requests per second: >50
# Time per request: <200ms
# Failed requests: 0
```

**Se performance baixa:**
- Ativar WP Rocket
- Ativar Cloudflare
- Otimizar database
- Lazy loading imagens

---

## Fase 7: Go-Live

### 7.1 Pre-Launch Checklist

**24h Antes:**
- [ ] Backup completo localhost (já feito Fase 1)
- [ ] Backup completo servidor produção
  ```bash
  cPanel → JetBackup → Create Backup
  ```
- [ ] Testar backups (download + verificar integridade)
- [ ] Documentar todas credenciais
- [ ] Avisar cliente da janela de deploy

**2h Antes:**
- [ ] WP Admin → Settings → Reading: "Desencorajar motores de busca" = OFF
- [ ] WP Admin → Settings → Permalinks: Post name (re-save para flush rewrite rules)
- [ ] Verificar WooCommerce → Status: Tudo verde
- [ ] Limpar cache (WP Rocket + Cloudflare)
- [ ] Modo manutenção OFF

**Go-Live:**
```bash
# 1. Verificar DNS propagado
nslookup chapeuslisboetas.pt

# 2. Aceder site
https://chapeuslisboetas.pt

# 3. Teste completo (usar checklist Fase 6)

# 4. Se tudo OK: Anunciar!
```

### 7.2 Anúncio Go-Live

**Instagram Post:**
```
[Foto: Loja/Chapéus]

🎉 GRANDE NOVIDADE! 🎉

A Chapéus Lisboetas está agora online!

Depois de 75 anos a servir Lisboa na Praça da Figueira,
levamos a nossa tradição artesanal para o digital.

🛍️ Compre online: chapeuslisboetas.pt
📍 Visite-nos: Praça da Figueira, Lisboa
📞 WhatsApp: +351 918 911 308

Envios GRÁTIS acima de €50 em Portugal 🇵🇹

#ChapeusLisboetas #ChapelariaTradição #MadeInPortugal #Artesanato
```

**Email Newsletter (se já têm lista):**
```
Subject: 🎩 A Chapéus Lisboetas está online!

[Email com link para site, promoção de lançamento opcional]
```

### 7.3 Monitoring Pós-Launch

**Primeiras 48h - Monitorizar:**

1. **Google Analytics:**
   - Real-time visitors
   - Bounce rate
   - Traffic sources
   - Conversions

2. **Google Search Console:**
   - Coverage errors
   - Mobile usability
   - Core Web Vitals

3. **Server Logs (cPanel):**
   - Error log: Verificar erros PHP
   - Access log: Tráfego incomum

4. **Uptime Monitoring:**
   - UptimeRobot: https://uptimerobot.com (grátis)
     - Monitor a cada 5 minutos
     - Alertas via email/SMS se down

5. **WooCommerce:**
   - Encomendas a processar corretamente
   - Emails transacionais a enviar
   - Pagamentos IfthenPay a funcionar

**Primeira Semana:**
- Análise diária Google Analytics
- Ajustes SEO conforme Search Console
- Otimizações performance conforme dados reais
- Responder feedback clientes

---

## Plano de Rollback

**Se algo correr mal durante deploy:**

### Cenário 1: Site não carrega (erro 500/database connection)

**Diagnóstico:**
```bash
# Verificar wp-config.php credentials
ssh deploy@chapeuslisboetas.pt
cat /home/deploy/public_html/wp-config.php | grep DB_

# Verificar database existe
mysql -u chapeuslisboetas_user -p -e "SHOW DATABASES;"

# Verificar error log
tail -f /home/deploy/logs/error_log
```

**Solução:**
1. Corrigir credenciais wp-config.php
2. Re-importar database se corrupto
3. Restaurar backup JetBackup

### Cenário 2: Imagens não carregam (404)

**Diagnóstico:**
```bash
# Verificar uploads existem
ls -lh /home/deploy/public_html/wp-content/uploads/

# Verificar permissões
find wp-content/uploads/ -type f -exec stat -c "%a %n" {} \; | grep -v "644"
```

**Solução:**
```bash
# Ajustar permissões
find wp-content/uploads/ -type d -exec chmod 755 {} \;
find wp-content/uploads/ -type f -exec chmod 644 {} \;

# Re-upload uploads/ via FTP se necessário
```

### Cenário 3: Checkout não funciona (IfthenPay)

**Diagnóstico:**
```
WP Admin → WooCommerce → Status → Logs
Procurar erros IfthenPay
```

**Solução:**
1. Verificar API keys IfthenPay (produção ≠ localhost)
2. Contactar suporte IfthenPay
3. Ativar gateway alternativo temporário (transferência bancária)

### Cenário 4: Performance horrível (>10s load time)

**Diagnóstico:**
```bash
# Query Monitor plugin
WP Admin → Plugins → Add New → Query Monitor

# Verificar:
- Queries lentas (>1s)
- Plugins pesados
- HTTP requests externos
```

**Solução Rápida:**
1. Ativar WP Rocket
2. Ativar Cloudflare CDN
3. Desativar plugins não essenciais
4. Otimizar imagens (Imagify plugin)

### Rollback Completo (último recurso)

**Se deploy é desastre total:**
```bash
# 1. Restaurar backup JetBackup
cPanel → JetBackup → Restore → [escolher backup pre-deploy]

# 2. Ou restaurar manual:
# Database:
mysql -u chapeuslisboetas_user -p chapeuslisboetas_db < backup-localhost/database.sql

# Files:
rm -rf /home/deploy/public_html/wp-content/
tar -xzf backup-localhost/wp-content.tar.gz -C /home/deploy/public_html/

# 3. Apontar domínio de volta para manutenção
# Criar página: /public_html/index.html
echo "Site em manutenção. Voltamos em breve!" > /home/deploy/public_html/index.html
mv /home/deploy/public_html/index.php /home/deploy/public_html/index.php.bak

# 4. Investigar problema offline
# 5. Re-deploy quando corrigido
```

---

## Checklist Final

### Pre-Deploy
- [ ] Backup completo localhost (database + files)
- [ ] Database limpa (sem transients, revisões)
- [ ] URLs localhost substituídos por produção
- [ ] Plugins atualizados e compatíveis
- [ ] wp-config.php produção preparado
- [ ] Compra alojamento PTisp confirmada
- [ ] Domínio registado e ativo
- [ ] Credenciais documentadas (password manager)

### Durante Deploy
- [ ] Database criada no PTisp
- [ ] Database importada com sucesso
- [ ] Ficheiros WordPress uploaded
- [ ] wp-content/uploads/ completo (381MB)
- [ ] Tema Flatsome child ativo
- [ ] Plugins críticos ativos (WooCommerce, IfthenPay)
- [ ] wp-config.php com credenciais corretas
- [ ] Permissões ajustadas (755/644)

### DNS & SSL
- [ ] DNS apontado para PTisp
- [ ] Propagação DNS confirmada
- [ ] SSL ativo (Let's Encrypt ou Cloudflare)
- [ ] HTTPS forçado (.htaccess)
- [ ] Redirects www funcionais

### Testes
- [ ] Site carrega sem erros
- [ ] Blog posts visíveis (15 total)
- [ ] Loja/produtos visíveis
- [ ] Checkout funcional
- [ ] IfthenPay ativo
- [ ] Emails transacionais funcionam
- [ ] Performance aceitável (PageSpeed >85)
- [ ] Mobile responsive
- [ ] Cross-browser testado

### SEO & Analytics
- [ ] Google Analytics instalado
- [ ] Google Search Console configurado
- [ ] Sitemap submetido
- [ ] robots.txt correto
- [ ] Meta descriptions presentes
- [ ] Schema markup ativo (Yoast)

### Post-Launch
- [ ] Backup pós-deploy criado
- [ ] Monitoring ativo (UptimeRobot)
- [ ] Cliente treinado (acesso admin)
- [ ] Documentação entregue
- [ ] Suporte 3 meses ativo
- [ ] Anúncio Instagram/newsletter

---

## Contactos de Suporte

**PTisp Hosting:**
- Telefone: 707 500 532 (24/7)
- Email: suporte@ptisp.pt
- Ticket: https://suporte.ptisp.pt

**IfthenPay:**
- Telefone: 707 500 600
- Email: suporte@ifthenpay.com

**Cloudflare:**
- Dashboard: https://dash.cloudflare.com
- Docs: https://developers.cloudflare.com

**WordPress.org:**
- Fórum: https://pt.wordpress.org/support/
- Docs: https://wordpress.org/documentation/

**Emergency Contact (AiParaTi/Bilal):**
- Durante 3 meses pós-launch incluído no projeto
- [Inserir contacto]

---

## Próximos Passos (Fase 2 - Futuro)

**Mês 1 Pós-Launch:**
- Análise dados Analytics
- Otimizações SEO baseadas em Search Console
- A/B testing CTAs
- Primeiras campanhas Instagram Ads (€50-100)

**Meses 2-3:**
- Implementar Reviews (Yotpo/Judge.me)
- Newsletter automatizada (Mailchimp/Klaviyo)
- Upsells/cross-sells WooCommerce
- Retargeting Facebook Pixel

**Mês 4+:**
- AI Chatbot (Tidio - Fase 2 opcional)
- Automated product importer (scraper - Fase 2 opcional)
- Programa fidelização
- Expansão catálogo

---

**Documento preparado:** 27 Outubro 2025
**Versão:** 1.0
**Próxima revisão:** Após compra alojamento PTisp
**Status:** ✅ Pronto para execução

---

## Anexos

### Anexo A: Credenciais Template

```
# COPIAR PARA PASSWORD MANAGER (1Password/Bitwarden)

=== LOCALHOST ===
Database Host: localhost:3306
Database Name: lisboetas_web
Database User: lisboetas
Database Password: e$4rU9h8
WP Admin URL: http://localhost:8080/wp-admin
WP Admin User: [verificar]
WP Admin Pass: [verificar]

=== PRODUÇÃO ===
Domain: https://chapeuslisboetas.pt
Database Host: localhost
Database Name: [preencher após PTisp]
Database User: [preencher após PTisp]
Database Password: [preencher após PTisp]
WP Admin URL: https://chapeuslisboetas.pt/wp-admin
WP Admin User: [mesmo do localhost]
WP Admin Pass: [mesmo do localhost]

FTP/SFTP Host: [preencher após PTisp]
FTP User: deploy
FTP Password: [preencher após criar]

cPanel URL: https://cpanel.ptisp.pt
cPanel User: [preencher após PTisp]
cPanel Pass: [preencher após PTisp]

=== INTEGRAÇÕES ===
IfthenPay Entity: [production entity]
IfthenPay Subentity: [production subentity]
IfthenPay API Key: [production key]

Google Analytics ID: [GA4-XXXXXXXXX]
Google Search Console: [property verified]

Cloudflare Email: [email]
Cloudflare Password: [password]
```

### Anexo B: Comandos Úteis

```bash
# Backup rápido database
docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web | gzip > backup-$(date +%Y%m%d-%H%M).sql.gz

# Verificar tamanho uploads
du -sh wordpress/wp-content/uploads/

# Contar posts
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "SELECT COUNT(*) FROM wp_posts WHERE post_status='publish' AND post_type='post';"

# Contar produtos
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "SELECT COUNT(*) FROM wp_posts WHERE post_status='publish' AND post_type='product';"

# Verificar plugins ativos
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "SELECT option_value FROM wp_options WHERE option_name='active_plugins';"

# Test site speed
curl -o /dev/null -s -w "Time: %{time_total}s\n" https://chapeuslisboetas.pt
```
