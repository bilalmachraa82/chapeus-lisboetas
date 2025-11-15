#!/usr/bin/env python3
import csv
from urllib.parse import urlparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS = BASE_DIR / 'wordpress' / 'wp-content' / 'uploads'
REPORT = BASE_DIR / 'relatorios' / 'IMPORT_VERIFIER_3_1.md'

def local_path(url):
    try:
        p = urlparse(url)
        return UPLOADS / Path(p.path.replace('/wp-content/uploads/',''))
    except:
        return None

def verify(csv_path):
    rows = list(csv.DictReader(open(csv_path, encoding='utf-8')))
    dup = {}
    missing = []
    invalid = []
    for r in rows:
        sku = (r.get('SKU') or '').strip()
        price = float(str(r.get('Regular price') or '0').replace(',','.'))
        dup[sku] = dup.get(sku, 0) + 1
        if price <= 0:
            invalid.append({'sku': sku, 'reason': 'price<=0'})
        imgs = (r.get('Images') or '').split(',')
        imgs = [i.strip() for i in imgs if i.strip()]
        for u in imgs[:3]:
            lp = local_path(u)
            if lp and not lp.exists():
                missing.append({'sku': sku, 'image': str(lp)})
    duplicates = [s for s, c in dup.items() if s and c > 1]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text('\n'.join([
        '# Import Verifier 3.1',
        f'- CSV: {csv_path}',
        f'- Linhas: {len(rows)}',
        f'- Duplicados SKU: {len(duplicates)}',
        *[f'- DUP {s}' for s in duplicates],
        f'- Imagens em falta: {len(missing)}',
        *[f"- MISS {m['sku']}: {m['image']}" for m in missing[:50]],
        f'- Registos inválidos (preço): {len(invalid)}'
    ]), encoding='utf-8')
    print(f'Relatório: {REPORT}')

if __name__ == '__main__':
    import sys
    verify(sys.argv[1] if len(sys.argv) > 1 else str(BASE_DIR / 'output_catalogo' / 'catalogo_clean_ready.csv'))