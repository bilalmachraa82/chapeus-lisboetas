const CATALOGO_SHEET = 'Catalogo';
const HISTORY_SHEET = 'Histórico';
const FALTAS_SHEET = 'Faltas';
const CLEAN_READY_SHEET = 'Clean & Ready';
const PENDING_SHEET = 'Pendentes';
const IMAGE_BASE_URL = 'https://chapeuslisboeta.pt/wp-content/uploads/';

const CLEAN_HEADERS = [
  'SKU',
  'Fonte',
  'Categoria',
  'Nome',
  'Preço',
  'URL fornecedor',
  'Descrição obtida',
  'Composição obtida',
  'Observações',
  'Scrape timestamp',
];

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Chapéus Premium')
    .addItem('Reaplicar fórmulas de preview/status', 'reapplyCatalogFormulas')
    .addItem('Atualizar data/autor manualmente (linha selecionada)', 'forceStampSelection')
    .addSeparator()
    .addItem('Abrir Clean & Ready', 'openCleanReady')
    .addItem('Abrir Pendentes', 'openPending')
    .addSeparator()
    .addItem('Enviar linha para Clean & Ready', 'pushSelectionToClean')
    .addItem('Enviar linha para Pendentes', 'pushSelectionToPending')
    .addToUi();
}

function onEdit(e) {
  if (!e) {
    return;
  }
  const sheet = e.range.getSheet();
  const sheetName = sheet.getName();

  if (sheetName === CATALOGO_SHEET) {
    handleCatalogEdit(e);
  } else if (sheetName === FALTAS_SHEET) {
    handleFaltasEdit(e);
  }
}

function handleCatalogEdit(e) {
  const range = e.range;
  const sheet = range.getSheet();
  if (range.getRow() === 1) {
    return;
  }

  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  const lastUpdateCol = columnIndex(headers, 'Última atualização');
  const responsibleCol = columnIndex(headers, 'Responsável');
  const skuCol = columnIndex(headers, 'SKU');
  const statusCol = columnIndex(headers, 'Status');

  if (lastUpdateCol > -1) {
    sheet.getRange(range.getRow(), lastUpdateCol)
      .setValue(new Date())
      .setNumberFormat('dd/mm/yyyy hh:mm');
  }

  const editor = resolveEditor(e);
  if (responsibleCol > -1 && editor) {
    sheet.getRange(range.getRow(), responsibleCol).setValue(editor);
  }

  validateSkuUniqueness(sheet, headers, skuCol, statusCol, range.getRow());
  validateUrlField(range, headers);
  appendHistoryLog(sheet, headers, e, editor, skuCol);
}

function openCleanReady() {
  SpreadsheetApp.getActive().getSheetByName(CLEAN_READY_SHEET)?.activate();
}

function openPending() {
  SpreadsheetApp.getActive().getSheetByName(PENDING_SHEET)?.activate();
}

function pushSelectionToClean() {
  pushSelectionToTarget(CLEAN_READY_SHEET, 'manual');
}

function pushSelectionToPending() {
  pushSelectionToTarget(PENDING_SHEET, 'manual-pendente');
}

function pushSelectionToTarget(targetSheetName, sourceLabel) {
  const ss = SpreadsheetApp.getActive();
  const catalogSheet = ss.getSheetByName(CATALOGO_SHEET);
  if (!catalogSheet) {
    SpreadsheetApp.getUi().alert('Aba Catalogo não encontrada.');
    return;
  }
  const cell = catalogSheet.getActiveCell();
  if (!cell || cell.getRow() === 1) {
    SpreadsheetApp.getUi().alert('Selecione uma célula com dados na aba Catalogo.');
    return;
  }

  const headers = catalogSheet.getRange(1, 1, 1, catalogSheet.getLastColumn()).getValues()[0];
  const row = cell.getRow();
  const getValue = (header) => {
    const idx = headers.indexOf(header);
    return idx > -1 ? catalogSheet.getRange(row, idx + 1).getValue() : '';
  };

  const sku = getValue('SKU');
  if (!sku) {
    SpreadsheetApp.getUi().alert('A linha selecionada não tem SKU.');
    return;
  }

  let targetSheet = ss.getSheetByName(targetSheetName);
  if (!targetSheet) {
    targetSheet = ss.insertSheet(targetSheetName);
  }
  if (targetSheet.getLastRow() === 0) {
    targetSheet.getRange(1, 1, 1, CLEAN_HEADERS.length).setValues([CLEAN_HEADERS]);
  }

  const timestamp = new Date();
  const record = [
    sku,
    sourceLabel,
    getValue('Sheet'),
    getValue('Nome'),
    getValue('Preço'),
    getValue('URL fornecedor'),
    getValue('Descrição longa'),
    getValue('Composição'),
    `Adicionado manualmente em ${timestamp.toLocaleString()}`,
    timestamp,
  ];

  targetSheet.appendRow(record);
  SpreadsheetApp.getUi().alert(`Produto ${sku} enviado para "${targetSheetName}".`);
}

function handleFaltasEdit(e) {
  const headers = e.range.getSheet().getRange(1, 1, 1, e.range.getSheet().getLastColumn()).getValues()[0];
  validateUrlField(e.range, headers);
}

function resolveEditor(e) {
  const sessionEmail = Session.getEffectiveUser().getEmail();
  if (sessionEmail) {
    return sessionEmail;
  }
  if (e && e.user && e.user.getEmail) {
    return e.user.getEmail() || 'Atualizado via API';
  }
  return 'Atualizado via API';
}

