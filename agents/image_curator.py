#!/usr/bin/env python3
"""
📸 Image Curator Agent
Analisa, curadora e otimiza as 180 fotos dos produtos
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
import hashlib
from PIL import Image
import imagehash

class ImageCurator:
    def __init__(self, catalog_file: str = "catalog_completo_classificado.json"):
        self.catalog_file = Path(catalog_file)
        self.products = []
        self.issues = {
            'duplicates': [],
            'low_quality': [],
            'wrong_rotation': [],
            'same_product_multiple': defaultdict(list),
            'missing': []
        }
        
    def load_catalog(self):
        """Carregar catálogo de produtos"""
        print("=" * 70)
        print("📸 IMAGE CURATOR AGENT")
        print("=" * 70)
        print("\n📂 Carregando catálogo...\n")
        
        with open(self.catalog_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.products = data.get('products', [])
        
        print(f"✅ {len(self.products)} produtos carregados\n")
    
    def analyze_images(self):
        """Análise completa das imagens"""
        print("🔍 ANALISANDO IMAGENS...\n")
        
        image_hashes = {}
        analyzed = 0
        
        for idx, product in enumerate(self.products):
            img_path = product.get('file_path', '')
            if not img_path:
                self.issues['missing'].append(idx)
                continue
            
            path = Path(img_path)
            if not path.exists():
                self.issues['missing'].append(idx)
                continue
            
            try:
                # Analisar imagem
                img = Image.open(path)
                
                # Verificar duplicados (perceptual hash)
                phash = str(imagehash.phash(img))
                
                if phash in image_hashes:
                    self.issues['duplicates'].append({
                        'original': image_hashes[phash],
                        'duplicate': idx,
                        'hash': phash
                    })
                else:
                    image_hashes[phash] = idx
                
                # Verificar qualidade (resolução)
                width, height = img.size
                if width < 500 or height < 500:
                    self.issues['low_quality'].append({
                        'index': idx,
                        'size': f"{width}x{height}"
                    })
                
                # Verificar rotação (ratio)
                ratio = width / height
                if ratio > 2 or ratio < 0.5:
                    self.issues['wrong_rotation'].append({
                        'index': idx,
                        'ratio': ratio,
                        'size': f"{width}x{height}"
                    })
                
                # Agrupar por nome similar (mesmo produto)
                filename = path.stem
                base_name = filename.split('-')[0] if '-' in filename else filename.split('.')[0]
                self.issues['same_product_multiple'][base_name].append(idx)
                
                analyzed += 1
                
            except Exception as e:
                print(f"   ⚠️  Erro ao analisar imagem {idx}: {e}")
                continue
        
        print(f"✅ {analyzed} imagens analisadas\n")
        self._print_report()
    
    def _print_report(self):
        """Relatório de análise"""
        print("=" * 70)
        print("📊 RELATÓRIO DE CURADORIA")
        print("=" * 70 + "\n")
        
        # Duplicados
        if self.issues['duplicates']:
            print(f"⚠️  DUPLICADOS ENCONTRADOS: {len(self.issues['duplicates'])}")
            for dup in self.issues['duplicates'][:5]:
                print(f"   • Produto {dup['original']} = Produto {dup['duplicate']}")
            if len(self.issues['duplicates']) > 5:
                print(f"   ... e mais {len(self.issues['duplicates']) - 5}")
            print()
        
        # Baixa qualidade
        if self.issues['low_quality']:
            print(f"⚠️  BAIXA QUALIDADE: {len(self.issues['low_quality'])}")
            for lq in self.issues['low_quality'][:3]:
                print(f"   • Produto {lq['index']}: {lq['size']}")
            if len(self.issues['low_quality']) > 3:
                print(f"   ... e mais {len(self.issues['low_quality']) - 3}")
            print()
        
        # Rotação errada
        if self.issues['wrong_rotation']:
            print(f"⚠️  POSSÍVEL ROTAÇÃO ERRADA: {len(self.issues['wrong_rotation'])}")
            for wr in self.issues['wrong_rotation'][:3]:
                print(f"   • Produto {wr['index']}: ratio {wr['ratio']:.2f}")
            if len(self.issues['wrong_rotation']) > 3:
                print(f"   ... e mais {len(self.issues['wrong_rotation']) - 3}")
            print()
        
        # Múltiplas fotos do mesmo produto
        multi = {k: v for k, v in self.issues['same_product_multiple'].items() if len(v) > 1}
        if multi:
            print(f"📸 PRODUTOS COM MÚLTIPLAS FOTOS: {len(multi)}")
            for name, indices in list(multi.items())[:5]:
                print(f"   • {name}: {len(indices)} fotos")
            if len(multi) > 5:
                print(f"   ... e mais {len(multi) - 5}")
            print()
        
        # Faltando
        if self.issues['missing']:
            print(f"❌ IMAGENS NÃO ENCONTRADAS: {len(self.issues['missing'])}")
            print()
        
        print("=" * 70)
        print("✅ ANÁLISE COMPLETA!")
        print("=" * 70 + "\n")
    
    def generate_recommendations(self) -> Dict:
        """Gerar recomendações de curadoria"""
        recommendations = {
            'remove_duplicates': [d['duplicate'] for d in self.issues['duplicates']],
            'improve_quality': [lq['index'] for lq in self.issues['low_quality']],
            'check_rotation': [wr['index'] for wr in self.issues['wrong_rotation']],
            'create_galleries': {
                k: v for k, v in self.issues['same_product_multiple'].items() 
                if len(v) > 1
            },
            'missing_images': self.issues['missing']
        }
        
        print("💡 RECOMENDAÇÕES:\n")
        print(f"   • Remover {len(recommendations['remove_duplicates'])} duplicados")
        print(f"   • Melhorar {len(recommendations['improve_quality'])} fotos de baixa qualidade")
        print(f"   • Verificar {len(recommendations['check_rotation'])} fotos com rotação suspeita")
        print(f"   • Criar {len(recommendations['create_galleries'])} galerias de produto")
        print(f"   • Adicionar {len(recommendations['missing_images'])} imagens faltando")
        print()
        
        return recommendations
    
    def save_report(self, recommendations: Dict, output_file: str = "image_curation_report.json"):
        """Salvar relatório"""
        report = {
            'total_products': len(self.products),
            'issues': self.issues,
            'recommendations': recommendations
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Relatório salvo: {output_file}\n")

if __name__ == "__main__":
    try:
        curator = ImageCurator()
        curator.load_catalog()
        curator.analyze_images()
        recommendations = curator.generate_recommendations()
        curator.save_report(recommendations)
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("\n💡 Nota: PIL/imagehash necessário: pip install Pillow imagehash")
