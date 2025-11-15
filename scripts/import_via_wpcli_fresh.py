#!/usr/bin/env python3
import csv
import subprocess
import json
import argparse
import sys
from pathlib import Path
import time

CONTAINER_NAME = "chapeus2_wordpress"
CSV_FILE = "output_catalogo/catalogo_clean_ready.csv"
WP_USER = "admin"
IMAGE_BASE_URL = "http://localhost:8084/wp-content/uploads"

stats = {'total':0,'success':0,'failed':0,'skipped':0,'errors':[]}
term_cache = []

def run_wp(args, capture_output=True):
    cmd = ["docker","exec",CONTAINER_NAME,
           "php","/var/www/html/wp-cli.phar", *args,
           f"--user={WP_USER}", "--allow-root"]
    return subprocess.run(cmd, capture_output=capture_output, text=True, timeout=120)

def product_exists(sku:str):
    r = run_wp(["post","list","--post_type=product",f"--meta_key=_sku",f"--meta_value={sku}","--field=ID","--format=csv"])
    if r.returncode==0 and r.stdout.strip():
        try:
            return int(r.stdout.strip())
        except: return None
    return None

def load_terms():
    global term_cache
    if term_cache: return
    r = run_wp(["term","list","product_cat","--format=json"])
    term_cache = json.loads(r.stdout) if r.returncode==0 and r.stdout.strip() else []

def find_term_id(name,parent):
    load_terms()
    for t in term_cache:
        if t.get("name")==name and int(t.get("parent",0))==parent:
            return int(t["term_id"])
    return None

def add_term(term_id,name,parent):
    term_cache.append({"term_id":term_id,"name":name,"parent":parent})

def ensure_category(path:str):
    if not path or path=="Uncategorized": return None
    parts=[p.strip() for p in path.split('>')]
    parent=0
    for p in parts:
        exist=find_term_id(p,parent)
        if exist: parent=exist
        else:
            r=run_wp(["term","create","product_cat",p,f"--parent={parent}","--porcelain"])
            if r.returncode==0:
                new_id=int(r.stdout.strip())
                add_term(new_id,p,parent)
                parent=new_id
            else:
                return None
    return parent

def prepare_images(images_str:str):
    if not images_str: return []
    urls=[]
    for img in images_str.split(','):
        img=img.strip()
        if not img: continue
        if img.startswith('http'): url=img
        else: url=f"{IMAGE_BASE_URL}/{img.lstrip('/')}"
        urls.append({"src":url})
    return urls

def import_row(row, dry=False):
    sku=(row.get('SKU','') or '').strip().split('\n')[0]
    name=(row.get('Name','') or '').strip()
    if not sku or not name:
        stats['skipped']+=1
        return False
    pid=product_exists(sku)
    base=["wc","product","update",str(pid)] if pid else ["wc","product","create"]
    cmd=base+[f"--name={name}",f"--sku={sku}",f"--status={'publish' if row.get('Published')=='1' else 'draft'}"]
    rp=(row.get('Regular price','') or '').strip()
    if rp: cmd.append(f"--regular_price={rp}")
    sp=(row.get('Sale price','') or '').strip()
    if sp: cmd.append(f"--sale_price={sp}")
    sd=(row.get('Short description','') or '').strip()
    if sd: cmd.append(f"--short_description={sd}")
    de=(row.get('Description','') or '').strip()
    if de: cmd.append(f"--description={de}")
    cat=(row.get('Categories','') or '').strip()
    if cat:
        cid=ensure_category(cat)
        if cid:
            cmd.append(f"--categories={json.dumps([{'id':cid}])}")
    imgs=(row.get('Images','') or '').strip()
    if imgs:
        lst=prepare_images(imgs)
        if lst: cmd.append(f"--images={json.dumps(lst)}")
    st=(row.get('Stock','') or '').strip()
    if st.isdigit():
        cmd+= [f"--stock_quantity={st}","--manage_stock=true"]
    if dry:
        print("DRY:","wp"," ".join(cmd)); return True
    r=run_wp(cmd)
    if r.returncode==0:
        stats['success']+=1; return True
    stats['failed']+=1; stats['errors'].append({'sku':sku,'name':name,'error':r.stderr}); return False

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--limit',type=int)
    ap.add_argument('--dry-run',action='store_true')
    ap.add_argument('--csv',default=CSV_FILE)
    a=ap.parse_args()
    p=Path(a.csv)
    if not p.exists():
        print("CSV not found:",p); sys.exit(1)
    rows=list(csv.DictReader(p.open()))
    stats['total']=len(rows)
    if a.limit: rows=rows[:a.limit]
    for i,row in enumerate(rows,1):
        print(f"[{i}/{len(rows)}] {row.get('Name','')[:48]}", end=' ')
        ok=import_row(row,a.dry_run)
        print("✓" if ok else "✗")
        if not a.dry_run: time.sleep(0.1)
    print("Summary:",stats)
    sys.exit(0 if stats['failed']==0 else 1)

if __name__=='__main__':
    main()