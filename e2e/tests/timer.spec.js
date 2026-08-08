const { test, expect } = require('@playwright/test');
const { openPanel, parseTimerSeconds } = require('./helpers');

async function timerSeconds(page) {
  return parseTimerSeconds(await page.locator('#summaryTimer').textContent());
}

test('timer runs, freezes while paused (no jump), resumes, and resets', async ({ page }) => {
  await page.request.post('/reset_config');
  await openPanel(page);

  await expect(page.locator('#timerDisplay')).toHaveText('00:00');

  // Start: elapsed climbs
  await page.getByRole('button', { name: 'Start' }).click();
  await expect
    .poll(() => timerSeconds(page), { timeout: 8000, intervals: [200] })
    .toBeGreaterThanOrEqual(1);

  // Pause: elapsed must freeze exactly (regression: used to jump by clock skew)
  await page.getByRole('button', { name: 'Pause' }).click();
  const frozen = await timerSeconds(page);
  await page.waitForTimeout(1500);
  expect(await timerSeconds(page)).toBe(frozen);

  // Resume: elapsed continues from where it froze
  await page.getByRole('button', { name: 'Resume' }).click();
  await expect
    .poll(() => timerSeconds(page), { timeout: 8000, intervals: [200] })
    .toBeGreaterThanOrEqual(frozen + 1);

  // Reset: everything clears
  await page.getByRole('button', { name: 'Reset', exact: true }).click();
  await expect(page.locator('#timerDisplay')).toHaveText('00:00');
  await expect(page.locator('#summaryTimer')).toHaveText('00:00');
});