function columnIndex(headers, name) {
  return headers.indexOf(name);
}

function validateSkuUniqueness(sheet, headers, skuCol, statusCol, row) {
  if (skuCol === -1 || row === 1) {
    return;
  }
  const skuRange = sheet.getRange(2, skuCol + 1, sheet.getLastRow() - 1, 1);
  const values = skuRange.getValues().flat().map(String);
  const currentSku = (sheet.getRange(row, skuCol + 1).getValue() || '').toString().trim();
  const occurrences = values.filter(value => value === currentSku).length;
  const cell = sheet.getRange(row, skuCol + 1);

  if (currentSku && occurrences > 1) {
    cell.setBackground('#F8D7DA').setNote('SKU duplicado nesta folha.');
    if (statusCol > -1) {
      sheet.getRange(row, statusCol + 1).setBackground('#F8D7DA');
    }
  } else {
    cell.setBackground(null).clearNote();
    if (statusCol > -1) {
      sheet.getRange(row, statusCol + 1).setBackground(null);
    }
  }
}

function validateUrlField(range, headers) {
  const header = headers[range.getColumn() - 1];
  const monitored = ['URL fornecedor', 'URLs extra', 'Nova URL/Foto'];
  if (monitored.indexOf(header) === -1) {
    return;
  }
  const value = String(range.getValue() || '').trim();
  const valid = !value || /^https?:\/\//i.test(value);
  if (!valid) {
    range.setBackground('#FDEDEC').setNote('URL deve começar por http:// ou https://');
  } else {
    range.setBackground(null).clearNote();
  }
}

function appendHistoryLog(sheet, headers, e, editor, skuCol) {
  if (!e || typeof e.oldValue === 'undefined' || e.oldValue === e.value) {
    return;
  }
  const history = sheet.getParent().getSheetByName(HISTORY_SHEET) || sheet.getParent().insertSheet(HISTORY_SHEET);
  if (history.getLastRow() === 0) {
    history.appendRow(['Timestamp', 'Utilizador', 'SKU', 'Campo', 'Valor antigo', 'Valor novo', 'Notas']);
  }

  const field = headers[e.range.getColumn() - 1] || `Coluna ${e.range.getColumn()}`;
  const sku = skuCol > -1 ? sheet.getRange(e.range.getRow(), skuCol + 1).getValue() : '';
  history.appendRow([
    new Date(),
    editor || 'Atualizado via API',
    sku,
    field,
    String(e.oldValue || ''),
    String(e.value || ''),
    '',
  ]);
}

function reapplyCatalogFormulas() {
  const ss = SpreadsheetApp.getActive();
  const sheet = ss.getSheetByName(CATALOGO_SHEET);
  if (!sheet) {
    SpreadsheetApp.getUi().alert('Aba Catalogo não encontrada.');
    return;
  }
  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  const dataRows = sheet.getLastRow() - 1;
  if (dataRows <= 0) {
    SpreadsheetApp.getUi().alert('Nenhum dado para reaplicar.');
    return;
  }

  const previewCol = columnIndex(headers, 'Preview');
  const statusCol = columnIndex(headers, 'Status');
  if (previewCol > -1) {
    const previewRange = sheet.getRange(2, previewCol + 1, dataRows, 1);
    const formulas = [];
    for (let r = 2; r <= dataRows + 1; r += 1) {
      formulas.push([
        '=IF(LEN(N' + r + ')=0,"",LET(first,IFERROR(REGEXEXTRACT(N' + r + ',"^[^\\n]+"),""),IF(first="","",IMAGE(IF(REGEXMATCH(first,"^https?://"),first,"' + IMAGE_BASE_URL + '"&first),4,120,120))))',
      ]);
    }
    previewRange.setFormulas(formulas);
  }

  if (statusCol > -1) {
    const statusRange = sheet.getRange(2, statusCol + 1, dataRows, 1);
    const formulas = [];
    for (let r = 2; r <= dataRows + 1; r += 1) {
      formulas.push([
        '=IF(AND(LEN(B' + r + ')=0,LEN(C' + r + ')=0),"",IF(LEN(B' + r + ')=0,"Sem SKU",IF(LEN(N' + r + ')=0,"Sem foto",IF(LEN(D' + r + ')=0,"Sem preço",IF(LEN(L' + r + ')=0,"Rever link",IF(LEN(F' + r + ')=0,"Sem descrição","OK")))))))',
      ]);
    }
    statusRange.setFormulas(formulas);
  }
}

function forceStampSelection() {
  const sheet = SpreadsheetApp.getActiveSheet();
  if (sheet.getName() !== CATALOGO_SHEET) {
    SpreadsheetApp.getUi().alert('Selecione uma linha na aba Catalogo.');
    return;
  }
  const range = sheet.getActiveCell();
  if (!range || range.getRow() === 1) {
    SpreadsheetApp.getUi().alert('Selecione uma célula com dados.');
    return;
  }
  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  const lastUpdateCol = columnIndex(headers, 'Última atualização');
  const responsibleCol = columnIndex(headers, 'Responsável');

  if (lastUpdateCol > -1) {
    sheet.getRange(range.getRow(), lastUpdateCol + 1).setValue(new Date()).setNumberFormat('dd/mm/yyyy hh:mm');
  }
  const editor = Session.getEffectiveUser().getEmail() || 'Atualizado via API';
  if (responsibleCol > -1) {
    sheet.getRange(range.getRow(), responsibleCol + 1).setValue(editor);
  }
}
