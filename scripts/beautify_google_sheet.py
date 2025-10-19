#!/usr/bin/env python3
"""Apply premium formatting and dashboard to the Google Sheet catalog."""
from __future__ import annotations

import os
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1, a1_to_rowcol
from gspread_formatting import (
    Color,
    TextFormat,
    CellFormat,
    format_cell_ranges,
    set_frozen,
    set_row_height,
    set_column_width,
    ConditionalFormatRule,
    BooleanRule,
    GridRange,
    BooleanCondition,
    set_data_validation_for_cell_range,
    DataValidationRule,
    get_conditional_format_rules,
)

SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "config/google-service-account.json")
WORKSHEET_NAME = os.getenv("GOOGLE_SHEETS_TAB", "worksheet")
IMAGE_BASE_URL = os.getenv("IMAGE_BASE_URL", "https://chapeuslisboeta.pt/wp-content/uploads/")

HEADER_BG = Color(0.12, 0.16, 0.20)
HEADER_TEXT = TextFormat(bold=True, foregroundColor=Color(1, 1, 1), fontFamily="Montserrat", fontSize=11)
ODD_ROW_BG = Color(0.97, 0.98, 0.99)


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def col_to_letter(col: int) -> str:
    result = ""
    while col > 0:
        col, remainder = divmod(col - 1, 26)
        result = chr(65 + remainder) + result
    return result


def get_client():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return gspread.authorize(creds)


def ensure_columns(ws):
    desired_order = [
        "Sheet",
        "SKU",
        "Nome",
        "Preço",
        "Descrição curta",
        "Descrição longa",
        "Tags",
        "Cor",
        "Tamanho",
        "Composição",
        "Pack",
        "URL fornecedor",
        "URLs extra",
        "Imagens",
        "Preview",
        "Status",
        "Prioridade",
        "Destaque homepage?",
        "Notas internas",
    ]

    values = ws.get_all_values()
    if not values:
        ws.update(range_name="A1", values=[desired_order])
        return

    header = values[0]
    data = values[1:]
    index_map = {name: idx for idx, name in enumerate(header)}

    reordered = []
    for row in data:
        new_row = []
        for col in desired_order:
            if col == "Preview" or col == "Status":
                new_row.append("")
            else:
                idx = index_map.get(col)
                new_row.append(row[idx] if idx is not None and idx < len(row) else "")
        reordered.append(new_row)

    ws.clear()
    ws.update(range_name="A1", values=[desired_order] + reordered)

    preview_col = desired_order.index("Preview") + 1
    preview_formula = (
        f"=ARRAYFORMULA(IF(ROW(A:A)=1,'Preview',"
        f"IF(LEN(N:N), IF(N:N<>'' ,IMAGE(\"{IMAGE_BASE_URL}\" & N:N), ''), ''))))"
    )
    ws.update_acell(rowcol_to_a1(1, preview_col), preview_formula)

    status_col = desired_order.index("Status") + 1
    status_formula = (
        "=ARRAYFORMULA(IF(ROW(A:A)=1,'Status',"
        "IF(LEN(B:B)=0,'',IF(LEN(N:N)=0,'Sem foto',IF(LEN(D:D)=0,'Sem preço','OK')))))"
    )
    ws.update_acell(rowcol_to_a1(1, status_col), status_formula)

    destaque_col = desired_order.index("Destaque homepage?") + 1
    rng = f"{rowcol_to_a1(2, destaque_col)}:{rowcol_to_a1(ws.row_count, destaque_col)}"
    validation_rule = DataValidationRule(BooleanCondition("BOOLEAN"), strict=True)
    set_data_validation_for_cell_range(ws, rng, validation_rule)


