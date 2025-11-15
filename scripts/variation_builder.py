#!/usr/bin/env python3
import json
import csv
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SRC = BASE_DIR / 'output_catalogo' / 'catalogo.json'
OUT = BASE_DIR / 'output_catalogo' / 'variations_map.csv'
REPORT = BASE_DIR / 'relatorios' / 'VARIATION_BUILDER_3_1.md'

def norm(text):
    t = str(text or '').strip().lower()
    t = t.replace('boné – ', '').replace('bone-','').replace('boné-','').replace('casquette-','').replace('gorro-','').replace('panama-','')
    return t

def base_sku(sku):
    s = norm(sku)
    m = re.search(r'(\d{3,6})', s)
    if m:
        return m.group(1)
    return s.split()[0]

def variation_label(sku):
    s = norm(sku)
    m = re.findall(r'[a-z]{1,3}', s)
    return m[-1].upper() if m else ''

def collect():
    data = json.load(SRC.open()) if SRC.exists() else []
    groups = {}
    for p in data:
        sku = p.get('sku') or p.get('supplier_code') or ''
        b = base_sku(sku)
        if not b:
            b = sku
        groups.setdefault(b, []).append(p)
    return groups

def choose_images(p):
    imgs = p.get('downloaded_images') or p.get('filtered_images') or []
    return ', '.join(imgs[:4])

def build():
    groups = collect()
    rows = []
    report_lines = []
    for parent, items in groups.items():
        if len(items) < 2:
            continue
        for p in items:
            sku = p.get('sku') or p.get('supplier_code') or ''
            val = p.get('color') or variation_label(sku)
            rows.append({
                'ParentSKU': parent,
                'VariationSKU': sku,
                'Attribute': 'Color',
                'Value': str(val),
                'Images': choose_images(p)
            })
        report_lines.append(f'- {parent}: {len(items)} variações')
    fieldnames = ['ParentSKU','VariationSKU','Attribute','Value','Images']
    with OUT.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text('\n'.join(['# Variation Builder 3.1', f'Total pais: {len(report_lines)}', '## Grupos', *report_lines]), encoding='utf-8')
    print(f'Mapa de variações criado: {OUT}')

if __name__ == '__main__':
    build()