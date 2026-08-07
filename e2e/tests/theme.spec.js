const { test, expect } = require('@playwright/test');
const { resetState } = require('./helpers');

async function setVisibility(
  request,
  { sets = false, timer = false, timeouts = false, history = false } = {}
) {
  await request.post('/update', {
    form: {
      overlay_sets: String(sets),
      overlay_timer: String(timer),
      overlay_timeouts: String(timeouts),
      overlay_history: String(history),
    },
  });
}

test('theme color change reaches the match timer overlay', async ({ page, request }) => {
  await resetState(request);
  const res = await request.post('/update', { form: { themeBgPrimary: '#112233' } });
  expect(res.status()).toBe(200);
  await page.goto('/match_timer');
  await expect
    .poll(
      () =>
        page.evaluate(() =>
          getComputedStyle(document.documentElement).getPropertyValue('--primary-blue').trim()
        ),
      { timeout: 5000 }
    )
    .toBe('#112233');
});

test('timer overlay responds to the overlay_timer flag (hidden by default)', async ({ page, request }) => {
  await resetState(request);
  await page.goto('/match_timer');
  await expect(page.locator('.timer-container')).toHaveClass(/hidden/, { timeout: 5000 });
  await setVisibility(request, { timer: true });
  await expect(page.locator('.timer-container')).not.toHaveClass(/hidden/);
  await setVisibility(request, {});
  await expect(page.locator('.timer-container')).toHaveClass(/hidden/);
});

test('score_history overlay respects its flag', async ({ page, request }) => {
  await resetState(request);
  await page.goto('/score_history');
  await expect(page.locator('.history-container')).toHaveClass(/hidden/);
  await setVisibility(request, { history: true });
  await expect(page.locator('.history-container')).not.toHaveClass(/hidden/);
});
