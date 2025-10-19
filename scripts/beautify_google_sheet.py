#!/usr/bin/env python3
"""Apply premium formatting and dashboards to the Google Sheets catálogo."""
from __future__ import annotations

import csv
import os
import time
from pathlib import Path
from typing import List

import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import a1_to_rowcol, rowcol_to_a1
from gspread_formatting import (
    BooleanCondition,
    BooleanRule,
    CellFormat,
    Color,
    ConditionalFormatRule,
    DataValidationRule,
    GridRange,
    NumberFormat,
    TextFormat,
    format_cell_ranges,
    get_conditional_format_rules,
    set_column_width,
    set_data_validation_for_cell_range,
    set_frozen,
    set_row_height,
)

SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "config/google-service-account.json")
WORKSHEET_NAME = os.getenv("GOOGLE_SHEETS_TAB", "Catalogo")
IMAGE_BASE_URL = os.getenv("IMAGE_BASE_URL", "https://chapeuslisboeta.pt/wp-content/uploads/")

BASE_DIR = Path(__file__).resolve().parents[1]
FALTAS_CSV = BASE_DIR / "relatorios" / "produtos_sem_imagem.csv"
RESUMO_COLECOES_CSV = BASE_DIR / "output_catalogo" / "catalogo_summary_sheet.csv"
RESUMO_TIPOS_CSV = BASE_DIR / "output_catalogo" / "catalogo_summary_sheet_tipo.csv"

# Paleta Chapéus Lisboeta
BRAND_ROSE = Color(238 / 255, 202 / 255, 201 / 255)
BRAND_AQUA = Color(168 / 255, 218 / 255, 223 / 255)
TEXT_DARK = Color(30 / 255, 30 / 255, 30 / 255)
LIGHT_BG = Color(1, 1, 1)

HEADER_BG = BRAND_ROSE
HEADER_TEXT = TextFormat(bold=True, foregroundColor=TEXT_DARK, fontFamily="Montserrat", fontSize=11)
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


def get_client() -> gspread.Client:
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return gspread.authorize(creds)


def ensure_columns(ws: gspread.Worksheet) -> int:
    """Reorder columns, inject formulas and return number of data rows."""

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
        "Última atualização",
        "Responsável",
        "Prioridade",
        "Destaque homepage?",
        "Notas internas",
    ]

    values = ws.get_all_values()
    reordered: List[List[str]] = []

    if values:
        header = values[0]
        data = values[1:]
        index_map = {name: idx for idx, name in enumerate(header)}

        for row in data:
            if not any(cell.strip() for cell in row):
                continue

            new_row: List[str] = []
            for col in desired_order:
                if col in {"Preview", "Status"}:
                    new_row.append("")
                else:
                    idx = index_map.get(col)
                    new_row.append(row[idx] if idx is not None and idx < len(row) else "")
            reordered.append(new_row)

    data_rows = len(reordered)

    ws.clear()
    ws.resize(rows=max(data_rows + 50, 200), cols=len(desired_order))

    if reordered:
        ws.update(
            range_name=f"A1:{rowcol_to_a1(data_rows + 1, len(desired_order))}",
            values=[desired_order] + reordered,
            value_input_option="USER_ENTERED",
        )
    else:
        ws.update(range_name="A1", values=[desired_order])

    if data_rows:
        preview_col = desired_order.index("Preview") + 1
        preview_range = f"{col_to_letter(preview_col)}2:{col_to_letter(preview_col)}{data_rows + 1}"
        preview_template = (
            '=IF(LEN(N{r})=0,"",'
            'LET('
            'raw,TO_TEXT(N{r}),'
            'first,TRIM(IFERROR(INDEX(SPLIT(SUBSTITUTE(raw,CHAR(10),","),","),1),"")),'
            f'url,IF(first="","",IF(REGEXMATCH(first,"^https?://"),first,"{IMAGE_BASE_URL}"&first)),'
            'url_encoded,SUBSTITUTE(url," ","%20"),'
            'IF(url="","",IMAGE(url_encoded,4,120,120))'
            '))'
        )
        preview_values = [[preview_template.format(r=row)] for row in range(2, data_rows + 2)]
        ws.update(range_name=preview_range, values=preview_values, value_input_option="USER_ENTERED")

        status_col = desired_order.index("Status") + 1
        status_range = f"{col_to_letter(status_col)}2:{col_to_letter(status_col)}{data_rows + 1}"
        status_template = (
            '=IF(AND(LEN(B{r})=0,LEN(C{r})=0),"",'
            'IF(LEN(B{r})=0,"Sem SKU",'
            'IF(LEN(N{r})=0,"Sem foto",'
            'IF(LEN(D{r})=0,"Sem preço",'
            'IF(LEN(L{r})=0,"Rever link",'
            'IF(LEN(F{r})=0,"Sem descrição","OK"))))))'
        )
        status_values = [[status_template.format(r=row)] for row in range(2, data_rows + 2)]
        ws.update(range_name=status_range, values=status_values, value_input_option="USER_ENTERED")

    destaque_col = desired_order.index("Destaque homepage?") + 1
    if data_rows:
        destaque_range = f"{rowcol_to_a1(2, destaque_col)}:{rowcol_to_a1(data_rows + 1, destaque_col)}"
    else:
        destaque_range = f"{rowcol_to_a1(2, destaque_col)}:{rowcol_to_a1(2, destaque_col)}"
    try:
        destaque_rule = DataValidationRule(BooleanCondition("BOOLEAN"), strict=True)
        set_data_validation_for_cell_range(ws, destaque_range, destaque_rule)
    except Exception:
        pass

    return data_rows


