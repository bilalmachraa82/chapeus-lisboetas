#!/usr/bin/env python3
"""
🤖 Sistema Multi-Agente para Setup Completo da Loja
Usando padrão de agentes especializados
"""

import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

class Agent:
    """Classe base para agentes"""
    def __init__(self, name: str):
        self.name = name
        self.status = "ready"
        
    def log(self, message: str, type: str = "info"):
        icons = {"info": "ℹ️", "success": "✅", "error": "❌", "working": "⚙️"}
        print(f"{icons.get(type, 'ℹ️')} [{self.name}] {message}")
    
    def execute_command(self, command: str) -> Tuple[bool, str]:
        """Executar comando shell"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)


class ThemeAgent(Agent):
    """Agente responsável por instalar e configurar o tema Flatsome"""
    
    def __init__(self):
        super().__init__("Theme Agent")
        
    def install_flatsome(self) -> bool:
        """Instalar tema Flatsome"""
        self.log("Instalando tema Flatsome...", "working")
        
        # Copiar tema para container
        flatsome_zip = "flatsome_v3.20.2_package.zip"
        
        commands = [
            f'docker cp "{flatsome_zip}" chapeus_wordpress:/tmp/',
            'docker exec chapeus_wordpress bash -c "cd /tmp && unzip -q flatsome_v3.20.2_package.zip -d /var/www/html/wp-content/themes/"',
            'docker exec chapeus_wordpress bash -c "chown -R www-data:www-data /var/www/html/wp-content/themes/flatsome"'
        ]
        
        for cmd in commands:
            success, output = self.execute_command(cmd)
            if not success:
                self.log(f"Erro: {output}", "error")
                return False
        
        self.log("Flatsome extraído com sucesso!", "success")
        return True
    
    def activate_flatsome(self) -> bool:
        """Ativar tema via PHP"""
        self.log("Ativando Flatsome...", "working")
        
        php_script = """
<?php
require('/var/www/html/wp-load.php');
$theme = wp_get_theme('flatsome');
if ($theme->exists()) {
    switch_theme('flatsome');
    echo "Flatsome ativado!\\n";
} else {
    echo "Flatsome não encontrado!\\n";
    exit(1);
}
?>
"""
        
        commands = [
            f'docker exec chapeus_wordpress bash -c "echo \'{php_script}\' > /tmp/activate_theme.php"',
            'docker exec chapeus_wordpress php /tmp/activate_theme.php'
        ]
        
        for cmd in commands:
            success, output = self.execute_command(cmd)
            if not success:
                self.log(f"Erro: {output}", "error")
                return False
        
        self.log("Flatsome ativado!", "success")
        return True
    
    def configure_colors(self) -> bool:
        """Configurar cores do tema"""
        self.log("Configurando cores do tema...", "working")
        
        php_script = """
<?php
require('/var/www/html/wp-load.php');

// Cores para chapelaria - tons terra e elegantes
set_theme_mod('color_primary', '#8B4513'); // Marrom chapéu
set_theme_mod('color_success', '#2E7D32'); // Verde sucesso
set_theme_mod('color_alert', '#FFA000'); // Laranja alerta
set_theme_mod('color_secondary', '#D2691E'); // Chocolate
set_theme_mod('header_bg_color', '#FFFFFF'); // Branco header
set_theme_mod('footer_bg_color', '#3E2723'); // Marrom escuro footer
set_theme_mod('footer_color', '#FFFFFF'); // Texto branco footer
set_theme_mod('type_texts', 'Lato'); // Font corpo
set_theme_mod('type_headings', 'Playfair Display'); // Font títulos
set_theme_mod('site_width', '1200px');

