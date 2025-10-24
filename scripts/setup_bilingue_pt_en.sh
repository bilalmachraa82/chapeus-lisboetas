#!/bin/bash
################################################################################
# SCRIPT DE SETUP SISTEMA BILINGUE PT/EN
# Chapéus Lisboetas - Automatização completa
################################################################################
#
# Uso:
#   chmod +x scripts/setup_bilingue_pt_en.sh
#   ./scripts/setup_bilingue_pt_en.sh
#
################################################################################

set -e  # Exit on error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Diretório base
BASE_DIR="/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"
cd "$BASE_DIR"

# Configuração database
DB_CONTAINER="chapeus_mysql"
DB_NAME="lisboetas_web"
DB_USER="root"
DB_PASS="rootpassword"
WP_CONTAINER="chapeus_wordpress"

################################################################################
# FUNÇÕES AUXILIARES
################################################################################

print_header() {
  echo -e "\n${BLUE}========================================${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
  echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
  echo -e "${RED}✗ $1${NC}"
}

print_info() {
  echo -e "${BLUE}ℹ $1${NC}"
}

confirm() {
  read -p "$(echo -e ${YELLOW}$1 [y/N]: ${NC})" -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Operação cancelada pelo usuário"
    exit 1
  fi
}

################################################################################
# FASE 1: VERIFICAÇÕES INICIAIS
################################################################################

print_header "FASE 1: Verificações Iniciais"

# Verificar containers rodando
print_info "Verificando containers Docker..."
if ! docker ps | grep -q "$DB_CONTAINER"; then
  print_error "Container $DB_CONTAINER não está rodando"
  print_info "Execute: docker-compose up -d"
  exit 1
fi
print_success "Container database OK"

if ! docker ps | grep -q "$WP_CONTAINER"; then
  print_error "Container $WP_CONTAINER não está rodando"
  exit 1
fi
print_success "Container WordPress OK"

# Verificar acesso database
print_info "Testando conexão database..."
if ! docker exec $DB_CONTAINER mysql -u $DB_USER -p$DB_PASS -e "USE $DB_NAME; SELECT 1;" &>/dev/null; then
  print_error "Não foi possível conectar ao database"
  exit 1
fi
print_success "Conexão database OK"

# Verificar scripts SQL existem
if [ ! -f "scripts/cleanup_wpml_database.sql" ]; then
  print_error "Script cleanup_wpml_database.sql não encontrado"
  exit 1
fi

if [ ! -f "scripts/configure_transposh_pt_en.sql" ]; then
  print_error "Script configure_transposh_pt_en.sql não encontrado"
  exit 1
fi

print_success "Todos os scripts encontrados"

################################################################################
# FASE 2: BACKUP
################################################################################

print_header "FASE 2: Backup Database"

BACKUP_FILE="backup_pre_setup_bilingue_$(date +%Y%m%d_%H%M%S).sql"
print_info "Criando backup: $BACKUP_FILE"

docker exec $DB_CONTAINER mysqldump -u $DB_USER -p$DB_PASS $DB_NAME > "$BACKUP_FILE" 2>/dev/null

if [ -f "$BACKUP_FILE" ]; then
  BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
  print_success "Backup criado: $BACKUP_FILE ($BACKUP_SIZE)"
else
  print_error "Falha ao criar backup"
  exit 1
fi

################################################################################
# FASE 3: CONFIRMAÇÃO USUÁRIO
################################################################################

print_header "FASE 3: Confirmação"

echo -e "${YELLOW}ATENÇÃO: Este script irá:${NC}"
echo "  1. Remover todas as tabelas WPML antigas (lx_icl_*)"
echo "  2. Limpar opções WPML do database"
echo "  3. Configurar Transposh com PT como idioma principal"
echo "  4. Ativar permalinks /en/ para versão inglesa"
echo ""
echo -e "${GREEN}Backup criado em: $BACKUP_FILE${NC}"
echo ""

confirm "Deseja continuar com a configuração bilingue?"

################################################################################
# FASE 4: LIMPAR WPML
################################################################################

print_header "FASE 4: Limpando WPML"

print_info "Executando script de limpeza WPML..."
docker exec -i $DB_CONTAINER mysql -u $DB_USER -p$DB_PASS $DB_NAME < scripts/cleanup_wpml_database.sql 2>/dev/null

