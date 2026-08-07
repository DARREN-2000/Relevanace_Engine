const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto("http://localhost:5173");
  // Wait for the components to render the real data from the API
  await page.waitForTimeout(3000);
  await page.screenshot({ path: "screenshot.png" });
  await browser.close();
})();
