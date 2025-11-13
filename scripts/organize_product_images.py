#!/usr/bin/env python3
"""
Organize Product Images - Fix misplaced files and standardize naming
Moves images to correct SKU folders and resolves hash mismatches
"""

from pathlib import Path
import shutil
import hashlib
from datetime import datetime
from collections import defaultdict
import re

BASE_PATH = Path("/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress/wp-content/uploads/catalogo2025")
REPORT_PATH = Path("/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/relatorios")

def extract_sku_from_filename(filename):
    """Extract SKU from filename (e.g., bone-22195_img_01.jpg -> bone-22195)"""
    if "_" not in filename:
        return None

    stem = Path(filename).stem
    parts = stem.split("_")

    # Check if first part looks like a SKU
    potential_sku = parts[0]
    if re.match(r'^(bone|gorro|boina|chapeu|panama)-\d+[A-Z]?$', potential_sku):
        return potential_sku

    return None

def calculate_file_hash(filepath):
    """Calculate MD5 hash of file"""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def get_file_size(filepath):
    """Get file size in bytes"""
    return filepath.stat().st_size

def audit_images():
    """Audit all images and find misplaced files"""
    print("\n" + "="*80)
    print("AUDITORIA DE IMAGENS - Identificando arquivos mal posicionados")
    print("="*80 + "\n")

    misplaced = []
    all_sku_dirs = {}

    # First pass: collect all SKU directories
    for categoria in BASE_PATH.iterdir():
        if not categoria.is_dir() or categoria.name.startswith('.'):
            continue

        for produto_dir in categoria.iterdir():
            if not produto_dir.is_dir() or produto_dir.name.startswith('.'):
                continue

            sku = produto_dir.name
            all_sku_dirs[sku] = produto_dir

    print(f"Total de pastas de produtos encontradas: {len(all_sku_dirs)}\n")

    # Second pass: find misplaced images
    for categoria in BASE_PATH.iterdir():
        if not categoria.is_dir() or categoria.name.startswith('.'):
            continue

        for produto_dir in categoria.iterdir():
            if not produto_dir.is_dir() or produto_dir.name.startswith('.'):
                continue

            sku_atual = produto_dir.name

            for img in produto_dir.glob("*.jpg"):
                sku_no_arquivo = extract_sku_from_filename(img.name)

                if sku_no_arquivo and sku_no_arquivo != sku_atual:
                    # This image belongs to a different SKU
                    destino_dir = all_sku_dirs.get(sku_no_arquivo)

                    if destino_dir:
                        misplaced.append({
                            'file': img,
                            'current_dir': produto_dir,
                            'current_sku': sku_atual,
                            'correct_sku': sku_no_arquivo,
                            'correct_dir': destino_dir,
                            'categoria': categoria.name
                        })
                        print(f"❌ {img.name}")
                        print(f"   Atual: {sku_atual}/")
                        print(f"   Correto: {sku_no_arquivo}/\n")
                    else:
                        print(f"⚠️  {img.name} - SKU correto não encontrado: {sku_no_arquivo}\n")

    print(f"\n{'='*80}")
    print(f"Total de imagens mal posicionadas: {len(misplaced)}")
    print(f"{'='*80}\n")

    return misplaced

def move_misplaced_images(misplaced_files, dry_run=False):
    """Move images to correct directories"""
    print("\n" + "="*80)
    print(f"{'[DRY RUN] ' if dry_run else ''}MOVENDO IMAGENS PARA PASTAS CORRETAS")
    print("="*80 + "\n")

    moved_count = 0

    for item in misplaced_files:
        src = item['file']
        dst = item['correct_dir'] / src.name

        # Check if destination already exists
        if dst.exists():
            print(f"⚠️  Destino já existe: {dst.name}")

            # Compare file sizes to determine which to keep
            src_size = get_file_size(src)
            dst_size = get_file_size(dst)

            if src_size > dst_size:
                print(f"   Origem maior ({src_size} vs {dst_size} bytes) - substituindo")
                if not dry_run:
                    dst.unlink()
                    shutil.move(str(src), str(dst))
                    moved_count += 1
            else:
                print(f"   Destino maior ou igual - removendo origem duplicada")
                if not dry_run:
                    src.unlink()
                    moved_count += 1
        else:
            print(f"✅ {src.name}")
            print(f"   {item['current_sku']}/ → {item['correct_sku']}/")

            if not dry_run:
                shutil.move(str(src), str(dst))
                moved_count += 1

    print(f"\n{'='*80}")
    print(f"Imagens {'que seriam ' if dry_run else ''}movidas/processadas: {moved_count}")
    print(f"{'='*80}\n")

    return moved_count

