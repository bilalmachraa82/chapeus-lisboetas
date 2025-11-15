#!/usr/bin/env python3
"""Quick validation of image organization"""

from pathlib import Path
import re

base = Path("/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress/wp-content/uploads/catalogo2025")
total_images = 0
misplaced = 0
correct = 0

for cat_dir in base.iterdir():
    if not cat_dir.is_dir() or cat_dir.name.startswith('.'):
        continue

    for prod_dir in cat_dir.iterdir():
        if not prod_dir.is_dir() or prod_dir.name.startswith('.'):
            continue

        current_sku = prod_dir.name

        for img in prod_dir.glob('*.jpg'):
            total_images += 1

            # Check if filename has SKU prefix
            if '_' in img.stem:
                parts = img.stem.split('_')
                if re.match(r'^(bone|gorro|boina|chapeu|panama)-\d+[A-Z]?$', parts[0]):
                    file_sku = parts[0]
                    if file_sku != current_sku:
                        misplaced += 1
                        print(f'❌ {img.name} in {current_sku}/ (should be in {file_sku}/)')
                    else:
                        correct += 1

print(f'\n=== VALIDAÇÃO FINAL ===')
print(f'Total de imagens: {total_images}')
print(f'Imagens com SKU correto: {correct}')
print(f'Imagens mal posicionadas: {misplaced}')
print(f'Status: {"✅ TUDO CORRETO" if misplaced == 0 else "⚠️  REQUER ATENÇÃO"}')