def apply_formatting(ws):
    header_range = f"A1:{rowcol_to_a1(1, ws.col_count)}"
    format_cell_ranges(
        ws,
        [
            (header_range, CellFormat(backgroundColor=HEADER_BG, textFormat=HEADER_TEXT, horizontalAlignment="CENTER")),
        ],
    )
    set_frozen(ws, rows=1, cols=2)

    # Alternate row striping (odd rows)
    # gspread-formatting lacks direct banded range; use conditional formatting for odd rows
    odd_rule = ConditionalFormatRule(
        ranges=[GridRange.from_a1_range(f"A2:{rowcol_to_a1(ws.row_count, ws.col_count)}", ws)],
        booleanRule=BooleanRule(
            condition=BooleanCondition("CUSTOM_FORMULA", ["=ISEVEN(ROW())"]),
            format=CellFormat(backgroundColor=ODD_ROW_BG),
        ),
    )
    rules = get_conditional_format_rules(ws)
    rules.clear()
    rules.append(odd_rule)

    # Column widths
    widths = {
        1: 110,
        2: 150,
        3: 280,
        4: 90,
        5: 240,
        6: 280,
        7: 200,
        8: 140,
        9: 140,
        10: 160,
        11: 120,
        12: 260,
        13: 220,
        14: 220,
        15: 160,
        16: 120,
        17: 120,
        18: 140,
        19: 220,
    }
    for col, width in widths.items():
        col_letter = col_to_letter(col)
        set_column_width(ws, f"{col_letter}:{col_letter}", width)
    set_row_height(ws, "1:1", 30)

    # Conditional formatting: preço vazio
    price_col = 4
    price_range = GridRange.from_a1_range(f"D2:D{ws.row_count}", ws)
    price_rule = ConditionalFormatRule(
        ranges=[price_range],
        booleanRule=BooleanRule(
            condition=BooleanCondition("BLANK"),
            format=CellFormat(backgroundColor=Color(1, 0.8, 0.8)),
        ),
    )
    rules.append(price_rule)

    # Conditional formatting: imagens vazias
    image_range = GridRange.from_a1_range(f"N2:N{ws.row_count}", ws)
    image_rule = ConditionalFormatRule(
        ranges=[image_range],
        booleanRule=BooleanRule(
            condition=BooleanCondition("BLANK"),
            format=CellFormat(backgroundColor=Color(1, 0.92, 0.75)),
        ),
    )
    rules.append(image_rule)
    rules.save()