def find_hash_mismatches():
    """Find duplicate filenames with different hashes (quality issues)"""
    print("\n" + "="*80)
    print("BUSCANDO HASH MISMATCHES (Duplicatas com Qualidade Diferente)")
    print("="*80 + "\n")

    # Group files by base name (ignoring path)
    file_groups = defaultdict(list)

    for categoria in BASE_PATH.iterdir():
        if not categoria.is_dir() or categoria.name.startswith('.'):
            continue

        for produto_dir in categoria.iterdir():
            if not produto_dir.is_dir() or produto_dir.name.startswith('.'):
                continue

            for img in produto_dir.glob("*.jpg"):
                # Normalize name for comparison
                base_name = img.name.lower()
                file_groups[base_name].append({
                    'path': img,
                    'sku': produto_dir.name,
                    'size': get_file_size(img),
                    'hash': calculate_file_hash(img)
                })

    # Find mismatches
    mismatches = []

    for name, files in file_groups.items():
        if len(files) > 1:
            # Check if hashes differ
            hashes = set(f['hash'] for f in files)
            if len(hashes) > 1:
                mismatches.append({
                    'name': name,
                    'files': files,
                    'hash_count': len(hashes)
                })

                print(f"❌ {name} ({len(files)} cópias, {len(hashes)} versões diferentes)")
                for f in sorted(files, key=lambda x: x['size'], reverse=True):
                    print(f"   {f['sku']}/: {f['size']:,} bytes, hash={f['hash'][:8]}")
                print()

    print(f"{'='*80}")
    print(f"Total de hash mismatches encontrados: {len(mismatches)}")
    print(f"{'='*80}\n")

    return mismatches

def resolve_hash_mismatches(mismatches, dry_run=False):
    """Resolve hash mismatches by keeping highest quality version"""
    print("\n" + "="*80)
    print(f"{'[DRY RUN] ' if dry_run else ''}RESOLVENDO HASH MISMATCHES")
    print("="*80 + "\n")

    resolved_count = 0

    for mismatch in mismatches:
        files = mismatch['files']
        name = mismatch['name']

        # Sort by size (descending) - assume larger = better quality
        sorted_files = sorted(files, key=lambda x: x['size'], reverse=True)
        keep_file = sorted_files[0]
        remove_files = sorted_files[1:]

        print(f"📁 {name}")
        print(f"   ✅ MANTENDO: {keep_file['sku']}/  ({keep_file['size']:,} bytes)")

        for remove in remove_files:
            print(f"   ❌ REMOVENDO: {remove['sku']}/  ({remove['size']:,} bytes)")

            if not dry_run:
                remove['path'].unlink()
                resolved_count += 1

        print()

    print(f"{'='*80}")
    print(f"Arquivos {'que seriam ' if dry_run else ''}removidos: {resolved_count}")
    print(f"{'='*80}\n")

    return resolved_count

def validate_naming_convention():
    """Check if all images follow naming convention"""
    print("\n" + "="*80)
    print("VALIDANDO CONVENÇÃO DE NOMENCLATURA")
    print("="*80 + "\n")

    patterns = {
        'original': r'^img_\d{2}\.jpg$',
        'editorial': r'^img_\d{2}_editorial\.jpg$',
        'angle': r'^img_\d{2}_angle\.jpg$',
        'lifestyle': r'^img_\d{2}_lifestyle_\w+\.jpg$',
        'sku_prefix': r'^(bone|gorro|boina|chapeu|panama)-\d+[A-Z]?_',
    }

    non_compliant = []
    stats = defaultdict(int)

    for categoria in BASE_PATH.iterdir():
        if not categoria.is_dir() or categoria.name.startswith('.'):
            continue

        for produto_dir in categoria.iterdir():
            if not produto_dir.is_dir() or produto_dir.name.startswith('.'):
                continue

            for img in produto_dir.glob("*.jpg"):
                name = img.name

                # Check if it matches any pattern
                matched = False

                # Check for SKU prefix patterns first
                if re.search(patterns['sku_prefix'], name):
                    # Remove SKU prefix for further checking
                    name_without_sku = name.split('_', 1)[1] if '_' in name else name

                    for pattern_name, pattern in patterns.items():
                        if pattern_name == 'sku_prefix':
                            continue
                        if re.match(pattern, name_without_sku):
                            stats[pattern_name] += 1
                            matched = True
                            break
                else:
                    # Check without SKU prefix
                    for pattern_name, pattern in patterns.items():
                        if pattern_name == 'sku_prefix':
                            continue
                        if re.match(pattern, name):
                            stats[pattern_name] += 1
                            matched = True
                            break

                if not matched:
                    non_compliant.append({
                        'file': img,
                        'sku': produto_dir.name
                    })

    print("Estatísticas por tipo de imagem:")
    for pattern_name, count in sorted(stats.items()):
        print(f"  {pattern_name}: {count}")

    if non_compliant:
        print(f"\n❌ {len(non_compliant)} arquivos fora do padrão:")
        for item in non_compliant[:20]:  # Show first 20
            print(f"   {item['sku']}/{item['file'].name}")
        if len(non_compliant) > 20:
            print(f"   ... e mais {len(non_compliant) - 20}")
    else:
        print("\n✅ Todos os arquivos seguem a convenção de nomenclatura!")

    print(f"\n{'='*80}\n")

    return non_compliant

