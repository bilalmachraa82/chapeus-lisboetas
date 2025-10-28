# Guia de Migração PTisp Premium
## Chapéus Lisboetas - WordPress WooCommerce

---

## 🎯 Objetivo

Migrar o site WordPress da Chapéus Lisboetas do ambiente local (Docker) para o alojamento PTisp Premium em produção, com zero downtime e máxima performance.

---

## 📦 O Que Incluiu no Pacote PTisp Premium

### Especificações Técnicas
- **NVMe Storage:** 40GB @ 3,500 MB/s
- **RAM Dedicada:** 3GB
- **Largura de Banda:** Ilimitada
- **CPU:** Compartilhado (adequado para e-commerce médio)
- **Datacenter:** Lisboa, Portugal (3ms latency local)
- **PHP:** 7.4, 8.0, 8.1 (selecionável)
- **MySQL:** 5.7 ou 8.0
- **Email:** Contas ilimitadas

### Segurança e Backups
- **JetBackup:** Daily automático (30 dias retenção)
- **Imunify360:** Antivírus + Firewall + IDS/IPS
- **SSL Let's Encrypt:** Grátis e automático
- **Anti-DDoS:** 40 Gbps proteção
- **Firewall:** ConfigServer (CSF)
- **ModSecurity:** Web Application Firewall

### Suporte
- **24/7:** Telefone 707 500 532
- **Ticket System:** <15 min primeira resposta
- **Live Chat:** Horário comercial
- **Email:** suporte@ptisp.pt

### Preço
- **€12-15/mês** (€144-180/ano)
- **1º ano incluído** no orçamento projeto (€1,887 Fase 1)
- Renovação: Mesmo preço (sem surpresas)

---

## 🛒 Processo de Compra PTisp

### Passo 1: Escolher Plano

1. Aceder: https://www.ptisp.pt/alojamento-web
2. Escolher: **Premium** (recomendado) ou **Business** (se precisar >40GB)
3. Ciclo de faturação: **Anual** (desconto vs. mensal)
4. Adicionar ao carrinho

### Passo 2: Registar/Transferir Domínio

**Opção A: Registar Novo Domínio via PTisp**
```
Durante checkout:
→ "Registar novo domínio"
→ Inserir: chapeuslisboetas.pt
→ Verificar disponibilidade
→ Se disponível: Adicionar (€10/ano .pt ou €15/ano .com)
→ Se não disponível: Tentar alternativas
```

**Opção B: Já Possui Domínio (Transferir)**
```
→ "Já tenho um domínio"
→ Inserir domínio existente
→ Mais tarde: Iniciar transferência (EPP code necessário)
```

**Opção C: Registar na DNS.pt Separadamente (RECOMENDADO)**
```
Vantagem: Controlo total DNS, preço mais baixo
1. https://online.dns.pt
2. Registo → Particulares ou Empresas
3. Verificar chapeuslisboetas.pt
4. Carrinho → Pagar (€10/ano)
5. Verificação NIF (1-2 dias)
6. Domínio ativo
7. Apontar para PTisp (ver Passo 3)
```

### Passo 3: Configuração Inicial

**Escolher durante checkout:**
- **Sistema Operativo:** CloudLinux (recomendado para WordPress)
- **cPanel:** Incluído
- **Localização:** Lisboa Datacenter
- **Backup Automático:** JetBackup (incluído)

