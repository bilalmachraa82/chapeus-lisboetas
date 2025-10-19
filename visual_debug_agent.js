/**
 * 🔍 VISUAL DEBUG AGENT - Puppeteer Analysis
 * Analyzes the site visually to identify image display issues
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:8080';
const SCREENSHOT_DIR = path.join(__dirname, 'screenshots');

// Ensure screenshots directory exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function analyzeImageDisplay(page) {
    return await page.evaluate(() => {
        const images = Array.from(document.querySelectorAll('img'));
        const productImages = images.filter(img => 
            img.closest('.product') || 
            img.closest('.product-small') || 
            img.closest('.box-image')
        );
        
        return productImages.map((img, index) => {
            const rect = img.getBoundingClientRect();
            const computedStyle = window.getComputedStyle(img);
            const parent = img.closest('.product') || img.closest('.product-small');
            const parentStyles = parent ? window.getComputedStyle(parent) : null;
            
            return {
                index,
                src: img.src,
                alt: img.alt,
                naturalWidth: img.naturalWidth,
                naturalHeight: img.naturalHeight,
                displayWidth: rect.width,
                displayHeight: rect.height,
                visible: rect.width > 0 && rect.height > 0,
                inViewport: rect.top < window.innerHeight && rect.bottom > 0,
                opacity: computedStyle.opacity,
                display: computedStyle.display,
                visibility: computedStyle.visibility,
                objectFit: computedStyle.objectFit,
                position: computedStyle.position,
                transform: computedStyle.transform,
                overflow: computedStyle.overflow,
                loaded: img.complete && img.naturalHeight > 0,
                parentOverflow: parentStyles ? parentStyles.overflow : null,
                parentHeight: parent ? parent.getBoundingClientRect().height : null,
                zIndex: computedStyle.zIndex
            };
        });
    });
}

async function analyzeProductCards(page) {
    return await page.evaluate(() => {
        const products = Array.from(document.querySelectorAll('.product, .product-small'));
        
        return products.slice(0, 12).map((product, index) => {
            const rect = product.getBoundingClientRect();
            const styles = window.getComputedStyle(product);
            const boxImage = product.querySelector('.box-image');
            const boxImageStyles = boxImage ? window.getComputedStyle(boxImage) : null;
            const img = product.querySelector('img');
            
            return {
                index,
                className: product.className,
                width: rect.width,
                height: rect.height,
                hasImage: !!img,
                imageSrc: img ? img.src : null,
                imageVisible: img ? (img.offsetWidth > 0 && img.offsetHeight > 0) : false,
                boxImageHeight: boxImage ? boxImage.getBoundingClientRect().height : null,
                boxImageOverflow: boxImageStyles ? boxImageStyles.overflow : null,
                overflow: styles.overflow,
                display: styles.display,
                position: styles.position
            };
        });
    });
}

async function checkCSSIssues(page) {
    return await page.evaluate(() => {
        const issues = [];
        
        // Check for common CSS issues
        const problematicRules = [
            { selector: '.box-image', property: 'height', issue: 'Fixed height might crop images' },
            { selector: '.box-image', property: 'overflow', issue: 'Overflow hidden might hide images' },
            { selector: 'img', property: 'opacity', issue: 'Opacity < 1 makes images transparent' },
            { selector: 'img', property: 'display', issue: 'Display none hides images' },
            { selector: '.product-small img', property: 'transform', issue: 'Transform might move images off-screen' }
        ];
        
        problematicRules.forEach(rule => {
            const elements = document.querySelectorAll(rule.selector);
            elements.forEach((el, idx) => {
                const styles = window.getComputedStyle(el);
                const value = styles[rule.property];
                
                if (rule.property === 'opacity' && parseFloat(value) < 1) {
                    issues.push({
                        selector: rule.selector,
                        element: idx,
                        property: rule.property,
                        value: value,
                        issue: rule.issue
                    });
                }
                
                if (rule.property === 'display' && value === 'none') {
                    issues.push({
                        selector: rule.selector,
                        element: idx,
                        property: rule.property,
                        value: value,
                        issue: rule.issue
                    });
                }
                
                if (rule.property === 'overflow' && value === 'hidden') {
                    const rect = el.getBoundingClientRect();
                    if (rect.height < 200) {
                        issues.push({
                            selector: rule.selector,
                            element: idx,
                            property: rule.property,
                            value: value,
                            height: rect.height,
                            issue: `${rule.issue} (height: ${rect.height}px)`
                        });
                    }
                }
            });
        });
        
        return issues;
    });
}

async function main() {
    console.log('🔍 VISUAL DEBUG AGENT - Starting Analysis\n');
    console.log('='.repeat(80) + '\n');
    
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const report = {
        timestamp: new Date().toISOString(),
        pages: {}
    };
    
    try {
        // ============================================================================
        // 1. ANALYZE HOMEPAGE
        // ============================================================================
        
        console.log('1️⃣ ANALYZING HOMEPAGE...\n');
        
        const homePage = await browser.newPage();
        await homePage.setViewport({ width: 1920, height: 1080 });
        
        try {
            await homePage.goto(`${BASE_URL}`, { 
                waitUntil: 'networkidle0',
                timeout: 30000 
            });
            
            // Wait for images to load
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            // Take screenshot
            await homePage.screenshot({ 
                path: path.join(SCREENSHOT_DIR, 'homepage_full.png'),
                fullPage: true
            });
            console.log('   ✅ Screenshot saved: homepage_full.png\n');
            
            // Analyze images
            const homeImages = await analyzeImageDisplay(homePage);
            const homeProducts = await analyzeProductCards(homePage);
            const homeCSSIssues = await checkCSSIssues(homePage);
            
            report.pages.homepage = {
                url: BASE_URL,
                images: homeImages,
                products: homeProducts,
                cssIssues: homeCSSIssues
            };
            
            console.log('   📊 Found ' + homeImages.length + ' product images');
            console.log('   📊 Found ' + homeProducts.length + ' product cards');
            console.log('   🚨 Found ' + homeCSSIssues.length + ' CSS issues\n');
            
            // Print image analysis
            console.log('   🖼️  IMAGE ANALYSIS:\n');
            homeImages.slice(0, 5).forEach(img => {
                console.log(`      Image ${img.index}:`);
                console.log(`        Loaded: ${img.loaded ? '✅' : '❌'}`);
                console.log(`        Visible: ${img.visible ? '✅' : '❌'} (${img.displayWidth}x${img.displayHeight}px)`);
                console.log(`        Opacity: ${img.opacity}`);
                console.log(`        Object-fit: ${img.objectFit}`);
                console.log(`        Overflow: ${img.overflow}`);
                if (!img.loaded) {
                    console.log(`        ⚠️  SRC: ${img.src}`);
                }
                console.log('');
            });
            
        } catch (error) {
            console.log('   ❌ Error analyzing homepage: ' + error.message + '\n');
        }
        
        await homePage.close();
        
        // ============================================================================
        // 2. ANALYZE SHOP PAGE
        // ============================================================================
        
        console.log('2️⃣ ANALYZING SHOP PAGE...\n');
        
        const shopPage = await browser.newPage();
        await shopPage.setViewport({ width: 1920, height: 1080 });
        
        try {
            await shopPage.goto(`${BASE_URL}/shop`, { 
                waitUntil: 'networkidle0',
                timeout: 30000 
            });
            
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            // Take screenshot
            await shopPage.screenshot({ 
                path: path.join(SCREENSHOT_DIR, 'shop_full.png'),
                fullPage: true
            });
            console.log('   ✅ Screenshot saved: shop_full.png\n');
            
            // Analyze
            const shopImages = await analyzeImageDisplay(shopPage);
            const shopProducts = await analyzeProductCards(shopPage);
            const shopCSSIssues = await checkCSSIssues(shopPage);
            
            report.pages.shop = {
                url: `${BASE_URL}/shop`,
                images: shopImages,
                products: shopProducts,
                cssIssues: shopCSSIssues
            };
            
            console.log('   📊 Found ' + shopImages.length + ' product images');
            console.log('   📊 Found ' + shopProducts.length + ' product cards');
            console.log('   🚨 Found ' + shopCSSIssues.length + ' CSS issues\n');
            
            // Print detailed issues
            if (shopCSSIssues.length > 0) {
                console.log('   🚨 CSS ISSUES FOUND:\n');
                shopCSSIssues.forEach((issue, idx) => {
                    console.log(`      ${idx + 1}. ${issue.selector} (element ${issue.element})`);
                    console.log(`         Property: ${issue.property} = ${issue.value}`);
                    console.log(`         Issue: ${issue.issue}`);
                    console.log('');
                });
            }
            
        } catch (error) {
            console.log('   ❌ Error analyzing shop: ' + error.message + '\n');
        }
        
        await shopPage.close();
        
        // ============================================================================
        // 3. ANALYZE HOVER BEHAVIOR
        // ============================================================================
        
        console.log('3️⃣ ANALYZING HOVER BEHAVIOR...\n');
        
        const hoverPage = await browser.newPage();
        await hoverPage.setViewport({ width: 1920, height: 1080 });
        
        try {
            await hoverPage.goto(`${BASE_URL}/shop`, { 
                waitUntil: 'networkidle0',
                timeout: 30000 
            });
            
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Take screenshot before hover
            await hoverPage.screenshot({ 
                path: path.join(SCREENSHOT_DIR, 'shop_before_hover.png')
            });
            console.log('   ✅ Screenshot saved: shop_before_hover.png\n');
            
            // Find first product and hover
            const firstProduct = await hoverPage.$('.product, .product-small');
            if (firstProduct) {
                await firstProduct.hover();
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                // Take screenshot after hover
                await hoverPage.screenshot({ 
                    path: path.join(SCREENSHOT_DIR, 'shop_after_hover.png')
                });
                console.log('   ✅ Screenshot saved: shop_after_hover.png\n');
                
                // Analyze hover state
                const hoverState = await hoverPage.evaluate(() => {
                    const product = document.querySelector('.product, .product-small');
                    if (!product) return null;
                    
                    const img = product.querySelector('img');
                    const styles = window.getComputedStyle(img);
                    
                    return {
                        transform: styles.transform,
                        opacity: styles.opacity,
                        scale: styles.scale,
                        transition: styles.transition
                    };
                });
                
                report.hoverBehavior = hoverState;
                
                console.log('   🖱️  HOVER STATE:');
                console.log(`      Transform: ${hoverState.transform}`);
                console.log(`      Opacity: ${hoverState.opacity}`);
                console.log(`      Transition: ${hoverState.transition}`);
                console.log('');
            }
            
        } catch (error) {
            console.log('   ❌ Error analyzing hover: ' + error.message + '\n');
        }
        
        await hoverPage.close();
        
    } catch (error) {
        console.error('❌ Fatal error: ' + error.message);
    } finally {
        await browser.close();
    }
    
    // ============================================================================
    // SAVE REPORT
    // ============================================================================
    
    const reportPath = path.join(__dirname, 'visual_debug_report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log('📄 Report saved: visual_debug_report.json\n');
    
    // ============================================================================
    // SUMMARY
    // ============================================================================
    
    console.log('='.repeat(80));
    console.log('📊 VISUAL DEBUG SUMMARY');
    console.log('='.repeat(80) + '\n');
    
    if (report.pages.homepage) {
        console.log('🏠 HOMEPAGE:');
        console.log(`   Images found: ${report.pages.homepage.images.length}`);
        console.log(`   Images loaded: ${report.pages.homepage.images.filter(i => i.loaded).length}`);
        console.log(`   Images visible: ${report.pages.homepage.images.filter(i => i.visible).length}`);
        console.log(`   CSS issues: ${report.pages.homepage.cssIssues.length}`);
        console.log('');
    }
    
    if (report.pages.shop) {
        console.log('🛍️  SHOP PAGE:');
        console.log(`   Images found: ${report.pages.shop.images.length}`);
        console.log(`   Images loaded: ${report.pages.shop.images.filter(i => i.loaded).length}`);
        console.log(`   Images visible: ${report.pages.shop.images.filter(i => i.visible).length}`);
        console.log(`   CSS issues: ${report.pages.shop.cssIssues.length}`);
        console.log('');
    }
    
    console.log('📸 SCREENSHOTS:');
    console.log('   • screenshots/homepage_full.png');
    console.log('   • screenshots/shop_full.png');
    console.log('   • screenshots/shop_before_hover.png');
    console.log('   • screenshots/shop_after_hover.png');
    console.log('');
    
    console.log('✅ VISUAL DEBUG COMPLETE!\n');
}

main().catch(console.error);
