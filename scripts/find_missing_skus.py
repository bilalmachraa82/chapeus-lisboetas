#!/usr/bin/env python3
"""
Encontra SKUs faltantes entre CSV e WordPress.
"""
import csv
import subprocess
import sys

# Ler SKUs do CSV com preço válido
csv_skus = []
csv_path = 'output_catalogo/woocommerce_import_localhost.csv'

print(f"Lendo CSV: {csv_path}")
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sku = row.get('SKU', '').strip()
        regular_price = row.get('Regular price', '').strip()

        # Apenas produtos com SKU e preço válido (não vazio e não começa com "Tag")
        if sku and regular_price and not regular_price.startswith('Tag'):
            csv_skus.append(sku)

print(f"CSV: {len(csv_skus)} produtos com preço válido")

# Ler SKUs do WordPress
print("\nBuscando SKUs no WordPress...")
wp_cmd = [
    'docker', 'exec', 'chapeus_wordpress',
    'wp', 'eval',
    'foreach (wc_get_products(array("limit" => -1)) as $p) { echo $p->get_sku() . PHP_EOL; }',
    '--allow-root'
]

result = subprocess.run(wp_cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"ERRO ao consultar WordPress: {result.stderr}")
    sys.exit(1)

wp_skus = set(result.stdout.strip().split('\n'))
wp_skus.discard('')  # Remove SKUs vazios
print(f"WordPress: {len(wp_skus)} produtos")

# Encontrar faltantes
missing_skus = [sku for sku in csv_skus if sku not in wp_skus]
print(f"\n{'='*60}")
print(f"FALTAM: {len(missing_skus)} SKUs")
print(f"{'='*60}\n")

if missing_skus:
    # Salvar lista (SOMENTE SKUs, sem output adicional)
    with open('/tmp/missing_skus.txt', 'w') as f:
        f.write('\n'.join(missing_skus))

    print(f"SKUs faltantes:")
    for i, sku in enumerate(missing_skus, 1):
        print(f"{i:2d}. {sku}")

    print(f"\nLista salva em: /tmp/missing_skus.txt")
else:
    print("Nenhum SKU faltante! Todos os produtos do CSV já estão no WordPress.")

sys.exit(0)
