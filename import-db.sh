#!/bin/bash

echo "🔄 Aguardando MySQL iniciar..."
sleep 20

echo "📦 Importando base de dados..."
docker exec -i chapeus_mysql mysql -u root -prootpassword lisboetas_web < database-backup.sql

if [ $? -eq 0 ]; then
    echo "✅ Base de dados importada com sucesso!"
else
    echo "❌ Erro ao importar base de dados"
    exit 1
fi

echo "🔧 Ajustando URLs na base de dados..."
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "UPDATE lx_options SET option_value = 'http://localhost:8080' WHERE option_name = 'siteurl';"
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "UPDATE lx_options SET option_value = 'http://localhost:8080' WHERE option_name = 'home';"

echo "✅ URLs atualizados para localhost:8080"
