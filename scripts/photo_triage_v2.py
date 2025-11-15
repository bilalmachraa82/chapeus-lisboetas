#!/usr/bin/env python3
"""
PhotoTriage-Agent v2 - Import Emergência Fotos AI (IMPROVED)
Versão melhorada com multi-candidate SKU matching
Importa fotos AI para WordPress Media Library e associa aos produtos

Melhorias v2:
- Extração multi-candidate de SKUs (tenta múltiplas variações)
- Matching parcial (SKU starts with candidate)
- Melhor logging de falhas para debugging
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

class PhotoTriageAgentV2:
    def __init__(self):
        self.db = None
        self.stats = {
            'scanned_folders': 0,
            'total_photos_found': 0,
            'imported_attachments': 0,
            'featured_images_set': 0,
            'galleries_updated': 0,
            'errors': [],
            'skipped_products': [],
            'match_details': []
        }

    def connect_db(self):
        """Conectar à database WordPress"""
        self.db = mysql.connector.connect(**DB_CONFIG, buffered=True)
        print(f"✓ Conectado à database: {DB_CONFIG['database']}")

    def extract_sku_candidates(self, folder_name: str) -> List[str]:
        """
        Extrair todos os SKU candidates do nome da pasta
        Retorna lista de candidates em ordem de prioridade
        """
        candidates = []

        # Pattern 1: Pure numeric (18220mi → 18220)
        matches = re.findall(r'\b(\d{4,6})[a-zA-Z]{0,2}\b', folder_name)
        candidates.extend(matches)

        # Pattern 2: After dash (bone-18074 → 18074)
        matches = re.findall(r'-(\d{4,6})[a-zA-Z]{0,2}\b', folder_name)
        candidates.extend(matches)

        # Pattern 3: Longer numbers (181056 → try 18105, 1810, etc.)
        matches = re.findall(r'\b(\d{5,7})\b', folder_name)
        for match in matches:
            candidates.append(match[:5])  # First 5 digits
            candidates.append(match[:4])  # First 4 digits

        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for c in candidates:
            c_upper = c.upper()
            if c_upper not in seen:
                seen.add(c_upper)
                unique_candidates.append(c_upper)

        return unique_candidates

    def scan_products_directory(self) -> Dict[str, Tuple[str, List[Path], List[str]]]:
        """
        Scan wordpress/wp-content/uploads/products/ para fotos AI
        Returns: {folder_path: (category, [photo_paths], [sku_candidates])}
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

                # Extrair SKU candidates
                candidates = self.extract_sku_candidates(sku_dir.name)

                photos = []

                # Coletar fotos principais (não thumbnails)
                for ext in ['*.jpg', '*.png']:
                    for photo in sku_dir.glob(ext):
                        # Skip thumbnails (têm -NNNxNNN no nome)
                        if re.search(r'-\d+x\d+\.(jpg|png)$', photo.name):
                            continue
                        # Skip se começar com ponto (ficheiros ocultos)
                        if photo.name.startswith('.'):
                            continue
                        photos.append(photo)

                if photos:
                    products_map[str(sku_dir)] = (
                        category_dir.name,
                        sorted(photos, key=lambda p: p.name),
                        candidates
                    )
                    self.stats['scanned_folders'] += 1
                    self.stats['total_photos_found'] += len(photos)

        print(f"\n✓ Scaneadas: {self.stats['scanned_folders']} pastas produtos")
        print(f"✓ Encontradas: {self.stats['total_photos_found']} fotos AI")
        return products_map

    def find_product_by_sku_candidates(self, candidates: List[str]) -> Optional[Tuple[int, str]]:
        """
        Encontrar ID produto WooCommerce usando lista de candidates
        Tenta match exato primeiro, depois match parcial
        Returns: (product_id, matched_sku) ou None
        """
        if not candidates:
            return None

        cursor = self.db.cursor()

        # Tentar match exato para cada candidate
        for candidate in candidates:
            cursor.execute("""
                SELECT post_id, meta_value FROM lx_postmeta
                WHERE meta_key = '_sku'
                AND UPPER(meta_value) = %s
                LIMIT 1
            """, (candidate.upper(),))

            result = cursor.fetchone()
            if result:
                cursor.close()
                return (result[0], result[1])

        # Tentar match parcial (SKU starts with candidate)
        for candidate in candidates:
            cursor.execute("""
                SELECT post_id, meta_value FROM lx_postmeta
                WHERE meta_key = '_sku'
                AND UPPER(meta_value) LIKE %s
                LIMIT 1
            """, (f"{candidate.upper()}%",))

            result = cursor.fetchone()
            if result:
                cursor.close()
                return (result[0], result[1])

        cursor.close()
        return None

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

            # Determinar MIME type
            mime_type = 'image/jpeg' if photo_path.suffix.lower() == '.jpg' else 'image/png'

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
                    %s, %s, %s, %s, 'attachment', %s,
                    '', '', ''
                )
            """, (
                now, now,
                photo_path.stem,  # post_title
                post_name,
                now, now,
                product_id,  # post_parent (link ao produto)
                guid,
                mime_type
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

    def process_product_photos(self, folder_path: str, category: str, photos: List[Path], candidates: List[str]):
        """
        Importar fotos produto e definir featured + galeria
        Prioridade featured: img_01_pro.jpg > img_01.jpg > primeira disponível
        """
        # Encontrar produto usando candidates
        result = self.find_product_by_sku_candidates(candidates)
        if not result:
            self.stats['errors'].append(
                f"Nenhum SKU match para folder: {Path(folder_path).name} (candidates: {', '.join(candidates[:3])})"
            )
            return

        product_id, matched_sku = result

        # Separar fotos por prioridade
        img_01_pro = None
        img_01 = None
        other_photos = []

        for photo in photos:
            name_lower = photo.name.lower()
            if name_lower == 'img_01_pro.jpg' or name_lower == 'img_01_pro.png':
                img_01_pro = photo
            elif name_lower == 'img_01.jpg' or name_lower == 'img_01.png':
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

        # Log success
        folder_name = Path(folder_path).name
        self.stats['match_details'].append({
            'folder': folder_name,
            'candidates': candidates,
            'matched_sku': matched_sku,
            'product_id': product_id,
            'photos_imported': len(attachment_ids),
            'featured_id': featured_id,
            'gallery_count': len(gallery_ids)
        })

        print(f"  ✓ {folder_name[:40]:40s} → SKU: {matched_sku:8s} | {len(attachment_ids):2d} fotos ({len(gallery_ids)} gallery)")

    def run(self):
        """Execução principal"""
        print("\n" + "="*70)
        print("PhotoTriage-Agent v2 - Import Emergência Fotos AI (IMPROVED)")
        print("="*70 + "\n")

        # Conectar à database
        self.connect_db()

        # Scanear diretório produtos
        products_map = self.scan_products_directory()

        if not products_map:
            print("\n❌ Nenhuma foto AI encontrada no diretório produtos")
            return False

        # Processar cada produto
        print(f"\n🚀 A processar {len(products_map)} produtos...\\n")

        for i, (folder_path, (category, photos, candidates)) in enumerate(products_map.items(), 1):
            folder_name = Path(folder_path).name
            print(f"[{i:3d}/{len(products_map)}] ", end='')
            self.process_product_photos(folder_path, category, photos, candidates)

        # Estatísticas finais
        print("\n" + "="*70)
        print("ESTATÍSTICAS FINAIS")
        print("="*70)
        print(f"✓ Pastas scaneadas: {self.stats['scanned_folders']}")
        print(f"✓ Total fotos encontradas: {self.stats['total_photos_found']}")
        print(f"✓ Attachments importados: {self.stats['imported_attachments']}")
        print(f"✓ Featured images definidas: {self.stats['featured_images_set']}")
        print(f"✓ Galerias atualizadas: {self.stats['galleries_updated']}")
        print(f"✗ Erros: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print(f"\n⚠️  ERROS (primeiros 10):")
            for error in self.stats['errors'][:10]:
                print(f"  - {error}")

        # Fechar database
        if self.db:
            self.db.close()

        print("\n" + "="*70)
        success_rate = (self.stats['featured_images_set'] / len(products_map) * 100) if products_map else 0
        print(f"Taxa de sucesso: {success_rate:.1f}% ({self.stats['featured_images_set']}/{len(products_map)} produtos)")
        print("="*70 + "\n")

        return self.stats['featured_images_set'] >= 50  # Sucesso se >=50 produtos (realistic target)

if __name__ == '__main__':
    agent = PhotoTriageAgentV2()
    success = agent.run()
    sys.exit(0 if success else 1)
