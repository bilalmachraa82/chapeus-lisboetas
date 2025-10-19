#!/usr/bin/env python3
"""
Importar produtos para WordPress LOCAL via WooCommerce REST API
"""

import json
import requests
from pathlib import Path
from tqdm import tqdm
import time
from requests.auth import HTTPBasicAuth
import sys

# ============================================================================
# CONFIGURAÇÃO AUTOMÁTICA (Docker Local)
# ============================================================================

WORDPRESS_URL = "http://localhost:8080"
WC_API_URL = f"{WORDPRESS_URL}/wp-json/wc/v3"

# Credenciais padrão (criadas pelo setup)
WC_USERNAME = "admin"
WC_PASSWORD = "ChapeusAdmin2024!"

# Ou via application password (vamos gerar)
WC_CONSUMER_KEY = ""
WC_CONSUMER_SECRET = ""

INPUT_FILE = Path("catalog_completo_classificado.json")


class WooCommerceLocalImporter:
    def __init__(self, url, username, password):
        self.url = url
        self.wordpress_url = WORDPRESS_URL
        self.session = requests.Session()
        
        # Não usar autenticação - WooCommerce API aceita sem auth no local
        # self.session.auth = HTTPBasicAuth(username, password)
        self.session.headers.update({
            'User-Agent': 'ChapeusImporter/1.0',
            'Content-Type': 'application/json'
        })
        self.session.params = {
            'consumer_key': username,
            'consumer_secret': password
        }
    
    def test_connection(self):
        """Testar conexão com WordPress"""
        try:
            # Testar se WordPress está up
            response = requests.get(self.wordpress_url, timeout=5)
            if response.status_code != 200:
                return False, f"WordPress não responde: {response.status_code}"
            
            # Testar API WooCommerce
            response = self.session.get(f"{self.url}/products", params={"per_page": 1})
            
            if response.status_code == 200:
                return True, "Conexão OK!"
            elif response.status_code == 401:
                return False, "Credenciais inválidas"
            elif response.status_code == 404:
                return False, "WooCommerce REST API não encontrada (WooCommerce instalado?)"
            else:
                return False, f"Erro: {response.status_code} - {response.text[:200]}"
        
        except requests.exceptions.ConnectionError:
            return False, "Não consegue conectar ao WordPress. Docker está rodando?"
        except Exception as e:
            return False, f"Erro: {e}"
    
    def get_or_create_category(self, category_name, parent_id=0):
        """Obter ou criar categoria"""
        # Procurar categoria existente
        params = {"search": category_name, "parent": parent_id}
        
        try:
            response = self.session.get(f"{self.url}/products/categories", params=params)
            
            if response.status_code == 200:
                categories = response.json()
                for cat in categories:
                    if cat['name'].lower() == category_name.lower():
                        return cat['id']
            
            # Criar nova categoria
            data = {"name": category_name, "parent": parent_id}
            response = self.session.post(f"{self.url}/products/categories", json=data)
            
            if response.status_code == 201:
                return response.json()['id']
            else:
                print(f"   ⚠️  Erro criar categoria '{category_name}': {response.text[:100]}")
                return None
        
        except Exception as e:
            print(f"   ⚠️  Exceção ao criar categoria: {e}")
            return None
    
    def get_categories_hierarchy(self, genero, tipo):
        """Criar hierarquia de categorias e retornar IDs"""
        category_ids = []
        
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
        
        # Categoria principal
        if tipo == "bone":
            main_cat_id = self.get_or_create_category("Bonés")
            if main_cat_id:
                category_ids.append(main_cat_id)
        else:
            main_cat_id = self.get_or_create_category("Chapéus")
            
            if genero != "unisex" and genero in genero_map:
                genero_cat_id = self.get_or_create_category(genero_map[genero], main_cat_id)
                if genero_cat_id:
                    category_ids.append(genero_cat_id)
                    
                    if tipo in tipo_map:
                        tipo_cat_id = self.get_or_create_category(tipo_map[tipo], genero_cat_id)
                        if tipo_cat_id:
                            category_ids.append(tipo_cat_id)
            else:
                if tipo in tipo_map:
                    tipo_cat_id = self.get_or_create_category(tipo_map[tipo], main_cat_id)
                    if tipo_cat_id:
                        category_ids.append(tipo_cat_id)
        
        return category_ids
    
    def upload_image(self, image_path):
        """Upload de imagem para WordPress"""
        if not Path(image_path).exists():
            return None
        
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            filename = Path(image_path).name
            
            files = {
                'file': (filename, image_data, 'image/jpeg')
            }
            
            response = self.session.post(
                f"{self.wordpress_url}/wp-json/wp/v2/media",
                files=files
            )
            
            if response.status_code == 201:
                return response.json()['id']
            else:
                return None
        
        except Exception as e:
            return None
    
    def create_product(self, product_data):
        """Criar produto no WooCommerce"""
        try:
            response = self.session.post(f"{self.url}/products", json=product_data)
            
            if response.status_code == 201:
                return True, response.json()
            else:
                return False, response.text[:200]
        
        except Exception as e:
            return False, str(e)
    
    def import_product(self, product_info, index):
        """Importar um produto completo"""
        classification = product_info.get('classification', {})
        
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
        
        # Dados do produto
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
            "tags": [{"name": str(tag)} for tag in tags[:5]],  # Limitar tags
            "weight": "0.2",
            "attributes": []
        }
        
        if image_id:
            product_data["images"] = [{"id": image_id}]
        
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
        
        success, result = self.create_product(product_data)
        return success, result


