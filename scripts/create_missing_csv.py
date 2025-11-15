#!/usr/bin/env python3
"""
Cria CSV com apenas produtos faltantes e preço válido.
"""
import csv

# Ler lista de SKUs faltantes
with open('/tmp/missing_skus_clean.txt', 'r') as f:
    missing_skus = set(line.strip() for line in f)

print(f"SKUs faltantes: {len(missing_skus)}")

# Ler CSV original e filtrar
csv_path = 'output_catalogo/woocommerce_import_localhost.csv'
output_path = '/tmp/missing_products_final.csv'

with open(csv_path, 'r', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames

    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        count_exported = 0
        count_invalid = 0

        for row in reader:
            sku = row.get('SKU', '').strip()
            price = row.get('Regular price', '').strip()

            # Pegar primeiro SKU se tiver múltiplos
            sku_first = sku.split('\n')[0].strip() if sku else ''

            if sku_first in missing_skus:
                # Validar preço
                if price and not price.startswith('Tag') and not price.startswith('Etiqueta'):
                    try:
                        float(price)
                        writer.writerow(row)
                        count_exported += 1
                        print(f"  ✓ {sku_first:30s} - €{price}")
                    except ValueError:
                        print(f"  ✗ {sku_first:30s} - Preço inválido: {price}")
                        count_invalid += 1
                else:
                    print(f"  ✗ {sku_first:30s} - Preço inválido: {price}")
                    count_invalid += 1

print(f"\n{count_exported} produtos exportados para: {output_path}")
print(f"{count_invalid} produtos com preço inválido (ignorados)")
