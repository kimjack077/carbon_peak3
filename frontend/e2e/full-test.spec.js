const { test, expect } = require('@playwright/test');

test.describe('碳达峰预测系统全面测试', () => {

  test.describe('数据上传页面', () => {
    test('页面加载正常', async ({ page }) => {
      await page.goto('/');

      // 检查标题
      await expect(page.locator('h1')).toContainText('碳达峰预测系统', { timeout: 30000 });

      // 检查标签页可见
      await expect(page.locator('.el-tabs__item').first()).toBeVisible();
    });

    test('自动加载示例数据', async ({ page }) => {
      await page.goto('/');

      // 数据加载后自动切换到情景设置页
      await expect(page.locator('#tab-scenarios')).toBeVisible({ timeout: 30000 });

      // 切换回数据来源页检查数据
      await page.locator('#tab-upload').click();

      // 检查数据表格显示
      await expect(page.locator('.el-table').first()).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('情景设置页面', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/');
      // 等待数据加载完成并自动切换到情景设置页
      await expect(page.locator('#tab-scenarios')).toBeVisible({ timeout: 30000 });
    });

    test('情景列表显示', async ({ page }) => {
      await page.locator('#tab-scenarios').click();

      // 检查情景管理组件
      await expect(page.locator('.scenario-manager')).toBeVisible({ timeout: 15000 });

      // 检查表格存在
      await expect(page.locator('.scenario-list-card .el-table')).toBeVisible({ timeout: 10000 });
    });

    test('创建新情景', async ({ page }) => {
      await page.locator('#tab-scenarios').click();

      // 输入情景名称
      const nameInput = page.locator('.scenario-card .el-form-item').first().locator('.el-input__inner');
      await nameInput.clear();
      await nameInput.fill('E2E测试情景');

      // 点击创建按钮
      await page.locator('.scenario-card .el-button--primary').click();

      // 等待创建成功消息
      await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 15000 });
    });

    test('运行预测', async ({ page }) => {
      await page.locator('#tab-scenarios').click();
      await expect(page.locator('.scenario-list-card')).toBeVisible({ timeout: 15000 });

      // 点击运行预测按钮
      const runButton = page.locator('.run-prediction .el-button--success');
      await expect(runButton).toBeVisible({ timeout: 10000 });
      await runButton.click();

      // 确认对话框
      const confirmButton = page.locator('.el-message-box__btns .el-button--primary');
      await expect(confirmButton).toBeVisible({ timeout: 10000 });
      await confirmButton.click();

      // 等待预测成功
      await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 120000 });
    });
  });

  test.describe('预测结果页面', () => {
    test('结果显示', async ({ page }) => {
      await page.goto('/');
      await expect(page.locator('#tab-scenarios')).toBeVisible({ timeout: 30000 });

      // 运行预测
      await page.locator('#tab-scenarios').click();
      const runButton = page.locator('.run-prediction .el-button--success');
      await expect(runButton).toBeVisible({ timeout: 10000 });
      await runButton.click();

      const confirmButton = page.locator('.el-message-box__btns .el-button--primary');
      await expect(confirmButton).toBeVisible({ timeout: 10000 });
      await confirmButton.click();

      await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 120000 });

      // 切换到结果页
      await page.locator('#tab-results').click();

      // 检查图表
      const chart = page.locator('#carbon-peak-chart');
      await expect(chart).toBeVisible({ timeout: 30000 });
    });
  });

  test.describe('情景对比页面', () => {
    test('对比页面显示', async ({ page }) => {
      await page.goto('/');
      await expect(page.locator('#tab-scenarios')).toBeVisible({ timeout: 30000 });

      // 切换到对比页
      await page.locator('#tab-compare').click();

      // 检查对比组件
      await expect(page.locator('.scenario-compare')).toBeVisible({ timeout: 30000 });
    });
  });

  test.describe('导航功能', () => {
    test('标签页切换', async ({ page }) => {
      await page.goto('/');
      await expect(page.locator('#tab-scenarios')).toBeVisible({ timeout: 30000 });

      // 测试所有标签页切换
      await page.locator('#tab-upload').click();
      await expect(page.locator('.data-upload')).toBeVisible();

      await page.locator('#tab-scenarios').click();
      await expect(page.locator('.scenario-manager')).toBeVisible({ timeout: 10000 });

      await page.locator('#tab-results').click();
      await expect(page.locator('.prediction-results')).toBeVisible({ timeout: 30000 });

      await page.locator('#tab-compare').click();
      await expect(page.locator('.scenario-compare')).toBeVisible({ timeout: 30000 });
    });
  });

  test.describe('控制台检查', () => {
    test('无JavaScript错误', async ({ page }) => {
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));

      await page.goto('/');
      await expect(page.locator('#tab-scenarios')).toBeVisible({ timeout: 30000 });

      // 执行主要操作
      await page.locator('#tab-scenarios').click();
      await expect(page.locator('.scenario-manager')).toBeVisible({ timeout: 10000 });

      await page.locator('#tab-results').click();
      await expect(page.locator('.prediction-results')).toBeVisible({ timeout: 30000 });

      await page.locator('#tab-compare').click();
      await expect(page.locator('.scenario-compare')).toBeVisible({ timeout: 30000 });

      // 检查无严重错误
      const criticalErrors = errors.filter(e =>
        !e.includes('Warning:') &&
        !e.includes('[HMR]') &&
        !e.includes('network')
      );
      expect(criticalErrors.length).toBe(0);
    });
  });
});