#!/bin/bash
# Setup automático WordPress + WooCommerce + Produtos

set -e

echo "🚀 Iniciando setup automático do WordPress..."

# Aguardar WordPress estar pronto
echo "⏳ Aguardando WordPress inicializar..."
sleep 10

cd /var/www/html

# Verificar se já está instalado
if ! wp core is-installed --allow-root 2>/dev/null; then
    echo "📦 Instalando WordPress..."
    
    wp core install \
        --url="http://localhost:8084" \
        --title="Chapéus Lisboetas" \
        --admin_user="admin" \
        --admin_password="ChapeusAdmin2024!" \
        --admin_email="admin@chapeuslisboetas.local" \
        --skip-email \
        --allow-root
    
    echo "✅ WordPress instalado!"
else
    echo "✅ WordPress já instalado"
fi

# Instalar WooCommerce
echo "🛒 Instalando WooCommerce..."
if ! wp plugin is-installed woocommerce --allow-root; then
    wp plugin install woocommerce --activate --allow-root
    echo "✅ WooCommerce instalado!"
else
    echo "✅ WooCommerce já instalado"
    wp plugin activate woocommerce --allow-root || true
fi

# Configurar WooCommerce
echo "⚙️  Configurando WooCommerce..."

# Criar páginas WooCommerce
wp wc --user=admin tool run install_pages --allow-root || true

# Configurações básicas
wp option update woocommerce_store_address "Rua Exemplo 123" --allow-root
wp option update woocommerce_store_city "Lisboa" --allow-root
wp option update woocommerce_default_country "PT" --allow-root
wp option update woocommerce_currency "EUR" --allow-root
wp option update woocommerce_price_decimal_sep "," --allow-root
wp option update woocommerce_price_thousand_sep "." --allow-root
wp option update woocommerce_calc_taxes "no" --allow-root

# Configurar permalinks
wp rewrite structure '/%postname%/' --allow-root
wp rewrite flush --allow-root

# Instalar tema básico (usaremos depois Flatsome)
echo "🎨 Configurando tema..."
wp theme activate twentytwentythree --allow-root || wp theme activate twentytwentyone --allow-root || true

# Criar usuário para API
echo "🔑 Criando credenciais API..."
wp user create api_user api@chapeuslisboetas.local \
    --role=administrator \
    --user_pass="ApiUser2024!" \
    --allow-root || echo "Usuário API já existe"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ WORDPRESS CONFIGURADO COM SUCESSO!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "🌐 URLs:"
echo "   WordPress: http://localhost:8084"
echo "   Admin:     http://localhost:8084/wp-admin"
echo ""
echo "🔑 Credenciais Admin:"
echo "   Username: admin"
echo "   Password: ChapeusAdmin2024!"
echo ""
echo "🔑 Credenciais API:"
echo "   Username: api_user"
echo "   Password: ApiUser2024!"
echo ""
echo "📊 Database:"
echo "   Host: db:3306"
echo "   Name: chapeus_wordpress"
echo "   User: chapeus_user"
echo "   Pass: chapeus_pass_2024"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "🎯 Próximo passo: Executar import_produtos_local.py"
echo ""
