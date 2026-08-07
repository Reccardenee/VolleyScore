const { test, expect } = require('@playwright/test');
const { resetState } = require('./helpers');

async function setVisibility(request, flags) {
  await request.post('/update', {
    form: {
      overlay_sets: flags.includes('sets') ? 'true' : 'false',
      overlay_timer: flags.includes('timer') ? 'true' : 'false',
      overlay_timeouts: flags.includes('timeouts') ? 'true' : 'false',
      overlay_history: flags.includes('history') ? 'true' : 'false',
    },
  });
}

test('theme color change reaches the match timer overlay', async ({ page, request }) => {
  await resetState(request);
  const res = await request.post('/update', { form: { themeBgPrimary: '#112233' } });
  expect(res.status()).toBe(200);
  await page.goto('/match_timer');
  await page.waitForTimeout(600);
  const primary = await page.evaluate(() =>
    getComputedStyle(document.documentElement).getPropertyValue('--primary-blue').trim());
  expect(primary).toBe('#112233');
});

test('hiding the timer fades the overlay out', async ({ page, request }) => {
  await resetState(request);
  await setVisibility(request, ['timer']);
  await page.goto('/match_timer');
  await page.waitForTimeout(500);
  await expect(page.locator('.timer-container')).not.toHaveClass(/hidden/);
  await setVisibility(request, []);
  await page.waitForTimeout(700);
  await expect(page.locator('.timer-container')).toHaveClass(/hidden/);
});

test('score_history overlay respects its flag', async ({ page, request }) => {
  await resetState(request);
  await page.goto('/score_history');
  await page.waitForTimeout(500);
  await expect(page.locator('.history-container')).toHaveClass(/hidden/);
  await setVisibility(request, ['history']);
  await page.waitForTimeout(700);
  await expect(page.locator('.history-container')).not.toHaveClass(/hidden/);
});