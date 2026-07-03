#!/usr/bin/env node
import { chromium } from "playwright-core";

const [url, out1, out2, out3] = process.argv.slice(2);
if (!url || !out1) {
  console.error("Uso: screenshot_helper.mjs <url> [out1] [out2] [out3]");
  process.exit(1);
}

let browser;
try {
  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
  await page.waitForTimeout(1500);

  async function snap(path) {
    if (!path) return null;
    await page.screenshot({ path, fullPage: false });
    console.error(`  → ${path}`);
  }

  // Screenshot 1: top (general overview)
  await page.evaluate("window.scrollTo(0, 0)");
  await page.waitForTimeout(500);
  await snap(out1);

  // Screenshot 2: scroll to 33%
  const scrollH = await page.evaluate("document.body.scrollHeight");
  const aboveFold = await page.evaluate("window.innerHeight");
  if (out2) {
    await page.evaluate(`window.scrollTo(0, ${Math.min(scrollH * 0.33, scrollH - aboveFold - 100)})`);
    await page.waitForTimeout(500);
    await snap(out2);
  }

  // Screenshot 3: scroll to 66%
  if (out3) {
    await page.evaluate(`window.scrollTo(0, ${Math.min(scrollH * 0.66, scrollH - aboveFold - 100)})`);
    await page.waitForTimeout(500);
    await snap(out3);
  }

  await browser.close();
} catch (err) {
  console.error(`  ✗ Error capturando ${url}: ${err.message}`);
  if (browser) await browser.close();
  process.exit(1);
}