def generate_report(misplaced, mismatches, non_compliant, moved_count, resolved_count):
    """Generate organization report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = REPORT_PATH / f"IMAGENS_ORGANIZACAO_{timestamp}.md"

    REPORT_PATH.mkdir(exist_ok=True)

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# Relatório de Organização de Imagens\n\n")
        f.write(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Base Path:** `{BASE_PATH}`\n\n")

        f.write(f"## Resumo Executivo\n\n")
        f.write(f"- ✅ Imagens movidas para pastas corretas: **{moved_count}**\n")
        f.write(f"- ✅ Hash mismatches resolvidos: **{resolved_count}**\n")
        f.write(f"- ⚠️  Arquivos fora do padrão de nomenclatura: **{len(non_compliant)}**\n\n")

        f.write(f"## Detalhes\n\n")

        f.write(f"### 1. Imagens Mal Posicionadas ({len(misplaced)})\n\n")
        if misplaced:
            for item in misplaced:
                f.write(f"- `{item['file'].name}`\n")
                f.write(f"  - Estava em: `{item['current_sku']}/`\n")
                f.write(f"  - Movida para: `{item['correct_sku']}/`\n\n")
        else:
            f.write("✅ Nenhuma imagem mal posicionada encontrada.\n\n")

        f.write(f"### 2. Hash Mismatches ({len(mismatches)})\n\n")
        if mismatches:
            for mismatch in mismatches:
                f.write(f"- `{mismatch['name']}` ({mismatch['hash_count']} versões diferentes)\n")
                sorted_files = sorted(mismatch['files'], key=lambda x: x['size'], reverse=True)
                f.write(f"  - ✅ Mantida: `{sorted_files[0]['sku']}/` ({sorted_files[0]['size']:,} bytes)\n")
                for removed in sorted_files[1:]:
                    f.write(f"  - ❌ Removida: `{removed['sku']}/` ({removed['size']:,} bytes)\n")
                f.write("\n")
        else:
            f.write("✅ Nenhum hash mismatch encontrado.\n\n")

        f.write(f"### 3. Nomenclatura Não-Padrão ({len(non_compliant)})\n\n")
        if non_compliant:
            f.write("Arquivos que não seguem a convenção de nomenclatura:\n\n")
            for item in non_compliant[:50]:  # First 50
                f.write(f"- `{item['sku']}/{item['file'].name}`\n")
            if len(non_compliant) > 50:
                f.write(f"\n... e mais {len(non_compliant) - 50} arquivos\n")
        else:
            f.write("✅ Todos os arquivos seguem a convenção de nomenclatura.\n")

        f.write(f"\n## Próximos Passos\n\n")
        f.write(f"1. ✅ Imagens organizadas em pastas corretas\n")
        f.write(f"2. ✅ Duplicatas de baixa qualidade removidas\n")
        f.write(f"3. {'⚠️  Renomear arquivos fora do padrão' if non_compliant else '✅ Nomenclatura padronizada'}\n")
        f.write(f"4. 🔄 Executar `consolidate_product_images.py` para validação final\n\n")

        f.write(f"---\n")
        f.write(f"*Relatório gerado automaticamente por `organize_product_images.py`*\n")

    print(f"\n📄 Relatório salvo em: {report_file}\n")

    return report_file

def main():
    print("\n" + "="*80)
    print("ORGANIZAÇÃO DE IMAGENS DE PRODUTOS")
    print("="*80)

    # Step 1: Audit misplaced images
    misplaced = audit_images()

    # Step 2: Move misplaced images
    moved_count = move_misplaced_images(misplaced, dry_run=False)

    # Step 3: Find hash mismatches
    mismatches = find_hash_mismatches()

    # Step 4: Resolve hash mismatches
    resolved_count = resolve_hash_mismatches(mismatches, dry_run=False)

    # Step 5: Validate naming convention
    non_compliant = validate_naming_convention()

    # Step 6: Generate report
    report_file = generate_report(misplaced, mismatches, non_compliant, moved_count, resolved_count)

    print("\n" + "="*80)
    print("✅ ORGANIZAÇÃO CONCLUÍDA")
    print("="*80)
    print(f"\nResumo:")
    print(f"  - Imagens movidas: {moved_count}")
    print(f"  - Hash mismatches resolvidos: {resolved_count}")
    print(f"  - Arquivos fora do padrão: {len(non_compliant)}")
    print(f"\n📄 Relatório: {report_file}\n")

if __name__ == "__main__":
    main()
