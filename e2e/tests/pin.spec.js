const { test, expect } = require('@playwright/test');
const { openPanel, openTab, pointsRow } = require('./helpers');

test('PIN protects the panel: set, wrong PIN rejected, correct PIN unlocks', async ({ page }) => {
  await page.request.post('/reset_config');
  await openPanel(page);
  await openTab(page, 'settings');

  // Set a PIN for the first time
  await page.getByRole('button', { name: 'Set PIN' }).click();
  await page.locator('#newPin').fill('1234');
  await page.locator('#confirmPin').fill('1234');
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.locator('#pinStatus')).toContainText('PIN Active');

  // A fresh operator (cleared localStorage) must unlock via the modal
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await expect(page.locator('#pinModal')).toHaveClass(/active/);

  // Wrong PIN: rejected with an error
  await page.locator('#pinInput').fill('9999');
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page.locator('#pinError')).toHaveText('Incorrect PIN');

  // Correct PIN: modal closes and scoring works again
  await page.locator('#pinInput').fill('1234');
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page.locator('#pinModal')).not.toHaveClass(/active/);

  await pointsRow(page, 'home').getByRole('button', { name: '+', exact: true }).click();
  await expect(page.locator('#summaryHomeScore')).toHaveText('1');

  // The PIN is enforced server-side too: timer control without the PIN is refused
  const bad = await page.request.post('/timer_control', { form: { action: 'start', pin: '9999' } });
  expect(bad.status()).toBe(403);
  const good = await page.request.post('/timer_control', { form: { action: 'start', pin: '1234' } });
  expect(good.status()).toBe(200);
});
