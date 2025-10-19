# 🚀 Setup WordPress SIMPLES - Para Quem Não Sabe Técnico

## 📋 O QUE TENS:
- ✅ Template Flatsome (tema e-commerce profissional)
- ✅ 180 fotos classificadas
- ✅ CSV pronto para importar
- ✅ Acesso cPanel

---

## 🎯 MÉTODO MAIS SIMPLES (Sem API, Sem Código)

### **PASSO 1: Instalar WordPress no cPanel (10 min)**

1. **Login cPanel:**
   ```
   URL: www.chapeuslisboetas.com/cpanel
   User: chapeuslisboetas
   Pass: vo5P^.2ioSLj
   ```

2. **Procurar "Softaculous" ou "WordPress Installer"**
   - É um ícone com símbolo WordPress
   - Ou procurar "Install WordPress" na barra de pesquisa

3. **Click "Install Now"**

4. **Preencher formulário:**
   ```
   Choose Domain: www.chapeuslisboetas.com
   Directory: (deixar vazio para instalar na raiz)
   
   Site Name: Chapéus Lisboetas
   Site Description: Chapelaria Artesanal Portuguesa
   
   Admin Username: admin_chapeus (GUARDAR!)
   Admin Password: [Criar senha forte] (GUARDAR!)
   Admin Email: teu@email.com
   
   Language: Portuguese (pt_PT)
   ```

5. **Click "Install"**
   - Aguardar 2-3 minutos
   - Vai aparecer URLs:
     ```
     Site: https://www.chapeuslisboetas.com
     Admin: https://www.chapeuslisboetas.com/wp-admin
     ```

6. **GUARDAR estas credenciais!**

---

### **PASSO 2: Instalar WooCommerce (5 min)**

1. **Login WordPress:**
   ```
   URL: https://www.chapeuslisboetas.com/wp-admin
   User: admin_chapeus (que criaste)
   Pass: [tua senha]
   ```

2. **Menu lateral: Plugins → Add New**

3. **Procurar: "WooCommerce"**
   - É o primeiro resultado (oficial)
   - 5+ milhões de instalações

4. **Click "Install Now"**
   - Depois: "Activate"

5. **WooCommerce Setup Wizard:**
   ```
   Página 1 - Store Details:
   ✓ Address: [tua morada]
   ✓ City: Lisboa
   ✓ Country: Portugal
   ✓ Currency: Euro (EUR)
   
   Página 2 - Industry:
   ✓ Fashion, apparel, and accessories
   
   Página 3 - Product Types:
   ✓ Physical products
   
   Página 4 - Business Details:
   ✓ Selling on site (não em redes sociais)
   
   Página 5 - Theme:
   → Skip (vamos instalar Flatsome)
   
   Página 6 - Complete!
   ```

---

### **PASSO 3: Instalar Tema Flatsome (10 min)**

#### Opção A: Via cPanel (Mais fácil)

1. **Voltar ao cPanel**

2. **File Manager:**
   - Navegar: `/public_html/wp-content/themes/`

3. **Upload:**
   - Click "Upload"
   - Selecionar: `flatsome_v3.20.2_package.zip`
   - Aguardar upload

4. **Extrair:**
   - Voltar File Manager
   - Right-click no ficheiro .zip
   - "Extract"
   - Delete o .zip depois

5. **Ativar no WordPress:**
   - WordPress → Appearance → Themes
   - Ver "Flatsome"
   - Click "Activate"

#### Opção B: Via WordPress Admin (Alternativa)

1. **WordPress → Appearance → Themes → Add New**

2. **Upload Theme:**
   - Click "Upload Theme"
   - Choose File: `flatsome_v3.20.2_package.zip`
   - Install Now
   - Activate

---

### **PASSO 4: Upload Fotos (15 min)**

1. **WordPress → Media → Add New**

2. **Arrastar pastas:**
   ```
   - processed_images/professional/fotos site1/
   - processed_images/professional/fotos site2/
   - processed_images/professional/CLOCHE/
   - processed_images/professional/PALHA/
   - processed_images/professional/PROTEÇÃO UV/
   - processed_images/professional/VISEIRA/
   ```

3. **Aguardar upload de 180 imagens**
   - Pode demorar 10-15 min dependendo da internet

4. **Verificar:**
   - Media → Library
   - Deve ter ~180 imagens

---