def ensure_faltas_sheet(sh):
    title = "Faltas"
    existing_notes = {}
    carry_over_rows: List[List[str]] = []
    try:
        ws = sh.worksheet(title)
        existing_records = ws.get_all_records()
        for record in existing_records:
            sku = (record.get("SKU") or record.get("SKU/Código") or "").strip()
            if sku:
                existing_notes[sku] = {
                    "nova": record.get("Nova URL/Foto", ""),
                    "notas": record.get("Notas", ""),
                }
            else:
                carry_over_rows.append(
                    [
                        record.get("Coleção", ""),
                        record.get("Produto", record.get("Nome produto", "")),
                        record.get("SKU", ""),
                        record.get("URL fornecedor", ""),
                        record.get("Links adicionais", ""),
                        record.get("Motivo", ""),
                        record.get("Nova URL/Foto", ""),
                        record.get("Notas", ""),
                    ]
                )
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=200, cols=8)

    headers = [
        "Coleção",
        "Produto",
        "SKU",
        "URL fornecedor",
        "Links adicionais",
        "Motivo",
        "Nova URL/Foto",
        "Notas",
    ]

    rows: List[List[str]] = []
    if FALTAS_CSV.exists():
        with FALTAS_CSV.open(encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for entry in reader:
                sku = (entry.get("SKU/Código", "") or "").strip()
                note_info = existing_notes.get(sku, {})
                rows.append(
                    [
                        entry.get("Folha", ""),
                        entry.get("Nome produto", ""),
                        sku,
                        entry.get("URL fornecedor", ""),
                        entry.get("Links adicionais", ""),
                        entry.get("Motivo", ""),
                        note_info.get("nova", ""),
                        note_info.get("notas", ""),
                    ]
                )
    else:
        rows.append(["", "Nenhum relatório gerado ainda.", "", "", "", "", "", ""])

    rows.extend(carry_over_rows)

    total_rows = len(rows)
    ws.resize(rows=max(total_rows + 10, 80), cols=len(headers))
    update_range = f"A1:{rowcol_to_a1(total_rows + 1, len(headers))}"
    ws.update(update_range, [headers] + rows, value_input_option="USER_ENTERED")

    header_range = f"A1:{rowcol_to_a1(1, len(headers))}"
    format_cell_ranges(
        ws,
        [
            (
                header_range,
                CellFormat(
                    backgroundColor=BRAND_AQUA,
                    textFormat=TextFormat(bold=True, foregroundColor=TEXT_DARK),
                    horizontalAlignment="CENTER",
                ),
            )
        ],
    )
    set_frozen(ws, rows=1, cols=1)

    wrap_cols = ["Motivo", "Notas"]
    for col_name in wrap_cols:
        if col_name in headers:
            letter = col_to_letter(headers.index(col_name) + 1)
            format_cell_ranges(ws, [(f"{letter}:{letter}", CellFormat(wrapStrategy="WRAP"))])

    widths = {1: 180, 2: 320, 3: 160, 4: 260, 5: 220, 6: 220, 7: 200, 8: 220}
    for idx, width in widths.items():
        col_letter = col_to_letter(idx)
        set_column_width(ws, f"{col_letter}:{col_letter}", width)

    set_row_height(ws, "1:1", 30)
    if total_rows:
        set_row_height(ws, f"2:{total_rows + 1}", 80)

    try:
        ws.set_basic_filter(header_range)
    except Exception:
        pass

    return ws


def ensure_summary_colecoes(sh):
    title = "Resumo Coleções"
    try:
        ws = sh.worksheet(title)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=200, cols=3)

    headers = ["Coleção", "Total", "% do catálogo"]
    rows: List[List[str]] = []
    if RESUMO_COLECOES_CSV.exists():
        with RESUMO_COLECOES_CSV.open(encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for entry in reader:
                rows.append([entry.get("Coleção", ""), entry.get("Total", ""), ""])
    else:
        rows.append(["Sem dados", "", ""])

    total_rows = len(rows)
    ws.resize(rows=max(total_rows + 10, 50), cols=len(headers))
    ws.update(f"A1:{rowcol_to_a1(total_rows + 1, len(headers))}", [headers] + rows)

    if total_rows:
        end_row = total_rows + 1
        percent_range = f"C2:C{end_row}"
        percent_values = [
            [f"=IF(B{row}=0,\"\",B{row}/SUM($B$2:$B${end_row}))"]
            for row in range(2, end_row + 1)
        ]
        ws.update(percent_range, percent_values, value_input_option="USER_ENTERED")
        format_cell_ranges(
            ws,
            [(f"C2:C{end_row}", CellFormat(numberFormat=NumberFormat(type="PERCENT", pattern="0%")))],
        )

    header_range = f"A1:{rowcol_to_a1(1, len(headers))}"
    format_cell_ranges(
        ws,
        [
            (
                header_range,
                CellFormat(
                    backgroundColor=BRAND_AQUA,
                    textFormat=TextFormat(bold=True, foregroundColor=TEXT_DARK),
                ),
            )
        ],
    )
    set_frozen(ws, rows=1, cols=1)

    widths = {1: 260, 2: 120, 3: 160}
    for idx, width in widths.items():
        col_letter = col_to_letter(idx)
        set_column_width(ws, f"{col_letter}:{col_letter}", width)

    try:
        ws.set_basic_filter(header_range)
    except Exception:
        pass

    return ws


def ensure_summary_tipos(sh):
    title = "Resumo Tipos"
    try:
        ws = sh.worksheet(title)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=300, cols=4)

    headers = ["Coleção", "Tipo", "Total", "Ranking"]
    rows: List[List[str]] = []
    if RESUMO_TIPOS_CSV.exists():
        with RESUMO_TIPOS_CSV.open(encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for entry in reader:
                rows.append([
                    entry.get("Coleção", ""),
                    entry.get("Tipo", ""),
                    entry.get("Total", ""),
                    "",
                ])
    else:
        rows.append(["Sem dados", "", "", ""])

    total_rows = len(rows)
    ws.resize(rows=max(total_rows + 10, 80), cols=len(headers))
    ws.update(f"A1:{rowcol_to_a1(total_rows + 1, len(headers))}", [headers] + rows)

    if total_rows:
        end_row = total_rows + 1
        ranking_range = f"D2:D{end_row}"
        ranking_values = [
            [f"=IF(C{row}=\"\",\"\",RANK(C{row},$C$2:$C${end_row}))"]
            for row in range(2, end_row + 1)
        ]
        ws.update(ranking_range, ranking_values, value_input_option="USER_ENTERED")

    header_range = f"A1:{rowcol_to_a1(1, len(headers))}"
    format_cell_ranges(
        ws,
        [
            (
                header_range,
                CellFormat(
                    backgroundColor=BRAND_AQUA,
                    textFormat=TextFormat(bold=True, foregroundColor=TEXT_DARK),
                ),
            )
        ],
    )
    set_frozen(ws, rows=1, cols=1)

    widths = {1: 200, 2: 320, 3: 120, 4: 120}
    for idx, width in widths.items():
        col_letter = col_to_letter(idx)
        set_column_width(ws, f"{col_letter}:{col_letter}", width)

    try:
        ws.set_basic_filter(header_range)
    except Exception:
        pass

    return ws


def ensure_history_sheet(sh):
    title = "Histórico"
    headers = ["Timestamp", "Utilizador", "SKU", "Campo", "Valor antigo", "Valor novo", "Notas"]
    try:
        ws = sh.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=1000, cols=len(headers))

    current_header = ws.row_values(1)
    if current_header != headers:
        ws.update("A1", [headers])

    header_range = f"A1:{rowcol_to_a1(1, len(headers))}"
    format_cell_ranges(
        ws,
        [
            (
                header_range,
                CellFormat(
                    backgroundColor=Color(0.88, 0.88, 0.92),
                    textFormat=TextFormat(bold=True, foregroundColor=TEXT_DARK),
                ),
            )
        ],
    )
    set_frozen(ws, rows=1, cols=2)

    return ws


