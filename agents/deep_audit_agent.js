#!/usr/bin/env node
/**
 * 🔍 DEEP AUDIT AGENT - Análise profunda de cada página
 */

const puppeteer = require('puppeteer');
const fs = require('fs');

class DeepAuditAgent {
    constructor() {
        this.issues = {
            missing_images: [],
            broken_images: [],
            empty_sections: [],
            styling_issues: [],
            layout_problems: []
        };
    }

    async init() {
        console.log('=' .repeat(70));
        console.log('🔍 DEEP AUDIT AGENT - ANÁLISE COMPLETA');
        console.log('=' .repeat(70));
        console.log('');
        
        this.browser = await puppeteer.launch({
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        this.page = await this.browser.newPage();
        await this.page.setViewport({ width: 1920, height: 1080 });
        
        console.log('✅ Puppeteer pronto\n');
    }

    async auditPage(url, name) {
        console.log(`\n${'='.repeat(70)}`);
        console.log(`📄 AUDITANDO: ${name}`);
        console.log('=' .repeat(70) + '\n');
        
        try {
            await this.page.goto(url, { 
                waitUntil: 'networkidle0', 
                timeout: 30000 
            });
            
            await this.page.waitForTimeout(2000);
            
            // Screenshot
            const screenshotPath = `/tmp/audit_${name.replace(/\s+/g, '_')}.png`;
            await this.page.screenshot({ 
                path: screenshotPath, 
                fullPage: true 
            });
            console.log(`📸 Screenshot: ${screenshotPath}\n`);
            
            // Verificar imagens
            const images = await this.page.$$eval('img', imgs => 
                imgs.map(img => ({
                    src: img.src,
                    alt: img.alt,
                    width: img.naturalWidth,
                    height: img.naturalHeight,
                    visible: img.offsetWidth > 0 && img.offsetHeight > 0
                }))
            );
            
            console.log(`🖼️  IMAGENS ENCONTRADAS: ${images.length}`);
            
            let broken = 0;
            let missing = 0;
            let ok = 0;
            
            images.forEach((img, i) => {
                if (img.width === 0 || img.height === 0) {
                    broken++;
                    console.log(`   ❌ Imagem ${i+1}: QUEBRADA (${img.src.substring(0, 60)}...)`);
                    this.issues.broken_images.push({
                        page: name,
                        src: img.src,
                        alt: img.alt
                    });
                } else if (!img.visible) {
                    missing++;
                    console.log(`   ⚠️  Imagem ${i+1}: NÃO VISÍVEL (${img.src.substring(0, 60)}...)`);
                    this.issues.missing_images.push({
                        page: name,
                        src: img.src,
                        alt: img.alt
                    });
                } else {
                    ok++;
                    if (i < 3) {
                        console.log(`   ✅ Imagem ${i+1}: OK (${img.width}x${img.height})`);
                    }
                }
            });
            
            if (ok >= 3) {
                console.log(`   ✅ ... e mais ${ok - 3} imagens OK`);
            }
            
            console.log(`\n📊 RESUMO:`);
            console.log(`   • OK: ${ok}`);
            console.log(`   • Quebradas: ${broken}`);
            console.log(`   • Não visíveis: ${missing}`);
            
            // Verificar produtos (se página de loja)
            if (name.includes('Loja') || name.includes('Shop')) {
                const products = await this.page.$$('.product');
                console.log(`\n🛍️  PRODUTOS VISÍVEIS: ${products.length}`);
                
                if (products.length === 0) {
                    console.log('   ❌ NENHUM PRODUTO RENDERIZADO!');
                    this.issues.empty_sections.push({
                        page: name,
                        section: 'products',
                        issue: 'Nenhum produto visível'
                    });
                }
            }
            
            // Verificar seções vazias
            const sections = await this.page.$$('section');
            console.log(`\n📐 SEÇÕES TOTAIS: ${sections.length}`);
            
            for (let i = 0; i < sections.length; i++) {
                const section = sections[i];
                const isEmpty = await section.evaluate(el => {
                    const text = el.textContent.trim();
                    const hasImages = el.querySelectorAll('img').length > 0;
                    return text.length < 10 && !hasImages;
                });
                
                if (isEmpty) {
                    console.log(`   ⚠️  Seção ${i+1}: VAZIA`);
                    this.issues.empty_sections.push({
                        page: name,
                        section: `section-${i+1}`,
                        issue: 'Seção vazia'
                    });
                }
            }
            
            // Verificar layout
            const bodyWidth = await this.page.evaluate(() => document.body.scrollWidth);
            const viewportWidth = await this.page.viewport().width;
            
            if (bodyWidth > viewportWidth + 50) {
                console.log(`\n⚠️  OVERFLOW HORIZONTAL: ${bodyWidth}px > ${viewportWidth}px`);
                this.issues.layout_problems.push({
                    page: name,
                    issue: 'Horizontal overflow',
                    details: `${bodyWidth}px de largura`
                });
            }
            
        } catch (error) {
            console.log(`❌ ERRO: ${error.message}\n`);
        }
    }

    async generateReport() {
        console.log('\n' + '='.repeat(70));
        console.log('📊 RELATÓRIO FINAL DE AUDITORIA');
        console.log('='.repeat(70) + '\n');
        
        const totalIssues = 
            this.issues.missing_images.length +
            this.issues.broken_images.length +
            this.issues.empty_sections.length +
            this.issues.layout_problems.length;
        
        console.log(`⚠️  TOTAL DE ISSUES: ${totalIssues}\n`);
        
        if (this.issues.broken_images.length > 0) {
            console.log(`❌ IMAGENS QUEBRADAS: ${this.issues.broken_images.length}`);
            this.issues.broken_images.slice(0, 5).forEach(img => {
                console.log(`   • ${img.page}: ${img.src.substring(0, 70)}...`);
            });
            if (this.issues.broken_images.length > 5) {
                console.log(`   ... e mais ${this.issues.broken_images.length - 5}`);
            }
            console.log('');
        }
        
        if (this.issues.missing_images.length > 0) {
            console.log(`⚠️  IMAGENS NÃO VISÍVEIS: ${this.issues.missing_images.length}`);
            this.issues.missing_images.slice(0, 5).forEach(img => {
                console.log(`   • ${img.page}: ${img.alt || 'sem alt'}`);
            });
            if (this.issues.missing_images.length > 5) {
                console.log(`   ... e mais ${this.issues.missing_images.length - 5}`);
            }
            console.log('');
        }
        
        if (this.issues.empty_sections.length > 0) {
            console.log(`📭 SEÇÕES VAZIAS: ${this.issues.empty_sections.length}`);
            this.issues.empty_sections.forEach(section => {
                console.log(`   • ${section.page} → ${section.section}: ${section.issue}`);
            });
            console.log('');
        }
        
        if (this.issues.layout_problems.length > 0) {
            console.log(`📐 PROBLEMAS DE LAYOUT: ${this.issues.layout_problems.length}`);
            this.issues.layout_problems.forEach(prob => {
                console.log(`   • ${prob.page}: ${prob.issue} (${prob.details})`);
            });
            console.log('');
        }
        
        // Salvar relatório
        const report = {
            timestamp: new Date().toISOString(),
            total_issues: totalIssues,
            issues: this.issues,
            recommendations: this.generateRecommendations()
        };
        
        fs.writeFileSync('deep_audit_report.json', JSON.stringify(report, null, 2));
        console.log('💾 Relatório salvo: deep_audit_report.json\n');
        
        // Recomendações
        console.log('💡 RECOMENDAÇÕES:\n');
        report.recommendations.forEach((rec, i) => {
            console.log(`${i+1}. ${rec}`);
        });
        console.log('');
    }

    generateRecommendations() {
        const recs = [];
        
        if (this.issues.broken_images.length > 0) {
            recs.push(`Corrigir ${this.issues.broken_images.length} imagens quebradas`);
            recs.push('Verificar URLs das imagens no WordPress');
            recs.push('Re-upload de imagens se necessário');
        }
        
        if (this.issues.missing_images.length > 0) {
            recs.push(`Tornar visíveis ${this.issues.missing_images.length} imagens`);
            recs.push('Verificar CSS display/visibility');
        }
        
        if (this.issues.empty_sections.length > 0) {
            recs.push(`Preencher ${this.issues.empty_sections.length} seções vazias`);
            recs.push('Adicionar conteúdo ou remover seções');
        }
        
        if (this.issues.layout_problems.length > 0) {
            recs.push('Corrigir overflow horizontal');
            recs.push('Verificar width de containers');
        }
        
        if (recs.length === 0) {
            recs.push('✅ Site está OK! Sem issues críticos.');
        }
        
        return recs;
    }

    async close() {
        if (this.browser) {
            await this.browser.close();
        }
    }

    async run() {
        try {
            await this.init();
            
            // Auditar páginas principais
            await this.auditPage('http://localhost:8080', 'Homepage');
            await this.auditPage('http://localhost:8080/teste-html', 'Loja Principal');
            await this.auditPage('http://localhost:8080/shop', 'Shop WooCommerce');
            await this.auditPage('http://localhost:8080/sobre', 'Sobre');
            await this.auditPage('http://localhost:8080/product-category/boinas', 'Categoria Boinas');
            
            await this.generateReport();
            
        } catch (error) {
            console.error(`❌ Erro crítico: ${error.message}`);
        } finally {
            await this.close();
        }
    }
}

// Executar
const agent = new DeepAuditAgent();
agent.run();
