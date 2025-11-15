#!/usr/bin/env python3
"""
Extrai linhas do CSV para SKUs faltantes.
"""
import csv

# Ler lista de SKUs faltantes
with open('/tmp/missing_skus.txt', 'r') as f:
    missing_skus = set(line.strip() for line in f)

print(f"SKUs faltantes: {len(missing_skus)}")

# Ler CSV original e filtrar
csv_path = 'output_catalogo/woocommerce_import_localhost.csv'
output_path = '/tmp/missing_products.csv'

with open(csv_path, 'r', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames

    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        count = 0
        for row in reader:
            sku = row.get('SKU', '').strip()
            if sku in missing_skus:
                writer.writerow(row)
                count += 1
                print(f"  ✓ {sku}")

print(f"\n{count} produtos exportados para: {output_path}")
