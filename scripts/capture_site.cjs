const { chromium } = require('playwright');
const path = require('path');

const baseUrl = process.argv[2] || 'http://127.0.0.1:19381';
const outputDir = path.resolve(__dirname, '..', 'quality', 'screenshots');

async function capture(browser, name, relativeUrl, viewport) {
  const page = await browser.newPage({ viewport });
  await page.goto(`${baseUrl}${relativeUrl}`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(outputDir, `${name}.png`), fullPage: false });
  const metrics = await page.evaluate(() => ({
    title: document.title,
    h1: document.querySelector('h1')?.textContent.trim(),
    viewportWidth: window.innerWidth,
    documentWidth: document.documentElement.scrollWidth,
    h1Count: document.querySelectorAll('main h1').length,
  }));
  await page.close();
  return { name, ...metrics };
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const results = [];
  results.push(await capture(browser, 'home-desktop', '/index.html', { width: 1440, height: 1000 }));
  results.push(await capture(browser, 'lesson-04-desktop', '/lessons/04.html', { width: 1440, height: 1000 }));
  results.push(await capture(browser, 'home-mobile', '/index.html', { width: 390, height: 844 }));
  results.push(await capture(browser, 'home-positions-mobile', '/index.html#positions', { width: 390, height: 844 }));
  results.push(await capture(browser, 'lesson-04-mobile', '/lessons/04.html', { width: 390, height: 844 }));
  await browser.close();
  console.log(JSON.stringify(results, null, 2));
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
