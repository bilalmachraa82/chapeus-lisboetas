# 🚀 Comandos Rápidos - Chapéus Lisboetas

## Iniciar/Parar Ambiente

```bash
# Ir para a pasta do projeto
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

# Iniciar tudo
docker-compose up -d

# Parar tudo
docker-compose stop

# Parar e remover containers
docker-compose down
```

## Acessos Rápidos

- 🌐 **Site**: http://localhost:8080
- 🔐 **Admin**: http://localhost:8080/wp-admin
- 💾 **phpMyAdmin**: http://localhost:8081

## Ver Logs

```bash
# WordPress
docker logs chapeus_wordpress -f

# MySQL
docker logs chapeus_mysql -f

# Últimas 50 linhas
docker logs chapeus_wordpress --tail 50
```

## Gestão da Base de Dados

```bash
# Aceder ao MySQL
docker exec -it chapeus_mysql mysql -u root -prootpassword lisboetas_web

# Fazer backup da BD
docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web > backup-$(date +%Y%m%d).sql

# Importar BD
docker exec -i chapeus_mysql mysql -u root -prootpassword lisboetas_web < backup.sql

# Ver utilizadores WordPress
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "SELECT user_login, user_email FROM lx_users;"

# Atualizar URLs (se necessário)
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "UPDATE lx_options SET option_value = 'http://localhost:8080' WHERE option_name IN ('siteurl', 'home');"
```

## Gestão de Plugins

```bash
# Listar plugins
ls -la backup/wp/wp-content/plugins/

# Desativar plugin (renomear pasta)
mv backup/wp/wp-content/plugins/NOME_PLUGIN backup/wp/wp-content/plugins/NOME_PLUGIN.disabled

# Reativar plugin
mv backup/wp/wp-content/plugins/NOME_PLUGIN.disabled backup/wp/wp-content/plugins/NOME_PLUGIN

# Ver debug log
tail -50 backup/wp/wp-content/debug.log

# Limpar debug log
rm backup/wp/wp-content/debug.log
```

## Resolução Rápida de Problemas

```bash
# Site não carrega?
docker-compose restart

# Ver status
docker-compose ps

# Verificar erros PHP
tail -100 backup/wp/wp-content/debug.log

# Testar conexão BD
docker exec chapeus_mysql mysql -u root -prootpassword -e "SELECT 1;"

# Verificar permissões
ls -la backup/wp/wp-content/
```

## Atualização de Plugins/WordPress

```bash
# CUIDADO: Fazer backup antes!

# 1. Backup da BD
docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web > backup-antes-update-$(date +%Y%m%d).sql

# 2. Backup dos ficheiros
tar -czf backup-files-$(date +%Y%m%d).tar.gz backup/

# 3. Atualizar via wp-admin ou WP-CLI
docker exec -it chapeus_wordpress bash
# wp core update
# wp plugin update --all
```

## Informação Rápida

```bash
# Versão WordPress
head -20 backup/wp/wp-includes/version.php | grep wp_version

# Contar produtos
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "SELECT COUNT(*) FROM lx_posts WHERE post_type='product' AND post_status='publish';"

# Espaço utilizado
du -sh backup/wp/wp-content/uploads/

# Ver containers ativos
docker ps | grep chapeus
```

## Plugins Desativados

- `revslider.disabled` - Revolution Slider (incompatível com PHP 7.4)

Para reativar: `mv backup/wp/wp-content/plugins/revslider.disabled backup/wp/wp-content/plugins/revslider`
