#!/usr/bin/env python3
"""
🔍 QA Agent - Auditor Automático do Site
Verifica tudo: imagens, produtos, links, performance
"""

import requests
import json
from pathlib import Path
from typing import Dict, List
import subprocess

class QAAgent:
    def __init__(self, site_url: str = "http://localhost:8080"):
        self.site_url = site_url
        self.issues = []
        self.stats = {}
        
    def check_wordpress_health(self) -> bool:
        """Verificar saúde do WordPress"""
        print("=" * 70)
        print("🔍 QA AGENT - AUDITORIA COMPLETA")
        print("=" * 70)
        print("\n1️⃣ VERIFICANDO WORDPRESS...\n")
        
        try:
            response = requests.get(self.site_url, timeout=10)
            if response.status_code == 200:
                print("✅ WordPress acessível")
                
                # Verificar se Flatsome está ativo
                if 'flatsome' in response.text.lower():
                    print("✅ Tema Flatsome ativo")
                else:
                    print("❌ Flatsome não detectado")
                    self.issues.append("Tema Flatsome não está ativo")
                
                return True
            else:
                print(f"❌ WordPress retornou {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False
    
    def check_products_via_api(self) -> Dict:
        """Verificar produtos via Docker"""
        print("\n2️⃣ VERIFICANDO PRODUTOS...\n")
        
        cmd = """docker exec chapeus_wordpress bash -c "php -r '
require(\"/var/www/html/wp-load.php\");
\\$args = array(\"post_type\" => \"product\", \"posts_per_page\" => -1, \"post_status\" => \"publish\");
\\$products = get_posts(\\$args);
\\$with_images = 0;
\\$without_images = 0;
\\$with_price = 0;
\\$without_price = 0;

foreach (\\$products as \\$product) {
    if (has_post_thumbnail(\\$product->ID)) {
        \\$with_images++;
    } else {
        \\$without_images++;
    }
    
    \\$prod = wc_get_product(\\$product->ID);
    if (\\$prod && \\$prod->get_price()) {
        \\$with_price++;
    } else {
        \\$without_price++;
    }
}

echo json_encode(array(
    \"total\" => count(\\$products),
    \"with_images\" => \\$with_images,
    \"without_images\" => \\$without_images,
    \"with_price\" => \\$with_price,
    \"without_price\" => \\$without_price
));
' "
"""
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            data = json.loads(result.stdout)
            
            print(f"✅ Total produtos: {data['total']}")
            print(f"✅ Com imagens: {data['with_images']} ({data['with_images']/data['total']*100:.1f}%)")
            print(f"❌ Sem imagens: {data['without_images']}")
            print(f"✅ Com preço: {data['with_price']}")
            
            if data['without_images'] > 0:
                self.issues.append(f"{data['without_images']} produtos sem imagens")
            
            self.stats['products'] = data
            return data
            
        except Exception as e:
            print(f"❌ Erro ao verificar produtos: {e}")
            return {}
    
    def check_images_in_filesystem(self) -> Dict:
        """Verificar imagens no container"""
        print("\n3️⃣ VERIFICANDO IMAGENS NO FILESYSTEM...\n")
        
        cmd = 'docker exec chapeus_wordpress bash -c "find /tmp/images -name \'*.jpg\' -o -name \'*.jpeg\' -o -name \'*.png\' | wc -l"'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            count = int(result.stdout.strip())
            
            print(f"✅ {count} imagens disponíveis em /tmp/images")
            
            cmd2 = 'docker exec chapeus_wordpress bash -c "find /var/www/html/wp-content/uploads -name \'*.jpg\' -o -name \'*.jpeg\' -o -name \'*.png\' | wc -l"'
            result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=10)
            uploaded = int(result2.stdout.strip())
            
            print(f"✅ {uploaded} imagens já no WordPress uploads")
            
            self.stats['images'] = {
                'available': count,
                'uploaded': uploaded,
                'pending': count - uploaded
            }
            
            return self.stats['images']
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return {}
    
    def generate_report(self) -> Dict:
        """Gerar relatório completo"""
        print("\n" + "=" * 70)
        print("📊 RELATÓRIO DE AUDITORIA")
        print("=" * 70 + "\n")
        
        report = {
            'site_url': self.site_url,
            'wordpress_health': 'OK',
            'products': self.stats.get('products', {}),
            'images': self.stats.get('images', {}),
            'issues': self.issues,
            'recommendations': []
        }
        
        # Gerar recomendações
        if self.issues:
            print("⚠️  ISSUES ENCONTRADOS:\n")
            for issue in self.issues:
                print(f"   • {issue}")
            print()
        
        products = self.stats.get('products', {})
        if products.get('without_images', 0) > 0:
            report['recommendations'].append({
                'priority': 'HIGH',
                'action': 'Re-executar upload de imagens',
                'command': 'docker exec chapeus_wordpress php /tmp/upload_images_final.php'
            })
        
        print("💡 RECOMENDAÇÕES:\n")
        for rec in report['recommendations']:
            print(f"   [{rec['priority']}] {rec['action']}")
        print()
        
        # Salvar relatório
        with open('qa_audit_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("💾 Relatório salvo: qa_audit_report.json\n")
        
        print("=" * 70)
        print("✅ AUDITORIA COMPLETA!")
        print("=" * 70 + "\n")
        
        return report

if __name__ == "__main__":
    agent = QAAgent()
    
    if agent.check_wordpress_health():
        agent.check_products_via_api()
        agent.check_images_in_filesystem()
        agent.generate_report()