def apply_formatting(ws: gspread.Worksheet) -> None:
    headers = ws.row_values(1)
    if not headers:
        return

    last_col_letter = col_to_letter(ws.col_count)
    header_range = f"A1:{last_col_letter}1"

    format_cell_ranges(
        ws,
        [
            (
                header_range,
                CellFormat(
                    backgroundColor=HEADER_BG,
                    textFormat=HEADER_TEXT,
                    horizontalAlignment="CENTER",
                    verticalAlignment="MIDDLE",
                ),
            ),
        ],
    )

    set_row_height(ws, "1:1", 36)
    if ws.row_count > 1:
        set_row_height(ws, f"2:{min(ws.row_count, 200)}", 140)

    set_frozen(ws, rows=1, cols=min(3, ws.col_count))

    try:
        ws.set_basic_filter(header_range)
    except Exception:  # API errors when filter already exists
        pass

    data_range = GridRange.from_a1_range(f"A2:{last_col_letter}{ws.row_count}", ws)
    odd_rule = ConditionalFormatRule(
        ranges=[data_range],
        booleanRule=BooleanRule(
            condition=BooleanCondition("CUSTOM_FORMULA", ["=ISEVEN(ROW())"]),
            format=CellFormat(backgroundColor=ODD_ROW_BG),
        ),
    )

    rules = get_conditional_format_rules(ws)
    rules.clear()
    rules.append(odd_rule)

    if "Status" in headers:
        status_idx = headers.index("Status") + 1
        status_letter = col_to_letter(status_idx)
        status_range = GridRange.from_a1_range(f"{status_letter}2:{status_letter}{ws.row_count}", ws)
        status_styles = [
            ("OK", Color(0.85, 0.96, 0.88)),
            ("Sem foto", Color(0.99, 0.86, 0.86)),
            ("Sem preço", Color(1.0, 0.93, 0.83)),
            ("Rever link", Color(1.0, 0.96, 0.82)),
            ("Sem descrição", Color(0.93, 0.93, 0.99)),
        ]
        for value, bg in status_styles:
            rules.append(
                ConditionalFormatRule(
                    ranges=[status_range],
                    booleanRule=BooleanRule(
                        condition=BooleanCondition("TEXT_EQ", [value]),
                        format=CellFormat(
                            backgroundColor=bg,
                            textFormat=TextFormat(bold=value == "OK", foregroundColor=TEXT_DARK),
                        ),
                    ),
                )
            )

    rules.save()

    widths = {
        1: 130,
        2: 150,
        3: 340,
        4: 110,
        5: 260,
        6: 320,
        7: 200,
        8: 140,
        9: 140,
        10: 160,
        11: 140,
        12: 260,
        13: 220,
        14: 220,
        15: 150,
        16: 140,
        17: 150,
        18: 150,
        19: 120,
        20: 140,
        21: 260,
    }
    for col, width in widths.items():
        if col <= ws.col_count:
            col_letter = col_to_letter(col)
            set_column_width(ws, f"{col_letter}:{col_letter}", width)

    if "Preço" in headers:
        price_letter = col_to_letter(headers.index("Preço") + 1)
        format_cell_ranges(
            ws,
            [(f"{price_letter}:{price_letter}", CellFormat(numberFormat=NumberFormat(type="NUMBER", pattern="#,##0.00")))],
        )

    for col_name in ("Preview", "Status"):
        if col_name in headers:
            letter = col_to_letter(headers.index(col_name) + 1)
            format_cell_ranges(
                ws,
                [(f"{letter}:{letter}", CellFormat(horizontalAlignment="CENTER", verticalAlignment="MIDDLE"))],
            )

    for col_name in ("Descrição curta", "Descrição longa", "Notas internas"):
        if col_name in headers:
            letter = col_to_letter(headers.index(col_name) + 1)
            format_cell_ranges(ws, [(f"{letter}:{letter}", CellFormat(wrapStrategy="WRAP"))])

    if "Última atualização" in headers:
        letter = col_to_letter(headers.index("Última atualização") + 1)
        format_cell_ranges(
            ws,
            [(f"{letter}:{letter}", CellFormat(numberFormat=NumberFormat(type="DATE_TIME", pattern="dd/mm/yyyy hh:mm")))],
        )

    if "Prioridade" in headers:
        idx = headers.index("Prioridade") + 1
        rng = f"{rowcol_to_a1(2, idx)}:{rowcol_to_a1(ws.row_count, idx)}"
        validation_rule = DataValidationRule(BooleanCondition("NUMBER_BETWEEN", ["1", "5"]), showCustomUi=True)
        set_data_validation_for_cell_range(ws, rng, validation_rule)