echo "Cores configuradas!\\n";
?>
"""
        
        cmd = f'docker exec chapeus_wordpress bash -c "echo \'{php_script}\' > /tmp/colors.php && php /tmp/colors.php"'
        success, output = self.execute_command(cmd)
        
        if success:
            self.log("Cores configuradas!", "success")
            return True
        else:
            self.log(f"Erro: {output}", "error")
            return False
    
    def run(self) -> bool:
        """Executar todas as tarefas do agente"""
        self.log("Iniciando configuração do tema...", "info")
        
        if not self.install_flatsome():
            return False
        
        time.sleep(2)
        
        if not self.activate_flatsome():
            return False
        
        time.sleep(1)
        
        if not self.configure_colors():
            return False
        
        self.log("Tema configurado com sucesso!", "success")
        return True


class ImageAgent(Agent):
    """Agente responsável por fazer upload das imagens dos produtos"""
    
    def __init__(self):
        super().__init__("Image Agent")
        self.catalog_file = Path("catalog_completo_classificado.json")
        
    def get_products_without_images(self) -> List[Dict]:
        """Obter produtos sem imagens"""
        self.log("Verificando produtos sem imagens...", "working")
        
        php_script = """
<?php
require('/var/www/html/wp-load.php');

$args = array(
    'post_type' => 'product',
    'posts_per_page' => -1,
    'meta_query' => array(
        array(
            'key' => '_thumbnail_id',
            'compare' => 'NOT EXISTS'
        )
    )
);

$products = get_posts($args);
echo count($products) . " produtos sem imagens\\n";

foreach ($products as $product) {
    echo $product->ID . ":" . get_post_meta($product->ID, '_sku', true) . "\\n";
}
?>
"""
        
        cmd = f'docker exec chapeus_wordpress bash -c "echo \'{php_script}\' > /tmp/check_images.php && php /tmp/check_images.php"'
        success, output = self.execute_command(cmd)
        
        if success:
            lines = output.strip().split('\n')
            count = lines[0] if lines else "0"
            self.log(count, "info")
            return True
        return False
    
    def upload_product_images(self) -> bool:
        """Upload imagens para produtos"""
        self.log("Fazendo upload de imagens...", "working")
        
        # Copiar JSON para container
        cmd1 = 'docker cp catalog_completo_classificado.json chapeus_wordpress:/tmp/'
        self.execute_command(cmd1)
        
        php_script = """
<?php
require('/var/www/html/wp-load.php');

$json = file_get_contents('/tmp/catalog_completo_classificado.json');
$data = json_decode($json, true);
$products_data = $data['products'] ?? [];

$uploaded = 0;
$skipped = 0;

foreach ($products_data as $index => $product_info) {
    $sku = sprintf("CL-%s-%04d", 
        strtoupper(substr(str_replace('-', '', $product_info['classification']['tipo'] ?? 'outros'), 0, 6)),
        $index + 1
    );
    
    // Encontrar produto por SKU
    $product_id = wc_get_product_id_by_sku($sku);
    
    if (!$product_id) {
        continue;
    }
    
    // Verificar se já tem imagem
    if (has_post_thumbnail($product_id)) {
        $skipped++;
        continue;
    }
    
    // Path da imagem
    $image_path = '/var/www/html/wp-content/uploads/produtos/' . $product_info['relative_path'];
    
    if (!file_exists($image_path)) {
        continue;
    }
    
    // Upload imagem
    $upload_file = wp_upload_bits(basename($image_path), null, file_get_contents($image_path));
    
    if (!$upload_file['error']) {
        $attachment = array(
            'post_mime_type' => $upload_file['type'],
            'post_title' => sanitize_file_name(basename($image_path)),
            'post_content' => '',
            'post_status' => 'inherit'
        );
        
        $attach_id = wp_insert_attachment($attachment, $upload_file['file']);
        
        require_once(ABSPATH . 'wp-admin/includes/image.php');
        $attach_data = wp_generate_attachment_metadata($attach_id, $upload_file['file']);
        wp_update_attachment_metadata($attach_id, $attach_data);
        
        set_post_thumbnail($product_id, $attach_id);
        $uploaded++;
        
        if ($uploaded % 20 == 0) {
            echo "Uploaded $uploaded images...\\n";
        }
    }
}