def ensure_guide_sheet(sh):
    title = "Guia"
    try:
        ws = sh.worksheet(title)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=200, cols=4)

    content = [
        ["Passo", "O que fazer"],
        [
            "1",
            "Revise a aba 'Catalogo': verifique Status, pré-visualizações e complete preços/descrições antes de sincronizar.",
        ],
        [
            "2",
            "Abra 'Faltas' para tratar produtos sem imagem/URL. Preencha 'Nova URL/Foto' ou adicione nota para a equipa.",
        ],
        [
            "3",
            "Use 'Resumo Coleções' e 'Resumo Tipos' para perceber desequilíbrios antes de campanhas.",
        ],
        [
            "4",
            "Quando terminar, executar scripts: python scripts/sync_google_sheet.py e scripts/generate_wc_catalog.py.",
        ],
        [
            "5",
            "Após importação no WooCommerce, correr util/qa_catalogo.py e validar destaques na homepage.",
        ],
        [
            "Sugestões",
            "Menu Format → Theme para aplicar as cores da marca; usar Inserir → Segmentador de dados para filtros rápidos.",
        ],
        [
            "Ajuda",
            "Contactar equipa Codex via canal habitual ou e-mail suporte@chapeuslisboeta.pt.",
        ],
    ]

    ws.update("A1:B8", content)

    header_range = "A1:B1"
    format_cell_ranges(
        ws,
        [
            (
                header_range,
                CellFormat(
                    backgroundColor=BRAND_ROSE,
                    textFormat=TextFormat(bold=True, foregroundColor=TEXT_DARK),
                ),
            )
        ],
    )
    ws.format("A2:A8", {"textFormat": {"bold": True}})

    widths = {1: 120, 2: 520}
    for idx, width in widths.items():
        col_letter = col_to_letter(idx)
        set_column_width(ws, f"{col_letter}:{col_letter}", width)

    set_row_height(ws, "1:1", 30)

    return ws

def ensure_dashboard(sh):
    dashboard_name = "Dashboard"
    try:
        dash_ws = sh.worksheet(dashboard_name)
        dash_ws.clear()
    except gspread.WorksheetNotFound:
        dash_ws = sh.add_worksheet(title=dashboard_name, rows=100, cols=20)

    dash_ws.update("A1", "🎩 Chapéus Lisboeta – Catálogo Premium")
    dash_ws.format("A1", CellFormat(textFormat=TextFormat(bold=True, fontSize=18)))

    metrics = [
        ("B3", "Total de produtos", "=COUNTA(Catalogo!B2:B)"),
        ("D3", "Produtos sem foto", "=COUNTIF(Catalogo!Status:Status, \"Sem foto\")"),
        ("F3", "Produtos sem preço", "=COUNTIF(Catalogo!Status:Status, \"Sem preço\")"),
        ("H3", "Produtos destacados", "=COUNTIF(Catalogo!P:P, TRUE)")
    ]
    dash_ws.update_acell("A3", "")
    from gspread.utils import a1_to_rowcol

    for cell, label, formula in metrics:
        dash_ws.update(cell, label)
        row, col = a1_to_rowcol(cell)
        value_cell = rowcol_to_a1(row + 1, col)
        dash_ws.update_acell(value_cell, formula)
        dash_ws.format(f"{cell}:{value_cell}", CellFormat(textFormat=TextFormat(bold=True)))

    # Tabelas de resumo
    dash_ws.update("A7", "Coleções")
    dash_ws.update("A8", "=QUERY(Catalogo!A2:B, \"select A, count(A) where A is not null group by A label count(A) 'Total'\")")
    dash_ws.update("D7", "Top tipos")
    dash_ws.update(
        "D8",
        "=QUERY({Catalogo!A2:A, Catalogo!C2:C}, \"select Col1, Col2, count(Col2) where Col2 is not null group by Col1, Col2 order by count(Col2) desc limit 10 label count(Col2) 'Total'\")",
    )

    dash_ws.update("A20", "Avisos & Ações")
    dash_ws.update("A21", "1. Preencher URLs/fotos pendentes na aba 'Faltas'.")
    dash_ws.update("A22", "2. Atualizar prioridade/destaque conforme campanhas.")
    dash_ws.update("A23", "3. Após alterações, correr sync_google_sheet.py e generate_wc_catalog.py.")

    dash_ws.format("A7:B7", CellFormat(textFormat=TextFormat(bold=True), backgroundColor=Color(0.87, 0.93, 1)))
    dash_ws.format("D7:F7", CellFormat(textFormat=TextFormat(bold=True), backgroundColor=Color(0.87, 0.93, 1)))


def main():
    if not SHEET_ID:
        raise SystemExit("Defina GOOGLE_SHEETS_ID.")

    client = get_client()
    sh = client.open_by_key(SHEET_ID)
    ws = sh.worksheet(WORKSHEET_NAME)

    ensure_columns(ws)
    apply_formatting(ws)
    ensure_dashboard(sh)

    print("Formatação premium aplicada com sucesso.")


if __name__ == "__main__":
    main()