def main():
    print("=" * 70)
    print("🚀 Importador WordPress LOCAL - Chapéus Lisboetas")
    print("=" * 70)
    print()
    
    print(f"🌐 WordPress: {WORDPRESS_URL}")
    print(f"🔑 User: {WC_USERNAME}")
    print()
    
    # Inicializar importer
    importer = WooCommerceLocalImporter(WC_API_URL, WC_USERNAME, WC_PASSWORD)
    
    # Testar conexão
    print("🔌 Testando conexão...")
    success, message = importer.test_connection()
    
    if not success:
        print(f"❌ {message}")
        print()
        print("💡 Troubleshooting:")
        print("   1. Docker está rodando? → docker ps")
        print("   2. WordPress instalado? → Abrir http://localhost:8080")
        print("   3. WooCommerce ativo? → Verificar plugins")
        print()
        sys.exit(1)
    
    print(f"✅ {message}")
    print()
    
    # Carregar produtos
    if not INPUT_FILE.exists():
        print(f"❌ Arquivo não encontrado: {INPUT_FILE}")
        sys.exit(1)
    
    print(f"📂 Carregando: {INPUT_FILE}")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data.get('products', [])
    print(f"✅ {len(products)} produtos carregados")
    print()
    
    # Confirmação
    print("⚠️  Vai importar 180 produtos (pode demorar ~30 min)")
    response = input("Continuar? (s/n): ").strip().lower()
    
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Cancelado")
        return
    
    print()
    print("🚀 Importando...")
    print()
    
    # Importar
    imported = 0
    failed = 0
    
    for idx, product in enumerate(tqdm(products, desc="Importing"), 1):
        try:
            success, result = importer.import_product(product, idx)
            
            if success:
                imported += 1
                nome = result.get('name', 'N/A')
                if idx % 10 == 0:  # Mostrar progresso a cada 10
                    tqdm.write(f"   ✅ [{idx}/{len(products)}] {nome}")
            else:
                failed += 1
                if failed <= 5:  # Mostrar primeiros 5 erros
                    tqdm.write(f"   ❌ [{idx}/{len(products)}] Erro: {result[:80]}")
            
            time.sleep(0.3)  # Rate limiting suave
        
        except Exception as e:
            failed += 1
            tqdm.write(f"   ❌ [{idx}/{len(products)}] Exceção: {str(e)[:80]}")
    
    # Resumo
    print()
    print("=" * 70)
    print("✅ IMPORTAÇÃO COMPLETA!")
    print("=" * 70)
    print()
    print(f"📊 Resultados:")
    print(f"   • Importados: {imported}")
    print(f"   • Falharam: {failed}")
    print(f"   • Total: {len(products)}")
    print(f"   • Taxa sucesso: {imported/len(products)*100:.1f}%")
    print()
    print(f"🌐 Ver produtos: {WORDPRESS_URL}/wp-admin/edit.php?post_type=product")
    print(f"🛒 Ver loja: {WORDPRESS_URL}/shop")
    print()


if __name__ == "__main__":
    main()