echo "\\nTotal: $uploaded uploaded, $skipped skipped\\n";
?>
"""
        
        cmd = f'docker exec chapeus_wordpress bash -c "echo \'{php_script}\' > /tmp/upload_images.php && php /tmp/upload_images.php"'
        success, output = self.execute_command(cmd)
        
        if success:
            self.log(output, "info")
            self.log("Upload concluído!", "success")
            return True
        else:
            self.log(f"Erro: {output}", "error")
            return False
    
    def run(self) -> bool:
        """Executar todas as tarefas do agente"""
        self.log("Iniciando upload de imagens...", "info")
        
        self.get_products_without_images()
        time.sleep(1)
        
        if not self.upload_product_images():
            return False
        
        self.log("Imagens configuradas!", "success")
        return True


class DesignAgent(Agent):
    """Agente responsável por criar homepage e design"""
    
    def __init__(self):
        super().__init__("Design Agent")
    
    def create_homepage(self) -> bool:
        """Criar homepage com Flatsome"""
        self.log("Criando homepage...", "working")
        
        php_script = """
<?php
require('/var/www/html/wp-load.php');

// Criar página homepage
$homepage_content = '[section bg_color="rgb(245, 245, 245)" padding="60px"]
[row]
[col span="12" align="center"]
<h1>Chapéus Lisboetas</h1>
<p class="lead">Chapelaria Artesanal Portuguesa</p>
[button text="Ver Loja" link="/shop" style="primary"]
[/col]
[/row]
[/section]

[section label="Produtos Destaque" padding="40px"]
[row]
[col span="12" align="center"]
<h2>Produtos em Destaque</h2>
[/col]
[/row]
[ux_products columns="4" show="featured"]
[/section]

[section label="Categorias" bg_color="rgb(250, 250, 250)" padding="40px"]
[row]
[col span="12" align="center"]
<h2>Explore por Categoria</h2>
[/col]
[/row]
[ux_product_categories style="overlay" columns="4"]
[/section]';

$homepage = array(
    'post_title' => 'Home',
    'post_content' => $homepage_content,
    'post_status' => 'publish',
    'post_type' => 'page'
);

$page_id = wp_insert_post($homepage);

if ($page_id) {
    update_option('page_on_front', $page_id);
    update_option('show_on_front', 'page');
    echo "Homepage criada!\\n";
} else {
    echo "Erro ao criar homepage\\n";
    exit(1);
}
?>
"""
        
        cmd = f'docker exec chapeus_wordpress bash -c "echo \'{php_script}\' > /tmp/homepage.php && php /tmp/homepage.php"'
        success, output = self.execute_command(cmd)
        
        if success:
            self.log("Homepage criada!", "success")
            return True
        else:
            self.log(f"Erro: {output}", "error")
            return False
    
    def run(self) -> bool:
        """Executar todas as tarefas do agente"""
        self.log("Iniciando criação de design...", "info")
        
        if not self.create_homepage():
            return False
        
        self.log("Design configurado!", "success")
        return True


class Orchestrator:
    """Orquestrador que coordena todos os agentes"""
    
    def __init__(self):
        self.agents = [
            ThemeAgent(),
            ImageAgent(),
            DesignAgent()
        ]
    
    def run(self):
        """Executar todos os agentes em sequência"""
        print("\n" + "=" * 70)
        print("🤖 SISTEMA MULTI-AGENTE - SETUP COMPLETO DA LOJA")
        print("=" * 70 + "\n")
        
        for agent in self.agents:
            print(f"\n{'─' * 70}")
            print(f"🚀 Executando: {agent.name}")
            print(f"{'─' * 70}\n")
            
            success = agent.run()
            
            if not success:
                print(f"\n❌ Falha no agente: {agent.name}")
                print("Parando execução...")
                return False
            
            time.sleep(2)
        
        print("\n" + "=" * 70)
        print("✅ SETUP COMPLETO CONCLUÍDO!")
        print("=" * 70)
        print("\n🌐 Acessar loja:")
        print("   • Homepage: http://localhost:8080")
        print("   • Loja: http://localhost:8080/shop")
        print("   • Admin: http://localhost:8080/wp-admin")
        print("\n🔑 Login: admin / ChapeusAdmin2024!")
        print()
        
        return True


if __name__ == "__main__":
    orchestrator = Orchestrator()
    success = orchestrator.run()
    
    exit(0 if success else 1)
