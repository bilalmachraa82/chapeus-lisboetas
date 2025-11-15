# RESUMO FINAL - Integração Fotos AI

## ESTADO ATUAL (13 Nov 2025 - 15:15)

### ✅ COMPLETADO COM SUCESSO

1. **Registar 351 fotos AI no WordPress**
   - IDs: 214474-214824
   - Todas registadas na tabela `lx_posts` como attachments
   - Status: inherit (correto)

2. **Matching de fotos a produtos** 
   - 24 produtos matched por extração de SKU (60%)
   - 8 produtos matched manualmente (Dockers Miki + Impermeáveis)
   - **TOTAL: 32 produtos com fotos AI ligadas** ✓

3. **Correção de duplicate galleries**
   - 25 produtos tinham galleries duplicadas
   - 33 entradas duplicadas removidas ✓

4. **Featured images atualizadas**
   - 32 produtos com primeira imagem AI como featured ✓

5. **Metadata WordPress adicionada**
   - 351 imagens com `_wp_attachment_metadata` completo
   - Formato: PHP serialized (correto)
   - Nomes de thumbnails: corretos (img_01_pro-100x150.jpg, etc.)

### ❌ PROBLEMA CRÍTICO NÃO RESOLVIDO

**WordPress não reconhece as imagens AI como attachments válidos**

**Sintoma:**
- Base de dados MySQL: ✓ Imagens existem
- Ficheiros físicos: ✓ Existem no disco
- Metadata: ✓ Correto
- WP-CLI: ❌ "Could not find the post with ID 214627"
- Site: ❌ Mostra placeholder em vez da imagem

**Causa Provável:**
WordPress precisa de mais do que inserir na BD - precisa de **registar attachments via WordPress API** para criar:
- Object cache entries
- Metadata adicional interno
- Hooks/filters WordPress

### 📊 NÚMEROS FINAIS

- Fotos AI criadas: 351
- Fotos linkadas a produtos: 236 (32 produtos × ~7 fotos cada)
- Fotos não usadas: 115
- Produtos com fotos AI: 32 de 54 (59%)
- Custo API Gemini: ~€24

### 🔧 SCRIPTS CRIADOS

1. `simple_register_ai_images.py` - Regista imagens AI na BD
2. `match_ai_images_by_sku.py` - Match por extração de SKU
3. `manual_match_remaining.py` - Match manual de casos especiais
4. `fix_duplicate_galleries.py` - Remove galleries duplicadas
5. `set_ai_as_featured.py` - Define primeira AI como featured
6. `add_image_metadata.py` - Adiciona metadata WordPress completo

### 📋 PRÓXIMOS PASSOS NECESSÁRIOS

Para resolver o problema e fazer as imagens aparecerem:

**Opção A: Usar WordPress Media Library Uploader**
- Apagar registos da BD (IDs 214474-214824)
- Re-upload via interface WordPress admin
- WordPress criará todos os registos internos corretos
- Tempo estimado: ~30 min manual ou script automatizado

**Opção B: Usar WP-CLI Media Import** 
```bash
wp media import /path/to/image.jpg --post_id=PRODUCT_ID --featured_image
```
- Mais rápido que upload manual
- WordPress regista corretamente
- Pode ser automatizado com script

**Opção C: Regenerar com WordPress API via Plugin**
- Criar plugin temporário
- Usar `wp_insert_attachment()` função WordPress
- Garantir todos os hooks WordPress são chamados

### 💡 RECOMENDAÇÃO

**Opção B (WP-CLI Media Import)** é a melhor:
- Rápida (scriptável)
- Usa WordPress API nativa
- Sem intervenção manual
- Preserva fotos existentes

### 📝 COMANDOS ÚTEIS

```bash
# Ver imagens AI na BD
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e \
  "SELECT COUNT(*) FROM lx_posts WHERE ID BETWEEN 214474 AND 214824"

# Produtos com AI images
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e \
  "SELECT COUNT(*) FROM lx_postmeta WHERE meta_key='_thumbnail_id' AND meta_value BETWEEN 214474 AND 214824"

# Verificar metadata
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e \
  "SELECT COUNT(*) FROM lx_postmeta WHERE meta_key='_wp_attachment_metadata' AND post_id BETWEEN 214474 AND 214824"
```

### 🎯 LIÇÃO APRENDIDA

WordPress é um CMS complexo que precisa de mais do que INSERT SQL direto na base de dados. Para attachments funcionarem corretamente, precisam passar pela **WordPress Media API** que:

1. Cria registos na BD
2. Gera thumbnails físicos
3. Atualiza object cache
4. Executa hooks/filters
5. Valida MIME types
6. Cria metadata interno

**Inserir diretamente na BD = imagens invisíveis para WordPress**