def ensure_faltas_sheet(sh: gspread.Spreadsheet) -> gspread.Worksheet:
    title = "Faltas"
    existing_notes: dict[str, dict[str, str]] = {}
    carry_over: List[List[str]] = []

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
                carry_over.append([
                    record.get("Coleção", ""),
                    record.get("Produto", record.get("Nome produto", "")),
                    record.get("SKU", ""),
                    record.get("URL fornecedor", ""),
                    record.get("Links adicionais", ""),
                    record.get("Motivo", ""),
                    record.get("Nova URL/Foto", ""),
                    record.get("Notas", ""),
                ])
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

    rows.extend(carry_over)

    total_rows = len(rows)
    ws.resize(rows=max(total_rows + 10, 80), cols=len(headers))
    ws.update(
        range_name=f"A1:{rowcol_to_a1(total_rows + 1, len(headers))}",
        values=[headers] + rows,
        value_input_option="USER_ENTERED",
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
                    horizontalAlignment="CENTER",
                ),
            )
        ],
    )
    set_frozen(ws, rows=1, cols=1)

    for col_name in ("Motivo", "Notas"):
        letter = col_to_letter(headers.index(col_name) + 1)
        format_cell_ranges(ws, [(f"{letter}:{letter}", CellFormat(wrapStrategy="WRAP"))])

    widths = {1: 180, 2: 320, 3: 160, 4: 260, 5: 220, 6: 220, 7: 200, 8: 220}
    for idx, width in widths.items():
        set_column_width(ws, f"{col_to_letter(idx)}:{col_to_letter(idx)}", width)

    set_row_height(ws, "1:1", 30)
    if total_rows:
        set_row_height(ws, f"2:{total_rows + 1}", 80)

    try:
        ws.set_basic_filter(header_range)
    except Exception:
        pass

    return ws