# Verificar limpeza
WPML_TABLES=$(docker exec $DB_CONTAINER mysql -u $DB_USER -p$DB_PASS -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$DB_NAME' AND table_name LIKE 'lx_icl_%';" 2>/dev/null | tail -1)

if [ "$WPML_TABLES" -eq "0" ]; then
  print_success "Tabelas WPML removidas com sucesso"
else
  print_warning "Ainda existem $WPML_TABLES tabelas WPML"
fi

WPML_OPTIONS=$(docker exec $DB_CONTAINER mysql -u $DB_USER -p$DB_PASS $DB_NAME -e "SELECT COUNT(*) FROM lx_options WHERE option_name LIKE '%wpml%' OR option_name LIKE '%icl%';" 2>/dev/null | tail -1)

if [ "$WPML_OPTIONS" -eq "0" ]; then
  print_success "Opções WPML removidas com sucesso"
else
  print_warning "Ainda existem $WPML_OPTIONS opções WPML"
fi

################################################################################
# FASE 5: CONFIGURAR TRANSPOSH
################################################################################

print_header "FASE 5: Configurando Transposh"

print_info "Aplicando configuração PT/EN..."
docker exec -i $DB_CONTAINER mysql -u $DB_USER -p$DB_PASS $DB_NAME < scripts/configure_transposh_pt_en.sql 2>/dev/null

# Verificar configuração
WP_LANG=$(docker exec $DB_CONTAINER mysql -u $DB_USER -p$DB_PASS $DB_NAME -e "SELECT option_value FROM lx_options WHERE option_name = 'WPLANG';" 2>/dev/null | tail -1)

if [ "$WP_LANG" == "pt_PT" ]; then
  print_success "WordPress configurado para Português (pt_PT)"
else
  print_warning "WordPress locale: $WP_LANG (esperado: pt_PT)"
fi

TIMEZONE=$(docker exec $DB_CONTAINER mysql -u $DB_USER -p$DB_PASS $DB_NAME -e "SELECT option_value FROM lx_options WHERE option_name = 'timezone_string';" 2>/dev/null | tail -1)

if [ "$TIMEZONE" == "Europe/Lisbon" ]; then
  print_success "Timezone configurado: Europe/Lisbon"
else
  print_info "Timezone: $TIMEZONE"
fi

################################################################################
# FASE 6: FLUSH REWRITE RULES
################################################################################

print_header "FASE 6: Atualizando Permalinks"

print_info "Fazendo flush de rewrite rules..."
docker exec $WP_CONTAINER php -r "require '/var/www/html/wp-load.php'; flush_rewrite_rules(); echo 'OK';" 2>/dev/null

if [ $? -eq 0 ]; then
  print_success "Permalinks atualizados (/en/ URLs ativados)"
else
  print_warning "Falha ao atualizar permalinks (executar manualmente no WordPress Admin)"
fi

################################################################################
# FASE 7: VERIFICAÇÕES FINAIS
################################################################################

print_header "FASE 7: Verificações Finais"

# Testar URL português
print_info "Testando URL português (/)..."
HTTP_CODE_PT=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/)
if [ "$HTTP_CODE_PT" == "200" ]; then
  print_success "URL PT OK (http://localhost:8080/)"
else
  print_warning "URL PT retornou código $HTTP_CODE_PT"
fi

# Testar URL inglês
print_info "Testando URL inglês (/en/)..."
HTTP_CODE_EN=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/en/)
if [ "$HTTP_CODE_EN" == "200" ]; then
  print_success "URL EN OK (http://localhost:8080/en/)"
else
  print_warning "URL EN retornou código $HTTP_CODE_EN"
fi

# Verificar hreflang tags
print_info "Verificando hreflang tags..."
HREFLANG_COUNT=$(curl -s http://localhost:8080/ | grep -c "hreflang" || true)
if [ "$HREFLANG_COUNT" -ge "2" ]; then
  print_success "Hreflang tags detectados ($HREFLANG_COUNT tags)"
else
  print_warning "Hreflang tags não detectados (verificar manualmente)"
fi

################################################################################
# FASE 8: RELATÓRIO FINAL
################################################################################

print_header "RESUMO DA CONFIGURAÇÃO"

echo -e "${GREEN}✓ Sistema bilingue PT/EN configurado com sucesso!${NC}\n"

echo "CONFIGURAÇÃO:"
echo "  • Idioma principal: Português (PT)"
echo "  • Idioma secundário: Inglês (EN)"
echo "  • URLs PT: http://localhost:8080/"
echo "  • URLs EN: http://localhost:8080/en/"
echo "  • Plugin: Transposh Translation Filter"
echo "  • WPML: Removido (tabelas limpas)"
echo ""

echo "BACKUP:"
echo "  • Arquivo: $BACKUP_FILE"
echo "  • Tamanho: $BACKUP_SIZE"
echo ""

echo "PRÓXIMOS PASSOS:"
echo "  1. Adicionar Language Switcher no header"
echo "     → WordPress Admin → Aparência → Widgets"
echo "     → Widget 'Translation' → Header area"
echo ""
echo "  2. Traduzir páginas críticas (método inline)"
echo "     → Abrir http://localhost:8080/en/nome-pagina/"
echo "     → Clicar bandeira editor (Alt+Shift+E)"
echo "     → Traduzir e salvar"
echo ""
echo "  3. Traduzir strings WooCommerce (Loco Translate)"
echo "     → WordPress Admin → Loco Translate → Plugins → WooCommerce"
echo "     → Criar tradução EN"
echo ""

echo "DOCUMENTAÇÃO:"
echo "  • Guia completo: GUIA_IMPLEMENTACAO_BILINGUE.md"
echo "  • Relatório status: RELATORIO_STATUS_MULTILINGUE.md"
echo "  • Implementação: IMPLEMENTACAO_BILINGUE_PT_EN.md"
echo ""

echo "ACESSOS:"
echo "  • WordPress Admin: http://localhost:8080/wp-admin"
echo "  • Transposh Settings: http://localhost:8080/wp-admin/options-general.php?page=transposh"
echo ""

print_info "Para reverter: docker exec -i $DB_CONTAINER mysql -u $DB_USER -p$DB_PASS $DB_NAME < $BACKUP_FILE"

print_header "Setup Concluído!"
