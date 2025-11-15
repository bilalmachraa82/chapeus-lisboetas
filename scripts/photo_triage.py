#!/usr/bin/env python3
import os
import re
import sys
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS = BASE_DIR / 'wordpress' / 'wp-content' / 'uploads' / 'catalogo2025'
REPORT_PATH = BASE_DIR / 'relatorios' / 'IMAGENS_TRIAGE_3_1.md'

SKU_PATTERN = re.compile(r'(bone|gorro|panama|palha|casquette|chapeu|bob|boina|hologramme|HOLOGRAMME)-[A-Za-z0-9\-]+', re.IGNORECASE)

def find_sku(text: str):
    m = SKU_PATTERN.search(text)
    return m.group(0) if m else None

def scan():
    anomalies = []
    totals = {'files': 0, 'dirs': 0, 'cross_sku': 0}
    for root, dirs, files in os.walk(UPLOADS):
        totals['dirs'] += len(dirs)
        for f in files:
            if not f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                continue
            totals['files'] += 1
            rel_dir = Path(root).relative_to(UPLOADS)
            rel_path = rel_dir / f
            current_sku = find_sku(str(rel_dir))
            file_sku = find_sku(f)
            if file_sku and current_sku and file_sku.lower() != current_sku.lower():
                anomalies.append({
                    'file': str(rel_path),
                    'in_dir_sku': current_sku,
                    'file_sku': file_sku,
                    'suggest_dest': str(Path(file_sku.lower()) / f)
                })
    return anomalies, totals

def write_report(anomalies, totals):
    lines = []
    lines.append('# Triagem de Imagens – Plano 3.1\n')
    lines.append(f'- Diretório: `{UPLOADS}`\n')
    lines.append(f'- Ficheiros: {totals["files"]} | Pastas: {totals["dirs"]}\n')
    lines.append(f'- Cruzamentos detectados: {len(anomalies)}\n')
    lines.append('\n## Anomalias (cross‑SKU)\n')
    if not anomalies:
        lines.append('Nenhuma anomalia encontrada.\n')
    else:
        for i, a in enumerate(anomalies, 1):
            lines.append(f'{i}. `{a["file"]}` → dir `{a["in_dir_sku"]}` mas nome indica `{a["file_sku"]}`; sugerido: `{a["suggest_dest"]}`')
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text('\n'.join(lines), encoding='utf-8')

def apply_moves(anomalies):
    for a in anomalies:
        src = UPLOADS / a['file']
        dest_dir = UPLOADS / a['file_sku'].lower()
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / Path(a['file']).name
        if src.exists():
            shutil.move(str(src), str(dest))

def main():
    do_apply = '--apply' in sys.argv
    anomalies, totals = scan()
    write_report(anomalies, totals)
    if do_apply and anomalies:
        apply_moves(anomalies)
        anomalies2, totals2 = scan()
        write_report(anomalies2, totals2)
    print(f'Triagem completa. Relatório: {REPORT_PATH}')

if __name__ == '__main__':
    main()