def ensure_summary_colecoes(sh: gspread.Spreadsheet) -> gspread.Worksheet:
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
    ws.update(
        range_name=f"A1:{rowcol_to_a1(total_rows + 1, len(headers))}",
        values=[headers] + rows,
    )

    if total_rows:
        end_row = total_rows + 1
        percent_range = f"C2:C{end_row}"
        percent_values = [
            [f"=IF(B{row}=0,\"\",B{row}/SUM($B$2:$B${end_row}))"]
            for row in range(2, end_row + 1)
        ]
        ws.update(
            range_name=percent_range,
            values=percent_values,
            value_input_option="USER_ENTERED",
        )
        format_cell_ranges(ws, [(percent_range, CellFormat(numberFormat=NumberFormat(type="PERCENT", pattern="0%")))])

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
        set_column_width(ws, f"{col_to_letter(idx)}:{col_to_letter(idx)}", width)

    try:
        ws.set_basic_filter(header_range)
    except Exception:
        pass

    return ws


def ensure_summary_tipos(sh: gspread.Spreadsheet) -> gspread.Worksheet:
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
    ws.update(
        range_name=f"A1:{rowcol_to_a1(total_rows + 1, len(headers))}",
        values=[headers] + rows,
    )

    if total_rows:
        end_row = total_rows + 1
        ranking_range = f"D2:D{end_row}"
        ranking_values = [
            [f"=IF(C{row}=\"\",\"\",RANK(C{row},$C$2:$C${end_row}))"]
            for row in range(2, end_row + 1)
        ]
        ws.update(
            range_name=ranking_range,
            values=ranking_values,
            value_input_option="USER_ENTERED",
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

    widths = {1: 200, 2: 320, 3: 120, 4: 120}
    for idx, width in widths.items():
        set_column_width(ws, f"{col_to_letter(idx)}:{col_to_letter(idx)}", width)

    try:
        ws.set_basic_filter(header_range)
    except Exception:
        pass

    return ws


def ensure_history_sheet(sh: gspread.Spreadsheet) -> gspread.Worksheet:
    title = "Histórico"
    headers = ["Timestamp", "Utilizador", "SKU", "Campo", "Valor antigo", "Valor novo", "Notas"]
    try:
        ws = sh.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=1000, cols=len(headers))

    current_header = ws.row_values(1)
    if current_header != headers:
        ws.update(range_name="A1", values=[headers])

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


def ensure_guide_sheet(sh: gspread.Spreadsheet) -> gspread.Worksheet:
    title = "Guia"
    try:
        ws = sh.worksheet(title)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=200, cols=4)

    content = [
        ["Passo", "O que fazer"],
        ["1", "Revise a aba 'Catalogo' e resolva entradas com Status diferente de OK."],
        ["2", "Abra 'Faltas' e preencha 'Nova URL/Foto' ou notas para cada pendência."],
        ["3", "Use 'Resumo Coleções' e 'Resumo Tipos' para planear campanhas."],
        ["4", "Execute python scripts/sync_google_sheet.py e scripts/generate_wc_catalog.py."],
        ["5", "Importe woocommerce_import.csv e corra util/qa_catalogo.py para QA."],
        ["Sugestões", "Format → Theme para aplicar cores da marca; Inserir → Segmentador para filtros rápidos."],
        ["Ajuda", "Equipa Codex: suporte@chapeuslisboeta.pt ou canal Slack habitual."],
    ]

    ws.update(range_name="A1:B8", values=content)

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
        set_column_width(ws, f"{col_to_letter(idx)}:{col_to_letter(idx)}", width)

    set_row_height(ws, "1:1", 30)

    return ws


