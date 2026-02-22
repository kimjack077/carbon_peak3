const { test, expect } = require('@playwright/test');

test('core prediction flow works', async ({ page }) => {
  await page.goto('/');

  await expect(page.locator('#tab-scenarios')).toBeVisible({ timeout: 30000 });
  await page.locator('#tab-scenarios').click();

  const runButton = page.locator('.run-prediction .el-button--success');
  await expect(runButton).toBeVisible({ timeout: 15000 });
  await runButton.click();

  const confirmButton = page.locator('.el-message-box__btns .el-button--primary');
  await expect(confirmButton).toBeVisible({ timeout: 10000 });
  await confirmButton.click();

  await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 120000 });

  await page.locator('#tab-results').click();

  const chart = page.locator('#carbon-peak-chart');
  await expect(chart).toBeVisible({ timeout: 30000 });

  await expect(page.locator('.data-card .el-select')).toBeVisible({ timeout: 30000 });
});
