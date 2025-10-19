# 🚀 WordPress LOCAL com Docker - Guia Rápido

## 📋 O QUE FOI CRIADO:

✅ **Docker Compose** - WordPress + MySQL + phpMyAdmin
✅ **Setup Automático** - Instala e configura tudo
✅ **Script Import** - Importa 180 produtos automaticamente
✅ **Credenciais Pré-definidas** - Sem configuração manual

---

## 🎯 INÍCIO RÁPIDO (3 Comandos)

```bash
# 1. Iniciar Docker
docker-compose -f docker-compose-fresh.yml up -d

# 2. Aguardar setup automático (30 segundos)
# Ver logs: docker logs -f chapeus_wpcli

# 3. Importar produtos
python3 import_produtos_local.py
```

**Pronto! Loja completa em http://localhost:8080**

---

## 📝 PASSO A PASSO DETALHADO

### PASSO 1: Verificar Docker Instalado

```bash
# Verificar Docker
docker --version

# Se não tiver instalado:
# Mac: https://docs.docker.com/desktop/install/mac-install/
# Download Docker Desktop e instalar
```

### PASSO 2: Iniciar Containers

```bash
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

# Iniciar tudo
docker-compose -f docker-compose-fresh.yml up -d

# Ver status
docker ps
```

**Deve ver 4 containers:**
- `chapeus_wordpress` - WordPress
- `chapeus_db` - MySQL
- `chapeus_wpcli` - Setup automático
- `chapeus_phpmyadmin` - Admin BD

### PASSO 3: Aguardar Setup Automático

```bash
# Ver logs do setup (em tempo real)
docker logs -f chapeus_wpcli

# Aguardar mensagem:
# "✅ WORDPRESS CONFIGURADO COM SUCESSO!"
```

**Tempo: ~30 segundos**

O script automático faz:
- ✅ Instala WordPress
- ✅ Instala WooCommerce
- ✅ Cria páginas (Shop, Cart, Checkout)
- ✅ Configura moeda (EUR)
- ✅ Cria credenciais admin

### PASSO 4: Verificar WordPress

```bash
# Abrir navegador:
open http://localhost:8080

# Deve ver homepage WordPress
```

**Login Admin:**
```
URL: http://localhost:8080/wp-admin
User: admin
Pass: ChapeusAdmin2024!
```

### PASSO 5: Importar Produtos

```bash
# Instalar dependências (se ainda não tiver)
pip3 install requests tqdm

# Executar import
python3 import_produtos_local.py

# Confirmar quando perguntar: s
```

**Tempo: ~30 minutos para 180 produtos**

---

## 🌐 URLs IMPORTANTES

```
WordPress:     http://localhost:8080
Admin:         http://localhost:8080/wp-admin
Loja:          http://localhost:8080/shop
phpMyAdmin:    http://localhost:8081
```

---

## 🔑 CREDENCIAIS

### WordPress Admin:
```
Username: admin
Password: ChapeusAdmin2024!
```

### Base de Dados:
```
Host: localhost:3306
Database: chapeus_wordpress
User: chapeus_user
Password: chapeus_pass_2024
Root Pass: chapeus_root_2024
```

### phpMyAdmin:
```
URL: http://localhost:8081
Server: db
User: root
Pass: chapeus_root_2024
```

---

## 📊 VERIFICAR IMPORTAÇÃO

### Via WordPress Admin:

1. Login: http://localhost:8080/wp-admin
2. Products → All Products
3. Deve ver 180 produtos

### Via Loja:

1. Abrir: http://localhost:8080/shop
2. Deve ver grid com chapéus

### Via API:

```bash
curl http://localhost:8080/wp-json/wc/v3/products \
  -u admin:ChapeusAdmin2024! \
  | jq length
```

---

## 🛠️ COMANDOS ÚTEIS

### Ver Logs:

```bash
# WordPress
docker logs -f chapeus_wordpress

# Setup
docker logs -f chapeus_wpcli

# MySQL
docker logs -f chapeus_db
```

### Parar Containers:

```bash
docker-compose -f docker-compose-fresh.yml down
```

### Reiniciar Tudo:

```bash
# Parar
docker-compose -f docker-compose-fresh.yml down

# Iniciar
docker-compose -f docker-compose-fresh.yml up -d
```

### Apagar TUDO e Recomeçar:

```bash
# ATENÇÃO: Apaga base de dados!
docker-compose -f docker-compose-fresh.yml down -v

# Iniciar fresh
docker-compose -f docker-compose-fresh.yml up -d
```

### Aceder Shell WordPress:

```bash
docker exec -it chapeus_wordpress bash

# Dentro do container:
cd /var/www/html
ls -la
```

### Executar WP-CLI Commands:

```bash
# Ver plugins
docker exec chapeus_wordpress wp plugin list --allow-root

# Ver produtos
docker exec chapeus_wordpress wp wc product list --allow-root

# Ver utilizadores
docker exec chapeus_wordpress wp user list --allow-root
```

