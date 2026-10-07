const { chromium } = require('playwright');
const { pathToFileURL } = require('url');
const path = require('path');
const fs = require('fs');

async function verifyReport() {
    const root = path.resolve(__dirname, '../../..');
    const report = path.resolve(root, process.argv[2] || 'docs/知识库升级与复查报告.html');
    const output = path.resolve(root, process.env.REPORT_QA_OUTPUT || 'docs/report-qa');
    if (!fs.existsSync(report)) throw new Error(`Report file does not exist: ${report}`);
    fs.mkdirSync(output, { recursive: true });

    const options = { headless: true };
    if (process.env.REPORT_BROWSER_PATH) options.executablePath = process.env.REPORT_BROWSER_PATH;
    const browser = await chromium.launch(options);
    try {
        const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        const url = pathToFileURL(report).href;
        await page.goto(url);
        await page.screenshot({ path: path.join(output, 'desktop.png'), fullPage: true });
        const brokenAnchors = await page.evaluate(() => [...document.querySelectorAll('nav a')]
            .filter(anchor => {
                const href = anchor.getAttribute('href');
                return href && href.startsWith('#') && !document.getElementById(decodeURIComponent(href.slice(1)));
            }).length);
        await page.locator('#files details').evaluate(element => element.open = true);
        await page.locator('#search').fill('Unity');
        const visibleRows = await page.locator('#fileRows tr:visible').count();
        if (visibleRows === 0) throw new Error('File filter did not return matching rows');
        await page.setViewportSize({ width: 390, height: 844 });
        await page.goto(url);
        await page.screenshot({ path: path.join(output, 'mobile.png'), fullPage: true });
        const mobileOverflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
        const result = { brokenAnchors, visibleRows, mobileOverflow, pageErrors: errors };
        fs.writeFileSync(path.join(output, 'result.json'), JSON.stringify(result, null, 2));
        console.log(result);
        if (brokenAnchors || mobileOverflow || errors.length) process.exitCode = 1;
    } finally {
        await browser.close();
    }
}

verifyReport().catch(error => {
    console.error(error.message);
    process.exitCode = 1;
});
