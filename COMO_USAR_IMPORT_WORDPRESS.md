# 🚀 Como Usar o Script de Importação WordPress

## 📋 PRÉ-REQUISITOS

1. **WordPress instalado** com WooCommerce ativo
2. **Acesso admin** ao WordPress
3. **Python 3** instalado no computador
4. **Internet** para conexão com o site

---

## 🔑 PASSO 1: Obter Credenciais API

### 1.1. Login no WordPress
```
https://seusite.com/wp-admin
```

### 1.2. Criar API Key
```
1. Menu lateral: WooCommerce → Settings
2. Aba superior: Advanced
3. Link: REST API
4. Botão: "Add Key"

5. Preencher formulário:
   - Description: "Import Script 180 Produtos"
   - User: [Selecionar seu usuário admin]
   - Permissions: Read/Write ✓

6. Click: "Generate API Key"
```

### 1.3. Copiar Credenciais
```
✅ Consumer Key: ck_1234567890abcdef...
✅ Consumer Secret: cs_1234567890abcdef...

⚠️ IMPORTANTE: Copiar AGORA!
   Só aparece uma vez!
   Guarda num lugar seguro.
```

---

## 📝 PASSO 2: Configurar Script

### 2.1. Abrir arquivo para editar
```bash
# No terminal:
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

# Abrir com editor:
nano import_to_wordpress.py
# ou
code import_to_wordpress.py
```

### 2.2. Editar linhas 12-14:
```python
# ANTES:
WORDPRESS_URL = "https://seusite.com"
WC_CONSUMER_KEY = "ck_xxxxxxxxxxxxxxxxxxxxx"
WC_CONSUMER_SECRET = "cs_xxxxxxxxxxxxxxxxxxxxx"

# DEPOIS (exemplo):
WORDPRESS_URL = "https://chapeuslisboetas.pt"
WC_CONSUMER_KEY = "ck_1234567890abcdef1234567890abcdef12345678"
WC_CONSUMER_SECRET = "cs_1234567890abcdef1234567890abcdef12345678"
```

### 2.3. Salvar arquivo
```
Ctrl+O (nano) ou Cmd+S (VSCode)
```

---

## 📦 PASSO 3: Instalar Dependências

```bash
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

# Instalar bibliotecas necessárias:
pip3 install requests tqdm

# ou se tiver requirements:
echo "requests>=2.31.0
tqdm>=4.66.0" > requirements-import.txt

pip3 install -r requirements-import.txt
```

---

## 🚀 PASSO 4: Executar Importação

### 4.1. Comando:
```bash
python3 import_to_wordpress.py
```

### 4.2. Output esperado:
```
======================================================================
🚀 WordPress/WooCommerce Importer
======================================================================

🌐 WordPress URL: https://chapeuslisboetas.pt
🔑 API Key: ck_1234567...

🔌 Testando conexão...
✅ Conexão OK!

📂 Carregando: catalog_completo_classificado.json
✅ 180 produtos carregados

⚠️  ATENÇÃO: Vai importar 180 produtos!

Continuar? (sim/não): sim

🚀 Iniciando importação...

Importing:   0%|          | 0/180 [00:00<?, ?it/s]
   ✅ [1/180] Boné Militar Verde Algodão Ajustável
   ✅ [2/180] Boné Estilo Militar Verde Algodão
   ✅ [3/180] Boné Militar Preto Unissexo
   ...
Importing: 100%|██████████| 180/180 [15:00<00:00,  5.00s/it]

======================================================================
✅ IMPORTAÇÃO COMPLETA!
======================================================================

📊 Resultados:
   • Importados com sucesso: 180
   • Falharam: 0
   • Total: 180

🌐 Ver produtos: https://chapeuslisboetas.pt/wp-admin/edit.php?post_type=product
🛒 Ver loja: https://chapeuslisboetas.pt/shop
```

### 4.3. Tempo estimado:
```
⏱️ 15-30 minutos para 180 produtos
   (depende da velocidade do servidor e internet)
```

---

## ✅ PASSO 5: Verificar Importação

### 5.1. No WordPress Admin:
```
Products → All Products

Deve ver: 180 produtos listados
```

### 5.2. Na Loja:
```
Visitar: https://seusite.com/shop

Deve ver: Grid com produtos
```

### 5.3. Checklist:
```
□ Produtos aparecem na lista
□ Nomes corretos
□ Preços corretos (€35-85)
□ Categorias atribuídas
□ Imagens carregadas (se upload funcionou)
□ Stock definido (10 unidades)
```

---

## 🔧 TROUBLESHOOTING

### ❌ Erro: "Configure as credenciais"
```
Problema: Não editou o arquivo com API keys
Solução: Voltar ao Passo 2.2 e configurar
```

### ❌ Erro: "Connection refused" ou "401 Unauthorized"
```
Problema: Credenciais erradas ou URL incorreto
Solução: 
  1. Verificar URL (https:// correto?)
  2. Verificar Consumer Key (completo?)
  3. Verificar Consumer Secret (completo?)
  4. Gerar novas credenciais se necessário
```