---

## 🔧 TROUBLESHOOTING

### Erro: "Cannot connect to Docker daemon"

```bash
# Mac: Abrir Docker Desktop app
# Verificar se está a correr
docker ps
```

### Erro: "Port already in use"

```bash
# Ver quem está a usar porta 8080
lsof -i :8080

# Ou mudar porta no docker-compose-fresh.yml:
# ports: "8081:80"  (em vez de 8080:80)
```

### WordPress não carrega:

```bash
# Ver logs
docker logs chapeus_wordpress

# Reiniciar container
docker restart chapeus_wordpress

# Aguardar 30 seg e tentar novamente
```

### Produtos não importaram:

```bash
# Verificar WooCommerce ativo
docker exec chapeus_wordpress wp plugin list --allow-root | grep woocommerce

# Se não estiver ativo:
docker exec chapeus_wordpress wp plugin activate woocommerce --allow-root

# Tentar import novamente
python3 import_produtos_local.py
```

### Imagens não aparecem:

```bash
# Verificar permissões
docker exec chapeus_wordpress chmod -R 755 /var/www/html/wp-content/uploads

# Regenerar thumbnails (via plugin ou WP-CLI)
docker exec chapeus_wordpress wp media regenerate --allow-root
```

### Base dados corrompida:

```bash
# Apagar e recomeçar
docker-compose -f docker-compose-fresh.yml down -v
docker-compose -f docker-compose-fresh.yml up -d

# Aguardar setup
# Reimportar produtos
```

---

## 🎨 INSTALAR TEMA FLATSOME

### Método 1: Via Admin (Manual)

1. Login WordPress Admin
2. Appearance → Themes → Add New
3. Upload Theme
4. Selecionar: `flatsome_v3.20.2_package.zip`
5. Install Now
6. Activate

### Método 2: Via Docker (Automático)

```bash
# Copiar tema para container
docker cp flatsome_v3.20.2_package.zip chapeus_wordpress:/tmp/

# Extrair e ativar
docker exec chapeus_wordpress bash -c "
  cd /tmp && 
  unzip flatsome_v3.20.2_package.zip -d /var/www/html/wp-content/themes/ && 
  wp theme activate flatsome --allow-root
"
```

---

## 📦 EXPORTAR PARA PRODUÇÃO

### Opção 1: Exportar WordPress completo

```bash
# Criar backup
docker exec chapeus_wordpress wp export --allow-root > chapeus_export.xml

# Backup base dados
docker exec chapeus_db mysqldump -u chapeus_user -pchapeus_pass_2024 chapeus_wordpress > chapeus_db_backup.sql

# Backup ficheiros
docker cp chapeus_wordpress:/var/www/html ./wordpress_backup/
```

### Opção 2: Plugin Duplicator

1. Install plugin "Duplicator"
2. Create Package
3. Download .zip + installer.php
4. Upload para servidor produção
5. Executar installer.php

### Opção 3: Re-importar CSV

- Já tens `woocommerce_import_180_produtos.csv`
- Upload imagens manualmente
- Importar CSV no WooCommerce produção

---

## ✅ CHECKLIST FINAL

Antes de ir para produção:

```
□ 180 produtos importados
□ Todas imagens visíveis
□ Categorias criadas
□ Preços corretos (€35-85)
□ Stock configurado (10 unidades)
□ Tema Flatsome instalado e personalizado
□ Homepage customizada
□ Menu navegação criado
□ Páginas essenciais (Sobre, Contacto)
□ Métodos pagamento configurados
□ Envios configurados
□ Testar compra completa
□ Mobile responsive OK
□ SEO básico (Yoast)
```

---

## 🎉 PRÓXIMOS PASSOS

### 1. Personalizar Design

- Flatsome → UX Builder
- Criar homepage custom
- Adicionar banners
- Configurar cores marca

### 2. Configurar Pagamentos

- Transferência Bancária
- PayPal
- MB Way / Multibanco (Plugin IFTHENPAY)

### 3. SEO

- Install Yoast SEO
- Configurar meta descriptions
- Sitemap
- Google Search Console

### 4. Marketing

- Google Analytics
- Facebook Pixel
- Newsletter (Mailchimp)

### 5. Migrar para Produção

- Comprar hosting
- Configurar domínio
- Exportar e importar
- Testar tudo
- GO LIVE!

---

## 📞 RESUMO COMANDOS

```bash
# INICIAR TUDO
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"
docker-compose -f docker-compose-fresh.yml up -d
docker logs -f chapeus_wpcli
python3 import_produtos_local.py

# ABRIR
open http://localhost:8080
open http://localhost:8080/wp-admin

# PARAR
docker-compose -f docker-compose-fresh.yml down

# LOGS
docker logs -f chapeus_wordpress

# COMANDOS WP
docker exec chapeus_wordpress wp --info --allow-root
```

---

**🚀 BOA SORTE!**

Qualquer dúvida, verificar logs ou consultar documentação Docker/WordPress.
