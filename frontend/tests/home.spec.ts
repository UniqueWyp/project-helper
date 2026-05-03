import { test, expect } from '@playwright/test';

test.describe('首页功能测试', () => {
  test('应该正确加载首页并显示标题', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('Project Helper');
  });

  test('应该显示输入框和分析按钮', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('input[placeholder="输入 GitHub 仓库地址..."]')).toBeVisible();
    await expect(page.locator('button', { hasText: '分析项目' })).toBeVisible();
  });

  test('应该显示已分析项目部分', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h2', { hasText: '已分析项目' })).toBeVisible();
  });

  test('刷新按钮应该存在且可点击', async ({ page }) => {
    await page.goto('/');
    const refreshButton = page.locator('.btn-refresh');
    await expect(refreshButton).toBeVisible();
    await refreshButton.click();
  });
});
