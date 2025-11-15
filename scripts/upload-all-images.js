#!/usr/bin/env node
/**
 * Upload todas as imagens de produtos para o Shopify via edge function Supabase.
 *
 * Uso:
 *   cd scripts
 *   npm install
 *   node upload-all-images.js
 *
 * Variáveis opcionais:
 *   LOVABLE_CSV_PATH=./public/data/lovable_import.csv
 *   LOVABLE_IMAGES_BASE=./output_catalogo
 *   SUPABASE_EDGE_URL=https://.../upload-product-images
 *   SUPABASE_EDGE_ANON_KEY=ey...
 *   UPLOAD_BATCH_SIZE=5
 *   UPLOAD_BATCH_DELAY_MS=2000
 *   UPLOAD_RETRY_LIMIT=3
 */

const fs = require('fs');
const path = require('path');
const fetch = require('node-fetch');
const { parse } = require('csv-parse');

const ROOT_DIR = path.resolve(__dirname, '..');
const DEFAULT_EDGE_URL =
  'https://dfygajzgojutvqqgaehz.supabase.co/functions/v1/upload-product-images';
const DEFAULT_EDGE_KEY =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRmeWdhanpnb2p1dHZxcWdhZWh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNjU2MTUsImV4cCI6MjA3ODY0MTYxNX0.PXeSOyN2q8eVzlwVpsGT6ZHfUyalj2o-L3tUyNXvx3g';

function resolveCsvPath() {
  if (process.env.LOVABLE_CSV_PATH) {
    return path.resolve(process.env.LOVABLE_CSV_PATH);
  }

  const candidates = [
    path.join(ROOT_DIR, 'output_catalogo', 'lovable_import_clean.csv'),
    path.join(ROOT_DIR, 'public', 'data', 'lovable_import.csv'),
    path.join(ROOT_DIR, 'output_catalogo', 'lovable_import.csv'),
  ];

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }

  return candidates[0];
}

function sanitizeSku(rawSku) {
  if (!rawSku) return '';
  const cleaned = rawSku
    .replace(/\r/g, '')
    .split('\n')
    .map((segment) => segment.trim())
    .filter(Boolean);
  return cleaned.length > 0 ? cleaned[0] : rawSku.trim();
}

const CONFIG = {
  csvPath: resolveCsvPath(),
  imagesBase: path.resolve(
    process.env.LOVABLE_IMAGES_BASE || path.join(ROOT_DIR, 'output_catalogo')
  ),
  edgeUrl: process.env.SUPABASE_EDGE_URL || DEFAULT_EDGE_URL,
  edgeKey: process.env.SUPABASE_EDGE_ANON_KEY || DEFAULT_EDGE_KEY,
  batchSize: Number(process.env.UPLOAD_BATCH_SIZE || 5),
  batchDelayMs: Number(process.env.UPLOAD_BATCH_DELAY_MS || 2000),
  retryLimit: Number(process.env.UPLOAD_RETRY_LIMIT || 3),
  errorLogPath: path.join(ROOT_DIR, 'errors.log'),
};

const STATE = {
  totalProducts: 0,
  totalImages: 0,
  success: 0,
  failures: 0,
  errors: [],
};

process.on('SIGINT', () => {
  console.log('\n⛔ Execução interrompida pelo utilizador. Salvando resumo...');
  writeErrorLog();
  process.exit(130);
});

function readCsv(filePath) {
  return new Promise((resolve, reject) => {
    const rows = [];
    fs.createReadStream(filePath)
      .pipe(
        parse({
          columns: true,
          skip_empty_lines: true,
          trim: true,
        })
      )
      .on('data', (row) => rows.push(row))
      .on('error', reject)
      .on('end', () => resolve(rows));
  });
}

function splitImagePaths(value) {
  if (!value) return [];
  return value
    .split('|')
    .map((segment) => segment.trim())
    .filter(Boolean);
}

function detectMimeType(fileName) {
  const ext = path.extname(fileName).toLowerCase();
  if (ext === '.png') return 'image/png';
  if (ext === '.webp') return 'image/webp';
  return 'image/jpeg';
}

function chunkArray(items, size) {
  const chunks = [];
  for (let i = 0; i < items.length; i += size) {
    chunks.push(items.slice(i, i + size));
  }
  return chunks;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function uploadBatch(batch, batchIndex, totalBatches) {
  for (let attempt = 1; attempt <= CONFIG.retryLimit; attempt += 1) {
    try {
      console.log(
        `  ⬆️  Batch ${batchIndex}/${totalBatches}: tentativa ${attempt} enviando ${batch.length} imagens...`
      );

      const response = await fetch(CONFIG.edgeUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${CONFIG.edgeKey}`,
        },
        body: JSON.stringify({ images: batch }),
        timeout: 120000,
      });

      const text = await response.text();
      let payload = null;
      try {
        payload = text ? JSON.parse(text) : null;
      } catch (err) {
        payload = { raw: text };
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status} ${response.statusText} → ${text}`);
      }

      const resultSummary = payload?.result || payload?.message || 'sucesso';
      console.log(
        `  ✅ Batch ${batchIndex}/${totalBatches} concluído (${batch.length}/${batch.length} sucesso) — ${resultSummary}`
      );
      STATE.success += batch.length;
      return;
    } catch (error) {
      console.error(`  ❌ Falha no batch ${batchIndex}: ${error.message}`);
      if (attempt === CONFIG.retryLimit) {
        batch.forEach((image) => {
          STATE.failures += 1;
          STATE.errors.push({ sku: image.sku, file: image.fileName, message: error.message });
        });
      } else {
        await sleep(1500);
      }
    }
  }
}

