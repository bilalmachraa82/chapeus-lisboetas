# ✅ WordPress LOCAL Pronto!

## 🎉 O QUE ESTÁ RODANDO:

```
✅ WordPress:    http://localhost:8080
✅ Admin:        http://localhost:8080/wp-admin  
✅ phpMyAdmin:   http://localhost:8081
✅ MySQL:        localhost:3306
```

---

## 🔑 CREDENCIAIS:

### WordPress Admin:
```
URL:      http://localhost:8080/wp-admin
Username: admin
Password: ChapeusAdmin2024!
```

### Base de Dados (phpMyAdmin):
```
URL:      http://localhost:8081
Server:   db  
Username: root
Password: chapeus_root_2024
```

---

## 📋 PRÓXIMOS PASSOS:

### PASSO 1: Completar Setup WordPress (2 min)

1. **Abrir:** http://localhost:8080
2. **Seguir wizard de instalação** (se aparecer)
3. **Ou fazer login:** http://localhost:8080/wp-admin
   - User: `admin`
   - Pass: `ChapeusAdmin2024!`

### PASSO 2: Instalar WooCommerce (3 min)

1. **WordPress Admin → Plugins → Add New**
2. **Procurar: "WooCommerce"**
3. **Install Now → Activate**
4. **Setup Wizard:**
   - Store Address: Lisboa, Portugal
   - Currency: EUR (€)
   - Industry: Fashion & accessories
   - Products: Physical products
   - Skip theme (usar Flatsome depois)
   - Complete

### PASSO 3: Instalar Flatsome (5 min)

1. **Appearance → Themes → Add New → Upload Theme**
2. **Selecionar:** `flatsome_v3.20.2_package.zip`
3. **Install Now → Activate**
4. **(Opcional) Import demo content** do Flatsome

### PASSO 4: Importar 180 Produtos (30 min)

```bash
# Rodar script Python
python3 import_produtos_local.py

# Confirmar: s
# Aguardar ~30 minutos
```

### PASSO 5: Verificar Loja

1. **Products → All Products** - Ver 180 produtos
2. **Visitar loja:** http://localhost:8080/shop
3. **Testar checkout completo**

---

## 🛠️ COMANDOS ÚTEIS:

### Ver Status:
```bash
docker ps --filter "name=chapeus"
```

### Ver Logs WordPress:
```bash
docker logs -f chapeus_wordpress
```

### Parar Tudo:
```bash
docker-compose -f docker-compose-fresh.yml down
```

### Reiniciar:
```bash
docker-compose -f docker-compose-fresh.yml restart
```

### Apagar Tudo e Recomeçar:
```bash
docker-compose -f docker-compose-fresh.yml down -v
docker-compose -f docker-compose-fresh.yml up -d
```

---

## 🔧 SE ALGO NÃO FUNCIONAR:

### WordPress não abre:
```bash
# Verificar se containers estão rodando
docker ps

# Reiniciar WordPress
docker restart chapeus_wordpress

# Aguardar 30 seg
open http://localhost:8080
```

### Erro de permissões:
```bash
# Corrigir permissões
docker exec -u root chapeus_wordpress bash -c "
  chown -R www-data:www-data /var/www/html &&
  chmod -R 755 /var/www/html
"
```

### WooCommerce não instala:
```bash
# Criar diretórios manualmente
docker exec -u root chapeus_wordpress mkdir -p /var/www/html/wp-content/upgrade
docker exec -u root chapeus_wordpress mkdir -p /var/www/html/wp-content/uploads  
docker exec -u root chapeus_wordpress chown -R www-data:www-data /var/www/html
```

### Base dados não conecta:
```bash
# Verificar MySQL
docker logs chapeus_db

# Reiniciar
docker restart chapeus_db
docker restart chapeus_wordpress
```

---

## 📦 FICHEIROS CRIADOS:

```
✅ docker-compose-fresh.yml - Docker config
✅ setup-scripts/setup-wordpress.sh - Auto-setup
✅ import_produtos_local.py - Import script
✅ START_LOCAL.md - Guia completo
✅ WORDPRESS_PRONTO.md - Este ficheiro
```

---

## 🎯 RESUMO RÁPIDO:

```bash
# 1. Docker já está rodando!
docker ps

# 2. Abrir WordPress
open http://localhost:8080/wp-admin

# 3. Login
# User: admin
# Pass: ChapeusAdmin2024!

# 4. Instalar WooCommerce (via admin)
# Plugins → Add New → WooCommerce → Install

# 5. Importar produtos
python3 import_produtos_local.py
```

---

## ✅ CHECKLIST:

```
✅ Docker containers rodando
✅ WordPress acessível em localhost:8080
□ WooCommerce instalado (fazer manual)
□ Tema Flatsome instalado (fazer manual)
□ 180 produtos importados (executar script)
□ Loja testada e funcionando
```

---

## 🚀 ESTÁ PRONTO PARA:

1. ✅ **Abrir WordPress:** http://localhost:8080/wp-admin
2. ⏳ **Instalar WooCommerce** (3 min via admin)
3. ⏳ **Upload Flatsome** (3 min via admin)
4. ⏳ **Importar produtos** (`python3 import_produtos_local.py`)

**Tempo total até loja completa: ~40 minutos**

---

**Qualquer dúvida, consultar `START_LOCAL.md` para guia detalhado!**

🎉 **BOA SORTE!**
