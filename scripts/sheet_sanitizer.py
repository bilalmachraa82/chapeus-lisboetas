#!/usr/bin/env python3
import json
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CATALOGO_JSON = BASE_DIR / 'output_catalogo' / 'catalogo.json'
OUT_CSV = BASE_DIR / 'output_catalogo' / 'catalogo_clean_ready.csv'
REPORT = BASE_DIR / 'relatorios' / 'SYNC_SHEET_3_1.md'

def to_float(val):
    try:
        s = str(val).replace('€','').replace(',','.')
        return float(s.strip())
    except:
        return 0.0

def build_short(p):
    nome = p.get('name') or ''
    tipo = p.get('type') or (nome.split()[0] if nome else '')
    material = p.get('material') or p.get('composition') or ''
    origem = p.get('origin') or p.get('label') or ''
    variacoes = p.get('variations') or p.get('color') or ''
    parts = [x for x in [tipo, material, origem, variacoes] if x]
    return ' · '.join(parts)

def build_long(p):
    lines = []
    comp = p.get('composition') or ''
    tam = p.get('size') or p.get('sizes') or ''
    vend = p.get('sold_by') or p.get('pack') or ''
    ocas = p.get('season') or p.get('collection') or ''
    if comp: lines.append(f'Composição: {comp}')
    if tam: lines.append(f'Tamanhos: {tam}')
    if vend: lines.append(f'Vendido por: {vend}')
    if ocas: lines.append(f'Ocultação/Coleção: {ocas}')
    return '\n'.join(lines)

def choose_images(p):
    raw = p.get('downloaded_images') or p.get('filtered_images') or []
    imgs = []
    for i in raw:
        if not i:
            continue
        if isinstance(i, str):
            imgs.append(i)
        elif isinstance(i, dict):
            # common keys: path, local_path, url
            val = i.get('path') or i.get('local_path') or i.get('url') or ''
            if val:
                imgs.append(str(val))
    return imgs[:9]

def main():
    data = []
    if CATALOGO_JSON.exists():
        data = json.load(CATALOGO_JSON.open())
    else:
        print('catalogo.json não encontrado')
        return
    complete = 0
    errors = []
    rows = []
    for p in data:
        name = p.get('name') or ''
        sku = p.get('sku') or p.get('supplier_code') or ''
        price = to_float(p.get('price'))
        images = choose_images(p)
        short = build_short(p)
        long = build_long(p)
        if not name or price <= 0 or len(images) < 2:
            errors.append({'sku': sku, 'name': name, 'price': price, 'images': len(images)})
            status = 'draft'
        else:
            status = 'publish'
            complete += 1
        rows.append({
            'Type':'simple',
            'SKU': sku,
            'Name': name,
            'Published': 1 if status=='publish' else 0,
            'Short description': short,
            'Description': long,
            'Regular price': price,
            'Categories': p.get('categories') or '',
            'Tags': p.get('tags') or '',
            'Images': ', '.join(images)
        })
    fieldnames = ['Type','SKU','Name','Published','Short description','Description','Regular price','Categories','Tags','Images']
    with OUT_CSV.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text('\n'.join([
        '# SYNC_SHEET_3_1',
        f'- Total linhas: {len(rows)}',
        f'- Completos (publish): {complete}',
        f'- Pendentes (draft): {len(rows)-complete}',
        '## Erros',
        *[f"- SKU {e['sku']}: name='{e['name']}' price={e['price']} images={e['images']}" for e in errors]
    ]), encoding='utf-8')
    print(f'Gerado {OUT_CSV} com {complete} publicados e {len(rows)-complete} draft')

if __name__ == '__main__':
    main()
