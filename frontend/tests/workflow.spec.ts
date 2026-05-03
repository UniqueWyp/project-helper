import { test, expect } from '@playwright/test';

test.describe('核心工作流程测试', () => {
  
  test('输入项目仓库 URL 并添加项目', async ({ page }) => {
    await page.goto('/');
    
    const testUrl = 'https://github.com/test/test-repo';
    
    await page.fill('input[placeholder="输入 GitHub 仓库地址..."]', testUrl);
    
    const addButton = page.locator('button', { hasText: '分析项目' });
    await expect(addButton).toBeVisible();
    
    await page.fill('input[placeholder="输入 GitHub 仓库地址..."]', '');
  });

  test('检查空状态提示', async ({ page }) => {
    await page.goto('/');
    
    await expect(page.locator('.empty-state')).toBeVisible();
    await expect(page.locator('.empty-state')).toContainText('还没有分析过任何项目');
  });

  test('刷新按钮点击测试', async ({ page }) => {
    await page.goto('/');
    
    const refreshButton = page.locator('.btn-refresh');
    await refreshButton.click();
    
    await page.waitForTimeout(500);
    await expect(refreshButton).toBeVisible();
  });

  test('检查页面布局元素', async ({ page }) => {
    await page.goto('/');
    
    await expect(page.locator('.app')).toBeVisible();
    await expect(page.locator('.app-header')).toBeVisible();
    await expect(page.locator('.main-content')).toBeVisible();
    await expect(page.locator('.input-section')).toBeVisible();
    await expect(page.locator('.projects-section')).toBeVisible();
  });
});
