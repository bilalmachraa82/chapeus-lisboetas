#!/usr/bin/env python3
"""Update Google Sheet to track products with AI-generated photos.

Adds a "Fotos AI Geradas" column to mark products that have received
AI-generated editorial photography (3 new images per product).

Usage:
    python3 scripts/update_google_sheet_ai_tracking.py --sku "Boné – 22182"
    python3 scripts/update_google_sheet_ai_tracking.py --sku "Boné – 25025" --scenario "Miradouro"
    python3 scripts/update_google_sheet_ai_tracking.py --report  # Show all marked products
"""

import argparse
import os
import sys
from datetime import datetime
from typing import Optional

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install gspread google-auth")
    sys.exit(1)

# Google Sheets configuration
SHEET_ID = os.environ.get("GOOGLE_SHEETS_ID", "1m5ObJBG3CXetWNN9BoXwE69EVA5RH-xMqozhY3d7ptw")
SERVICE_ACCOUNT_FILE = os.environ.get(
    "GOOGLE_SERVICE_ACCOUNT_FILE",
    "config/google-service-account.json"
)
WORKSHEET_NAME = "Catalogo"
AI_COLUMN_NAME = "Fotos AI Geradas"
SCENARIO_COLUMN_NAME = "Cenário Lisboa"
DATE_COLUMN_NAME = "Data Geração AI"

# Google Sheets API scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_google_sheet():
    """Connect to Google Sheet and return worksheet."""
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SHEET_ID)

    try:
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        print(f"⚠️  Worksheet '{WORKSHEET_NAME}' not found. Creating it...")
        worksheet = spreadsheet.add_worksheet(title=WORKSHEET_NAME, rows=100, cols=20)

    return worksheet


def ensure_tracking_columns(worksheet):
    """Ensure AI tracking columns exist in the sheet."""
    headers = worksheet.row_values(1)

    # Find or create columns
    columns_to_add = []

    if AI_COLUMN_NAME not in headers:
        columns_to_add.append(AI_COLUMN_NAME)
    if SCENARIO_COLUMN_NAME not in headers:
        columns_to_add.append(SCENARIO_COLUMN_NAME)
    if DATE_COLUMN_NAME not in headers:
        columns_to_add.append(DATE_COLUMN_NAME)

    if columns_to_add:
        print(f"➕ Adding columns: {', '.join(columns_to_add)}")
        next_col = len(headers) + 1
        for i, col_name in enumerate(columns_to_add):
            worksheet.update_cell(1, next_col + i, col_name)

        # Refresh headers
        headers = worksheet.row_values(1)

    # Return column indices (1-indexed)
    sku_col = headers.index("SKU") + 1 if "SKU" in headers else None
    ai_col = headers.index(AI_COLUMN_NAME) + 1
    scenario_col = headers.index(SCENARIO_COLUMN_NAME) + 1
    date_col = headers.index(DATE_COLUMN_NAME) + 1

    return sku_col, ai_col, scenario_col, date_col


def mark_product_ai_generated(
    worksheet,
    sku: str,
    scenario: Optional[str] = None,
    sku_col: int = 1,
    ai_col: int = 2,
    scenario_col: int = 3,
    date_col: int = 4
) -> bool:
    """Mark a product as having AI-generated photos."""
    # Find product row by SKU
    try:
        cell = worksheet.find(sku, in_column=sku_col)
        row = cell.row
    except gspread.CellNotFound:
        print(f"⚠️  SKU '{sku}' not found in sheet")
        return False

    # Update tracking columns
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    updates = [
        {"range": f"{gspread.utils.rowcol_to_a1(row, ai_col)}", "values": [["✅ 3 fotos novas"]]},
        {"range": f"{gspread.utils.rowcol_to_a1(row, date_col)}", "values": [[timestamp]]}
    ]

    if scenario:
        updates.append({
            "range": f"{gspread.utils.rowcol_to_a1(row, scenario_col)}",
            "values": [[scenario]]
        })

    worksheet.batch_update(updates)

    print(f"✅ Marked {sku} as AI-generated{f' ({scenario})' if scenario else ''}")
    return True


def get_ai_generated_report(worksheet, sku_col: int, ai_col: int, scenario_col: int) -> list:
    """Get list of all products marked as AI-generated."""
    all_values = worksheet.get_all_values()

    report = []
    for i, row in enumerate(all_values[1:], start=2):  # Skip header
        if len(row) >= ai_col and row[ai_col - 1]:  # Check if AI column has value
            sku = row[sku_col - 1] if len(row) >= sku_col else ""
            scenario = row[scenario_col - 1] if len(row) >= scenario_col else ""
            report.append({
                "row": i,
                "sku": sku,
                "ai_status": row[ai_col - 1],
                "scenario": scenario
            })

    return report


def main():
    parser = argparse.ArgumentParser(description="Track AI-generated photos in Google Sheet")
    parser.add_argument("--sku", help="Product SKU to mark as AI-generated")
    parser.add_argument("--scenario", help="Lisboa scenario used (optional)")
    parser.add_argument("--report", action="store_true", help="Show all AI-generated products")
    args = parser.parse_args()

    if not args.sku and not args.report:
        parser.print_help()
        sys.exit(1)

    # Connect to Google Sheet
    print(f"📊 Connecting to Google Sheet: {SHEET_ID}")
    worksheet = get_google_sheet()
    print(f"✓ Connected to worksheet: {worksheet.title}")

    # Ensure tracking columns exist
    sku_col, ai_col, scenario_col, date_col = ensure_tracking_columns(worksheet)
    print(f"✓ Tracking columns ready")

    if args.report:
        # Show report
        report = get_ai_generated_report(worksheet, sku_col, ai_col, scenario_col)

        if not report:
            print("\n📋 No products marked as AI-generated yet")
        else:
            print(f"\n📋 AI-Generated Products ({len(report)} total):")
            print("=" * 70)
            for item in report:
                scenario_info = f" - {item['scenario']}" if item['scenario'] else ""
                print(f"  • Row {item['row']}: {item['sku']}{scenario_info}")

    elif args.sku:
        # Mark product
        success = mark_product_ai_generated(
            worksheet, args.sku, args.scenario,
            sku_col, ai_col, scenario_col, date_col
        )

        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