def ensure_dashboard(
    sh: gspread.Spreadsheet,
    catalog_ws: gspread.Worksheet,
    faltas_ws: gspread.Worksheet,
    resumo_colecoes_ws: gspread.Worksheet,
    resumo_tipos_ws: gspread.Worksheet,
    guia_ws: gspread.Worksheet,
) -> gspread.Worksheet:
    dashboard_name = "Dashboard"
    try:
        dash_ws = sh.worksheet(dashboard_name)
        dash_ws.clear()
    except gspread.WorksheetNotFound:
        dash_ws = sh.add_worksheet(title=dashboard_name, rows=200, cols=12)

    def sheet_range(title: str, rng: str) -> str:
        safe = title.replace("'", "''")
        return f"'{safe}'!{rng}"

    catalog_title = catalog_ws.title

    dash_ws.update(range_name="A1", values=[["🎩 Chapéus Lisboeta – Cockpit do Catálogo"]])
    format_cell_ranges(dash_ws, [("A1", CellFormat(textFormat=TextFormat(bold=True, fontSize=18)))])
    set_row_height(dash_ws, "1:1", 40)

    cards = [
        ("A3", "Total de produtos", f"=COUNTA({sheet_range(catalog_title, 'B2:B')})"),
        ("C3", "Produtos sem foto", f"=COUNTIF({sheet_range(catalog_title, 'P:P')},\"Sem foto\")"),
        ("E3", "Sem preço", f"=COUNTIF({sheet_range(catalog_title, 'P:P')},\"Sem preço\")"),
        ("G3", "Destaques ativos", f"=COUNTIF({sheet_range(catalog_title, 'T:T')},TRUE)"),
        ("I3", "Última atualização", f"=IFERROR(MAX({sheet_range(catalog_title, 'Q:Q')}),\"\")"),
        ("K3", "Produtos validados", "=IFERROR(COUNTA('Clean & Ready'!A2:A),0)"),
        ("M3", "Pendentes", "=IFERROR(COUNTA('Pendentes'!A2:A),0)"),
    ]

    for cell, label, formula in cards:
        dash_ws.update(range_name=cell, values=[[label]])
        row, col = a1_to_rowcol(cell)
        value_cell = rowcol_to_a1(row + 1, col)
        dash_ws.update(range_name=value_cell, values=[[formula]], value_input_option="USER_ENTERED")
        format_cell_ranges(
            dash_ws,
            [
                (
                    f"{cell}:{value_cell}",
                    CellFormat(
                        backgroundColor=BRAND_AQUA if cell != "I3" else BRAND_ROSE,
                        textFormat=TextFormat(bold=True, foregroundColor=TEXT_DARK),
                        horizontalAlignment="CENTER",
                        verticalAlignment="MIDDLE",
                    ),
                )
            ],
        )

    format_cell_ranges(
        dash_ws,
        [
            ("I4", CellFormat(numberFormat=NumberFormat(type="DATE_TIME", pattern="dd/mm/yyyy hh:mm"))),
            ("K4:M4", CellFormat(numberFormat=NumberFormat(type="NUMBER", pattern="0"))),
        ],
    )

    progress_expr = (
        "IFERROR(COUNTA('Clean & Ready'!A2:A)/"
        f"MAX(1,COUNTA({sheet_range(catalog_title, 'B:B')})),0)"
    )
    dash_ws.update(range_name="A7", values=[["Cobertura de fotos"]])
    dash_ws.update(range_name="A8", values=[[f"=TEXT({progress_expr},\"0%\")"]], value_input_option="USER_ENTERED")
    dash_ws.update(
        range_name="B8",
        values=[[f"=SPARKLINE({progress_expr},{{\"charttype\",\"bar\";\"max\",1;\"color\",\"#A8DADF\"}})"]],
        value_input_option="USER_ENTERED",
    )
    format_cell_ranges(
        dash_ws,
        [("A7:B8", CellFormat(textFormat=TextFormat(bold=True, foregroundColor=TEXT_DARK)))],
    )

    catalog_link = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={catalog_ws.id}"
    faltas_link = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={faltas_ws.id}"
    colecoes_link = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={resumo_colecoes_ws.id}"
    tipos_link = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={resumo_tipos_ws.id}"
    guia_link = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={guia_ws.id}"

    dash_ws.update(range_name="A11", values=[["Avisos & Atalhos"]])
    dash_ws.update(
        range_name="A12",
        values=[[f"=HYPERLINK(\"{faltas_link}\",COUNTA({sheet_range(faltas_ws.title, 'A2:A')})&\" produtos sem imagem\")"]],
        value_input_option="USER_ENTERED",
    )
    dash_ws.update(range_name="A13", values=[[f"=HYPERLINK(\"{catalog_link}\",\"Abrir catálogo completo\")"]], value_input_option="USER_ENTERED")
    dash_ws.update(range_name="A14", values=[[f"=HYPERLINK(\"{colecoes_link}\",\"Resumo por coleções\")"]], value_input_option="USER_ENTERED")
    dash_ws.update(range_name="A15", values=[[f"=HYPERLINK(\"{tipos_link}\",\"Resumo por tipos\")"]], value_input_option="USER_ENTERED")
    format_cell_ranges(
        dash_ws,
        [("A11:A15", CellFormat(textFormat=TextFormat(bold=True, foregroundColor=TEXT_DARK)))],
    )

    dash_ws.update(range_name="D11", values=[["Fluxo rápido"]])
    dash_ws.update(range_name="D12", values=[["1️⃣ Atualizar status no catálogo"]])
    dash_ws.update(range_name="D13", values=[["2️⃣ Resolver pendências em Faltas"]])
    dash_ws.update(range_name="D14", values=[["3️⃣ Correr scripts de sync e QA"]])
    dash_ws.update(range_name="D15", values=[[f"=HYPERLINK(\"{guia_link}\",\"Ver guia completo\")"]], value_input_option="USER_ENTERED")
    format_cell_ranges(
        dash_ws,
        [("D11:D15", CellFormat(textFormat=TextFormat(bold=True, foregroundColor=TEXT_DARK)))],
    )

    dash_ws.update(range_name="A18", values=[["Indicadores extra"]])
    dash_ws.update(
        range_name="A19",
        values=[[f"=IFERROR(AVERAGEIF({sheet_range(catalog_title, 'S:S')},\">0\"),\"Sem prioridade definida\")"]],
        value_input_option="USER_ENTERED",
    )
    dash_ws.update(
        range_name="A20",
        values=[[f"=COUNTIF({sheet_range(catalog_title, 'P:P')},\"Sem descrição\") & \" produtos sem descrição\""]],
        value_input_option="USER_ENTERED",
    )

    widths = {1: 240, 2: 200, 3: 180, 4: 180, 5: 180, 6: 180, 7: 180, 8: 180, 9: 180, 11: 180, 13: 160}
    for idx, width in widths.items():
        set_column_width(dash_ws, f"{col_to_letter(idx)}:{col_to_letter(idx)}", width)

    format_cell_ranges(dash_ws, [("A11:B15", CellFormat(backgroundColor=Color(0.96, 0.97, 0.99)))])
    format_cell_ranges(dash_ws, [("D11:D15", CellFormat(backgroundColor=Color(0.98, 0.96, 0.94)))])

    return dash_ws


def main() -> None:
    if not SHEET_ID:
        raise SystemExit("Defina GOOGLE_SHEETS_ID.")

    client = get_client()
    sh = client.open_by_key(SHEET_ID)
    catalog_ws = sh.worksheet(WORKSHEET_NAME)

    ensure_columns(catalog_ws)
    apply_formatting(catalog_ws)

    time.sleep(70)

    faltas_ws = ensure_faltas_sheet(sh)
    time.sleep(70)
    resumo_colecoes_ws = ensure_summary_colecoes(sh)
    time.sleep(70)
    resumo_tipos_ws = ensure_summary_tipos(sh)
    time.sleep(15)
    ensure_history_sheet(sh)
    time.sleep(15)
    guia_ws = ensure_guide_sheet(sh)
    time.sleep(20)
    ensure_dashboard(sh, catalog_ws, faltas_ws, resumo_colecoes_ws, resumo_tipos_ws, guia_ws)

    print("Formatação premium aplicada com sucesso. Abas actualizadas: Catalogo, Dashboard, Faltas, Resumos e Guia.")


if __name__ == "__main__":
    main()
