const { test, expect } = require('@playwright/test');
const { openPanel, clickPlus } = require('./helpers');

test('panel and overlays work with no Internet access', async ({ page, context }) => {
  // Only the local server is reachable (web fonts may fail, scripts must not)
  await context.route(/^https?:\/\/(?!127\.0\.0\.1)/, (route) => route.abort());
  const errors = [];
  context.on('weberror', (e) => errors.push(e.error().message));

  await page.request.post('/reset_config');
  await openPanel(page);
  await clickPlus(page, 'home', 1);

  const overlay = await context.newPage();
  await overlay.goto('/');
  await expect(overlay.locator('#points_1')).toHaveText('1');
  await expect(overlay.locator('svg.lucide')).not.toHaveCount(0);
  await overlay.close();

  const guide = await context.newPage();
  await guide.goto('/guide');
  await guide.close();

  expect(errors).toEqual([]);
});
