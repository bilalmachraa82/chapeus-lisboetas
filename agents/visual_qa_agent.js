#!/usr/bin/env node
/**
 * 🎯 Visual QA Agent com Puppeteer
 * Audita visualmente o site completo
 */

const puppeteer = require('puppeteer');
const fs = require('fs');

class VisualQAAgent {
    constructor(siteUrl = 'http://localhost:8080') {
        this.siteUrl = siteUrl;
        this.issues = [];
        this.stats = {
            pagesChecked: 0,
            productsWithImages: 0,
            productsWithoutImages: 0,
            brokenImages: 0
        };
    }

    async init() {
        console.log('=' .repeat(70));
        console.log('🎯 VISUAL QA AGENT COM PUPPETEER');
        console.log('=' .repeat(70));
        console.log('');
        
        this.browser = await puppeteer.launch({
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        this.page = await this.browser.newPage();
        await this.page.setViewport({ width: 1920, height: 1080 });
        
        console.log('✅ Puppeteer inicializado\n');
    }

    async checkHomepage() {
        console.log('1️⃣ VERIFICANDO HOMEPAGE...\n');
        
        try {
            await this.page.goto(this.siteUrl, { waitUntil: 'networkidle2', timeout: 30000 });
            this.stats.pagesChecked++;
            
            // Screenshot
            await this.page.screenshot({ path: '/tmp/homepage_screenshot.png', fullPage: true });
            console.log('✅ Homepage carregada');
            console.log('📸 Screenshot salvo: /tmp/homepage_screenshot.png');
            
            // Verificar título
            const title = await this.page.title();
            console.log(`✅ Título: ${title}`);
            
            // Verificar se tem hero section
            const heroExists = await this.page.$('.hero-section');
            if (heroExists) {
                console.log('✅ Hero section presente');
            } else {
                console.log('⚠️  Hero section não encontrada');
                this.issues.push('Hero section ausente na homepage');
            }
            
            // Verificar trust badges
            const trustBadges = await this.page.$$('.trust-badge');
            console.log(`✅ ${trustBadges.length} trust badges encontrados`);
            
            // Verificar botões
            const buttons = await this.page.$$('a.button, button');
            console.log(`✅ ${buttons.length} botões encontrados`);
            
            console.log('');
            
        } catch (error) {
            console.log(`❌ Erro ao verificar homepage: ${error.message}\n`);
            this.issues.push(`Homepage error: ${error.message}`);
        }
    }

    async checkShopPage() {
        console.log('2️⃣ VERIFICANDO PÁGINA DA LOJA...\n');
        
        try {
            await this.page.goto(`${this.siteUrl}/shop`, { waitUntil: 'networkidle2', timeout: 30000 });
            this.stats.pagesChecked++;
            
            await this.page.screenshot({ path: '/tmp/shop_screenshot.png', fullPage: true });
            console.log('✅ Loja carregada');
            console.log('📸 Screenshot salvo: /tmp/shop_screenshot.png');
            
            // Aguardar produtos carregarem
            await this.page.waitForSelector('.product', { timeout: 5000 }).catch(() => {});
            
            // Contar produtos visíveis
            const products = await this.page.$$('.product');
            console.log(`✅ ${products.length} produtos visíveis na primeira página`);
            
            // Verificar cada produto
            for (let i = 0; i < Math.min(products.length, 20); i++) {
                const product = products[i];
                
                // Verificar imagem
                const img = await product.$('img');
                if (img) {
                    const src = await img.evaluate(el => el.src);
                    const naturalWidth = await img.evaluate(el => el.naturalWidth);
                    
                    if (naturalWidth > 0) {
                        this.stats.productsWithImages++;
                    } else {
                        this.stats.productsWithoutImages++;
                        this.stats.brokenImages++;
                        console.log(`   ❌ Produto ${i+1}: Imagem quebrada (${src})`);
                    }
                } else {
                    this.stats.productsWithoutImages++;
                    console.log(`   ❌ Produto ${i+1}: Sem imagem`);
                }
            }
            
            console.log(`\n📊 Produtos com imagens: ${this.stats.productsWithImages}/${products.length}`);
            console.log(`📊 Produtos sem imagens: ${this.stats.productsWithoutImages}/${products.length}\n`);
            
        } catch (error) {
            console.log(`❌ Erro ao verificar loja: ${error.message}\n`);
            this.issues.push(`Shop page error: ${error.message}`);
        }
    }

    async checkSingleProduct() {
        console.log('3️⃣ VERIFICANDO PÁGINA DE PRODUTO INDIVIDUAL...\n');
        
        try {
            // Pegar primeiro produto
            await this.page.goto(`${this.siteUrl}/shop`, { waitUntil: 'networkidle2' });
            await this.page.waitForSelector('.product a', { timeout: 5000 });
            
            const firstProductLink = await this.page.$eval('.product a', el => el.href);
            
            if (firstProductLink) {
                await this.page.goto(firstProductLink, { waitUntil: 'networkidle2' });
                this.stats.pagesChecked++;
                
                await this.page.screenshot({ path: '/tmp/product_screenshot.png', fullPage: true });
                console.log('✅ Página de produto carregada');
                console.log('📸 Screenshot salvo: /tmp/product_screenshot.png');
                
                // Verificar galeria de imagens
                const gallery = await this.page.$$('.product-gallery img');
                console.log(`✅ ${gallery.length} imagens na galeria`);
                
                // Verificar preço
                const price = await this.page.$('.price');
                if (price) {
                    const priceText = await price.evaluate(el => el.textContent);
                    console.log(`✅ Preço: ${priceText.trim()}`);
                } else {
                    console.log('⚠️  Preço não encontrado');
                    this.issues.push('Preço ausente em produto');
                }
                
                // Verificar botão adicionar ao carrinho
                const addToCart = await this.page.$('.single_add_to_cart_button');
                if (addToCart) {
                    console.log('✅ Botão "Adicionar ao carrinho" presente');
                } else {
                    console.log('⚠️  Botão "Adicionar ao carrinho" não encontrado');
                    this.issues.push('Botão add to cart ausente');
                }
                
                console.log('');
            }
            
        } catch (error) {
            console.log(`❌ Erro ao verificar produto: ${error.message}\n`);
            this.issues.push(`Product page error: ${error.message}`);
        }
    }

    async checkPerformance() {
        console.log('4️⃣ VERIFICANDO PERFORMANCE...\n');
        
        try {
            const metrics = await this.page.metrics();
            
            console.log('📊 MÉTRICAS:');
            console.log(`   • Nodes DOM: ${metrics.Nodes}`);
            console.log(`   • JS Heap Size: ${(metrics.JSHeapUsedSize / 1024 / 1024).toFixed(2)} MB`);
            console.log(`   • Layouts: ${metrics.LayoutCount}`);
            
            if (metrics.Nodes > 3000) {
                this.issues.push('Muitos nodes DOM (performance)');
            }
            
            console.log('');
            
        } catch (error) {
            console.log(`❌ Erro ao verificar performance: ${error.message}\n`);
        }
    }

    async generateReport() {
        console.log('=' .repeat(70));
        console.log('📊 RELATÓRIO VISUAL QA');
        console.log('=' .repeat(70));
        console.log('');
        
        const report = {
            timestamp: new Date().toISOString(),
            site_url: this.siteUrl,
            stats: this.stats,
            issues: this.issues,
            screenshots: [
                '/tmp/homepage_screenshot.png',
                '/tmp/shop_screenshot.png',
                '/tmp/product_screenshot.png'
            ]
        };
        
        console.log('📊 ESTATÍSTICAS:');
        console.log(`   • Páginas verificadas: ${this.stats.pagesChecked}`);
        console.log(`   • Produtos com imagens: ${this.stats.productsWithImages}`);
        console.log(`   • Produtos sem imagens: ${this.stats.productsWithoutImages}`);
        console.log(`   • Imagens quebradas: ${this.stats.brokenImages}`);
        console.log('');
        
        if (this.issues.length > 0) {
            console.log('⚠️  ISSUES ENCONTRADOS:');
            this.issues.forEach(issue => {
                console.log(`   • ${issue}`);
            });
            console.log('');
        } else {
            console.log('✅ NENHUM ISSUE CRÍTICO ENCONTRADO!\n');
        }
        
        fs.writeFileSync('visual_qa_report.json', JSON.stringify(report, null, 2));
        console.log('💾 Relatório salvo: visual_qa_report.json');
        console.log('📸 Screenshots salvos em /tmp/');
        
        console.log('');
        console.log('=' .repeat(70));
        console.log('✅ AUDITORIA VISUAL COMPLETA!');
        console.log('=' .repeat(70));
        console.log('');
    }

    async close() {
        if (this.browser) {
            await this.browser.close();
        }
    }

    async run() {
        try {
            await this.init();
            await this.checkHomepage();
            await this.checkShopPage();
            await this.checkSingleProduct();
            await this.checkPerformance();
            await this.generateReport();
        } catch (error) {
            console.error(`❌ Erro crítico: ${error.message}`);
        } finally {
            await this.close();
        }
    }
}

// Executar
const agent = new VisualQAAgent();
agent.run();
