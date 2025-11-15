#!/usr/bin/env python3
"""
Compara produtos entre CSV e WordPress de forma precisa.
"""
import csv
import subprocess
import json

print("="*60)
print("COMPARAÇÃO CSV vs WordPress")
print("="*60)

# 1. Ler produtos do CSV
csv_products = []
with open('output_catalogo/woocommerce_import_localhost.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sku = row.get('SKU', '').strip()
        name = row.get('Name', '').strip()
        price = row.get('Regular price', '').strip()

        # Normalizar SKU (pegar primeiro se tiver múltiplos)
        sku_first = sku.split('\n')[0].strip() if sku else ''

        if sku_first and name and price and not price.startswith('Tag'):
            csv_products.append({
                'sku': sku_first,
                'name': name,
                'price': price
            })

print(f"\nCSV: {len(csv_products)} produtos válidos")

# 2. Ler produtos do WordPress via WP-CLI
wp_cmd = '''
$products = wc_get_products(array("limit" => -1));
$result = array();
foreach ($products as $p) {
    $result[] = array(
        "id" => $p->get_id(),
        "sku" => $p->get_sku(),
        "name" => $p->get_name(),
        "price" => $p->get_regular_price(),
        "status" => $p->get_status()
    );
}
echo json_encode($result);
'''

result = subprocess.run(
    ['docker', 'exec', 'chapeus_wordpress', 'wp', 'eval', wp_cmd, '--allow-root'],
    capture_output=True, text=True
)

if result.returncode != 0:
    print(f"ERRO: {result.stderr}")
    exit(1)

wp_products = json.loads(result.stdout)
print(f"WordPress: {len(wp_products)} produtos")

# 3. Criar mapas por SKU
wp_by_sku = {p['sku']: p for p in wp_products if p['sku']}
csv_by_sku = {p['sku']: p for p in csv_products}

# 4. Encontrar faltantes
missing = []
for sku, csv_prod in csv_by_sku.items():
    if sku not in wp_by_sku:
        missing.append(csv_prod)

# 5. Estatísticas
print(f"\n{'='*60}")
print(f"FALTAM: {len(missing)} produtos")
print(f"{'='*60}")

if missing:
    print("\nProdutos faltantes (SKU - Nome - Preço):")
    for i, prod in enumerate(missing, 1):
        print(f"{i:2d}. {prod['sku']:20s} - {prod['name'][:40]:40s} - €{prod['price']}")

    # Salvar lista de SKUs faltantes
    with open('/tmp/missing_skus_clean.txt', 'w') as f:
        for prod in missing:
            f.write(f"{prod['sku']}\n")

    print(f"\nSKUs salvos em: /tmp/missing_skus_clean.txt")

# 6. Publicados vs Rascunhos
published = sum(1 for p in wp_products if p['status'] == 'publish')
drafts = sum(1 for p in wp_products if p['status'] == 'draft')
print(f"\nStatus WordPress:")
print(f"  Publicados: {published}")
print(f"  Rascunhos: {drafts}")
