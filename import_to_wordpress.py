#!/usr/bin/env python3
"""
Importar produtos diretamente para WordPress/WooCommerce via REST API
"""

import json
import requests
from pathlib import Path
from tqdm import tqdm
import time
from requests.auth import HTTPBasicAuth
import base64

# ============================================================================
# CONFIGURAÇÃO - EDITAR AQUI!
# ============================================================================

WORDPRESS_URL = "https://seusite.com"  # URL do WordPress (sem trailing slash)
WC_CONSUMER_KEY = "ck_xxxxxxxxxxxxxxxxxxxxx"  # WooCommerce API Key
WC_CONSUMER_SECRET = "cs_xxxxxxxxxxxxxxxxxxxxx"  # WooCommerce API Secret

# ============================================================================
# NÃO EDITAR ABAIXO (a menos que saiba o que está fazendo)
# ============================================================================

API_URL = f"{WORDPRESS_URL}/wp-json/wc/v3"
INPUT_FILE = Path("catalog_completo_classificado.json")


class WooCommerceImporter:
    def __init__(self, url, consumer_key, consumer_secret):
        self.url = url
        self.auth = HTTPBasicAuth(consumer_key, consumer_secret)
        self.session = requests.Session()
        self.session.auth = self.auth
        
    def test_connection(self):
        """Testar conexão com API"""
        try:
            response = self.session.get(f"{self.url}/products", params={"per_page": 1})
            if response.status_code == 200:
                return True, "Conexão OK!"
            else:
                return False, f"Erro: {response.status_code} - {response.text}"
        except Exception as e:
            return False, f"Erro de conexão: {e}"
    
    def get_or_create_category(self, category_name, parent_id=0):
        """Obter ou criar categoria"""
        # Procurar categoria existente
        params = {
            "search": category_name,
            "parent": parent_id
        }
        response = self.session.get(f"{self.url}/products/categories", params=params)
        
        if response.status_code == 200:
            categories = response.json()
            for cat in categories:
                if cat['name'].lower() == category_name.lower():
                    return cat['id']
        
        # Criar nova categoria
        data = {
            "name": category_name,
            "parent": parent_id
        }
        response = self.session.post(f"{self.url}/products/categories", json=data)
        
        if response.status_code == 201:
            return response.json()['id']
        else:
            print(f"   ⚠️  Erro ao criar categoria '{category_name}': {response.text}")
            return None
    
    def get_categories_hierarchy(self, genero, tipo):
        """Criar hierarquia de categorias e retornar IDs"""
        category_ids = []
        
        # Mapeamento de tipos
        tipo_map = {
            "boina": "Boinas",
            "chapeu-fedora": "Fedora",
            "chapeu-panama": "Panama",
            "bone": "Bonés",
            "bucket-hat": "Bucket Hat",
            "capeline": "Capeline",
            "gorro": "Gorros",
            "cartola": "Cartola",
            "trilby": "Trilby",
            "outros": "Acessórios"
        }
        
        genero_map = {
            "homem": "Homem",
            "mulher": "Mulher",
            "crianca": "Criança",
            "unisex": "Unisex"
        }
        
        # Categoria principal: Chapéus ou Bonés
        if tipo == "bone":
            main_cat_id = self.get_or_create_category("Bonés")
            if main_cat_id:
                category_ids.append(main_cat_id)
        else:
            main_cat_id = self.get_or_create_category("Chapéus")
            
            # Sub-categoria por género (se não for unisex)
            if genero != "unisex" and genero in genero_map:
                genero_cat_id = self.get_or_create_category(genero_map[genero], main_cat_id)
                if genero_cat_id:
                    category_ids.append(genero_cat_id)
                    
                    # Tipo dentro do género
                    if tipo in tipo_map:
                        tipo_cat_id = self.get_or_create_category(tipo_map[tipo], genero_cat_id)
                        if tipo_cat_id:
                            category_ids.append(tipo_cat_id)
            else:
                # Unisex: Tipo direto sob Chapéus
                if tipo in tipo_map:
                    tipo_cat_id = self.get_or_create_category(tipo_map[tipo], main_cat_id)
                    if tipo_cat_id:
                        category_ids.append(tipo_cat_id)
        
        return category_ids
    
    def upload_image(self, image_path):
        """Upload de imagem para WordPress Media Library"""
        if not Path(image_path).exists():
            print(f"   ⚠️  Imagem não encontrada: {image_path}")
            return None
        
        try:
            # Ler imagem
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Preparar upload
            filename = Path(image_path).name
            
            headers = {
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'image/jpeg'
            }
            
            # Upload
            response = self.session.post(
                f"{WORDPRESS_URL}/wp-json/wp/v2/media",
                headers=headers,
                data=image_data
            )
            
            if response.status_code == 201:
                return response.json()['id']
            else:
                print(f"   ⚠️  Erro ao fazer upload: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"   ⚠️  Erro no upload: {e}")
            return None
    
    def create_product(self, product_data):
        """Criar produto no WooCommerce"""
        response = self.session.post(f"{self.url}/products", json=product_data)
        
        if response.status_code == 201:
            return True, response.json()
        else:
            return False, response.text
    
    def import_product(self, product_info, index):
        """Importar um produto completo"""
        classification = product_info.get('classification', {})
        
        # Dados básicos
        tipo = classification.get('tipo', 'outros')
        genero = classification.get('genero', 'unisex')
        nome = classification.get('nome_produto', f'Produto {index}')
        desc_curta = classification.get('descricao_curta', '')
        desc_longa = classification.get('descricao_longa', '')
        preco = str(classification.get('preco_sugerido_eur', 45))
        stock = classification.get('stock_sugerido', 10)
        tags = classification.get('tags', [])
        material = classification.get('material_aparente', '')
        temporada = classification.get('temporada', '')
        
        # SKU
        tipo_code = tipo.upper().replace("-", "")[:6]
        sku = f"CL-{tipo_code}-{index:04d}"
        
        # Categorias
        category_ids = self.get_categories_hierarchy(genero, tipo)
        
        # Upload imagem
        image_path = product_info.get('file_path', '')
        image_id = None
        if image_path and Path(image_path).exists():
            image_id = self.upload_image(image_path)
        
        # Preparar dados do produto
        product_data = {
            "name": nome,
            "type": "simple",
            "sku": sku,
            "regular_price": preco,
            "description": desc_longa,
            "short_description": desc_curta,
            "manage_stock": True,
            "stock_quantity": stock,
            "stock_status": "instock",
            "categories": [{"id": cat_id} for cat_id in category_ids] if category_ids else [],
            "tags": [{"name": str(tag)} for tag in tags],
            "weight": "0.2",
            "attributes": []
        }
        
        # Adicionar imagem se fez upload
        if image_id:
            product_data["images"] = [{"id": image_id}]
        
        # Atributos
        if material:
            product_data["attributes"].append({
                "name": "Material",
                "visible": True,
                "options": [material.capitalize()]
            })
        
        if temporada:
            product_data["attributes"].append({
                "name": "Temporada",
                "visible": True,
                "options": [temporada.capitalize()]
            })
        
        # Criar produto
        success, result = self.create_product(product_data)
        
        return success, result


def main():
    print("=" * 70)
    print("🚀 WordPress/WooCommerce Importer")
    print("=" * 70)
    print()
    
    # Verificar configuração
    if "seusite.com" in WORDPRESS_URL or "xxxxx" in WC_CONSUMER_KEY:
        print("❌ ERRO: Configure as credenciais no topo do arquivo!")
        print()
        print("📝 Como obter as credenciais:")
        print()
        print("1. Login WordPress: https://seusite.com/wp-admin")
        print("2. WooCommerce → Settings → Advanced → REST API")
        print("3. Add Key:")
        print("   - Description: 'Import Script'")
        print("   - User: Seu usuário admin")
        print("   - Permissions: Read/Write")
        print("4. Generate API Key")
        print("5. Copiar:")
        print("   - Consumer Key (ck_...)")
        print("   - Consumer Secret (cs_...)")
        print("6. Editar este arquivo e colar as chaves no topo")
        print()
        return
    
    print(f"🌐 WordPress URL: {WORDPRESS_URL}")
    print(f"🔑 API Key: {WC_CONSUMER_KEY[:10]}...")
    print()
    
    # Inicializar importer
    importer = WooCommerceImporter(API_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET)
    
    # Testar conexão
    print("🔌 Testando conexão...")
    success, message = importer.test_connection()
    
    if not success:
        print(f"❌ {message}")
        print()
        print("💡 Troubleshooting:")
        print("   - Verificar URL do WordPress")
        print("   - Verificar Consumer Key e Secret")
        print("   - Verificar se WooCommerce está instalado")
        print("   - Verificar se API REST está ativada")
        return
    
    print(f"✅ {message}")
    print()
    
    # Carregar produtos
    print(f"📂 Carregando: {INPUT_FILE}")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data.get('products', [])
    print(f"✅ {len(products)} produtos carregados")
    print()
    
    # Perguntar confirmação
    print("⚠️  ATENÇÃO: Vai importar 180 produtos!")
    print()
    response = input("Continuar? (sim/não): ").strip().lower()
    
    if response not in ['sim', 's', 'yes', 'y']:
        print("❌ Importação cancelada")
        return
    
    print()
    print("🚀 Iniciando importação...")
    print()
    
    # Importar produtos
    imported = 0
    failed = 0
    
    for idx, product in enumerate(tqdm(products, desc="Importing"), 1):
        try:
            success, result = importer.import_product(product, idx)
            
            if success:
                imported += 1
                nome = result.get('name', 'N/A')
                tqdm.write(f"   ✅ [{idx}/{len(products)}] {nome}")
            else:
                failed += 1
                tqdm.write(f"   ❌ [{idx}/{len(products)}] Falhou: {result[:100]}")
            
            # Rate limiting (evitar sobrecarga do servidor)
            time.sleep(0.5)
            
        except Exception as e:
            failed += 1
            tqdm.write(f"   ❌ [{idx}/{len(products)}] Erro: {e}")
    
    # Resumo
    print()
    print("=" * 70)
    print("✅ IMPORTAÇÃO COMPLETA!")
    print("=" * 70)
    print()
    print(f"📊 Resultados:")
    print(f"   • Importados com sucesso: {imported}")
    print(f"   • Falharam: {failed}")
    print(f"   • Total: {len(products)}")
    print()
    print(f"🌐 Ver produtos: {WORDPRESS_URL}/wp-admin/edit.php?post_type=product")
    print(f"🛒 Ver loja: {WORDPRESS_URL}/shop")
    print()


if __name__ == "__main__":
    main()
