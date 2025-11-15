#!/usr/bin/env python3
"""
Cleanup WordPress Products Without Price
Remove products from WooCommerce that don't have a valid price (violates business rule)
"""

import mysql.connector
import json
from datetime import datetime

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'rootpassword',
    'database': 'lisboetas_web',
    'port': 3306
}

def connect_db():
    """Connect to WordPress database"""
    return mysql.connector.connect(**DB_CONFIG)

def get_products_without_price():
    """Find all published products without a valid price"""
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    # Query: Products published but no price OR price empty/zero
    query = """
    SELECT
        p.ID,
        p.post_name as slug,
        p.post_title as title,
        p.post_date,
        pm_price.meta_value as price,
        pm_sku.meta_value as sku
    FROM lx_posts p
    LEFT JOIN lx_postmeta pm_price ON p.ID = pm_price.post_id
        AND pm_price.meta_key = '_price'
    LEFT JOIN lx_postmeta pm_sku ON p.ID = pm_sku.post_id
        AND pm_sku.meta_key = '_sku'
    WHERE p.post_type = 'product'
        AND p.post_status = 'publish'
        AND (pm_price.meta_value IS NULL
             OR pm_price.meta_value = ''
             OR pm_price.meta_value = '0'
             OR pm_price.meta_value = '0.00')
    ORDER BY p.post_date DESC
    """

    cursor.execute(query)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return products

def delete_product(product_id):
    """Delete product and all its metadata"""
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # 1. Delete product meta
        cursor.execute("DELETE FROM lx_postmeta WHERE post_id = %s", (product_id,))

        # 2. Delete taxonomy relationships
        cursor.execute("DELETE FROM lx_term_relationships WHERE object_id = %s", (product_id,))

        # 3. Delete post
        cursor.execute("DELETE FROM lx_posts WHERE ID = %s", (product_id,))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Error deleting product {product_id}: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    print("\n" + "="*80)
    print("FASE 2: CLEANUP PRODUTOS SEM PREÇO")
    print("="*80 + "\n")

    # 1. Find products without price
    print("🔍 Buscando produtos sem preço...")
    products_no_price = get_products_without_price()

    print(f"   Encontrados: {len(products_no_price)} produtos sem preço válido\n")

    if not products_no_price:
        print("✅ Nenhum produto sem preço encontrado. Database já está limpo.")
        return

    # 2. Display list
    print("="*80)
    print("PRODUTOS A DELETAR:")
    print("="*80)
    print(f"{'ID':<8} {'SKU':<20} {'PREÇO':<10} {'TÍTULO':<40}")
    print("-"*80)

    for product in products_no_price:
        price_display = product.get('price', 'NULL') or 'NULL'
        sku_display = product.get('sku', 'N/A') or 'N/A'
        title_display = (product['title'][:37] + '...') if len(product['title']) > 40 else product['title']

        print(f"{product['ID']:<8} {sku_display:<20} {price_display:<10} {title_display:<40}")

    print("-"*80)
    print(f"TOTAL: {len(products_no_price)} produtos\n")

    # 3. Save report before deletion
    report = {
        'date': datetime.now().isoformat(),
        'total_products': len(products_no_price),
        'products': [
            {
                'id': p['ID'],
                'slug': p['slug'],
                'title': p['title'],
                'sku': p.get('sku'),
                'price': p.get('price'),
                'post_date': str(p['post_date'])
            }
            for p in products_no_price
        ]
    }

    report_path = f"relatorios/PRODUCTS_DELETED_NO_PRICE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"💾 Relatório salvo: {report_path}\n")

    # 4. Delete products
    print("🗑️  Deletando produtos...")
    deleted_count = 0
    failed_count = 0

    for i, product in enumerate(products_no_price, 1):
        print(f"   [{i}/{len(products_no_price)}] ID {product['ID']} ({product['slug']})...", end=" ")

        if delete_product(product['ID']):
            deleted_count += 1
            print("✅")
        else:
            failed_count += 1
            print("❌")

    # 5. Summary
    print("\n" + "="*80)
    print("📊 RESUMO")
    print("="*80)
    print(f"Produtos deletados:  {deleted_count}")
    print(f"Falhas:              {failed_count}")
    print(f"Total processado:    {len(products_no_price)}")

    # 6. Verify final state
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM lx_posts WHERE post_type='product' AND post_status='publish'")
    total_after = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    print(f"\nProdutos publicados após cleanup: {total_after}")
    print(f"Esperado redução: {len(products_no_price)}")

    print("\n✅ FASE 2 COMPLETA\n")

    return report

if __name__ == "__main__":
    main()
