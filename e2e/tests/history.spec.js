const { test, expect } = require('@playwright/test');

test('score history overlay attributes the oldest shown point correctly and escapes names', async ({ page }) => {
  await page.request.post('/reset_config');
  await page.request.post('/update', { form: { homeName: 'Home', awayName: '<b>X</b>' } });
  // 1-0, then away scores five in a row: the 5-point window is 1-1 ... 1-5
  await page.request.post('/update', { form: { homeScore: '1', awayScore: '0' } });
  for (let a = 1; a <= 5; a++) {
    await page.request.post('/update', { form: { homeScore: '1', awayScore: String(a) } });
  }

  await page.goto('/score_history');
  const names = page.locator('#historyList .team-name');
  await expect(names).toHaveCount(5);
  await expect(names).toHaveText(Array(5).fill('<b>X</b>'));
  await expect(page.locator('#historyList b')).toHaveCount(0);
});

test('the PIN is never shown on the broadcast scorebug', async ({ page }) => {
  await page.request.post('/reset_config');
  await page.request.post('/update', {
    form: { isSettingPin: 'true', newPin: '1234', confirmPin: '1234' },
  });
  await page.goto('/');
  await expect(page.locator('#set_1')).toHaveText('0');
  await expect(page.locator('#pinDisplay')).toHaveText('');
  await page.request.post('/reset_config');
});