### **PASSO 5: Importar Produtos via CSV (10 min)**

1. **WordPress → WooCommerce → Products**

2. **Click "Import"** (topo da página)

3. **Choose File:**
   - Selecionar: `woocommerce_import_180_produtos.csv`
   - Click "Continue"

4. **Column Mapping:**
   - WooCommerce vai mapear automaticamente
   - Verificar se está tudo OK
   - Click "Run the importer"

5. **Aguardar importação:**
   - Progress bar: 0/180... 50/180... 180/180
   - Pode demorar 5-10 minutos

6. **Success!**
   - Click "View Products"
   - Deve ver 180 produtos

---

### **PASSO 6: Associar Imagens aos Produtos**

**Problema:** Imagens podem não associar automaticamente.

#### Solução Fácil: Plugin

1. **Plugins → Add New**

2. **Procurar: "Auto Upload Images"**
   - Ou "Product Image Association"

3. **Install + Activate**

4. **Settings:**
   - Match by: Filename
   - Run: "Process all products"

5. **Aguardar processo**
   - Vai associar imagens automaticamente

#### Solução Manual (se plugin não funcionar):

1. **Products → All Products**

2. **Para cada produto sem imagem:**
   - Edit
   - Scroll até "Product Image"
   - Set product image
   - Selecionar da Media Library
   - Update

---

### **PASSO 7: Configurar Loja (10 min)**

#### A) Páginas Essenciais:

1. **WooCommerce → Settings → Advanced:**
   - Shop page: Criar "Loja" (auto)
   - Cart page: Criar "Carrinho" (auto)
   - Checkout: Criar "Checkout" (auto)
   - My Account: Criar "A Minha Conta" (auto)

#### B) Envios:

1. **WooCommerce → Settings → Shipping:**
   ```
   Zona: Portugal
   Método: Taxa Fixa
   Custo: €5.00
   ```

2. **Adicionar mais zonas se necessário:**
   - Europa: €10
   - Resto do mundo: €20

#### C) Pagamentos:

1. **WooCommerce → Settings → Payments:**
   ```
   ✓ Transferência Bancária (ativar)
   ✓ PayPal (se tiver conta)
   ```

2. **Para Multibanco/MB Way:**
   - Instalar plugin: "IFTHENPAY" ou "Eupago"

#### D) Impostos:

1. **WooCommerce → Settings → Tax:**
   ```
   IVA Portugal: 23%
   ```

---

### **PASSO 8: Personalizar Tema Flatsome (15 min)**

1. **Appearance → Customize**

2. **Header:**
   - Upload logo (se tiver)
   - Menu: Criar menu principal
   - Cores: Ajustar ao gosto

3. **Homepage:**
   - Flatsome tem demos pré-feitas
   - Importar demo "Fashion" ou "Store"
   - Ou criar custom com Page Builder

4. **Shop Page:**
   - Customize → WooCommerce
   - Products per page: 12
   - Columns: 3 ou 4
   - Layout: Grid

5. **Colors:**
   - Primary color: Escolher cor da marca
   - Secondary: Complementar

6. **Typography:**
   - Font headers: Escolher
   - Font body: Escolher

7. **Click "Publish"**

---

### **PASSO 9: Criar Categorias Manualmente (10 min)**

1. **Products → Categories**

2. **Adicionar hierarquia:**

```
Chapéus (pai)
  ├─ Homem
  │   ├─ Boinas
  │   ├─ Fedora
  │   └─ Panama
  ├─ Mulher
  │   ├─ Capeline
  │   ├─ Cloche
  │   └─ Boinas
  └─ Unisex
      ├─ Boinas
      ├─ Fedora
      └─ Bucket Hat

Bonés (pai)
  ├─ Homem
  ├─ Mulher
  └─ Unisex

Acessórios
```

3. **Para cada categoria:**
   - Add New Category
   - Name: [nome]
   - Parent: [selecionar pai se tiver]
   - Add

---

### **PASSO 10: Atribuir Produtos às Categorias**

Se produtos não tiverem categorias após import:

1. **Products → All Products**

2. **Filtrar por tipo:**
   - Procurar "boina" na search

3. **Bulk Edit:**
   - Selecionar todos os produtos
   - Bulk Actions → Edit
   - Categories: Selecionar "Boinas"
   - Update

4. **Repetir para outros tipos**

---