**Adicionar (opcional mas recomendado):**
- [ ] **SiteLock:** €5/mês (segurança extra) - **NÃO** (Imunify360 já incluído)
- [ ] **CodeGuard:** €3/mês (backup cloud extra) - **SIM** (redundância)
- [ ] **SitePad:** Website builder - **NÃO** (já temos WordPress)
- [ ] **SSL Premium:** €50/ano - **NÃO** (Let's Encrypt grátis suficiente)

**Total Recomendado:**
```
Alojamento Premium: €144/ano
Domínio .pt:        €10/ano (se via PTisp) ou €0 (se DNS.pt)
CodeGuard Backup:   €36/ano (opcional)
------------------------
Total:              €154-190/ano
```

### Passo 4: Pagamento

**Métodos aceites:**
- Multibanco (referência gerada)
- MB Way
- Cartão Crédito/Débito
- Transferência Bancária
- PayPal

**Ativação:**
- Multibanco/MB Way: 1-2h após pagamento confirmado
- Cartão: Imediato
- Transferência: 1-2 dias úteis

### Passo 5: Email de Ativação

**Receberá email com:**
```
Subject: Ativação de Alojamento - Chapéus Lisboetas

Parabéns! O seu alojamento está ativo.

Dados de Acesso cPanel:
URL: https://cpanel.ptisp.pt
Username: chapeusl (ou similar)
Password: [senha temporária - ALTERAR!]

Nameservers:
ns1.ptisp.pt
ns2.ptisp.pt

Servidor IP: XXX.XXX.XXX.XXX

FTP/SFTP:
Host: ftp.seudominio.pt
Username: chapeusl
Password: [mesma do cPanel]
Port: 21 (FTP) ou 22 (SFTP)

MySQL:
Host: localhost
Criar database via cPanel

Suporte:
Telefone: 707 500 532
Email: suporte@ptisp.pt
```

**AÇÃO IMEDIATA:**
1. Guardar email (não apagar!)
2. Login cPanel: https://cpanel.ptisp.pt
3. Alterar password (cPanel → Password & Security)
4. Anotar credenciais em password manager (1Password/Bitwarden)

---

## ⚙️ Configuração cPanel Pós-Ativação

### 1. Primeiro Login

```
URL: https://cpanel.ptisp.pt
User: [do email ativação]
Pass: [alterar imediatamente]

Ao fazer login, verá dashboard com:
- Estatísticas de uso (disco, banda, CPU)
- Quick shortcuts (Email, Files, Databases)
- Software (WordPress, Joomla, etc.)
```

### 2. Alterar Password

```
cPanel → Preferences → Password & Security
→ New Password: [gerar forte 20+ caracteres]
→ Confirmar
→ Guardar em password manager
```

### 3. Configurar Domínio Principal

**Se domínio já propagado:**
```
cPanel → Domains
→ Domain já aparece listado
→ Verificar Document Root: /public_html
```

**Se precisa adicionar domínio:**
```
cPanel → Domains → Create A New Domain
Domain: chapeuslisboetas.pt
Document Root: public_html (auto-fill)
→ Submit
```

### 4. Criar Base de Dados MySQL

**Passo 4.1: Criar Database**
```
cPanel → Databases → MySQL Databases
→ Create New Database

Database Name: chapeuslisboetas_db
(Será criado como: chapeusl_chapeuslisboetas_db)
→ Create Database
```

**Passo 4.2: Criar User**
```
→ Scroll: MySQL Users → Add New User

Username: chapeuslisboetas_user
(Será: chapeusl_chapeuslisboetas_user)

Password: [GERAR FORTE]
→ Usar Password Generator
→ Copiar senha (não perder!)
→ Create User
```

**Passo 4.3: Associar User a Database**
```
→ Scroll: Add User To Database

User: chapeusl_chapeuslisboetas_user
Database: chapeusl_chapeuslisboetas_db
→ Add

→ Manage Privileges:
✓ ALL PRIVILEGES (selecionar tudo)
→ Make Changes
```

**Passo 4.4: Anotar Credenciais**
```
Database Host: localhost
Database Name: chapeusl_chapeuslisboetas_db
Database User: chapeusl_chapeuslisboetas_user
Database Password: [senha gerada no passo 4.2]
```

### 5. Criar Conta FTP/SFTP

**Para deploy de ficheiros:**
```
cPanel → Files → FTP Accounts
→ Add FTP Account

Log in: deploy
Password: [GERAR FORTE]
Directory: /public_html (já selecionado)
Quota: Unlimited
→ Create FTP Account

Dados FTP criados:
Username: deploy@chapeuslisboetas.pt
Password: [senha gerada]
Server: ftp.chapeuslisboetas.pt
Port: 21 (FTP) ou 22 (SFTP recomendado)
```

### 6. Ativar SSL (Let's Encrypt)

**Automático via cPanel:**
```
cPanel → Security → SSL/TLS Status

→ Domain: chapeuslisboetas.pt
→ Status: [Verá "No SSL" inicialmente]
→ Click: "Run AutoSSL"

Aguardar 2-5 minutos...

Status: ✓ SSL certificate successfully installed
Issuer: Let's Encrypt
Valid until: [90 dias depois]
Auto-renew: Enabled (renova automaticamente a cada 60 dias)
```

**Se AutoSSL falhar:**
```
Causa comum: DNS ainda não propagado
Solução: Aguardar 6-24h, tentar novamente
Ou: Usar Cloudflare SSL (ver Cloudflare setup)
```

### 7. Configurar PHP

**Otimizar para WordPress/WooCommerce:**
```
cPanel → Software → Select PHP Version

PHP Version: 8.0 (recomendado) ou 7.4 (se problemas compatibilidade)

→ Extensions (ativar todas estas):
✓ mysqli (database)
✓ gd (imagens)
✓ curl (HTTP requests)
✓ zip (importação/exportação)
✓ mbstring (strings multibyte)
✓ xml (feeds, XML-RPC)
✓ xmlreader (importação)
✓ xmlwriter (exportação)
✓ opcache (performance)
✓ imagick (processamento imagens avançado)
✓ exif (metadata imagens)
✓ fileinfo (upload validation)
✓ iconv (conversão caracteres)
✓ json (API)
✓ openssl (segurança)
✓ pdo_mysql (database alternativo)

→ Options (ajustar valores):
memory_limit: 256M (ou 512M se disponível)
max_execution_time: 300
max_input_time: 300
post_max_size: 64M
upload_max_filesize: 64M
max_input_vars: 3000 (importante para WooCommerce)
display_errors: Off
log_errors: On

→ Save
```

### 8. Configurar Email (Opcional mas Recomendado)

**Criar mail@chapeuslisboetas.pt:**
```
cPanel → Email → Email Accounts
→ Create

Email: mail
Password: [GERAR FORTE]
Storage Space: 1000 MB (1GB suficiente)
→ Create

Email criado: mail@chapeuslisboetas.pt

Acesso Webmail: https://webmail.chapeuslisboetas.pt
Apps: Roundcube (recomendado), Horde, SquirrelMail
```

**Configurar em cliente email (Outlook/Apple Mail):**
```
IMAP (receber):
Server: mail.chapeuslisboetas.pt
Port: 993
Security: SSL/TLS
Username: mail@chapeuslisboetas.pt
Password: [senha criada]

SMTP (enviar):
Server: mail.chapeuslisboetas.pt
Port: 465
Security: SSL/TLS
Username: mail@chapeuslisboetas.pt
Password: [senha criada]
Auth: Required
```

### 9. Configurar Backups JetBackup

**Verificar configuração:**
```
cPanel → Files → JetBackup

Configuração Automática:
- Full Backup: Daily @ 2:00 AM
- Retention: 30 days
- Location: Servidor PTisp + offsite

Restaurar backup (se necessário):
→ JetBackup → File Backups
→ Escolher data
→ Download ou Restore in place
```

**Backup manual antes de deploy:**
```
cPanel → Files → Backup
→ Download a Home Directory Backup
(Vai gerar .tar.gz - demora 10-30min)
→ Guardar localmente
```

### 10. Instalar WordPress (MÉTODO 1: Manual)

**Download WordPress PT:**
```
cPanel → File Manager
→ public_html/
→ Upload

Ou via SSH:
ssh chapeusl@seuservidor.ptisp.pt
cd public_html/
wget https://pt.wordpress.org/latest-pt_PT.tar.gz
tar -xzf latest-pt_PT.tar.gz --strip-components=1
rm latest-pt_PT.tar.gz
```

**Ou via terminal local e FTP:**
```bash
# Download WordPress PT
curl -O https://pt.wordpress.org/latest-pt_PT.tar.gz
tar -xzf latest-pt_PT.tar.gz

# Upload via SFTP (FileZilla ou comando)
sftp deploy@ftp.chapeuslisboetas.pt
cd /public_html/
put -r wordpress/* .
```

### 11. Instalar WordPress (MÉTODO 2: Softaculous - MAIS FÁCIL)

**Instalação 1-click:**
```
cPanel → Software → Softaculous Apps Installer
→ WordPress

Choose Installation URL:
Protocol: https:// (se SSL já ativo)
Domain: chapeuslisboetas.pt
Directory: [deixar vazio - instala em raiz]

Site Settings:
Site Name: Chapéus Lisboetas
Site Description: Chapelaria Artesanal desde 1950

Admin Account:
Username: [escolher - ex: admin_tiago]
Password: [GERAR FORTE]
Email: mail@chapeuslisboetas.pt

Choose Language: Portuguese (pt_PT)

Advanced Options:
Database Name: chapeusl_wp_db (auto)
Table Prefix: wp_ (manter padrão)

Auto Upgrade:
WordPress: Minor versions (segurança)
Plugins: No (controlo manual)
Themes: No (controlo manual)

Backup:
Automated: Não (JetBackup já faz)

→ Install

Aguardar 2-5 minutos...

Success!
URL: https://chapeuslisboetas.pt
Admin URL: https://chapeuslisboetas.pt/wp-admin
Username: [escolhido]
Password: [gerado]
```

**IMPORTANTE: Se usar Softaculous, NÃO precisa importar database/files manualmente - só para site já existente**

---

## 🔄 Migração de Site Existente (Localhost → PTisp)

**Se já tem site desenvolvido localmente (nosso caso):**

### Método A: Migração Manual (Controlo Total)

**Ver PLANO_DEPLOY_PRODUCAO.md Fase 3 e 4 para detalhes completos**

Resumo:
1. Exportar database localhost (mysqldump)
2. Importar para PTisp MySQL (phpMyAdmin ou SSH)
3. Upload ficheiros wp-content/ via FTP/SFTP
4. Editar wp-config.php com credenciais PTisp
5. Search & Replace URLs (localhost → produção)

### Método B: Plugin de Migração (Mais Simples)

**All-in-One WP Migration (Grátis até 512MB):**

```
LOCALHOST:
1. WP Admin → Plugins → Add New
2. Procurar: "All-in-One WP Migration"
3. Install + Activate
4. Tools → All-in-One WP Migration → Export
5. Export To: File
6. Aguardar (gera .wpress file)
7. Download

PRODUÇÃO (PTisp):
1. Instalar WordPress limpo (Softaculous)
2. WP Admin → Plugins → Add New
3. Instalar "All-in-One WP Migration"
4. Tools → All-in-One WP Migration → Import
5. Import From: File
6. Upload .wpress file
7. Aguardar importação
8. Proceed → Yes (sobrescreve)
9. Permalink Settings → Save (flush rewrite rules)

Limitação: Grátis só até 512MB
Nosso site: ~450MB (deve funcionar)
Se maior: Comprar extensão (€69) ou método manual
```

### Método C: Duplicator Pro (Profissional)

**Duplicator (Grátis) ou Pro (€50/ano):**
```
LOCALHOST:
1. Install Duplicator plugin
2. Duplicator → Create New Package
3. Name: chapeuslisboetas-production
4. Archive: Build (gera .zip)
5. Installer: Build (gera installer.php)
6. Download ambos ficheiros

PRODUÇÃO (PTisp):
1. Criar database vazia (já feito)
2. Upload via FTP para /public_html/:
   - installer.php
   - [package].zip
3. Aceder: https://chapeuslisboetas.pt/installer.php
4. Wizard:
   Step 1: Verificação
   Step 2: Database credentials (PTisp)
   Step 3: Search & Replace URLs
   Step 4: Admin login
5. Concluir
6. Apagar installer.php e .zip (segurança)
```

---

## 🌐 Configuração DNS

### Cenário 1: Domínio Registado na DNS.pt

**Apontar para PTisp:**
```
Login: https://online.dns.pt
→ Domínios → chapeuslisboetas.pt → Gerir DNS

Adicionar/Editar Records:

A Record:
Name: @
Type: A
Value: [IP servidor PTisp - ex: 185.XXX.XXX.XXX]
TTL: 3600

A Record (www):
Name: www
Type: A
Value: [mesmo IP]
TTL: 3600

MX Record (email):
Priority: 10
Value: mail.chapeuslisboetas.pt
TTL: 3600

TXT Record (SPF - evitar spam):
Name: @
Type: TXT
Value: v=spf1 a mx ip4:[IP PTisp] ~all
TTL: 3600

→ Guardar
→ Aguardar propagação: 2-48h (geralmente 2-6h)
```

**Verificar propagação:**
```bash
# Terminal Mac/Linux
nslookup chapeuslisboetas.pt
# Deve retornar IP PTisp

dig chapeuslisboetas.pt
# Deve mostrar A record com IP correto

# Online
https://www.whatsmydns.net/#A/chapeuslisboetas.pt
```

### Cenário 2: Domínio Registado na PTisp

**DNS já configurado automaticamente!**
```
Não precisa fazer nada - PTisp auto-configura
Verificar apenas:
cPanel → Domains → chapeuslisboetas.pt
→ Zone Editor → Verify records
```

### Cenário 3: Usar Cloudflare (RECOMENDADO)

**Setup Cloudflare CDN + SSL:**

**Passo 1: Criar Conta**
```
https://dash.cloudflare.com/sign-up
Email: mail@chapeuslisboetas.pt
Password: [FORTE]
→ Create Account
```

**Passo 2: Adicionar Site**
```
Dashboard → Add a Site
→ Enter your site: chapeuslisboetas.pt
→ Continue

Select a Plan:
→ Free ($0/month) [suficiente para começar]
→ Confirm Plan
```

**Passo 3: Review DNS Records**
```
Cloudflare vai detectar automaticamente records existentes:

A     @     [IP PTisp]    [Proxied 🟠] ← IMPORTANTE
A     www   [IP PTisp]    [Proxied 🟠]
MX    @     mail.chapeuslisboetas.pt [DNS only ☁️]

→ Verify records estão corretos
→ Continue
```

**Passo 4: Alterar Nameservers**
```
Cloudflare fornece 2 nameservers:
Example:
    dana.ns.cloudflare.com
    rob.ns.cloudflare.com

Voltar a DNS.pt (ou registador domínio):
→ Domínios → chapeuslisboetas.pt → Nameservers
→ Custom Nameservers:
    NS1: dana.ns.cloudflare.com
    NS2: rob.ns.cloudflare.com
→ Guardar

Voltar a Cloudflare:
→ Done, check nameservers
→ Aguardar ativação: 1-24h (geralmente <2h)
```

**Passo 5: Configurar SSL**
```
Cloudflare Dashboard → SSL/TLS

Encryption Mode: Full (strict)
[Certifica-se que PTisp tem SSL ativo]

→ Edge Certificates:
✓ Always Use HTTPS: ON
✓ Automatic HTTPS Rewrites: ON
✓ Minimum TLS Version: 1.2
✓ Opportunistic Encryption: ON
✓ TLS 1.3: ON
✓ Certificate Transparency Monitoring: ON
```

**Passo 6: Otimizações Performance**
```
→ Speed → Optimization

Auto Minify:
✓ JavaScript
✓ CSS
✓ HTML

Brotli: ON
Rocket Loader: OFF (pode quebrar WooCommerce)
Mirage: OFF (versão paga)

→ Caching:
Caching Level: Standard
Browser Cache TTL: 4 hours

→ Page Rules (Free: 3 rules):
Rule 1: Cache Everything
    URL: *chapeuslisboetas.pt/wp-content/*
    Settings: Cache Level = Cache Everything

Rule 2: Bypass Cache (Admin)
    URL: *chapeuslisboetas.pt/wp-admin/*
    Settings: Cache Level = Bypass

Rule 3: Bypass Cache (Checkout)
    URL: *chapeuslisboetas.pt/checkout/*
    Settings: Cache Level = Bypass
```

**Passo 7: Verificar Ativo**
```
Após nameservers propagados:
Dashboard → Overview
Status: Active ✓

Test:
https://www.cloudflare.com/ssl-test/chapeuslisboetas.pt
Grade: A ou A+ esperado
```

---

## 🔒 Segurança Pós-Migração

### 1. Hardening WordPress

**wp-config.php security:**
```php
// Já incluído em PLANO_DEPLOY_PRODUCAO.md
// Verificar:
define('DISALLOW_FILE_EDIT', true); // Desativa editor de temas/plugins
define('FORCE_SSL_ADMIN', true);    // Força HTTPS no admin
```

**Permissions corretas:**
```bash
# SSH no servidor
ssh chapeusl@servidor.ptisp.pt

cd /home/chapeusl/public_html/

# Directories: 755
find . -type d -exec chmod 755 {} \;

# Files: 644
find . -type f -exec chmod 644 {} \;

# wp-config.php: 640 (mais restritivo)
chmod 640 wp-config.php

# .htaccess: 644
chmod 644 .htaccess
```

### 2. Plugins de Segurança

**Wordfence Security (Grátis):**
```
WP Admin → Plugins → Add New
→ Wordfence Security
→ Install + Activate

Setup Wizard:
Email: mail@chapeuslisboetas.pt
Get Premium: No, thanks (grátis suficiente)

Firewall: Extended Protection
Login Security: Enable

Schedule Scan: Daily 3:00 AM

Email Alerts: ON (critical only)
```

**iThemes Security (Alternativa):**
```
Similar a Wordfence
Mais user-friendly
Menos resource-intensive
```

### 3. Backup Redundante

**UpdraftPlus (além JetBackup):**
```
WP Admin → Plugins → Add New
→ UpdraftPlus

Settings:
Schedule: Daily (files) + Weekly (database)
Retain: 7 daily + 4 weekly

Remote Storage (escolher um):
- Google Drive (15GB grátis)
- Dropbox (2GB grátis)
- OneDrive

Email: mail@chapeuslisboetas.pt (notificações)

→ Save + Backup Now (teste inicial)
```

### 4. Firewall .htaccess

**Adicionar a /public_html/.htaccess:**
```apache
# Ver PLANO_DEPLOY_PRODUCAO.md Fase 5.3
# Já inclui:
# - Force HTTPS
# - Security headers
# - Disable directory browsing
# - Protect wp-config.php
# - Block common attacks
```

### 5. Two-Factor Authentication

**Google Authenticator Plugin:**
```
WP Admin → Plugins → Add New
→ Google Authenticator – WordPress Two Factor Authentication (2FA)

Configurar:
→ Users → Your Profile
→ Two Factor Authentication
→ Scan QR code com app (Google Authenticator ou Authy)
→ Enter code → Enable

Ativar para todos admins!
```

---

## 📊 Monitorização e Analytics

### 1. Google Analytics 4

**Setup:**
```
1. https://analytics.google.com
2. Create Account: Chapéus Lisboetas
3. Property: chapeuslisboetas.pt
4. Data stream: Web
5. Copy Measurement ID: G-XXXXXXXXX

WordPress:
Install plugin: "Site Kit by Google"
→ Connect Google Account
→ Analytics → Complete setup
→ Insert Measurement ID

Ou manualmente:
WP Admin → Appearance → Theme Editor
→ header.php (antes </head>)
→ Paste Google Analytics code
```

**Eventos E-commerce:**
```
Site Kit auto-configura para WooCommerce:
- view_item
- add_to_cart
- begin_checkout
- purchase

Verificar:
Analytics → Reports → Realtime
(fazer compra teste, ver evento aparecer)
```

### 2. Google Search Console

**Setup:**
```
1. https://search.google.com/search-console
2. Add Property: chapeuslisboetas.pt
3. Verification:
   Método: HTML tag
   Ou: Site Kit auto-verifica

4. Submit Sitemap:
   URL: https://chapeuslisboetas.pt/sitemap_index.xml
   (Yoast SEO auto-gera)

5. Coverage: Verificar páginas indexadas
6. Performance: Monitorizar clicks/impressões
```

### 3. Uptime Monitoring

**UptimeRobot (Grátis):**
```
1. https://uptimerobot.com
2. Sign Up → Free
3. Add New Monitor:
   Type: HTTP(s)
   URL: https://chapeuslisboetas.pt
   Name: Chapéus Lisboetas Main
   Interval: 5 minutes

4. Alert Contacts:
   Email: mail@chapeuslisboetas.pt
   SMS: +351 918 911 308 (opcional)

5. Add Monitor

Adicionar mais:
- https://chapeuslisboetas.pt/loja/
- https://chapeuslisboetas.pt/wp-admin/
- https://chapeuslisboetas.pt/checkout/
```

### 4. Performance Monitoring

**Pingdom (Trial grátis 14 dias, depois €10/mês):**
```
https://www.pingdom.com
→ Start free trial

Synthetic Monitoring:
URL: https://chapeuslisboetas.pt
Location: Europe - Portugal (se disponível) ou Spain
Interval: 5 minutes

Real User Monitoring (RUM):
Install script on site
Tracks real user experience

Alerts:
Email: Down > 2 min
SMS: Down > 5 min
```

**Alternativa Grátis: Google PageSpeed Insights**
```
https://pagespeed.web.dev/
→ Analyze: https://chapeuslisboetas.pt

Target:
Mobile: >85
Desktop: >90

Monitorizar semanalmente
Implementar sugestões
```

---

## ✅ Checklist Pós-Migração

### Imediatamente Após Go-Live

- [ ] Site carrega: https://chapeuslisboetas.pt
- [ ] SSL ativo (cadeado verde)
- [ ] WP Admin acessível: /wp-admin
- [ ] Database conectada (sem erros)
- [ ] Imagens carregam
- [ ] Menu navegação funciona
- [ ] Footer completo

### Primeiras 24h

- [ ] Compra teste WooCommerce (€1 produto)
- [ ] Email confirmação recebido
- [ ] IfthenPay funcional
- [ ] Google Analytics tracking (ver Realtime)
- [ ] Search Console sitemap submetido
- [ ] Uptime monitoring ativo (0 downtime)
- [ ] Backup automático executado (verificar JetBackup)

### Primeira Semana

- [ ] Performance >85 mobile PageSpeed
- [ ] Zero erros Search Console
- [ ] Todas páginas indexadas Google
- [ ] Blog posts ranking para keywords
- [ ] Email marketing enviado (anúncio)
- [ ] Instagram post go-live
- [ ] Primeiras vendas orgânicas

### Primeiro Mês

- [ ] Analytics: >100 sessões/dia
- [ ] Conversão: >1%
- [ ] SEO: Top 20 para 5+ keywords
- [ ] Backups redundantes (JetBackup + UpdraftPlus)
- [ ] Zero incidentes segurança
- [ ] Cliente satisfeito e treinado

---

## 🆘 Troubleshooting Comum

### Erro 1: "Error establishing database connection"

**Causa:** Credenciais wp-config.php incorretas

**Solução:**
```php
// Editar wp-config.php via FTP/File Manager
define( 'DB_NAME', 'chapeusl_chapeuslisboetas_db' ); // Nome EXATO
define( 'DB_USER', 'chapeusl_chapeuslisboetas_user' );
define( 'DB_PASSWORD', '[senha EXATA criada]' );
define( 'DB_HOST', 'localhost' ); // NÃO mudar

// Verificar no cPanel → MySQL Databases
// Copiar nomes exatos (com prefix)
```

### Erro 2: "Too Many Redirects"

**Causa:** Loop HTTPS ou Cloudflare SSL

**Solução:**
```php
// Adicionar a wp-config.php ANTES de "require_once ABSPATH"
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] = 'on';
}

// Se Cloudflare: Encryption mode = Full (strict)
```

### Erro 3: Imagens 404 (Not Found)

**Causa:** Permalinks ou uploads não migrados

**Solução:**
```
1. WP Admin → Settings → Permalinks
   → Click "Save Changes" (flush rewrite rules)

2. Verificar uploads existem:
   FTP → /public_html/wp-content/uploads/

3. Se faltam: Re-upload via FTP

4. Regenerar .htaccess:
   cPanel → File Manager → public_html
   → Apagar .htaccess
   → WP Admin → Permalinks → Save (recria)
```

### Erro 4: WooCommerce Checkout Não Funciona

**Causa:** SSL, permalinks, ou plugin conflito

**Solução:**
```
1. Verificar SSL ativo (HTTPS)
2. WooCommerce → Settings → Advanced → Page setup
   → Recreate pages se necessário
3. Permalinks → Save
4. Desativar plugins um a um (testar)
5. PHP memory limit:
   cPanel → PHP Settings → memory_limit = 256M
```

### Erro 5: Site Lento (>5s load)

**Causa:** Cache desativado, imagens não otimizadas

**Solução:**
```
1. Instalar WP Rocket ou W3 Total Cache
2. Ativar Cloudflare CDN
3. Comprimir imagens (Imagify plugin)
4. Lazy loading (native WordPress ou plugin)
5. PHP OPcache: cPanel → PHP → opcache = ON
6. Database optimize:
   WP Admin → WP-Optimize plugin → Run
```

---

## 📞 Suporte PTisp

**Telefone:** 707 500 532 (24/7)
**Email:** suporte@ptisp.pt
**Ticket:** https://suporte.ptisp.pt
**Live Chat:** https://www.ptisp.pt (horário comercial)

**Base Conhecimento:** https://ajuda.ptisp.pt

**Comum pedir ajuda:**
- Configuração DNS
- Problemas SSL
- Performance tuning
- Backup restore
- Email configuration

**Resposta média:** <15 min tickets, imediato telefone

---

## 📚 Recursos Úteis

**WordPress:**
- Codex: https://codex.wordpress.org
- Fórum PT: https://pt.wordpress.org/support/
- WooCommerce Docs: https://docs.woocommerce.com

**PTisp:**
- Tutoriais: https://ajuda.ptisp.pt/tutoriais
- Video guias: https://www.youtube.com/c/PTispHosting

**Performance:**
- PageSpeed: https://pagespeed.web.dev
- GTmetrix: https://gtmetrix.com
- WebPageTest: https://webpagetest.org

**SEO:**
- Yoast Academy: https://yoast.com/academy/
- Google SEO Guide: https://developers.google.com/search/docs

---

**Documento criado:** 27 Outubro 2025
**Versão:** 1.0
**Autor:** AiParaTi (Bilal Machraa)
**Cliente:** Chapéus Lisboetas

**Status:** ✅ Pronto para execução
