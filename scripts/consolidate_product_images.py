#!/usr/bin/env python3
"""Consolidate product images into catalogo2025 directory.

- Scans legacy directory (uploads/products) and canonical directory (uploads/catalogo2025)
- Copies any files that only exist in legacy into canonical, preserving relative structure
- Reports duplicates present in both locations (with size/hash mismatch detection)
- Supports dry-run mode
"""

import argparse
import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'wordpress' / 'wp-content' / 'uploads'
LEGACY = ROOT / 'products'
CANON = ROOT / 'catalogo2025'


def hash_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    md5 = hashlib.md5()
    with path.open('rb') as f:
        while chunk := f.read(chunk_size):
            md5.update(chunk)
    return md5.hexdigest()


def collect_files(base: Path) -> dict:
    mapping = {}
    for file in base.rglob('*'):
        if file.is_file():
            mapping[file.relative_to(base)] = file
    return mapping


def main(dry_run: bool, verbose: bool):
    legacy = collect_files(LEGACY)
    canon = collect_files(CANON)

    to_copy = []
    duplicates = []
    hash_mismatches = []

    for rel, src in legacy.items():
        dest = CANON / rel
        if rel not in canon:
            to_copy.append((src, dest))
        else:
            # detect if files differ
            src_hash = hash_file(src)
            dest_hash = hash_file(canon[rel])
            if src_hash != dest_hash:
                hash_mismatches.append((rel, src_hash, dest_hash))
            duplicates.append(rel)

    print(f"Legacy files: {len(legacy)}, Canon files: {len(canon)}")
    print(f"Duplicates: {len(duplicates)}, Unique legacy files to copy: {len(to_copy)}")

    if hash_mismatches:
        print("Hash mismatches (need manual review):")
        for rel, s_hash, d_hash in hash_mismatches[:10]:
            print(f"  {rel}: legacy={s_hash} canon={d_hash}")

    if dry_run:
        print("Dry-run mode, not copying any files.")
        return

    for idx, (src, dest) in enumerate(to_copy, 1):
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        if verbose:
            print(f"[{idx}/{len(to_copy)}] Copied {src.relative_to(LEGACY)}")

    print(f"Copied {len(to_copy)} files into {CANON.relative_to(ROOT)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Consolidate product images')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    main(args.dry_run, args.verbose)