### **PASSO 11: SEO Básico (10 min)**

1. **Plugins → Add New**

2. **Procurar: "Yoast SEO"**
   - Install + Activate

3. **Configuration Wizard:**
   - Seguir passos do wizard
   - Tipo site: Online store

4. **Settings automáticas:**
   - Sitemap: Ativado
   - Social: Preencher com redes sociais

5. **Google Search Console:**
   - Adicionar site
   - Submeter sitemap: seusite.com/sitemap_index.xml

---

### **PASSO 12: Testar Loja (5 min)**

#### Checklist:

```
□ Visitar homepage: Aparece bonita?
□ Visitar loja: /shop - Produtos aparecem?
□ Clicar num produto: Imagem OK? Preço OK?
□ Adicionar ao carrinho: Funciona?
□ Ver carrinho: Produto está lá?
□ Checkout: Formulário funciona?
□ Testar métodos pagamento
□ Mobile: Site é responsive?
```

---

### **PASSO 13: GO LIVE! (5 min)**

1. **Settings → Reading:**
   - Desmarcar: "Discourage search engines"

2. **Settings → Permalinks:**
   - Selecionar: "Post name"
   - Save

3. **WooCommerce → Status:**
   - Verificar que está tudo verde

4. **Testar compra completa:**
   - Do início ao fim
   - Com email de teste

5. **Anunciar!**
   - Instagram
   - Facebook
   - Newsletter

---

## 🆘 PROBLEMAS COMUNS

### Site não abre depois de instalar:
```
- Verificar DNS apontado para servidor
- Pode demorar 24h propagação DNS
- Testar: www.chapeuslisboetas.com E chapeuslisboetas.com
```

### Imagens não fazem upload:
```
cPanel → File Manager:
- Navegar: /public_html/wp-content/uploads
- Right-click → Permissions
- Mudar para: 755
- Apply to subfolders
```

### Tema não ativa:
```
- Verificar se extraiu corretamente
- Pasta deve ser: /wp-content/themes/flatsome
- Não: /wp-content/themes/flatsome_v3.20.2_package
```

### Produtos sem preço:
```
- Edit produto
- Scroll até "Product data"
- Regular price: Preencher
- Update
```

### Checkout não funciona:
```
- WooCommerce → Settings → Payments
- Ativar pelo menos um método
- Transferência bancária: Sempre funciona
```

---

## 💡 ALTERNATIVA: Restaurar Backup

Se já tinhas WordPress antes:

1. **cPanel → phpMyAdmin**

2. **Import Database:**
   - Select: `database-backup.sql`
   - Import

3. **File Manager:**
   - Upload backup/wp/ para /public_html/

4. **Editar wp-config.php:**
   - Database name
   - Database user
   - Database password

---

## 📞 PRÓXIMOS PASSOS

### Depois do lançamento:

1. **Marketing:**
   - Instagram stories
   - Facebook posts
   - Google Ads

2. **Otimização:**
   - Plugin cache: WP Super Cache
   - Plugin images: Smush
   - CDN: Cloudflare

3. **Analytics:**
   - Google Analytics
   - Facebook Pixel
   - WooCommerce Reports

4. **Manutenção:**
   - Backup automático
   - Updates plugins
   - Monitor vendas

---

## ✅ RESUMO RÁPIDO

```
1. Instalar WordPress (cPanel Softaculous)
2. Instalar WooCommerce (Plugin)
3. Instalar Flatsome (Upload ZIP)
4. Upload 180 fotos (Media Library)
5. Import CSV (WooCommerce → Products → Import)
6. Associar imagens (Plugin ou manual)
7. Configurar loja (Envios, Pagamentos)
8. Personalizar design (Flatsome Customizer)
9. Criar categorias (Products → Categories)
10. Testar compra completa
11. GO LIVE!
```

**Tempo total: 2-3 horas** (para quem nunca fez)
**Custo: €0** (já tens hosting e tema)

---

## 🎉 DICAS FINAIS

✅ **Fazer backup antes de tudo**
✅ **Testar em mobile também**
✅ **Não pular passo de configurar pagamentos**
✅ **Ter paciência com upload das imagens**
✅ **Se algo falhar, restaurar backup e tentar outra vez**

**Boa sorte! 🚀**

Se tiveres dúvidas em algum passo específico, posso criar guia mais detalhado para esse passo!
