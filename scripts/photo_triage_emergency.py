#!/usr/bin/env python3
"""
PhotoTriage-Agent - Import Emergência Fotos AI
Importa 7.827 fotos AI para WordPress Media Library e associa aos produtos
Zero custo AI - usa fotos já geradas existentes

Adaptado para padrão real: img_01.jpg, img_01_pro.jpg, img_02.jpg...
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import mysql.connector
from datetime import datetime

# Configuração
BASE_DIR = Path(__file__).resolve().parent.parent
PRODUCTS_DIR = BASE_DIR / 'wordpress' / 'wp-content' / 'uploads' / 'products'
WORDPRESS_URL = "http://localhost:8080"

# Credenciais database
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'rootpassword',
    'database': 'lisboetas_web'
}

class PhotoTriageAgent:
    def __init__(self):
        self.db = None
        self.stats = {
            'scanned_folders': 0,
            'total_photos_found': 0,
            'imported_attachments': 0,
            'featured_images_set': 0,
            'galleries_updated': 0,
            'errors': [],
            'skipped_products': []
        }

    def connect_db(self):
        """Conectar à database WordPress"""
        self.db = mysql.connector.connect(**DB_CONFIG, buffered=True)
        print(f"✓ Conectado à database: {DB_CONFIG['database']}")

    def extract_sku_from_folder(self, folder_name: str) -> Optional[str]:
        """
        Extrair SKU do nome da pasta
        Exemplos:
        - "18220mi" -> "18220mi"
        - "bone-18074" -> "18074"
        - "gorro-miki-12601-gorro-640182503" -> "12601"
        """
        # Tentar match numérico simples primeiro
        match = re.search(r'\b(\d{4,6}[a-zA-Z]{0,2})\b', folder_name)
        if match:
            return match.group(1).upper()

        # Tentar match com hífen
        match = re.search(r'-(\d{4,6}[a-zA-Z]{0,2})\b', folder_name)
        if match:
            return match.group(1).upper()

        return None

    def scan_products_directory(self) -> Dict[str, Tuple[str, List[Path]]]:
        """
        Scan wordpress/wp-content/uploads/products/ para fotos AI
        Returns: {sku: (folder_path, [photo_paths])}
        """
        products_map = {}

        if not PRODUCTS_DIR.exists():
            print(f"❌ Diretório não existe: {PRODUCTS_DIR}")
            return products_map

        for category_dir in PRODUCTS_DIR.iterdir():
            if not category_dir.is_dir():
                continue

            for sku_dir in category_dir.iterdir():
                if not sku_dir.is_dir():
                    continue

                # Tentar extrair SKU do nome da pasta
                sku = self.extract_sku_from_folder(sku_dir.name)
                if not sku:
                    self.stats['skipped_products'].append(f"Não consegui extrair SKU de: {sku_dir.name}")
                    continue

                photos = []

                # Coletar fotos principais (não thumbnails)
                for photo in sku_dir.glob('*.jpg'):
                    # Skip thumbnails (têm -NNNxNNN no nome)
                    if re.search(r'-\d+x\d+\.jpg$', photo.name):
                        continue
                    # Skip se começar com ponto (ficheiros ocultos)
                    if photo.name.startswith('.'):
                        continue
                    photos.append(photo)

                for photo in sku_dir.glob('*.png'):
                    if re.search(r'-\d+x\d+\.png$', photo.name):
                        continue
                    if photo.name.startswith('.'):
                        continue
                    photos.append(photo)

                if photos:
                    products_map[sku] = (str(sku_dir), sorted(photos, key=lambda p: p.name))
                    self.stats['scanned_folders'] += 1
                    self.stats['total_photos_found'] += len(photos)

        print(f"\n✓ Scaneadas: {self.stats['scanned_folders']} pastas produtos")
        print(f"✓ Encontradas: {self.stats['total_photos_found']} fotos AI")
        print(f"⊘ Skipped: {len(self.stats['skipped_products'])} pastas (sem SKU reconhecível)")
        return products_map

    def find_product_by_sku(self, sku: str) -> Optional[int]:
        """
        Encontrar ID produto WooCommerce por SKU
        Tenta match exato e variações
        """
        cursor = self.db.cursor()

        # Tentar match exato
        cursor.execute("""
            SELECT post_id FROM lx_postmeta
            WHERE meta_key = '_sku'
            AND UPPER(meta_value) = %s
            LIMIT 1
        """, (sku.upper(),))

        result = cursor.fetchone()
        if result:
            cursor.close()
            return result[0]

        # Tentar match parcial (para variações tipo 18456-A)
        sku_base = re.sub(r'-[A-Z]$', '', sku.upper())
        cursor.execute("""
            SELECT post_id FROM lx_postmeta
            WHERE meta_key = '_sku'
            AND UPPER(meta_value) LIKE %s
            LIMIT 1
        """, (f"{sku_base}%",))

        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    def import_photo_as_attachment(self, photo_path: Path, product_id: int) -> Optional[int]:
        """
        Importar foto para WordPress Media Library
        Returns: attachment_id ou None se falhar
        """
        try:
            # Determinar path relativo upload
            rel_path = photo_path.relative_to(PRODUCTS_DIR)
            upload_path = f"products/{rel_path}"

            # Path completo no filesystem
            guid = f"{WORDPRESS_URL}/wp-content/uploads/{upload_path}"

            cursor = self.db.cursor()

            # Verificar se já existe (evitar duplicados)
            cursor.execute("""
                SELECT ID FROM lx_posts
                WHERE guid = %s
                AND post_type = 'attachment'
                LIMIT 1
            """, (guid,))

            existing = cursor.fetchone()
            if existing:
                cursor.close()
                return existing[0]  # Já existe, retornar ID existente

            # Obter timestamp atual
            now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            # Post name slug
            post_name = photo_path.stem.lower().replace('_', '-')

            # Inserir post attachment (com todos campos necessários)
            cursor.execute("""
                INSERT INTO lx_posts (
                    post_author, post_date, post_date_gmt, post_content,
                    post_title, post_excerpt, post_status, post_name,
                    post_modified, post_modified_gmt, post_parent,
                    guid, post_type, post_mime_type,
                    to_ping, pinged, post_content_filtered
                ) VALUES (
                    1, %s, %s, '', %s, '', 'inherit', %s,
                    %s, %s, %s, %s, 'attachment', 'image/jpeg',
                    '', '', ''
                )
            """, (
                now, now,
                photo_path.stem,  # post_title
                post_name,
                now, now,
                product_id,  # post_parent (link ao produto)
                guid
            ))

            attachment_id = cursor.lastrowid

            # Inserir metadata básico
            cursor.execute("""
                INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
                VALUES (%s, '_wp_attached_file', %s)
            """, (attachment_id, upload_path))

            self.db.commit()
            cursor.close()

            self.stats['imported_attachments'] += 1
            return attachment_id

        except Exception as e:
            self.stats['errors'].append(f"Erro importar {photo_path.name}: {e}")
            return None

    def set_featured_image(self, product_id: int, attachment_id: int):
        """Definir featured image produto (_thumbnail_id)"""
        cursor = self.db.cursor()

        # Verificar se já tem featured image
        cursor.execute("""
            SELECT meta_value FROM lx_postmeta
            WHERE post_id = %s AND meta_key = '_thumbnail_id'
        """, (product_id,))

        existing = cursor.fetchone()

        if existing:
            # Atualizar existente
            cursor.execute("""
                UPDATE lx_postmeta
                SET meta_value = %s
                WHERE post_id = %s AND meta_key = '_thumbnail_id'
            """, (attachment_id, product_id))
        else:
            # Inserir novo
            cursor.execute("""
                INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
                VALUES (%s, '_thumbnail_id', %s)
            """, (product_id, attachment_id))

        self.db.commit()
        cursor.close()

        self.stats['featured_images_set'] += 1

    def update_product_gallery(self, product_id: int, attachment_ids: List[int]):
        """Atualizar galeria produto (_product_image_gallery)"""
        if not attachment_ids:
            return

        cursor = self.db.cursor()

        # IDs separados por vírgulas
        gallery_value = ','.join(map(str, attachment_ids))

        # Verificar se já tem galeria
        cursor.execute("""
            SELECT meta_value FROM lx_postmeta
            WHERE post_id = %s AND meta_key = '_product_image_gallery'
        """, (product_id,))

        existing = cursor.fetchone()

        if existing:
            # Atualizar
            cursor.execute("""
                UPDATE lx_postmeta
                SET meta_value = %s
                WHERE post_id = %s AND meta_key = '_product_image_gallery'
            """, (gallery_value, product_id))
        else:
            # Inserir
            cursor.execute("""
                INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
                VALUES (%s, '_product_image_gallery', %s)
            """, (product_id, gallery_value))

        self.db.commit()
        cursor.close()

        self.stats['galleries_updated'] += 1

    def process_product_photos(self, sku: str, folder_path: str, photos: List[Path]):
        """
        Importar fotos produto e definir featured + galeria
        Prioridade featured: img_01_pro.jpg > img_01.jpg > primeira disponível
        """
        # Encontrar produto
        product_id = self.find_product_by_sku(sku)
        if not product_id:
            self.stats['errors'].append(f"SKU não encontrado no WooCommerce: {sku}")
            return

        # Separar fotos por prioridade
        img_01_pro = None
        img_01 = None
        other_photos = []

        for photo in photos:
            name_lower = photo.name.lower()
            if name_lower == 'img_01_pro.jpg':
                img_01_pro = photo
            elif name_lower == 'img_01.jpg':
                img_01 = photo
            else:
                other_photos.append(photo)

        # Importar todas fotos
        attachment_ids = []
        featured_id = None

        # Prioridade para featured: img_01_pro > img_01 > outras
        if img_01_pro:
            att_id = self.import_photo_as_attachment(img_01_pro, product_id)
            if att_id:
                attachment_ids.append(att_id)
                featured_id = att_id

        if img_01:
            att_id = self.import_photo_as_attachment(img_01, product_id)
            if att_id:
                attachment_ids.append(att_id)
                if not featured_id:
                    featured_id = att_id

        # Importar outras fotos (máximo 10 para não sobrecarregar)
        for photo in other_photos[:10]:
            att_id = self.import_photo_as_attachment(photo, product_id)
            if att_id:
                attachment_ids.append(att_id)
                if not featured_id:
                    featured_id = att_id

        # Definir featured image
        if featured_id:
            self.set_featured_image(product_id, featured_id)

        # Definir galeria (todas exceto featured)
        gallery_ids = [aid for aid in attachment_ids if aid != featured_id]
        if gallery_ids:
            self.update_product_gallery(product_id, gallery_ids)

        print(f"  ✓ {sku}: Featured={featured_id}, Galeria={len(gallery_ids)} fotos")

    def run(self):
        """Execução principal"""
        print("\n" + "="*70)
        print("PhotoTriage-Agent - Import Emergência Fotos AI")
        print("="*70 + "\n")

        # Conectar à database
        self.connect_db()

        # Scanear diretório produtos
        products_map = self.scan_products_directory()

        if not products_map:
            print("\n❌ Nenhuma foto AI encontrada no diretório produtos")
            return False

        # Processar cada produto
        print(f"\n🚀 A processar {len(products_map)} produtos...\n")

        for i, (sku, (folder_path, photos)) in enumerate(products_map.items(), 1):
            print(f"[{i:3d}/{len(products_map)}] {sku:15s} ({len(photos):2d} fotos)")
            self.process_product_photos(sku, folder_path, photos)

        # Estatísticas finais
        print("\n" + "="*70)
        print("ESTATÍSTICAS FINAIS")
        print("="*70)
        print(f"✓ Pastas scaneadas: {self.stats['scanned_folders']}")
        print(f"✓ Total fotos encontradas: {self.stats['total_photos_found']}")
        print(f"✓ Attachments importados: {self.stats['imported_attachments']}")
        print(f"✓ Featured images definidas: {self.stats['featured_images_set']}")
        print(f"✓ Galerias atualizadas: {self.stats['galleries_updated']}")
        print(f"⊘ Produtos skipped: {len(self.stats['skipped_products'])}")
        print(f"✗ Erros: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print("\n⚠️  ERROS (primeiros 10):")
            for error in self.stats['errors'][:10]:
                print(f"  - {error}")

        # Fechar database
        if self.db:
            self.db.close()

        print("\n" + "="*70)
        success_rate = (self.stats['featured_images_set'] / len(products_map) * 100) if products_map else 0
        print(f"Taxa de sucesso: {success_rate:.1f}% ({self.stats['featured_images_set']}/{len(products_map)} produtos)")
        print("="*70 + "\n")

        return self.stats['featured_images_set'] >= 90  # Sucesso se >=90 produtos

if __name__ == '__main__':
    agent = PhotoTriageAgent()
    success = agent.run()
    sys.exit(0 if success else 1)