async function processProduct(row, index, total) {
  const rawSku = row.sku ? row.sku.trim() : '';
  const sku = sanitizeSku(rawSku);
  const displaySku = rawSku && rawSku !== sku ? `${sku} ← ${rawSku.replace(/\s+/g, ' ')}` : sku;
  const imagePaths = splitImagePaths(row.image_paths);

  if (!sku) {
    console.log(`[${index}/${total}] ⚠️  SKU vazio — ignorado`);
    return;
  }

  console.log(`\n[${index}/${total}] Processando: ${displaySku || '(SKU vazio)'}`);
  if (!imagePaths.length) {
    console.log('  ⚠️  Nenhuma imagem associada, seguindo.');
    return;
  }

  console.log(`  ✓ ${imagePaths.length} imagens encontradas`);
  const prepared = [];

  for (const relativePath of imagePaths) {
    const absolutePath = path.join(CONFIG.imagesBase, relativePath);
    if (!fs.existsSync(absolutePath)) {
      const warning = `Arquivo inexistente: ${absolutePath}`;
      console.warn(`  ⚠️  ${warning}`);
      STATE.failures += 1;
      STATE.errors.push({ sku, file: relativePath, message: warning });
      continue;
    }

    const buffer = fs.readFileSync(absolutePath);
    prepared.push({
      sku,
      fileName: path.basename(relativePath),
      base64: buffer.toString('base64'),
      mimeType: detectMimeType(relativePath),
    });
  }

  STATE.totalImages += prepared.length;

  if (!prepared.length) {
    console.log('  ⚠️  Nenhuma imagem válida para upload.');
    return;
  }

  const batches = chunkArray(prepared, CONFIG.batchSize);

  for (let batchIndex = 1; batchIndex <= batches.length; batchIndex += 1) {
    const batch = batches[batchIndex - 1];
    await uploadBatch(batch, batchIndex, batches.length);
    await sleep(CONFIG.batchDelayMs);
  }

  console.log(
    `  🎉 Produto concluído: ${prepared.length} imagens preparadas, ${STATE.success} sucesso acumulado`
  );
}

function writeErrorLog() {
  if (!STATE.errors.length) {
    if (fs.existsSync(CONFIG.errorLogPath)) {
      fs.unlinkSync(CONFIG.errorLogPath);
    }
    return;
  }

  const lines = [
    `Relatório ${new Date().toISOString()}`,
    'SKU,File,Mensagem',
    ...STATE.errors.map((entry) => `${entry.sku},${entry.file},${entry.message.replace(/\n/g, ' ')}`),
  ];
  fs.writeFileSync(CONFIG.errorLogPath, `${lines.join('\n')}\n`, 'utf8');
}

async function run() {
  console.log('🚀 Iniciando upload automático de imagens...');
  console.log(`📄 CSV: ${CONFIG.csvPath}`);
  console.log(`🖼️  Base de imagens: ${CONFIG.imagesBase}`);
  console.log(`🌐 Edge Function: ${CONFIG.edgeUrl}`);
  console.log('------------------------------------------------------------');

  if (!fs.existsSync(CONFIG.csvPath)) {
    throw new Error(`CSV não encontrado em ${CONFIG.csvPath}`);
  }

  if (!fs.existsSync(CONFIG.imagesBase)) {
    throw new Error(`Diretório de imagens não encontrado em ${CONFIG.imagesBase}`);
  }

  const rows = await readCsv(CONFIG.csvPath);
  STATE.totalProducts = rows.length;

  console.log(`📦 Produtos no CSV: ${rows.length}`);

  let index = 0;
  for (const row of rows) {
    index += 1;
    await processProduct(row, index, rows.length);
  }

  console.log('\n================================================');
  console.log('📊 RESUMO FINAL');
  console.log('================================================');
  console.log(`Total de produtos processados: ${STATE.totalProducts}`);
  console.log(`Total de imagens preparadas: ${STATE.totalImages}`);
  console.log(`✅ Sucesso: ${STATE.success}`);
  console.log(`❌ Falhas: ${STATE.failures}`);

  if (STATE.errors.length) {
    console.log('Erros registados (ver errors.log):');
    STATE.errors.forEach((err) => {
      console.log(`  - SKU ${err.sku} | ${err.file} | ${err.message}`);
    });
  } else {
    console.log('Sem erros registrados.');
  }

  writeErrorLog();
}

run().catch((error) => {
  console.error('❌ Execução falhou:', error);
  STATE.errors.push({ sku: 'GLOBAL', file: 'N/A', message: error.message });
  writeErrorLog();
  process.exit(1);
});