### ❌ Erro: "404 Not Found"
```
Problema: WooCommerce não instalado ou API desativada
Solução:
  1. Instalar/ativar WooCommerce
  2. WooCommerce → Settings → Advanced → REST API
  3. Verificar se permalinks estão configurados
     (Settings → Permalinks → Post name)
```

### ❌ Erro: "Module not found: requests"
```
Problema: Falta instalar dependências
Solução: pip3 install requests tqdm
```

### ⚠️ Produtos importaram mas sem imagens
```
Problema: Paths das imagens não encontrados
Solução:
  1. Verificar se processed_images/ existe
  2. Upload manual das imagens depois
  3. Ou usar plugin "Auto Upload Images"
```

### ⚠️ Importação lenta (>1min por produto)
```
Problema: Servidor lento ou upload de imagens grande
Solução:
  1. Comentar linha do upload de imagens (linha ~150)
  2. Fazer upload manual depois
  3. Ou aumentar rate limiting (linha 350)
```

### ❌ Erro: "Memory exhausted"
```
Problema: Servidor com pouca memória
Solução:
  1. Importar em lotes menores
  2. Editar script: products[:50] para primeiros 50
  3. Rodar 4x (50, depois [50:100], etc)
```

---

## 🎯 OPÇÕES AVANÇADAS

### Importar apenas 10 produtos (teste):
```python
# Editar linha ~340, antes do for:
products = products[:10]  # Apenas primeiros 10
```

### Desativar upload de imagens (mais rápido):
```python
# Comentar linhas ~145-150:
# image_id = None
# if image_path and Path(image_path).exists():
#     image_id = self.upload_image(image_path)
```

### Mudar rate limiting (velocidade):
```python
# Linha ~350:
time.sleep(0.5)  # Pausa entre produtos

# Mais rápido (mas pode sobrecarregar):
time.sleep(0.1)

# Mais lento (mais seguro):
time.sleep(2)
```

### Importar apenas categoria específica:
```python
# Antes do for, filtrar:
products = [p for p in products 
            if p['classification'].get('tipo') == 'boina']
```

---

## 📊 DEPOIS DA IMPORTAÇÃO

### 1. Verificar Categorias:
```
Products → Categories
→ Deve ter hierarquia criada automaticamente
```

### 2. Ajustar Preços:
```
Products → All Products
→ Quick Edit para ajustes rápidos
→ Ou Bulk Edit para mudanças em massa
```

### 3. Produtos Destacados:
```
Selecionar 5-10 melhores
→ Quick Edit → Featured ✓
```

### 4. SEO:
```
Instalar Yoast SEO
→ Bulk Editor para otimizar títulos/descrições
```

### 5. Imagens:
```
Se não fez upload automático:
→ Plugins → Add New → "Auto Upload Images"
→ Ou upload manual via Media Library
```

---

## 🔐 SEGURANÇA

### Depois da importação:
```
1. Deletar ou revogar API Key:
   WooCommerce → Settings → Advanced → REST API
   → Delete/Revoke key "Import Script"

2. Ou mudar permissões:
   → Edit → Permissions: Read Only

3. Nunca commitar arquivo com credenciais:
   git add import_to_wordpress.py  # ❌ NÃO!
```

### Backup antes:
```
1. WordPress → Tools → Export
   → Export All

2. Ou plugin: UpdraftPlus
   → Backup Now

3. Se algo der errado, restaurar backup
```

---

## 💡 DICAS

✅ **Fazer primeiro teste com 10 produtos**
✅ **Fazer backup antes da importação completa**
✅ **Verificar credenciais 2x antes de rodar**
✅ **Monitorar primeira importação (não sair do terminal)**
✅ **Se falhar, verificar logs: WooCommerce → Status → Logs**

---

## 🆘 SUPORTE

Se algo não funcionar:

1. **Verificar error logs:**
   ```
   WooCommerce → Status → Logs
   → Procurar erros recentes
   ```

2. **WordPress Debug:**
   ```
   wp-config.php:
   define('WP_DEBUG', true);
   define('WP_DEBUG_LOG', true);
   
   Ver: /wp-content/debug.log
   ```

3. **Script debug:**
   ```python
   # Adicionar no import_to_wordpress.py:
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

---

## ✅ CHECKLIST FINAL

Antes de executar:

```
□ WordPress instalado e acessível
□ WooCommerce ativo
□ API Key gerada (Read/Write)
□ Consumer Key copiado
□ Consumer Secret copiado
□ Script editado com credenciais
□ Dependências instaladas (requests, tqdm)
□ Backup feito (opcional mas recomendado)
□ Terminal aberto na pasta correta
□ Internet estável
□ Tempo disponível (15-30 min)
```

**Pronto? Executar:**
```bash
python3 import_to_wordpress.py
```

🚀 **BOA SORTE!**
