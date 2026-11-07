const { test, expect } = require('@playwright/test');
const { openPanel, openTab } = require('./helpers');

test('the IT switch translates the whole control panel and is remembered', async ({ page }) => {
  await page.request.post('/reset_config');
  await page.request.post('/update', { form: { homeScore: '1' } });
  await openPanel(page);

  await page.getByRole('button', { name: 'IT', exact: true }).click();

  // Static texts
  await expect(page.locator('#connectionText')).toHaveText('Connesso');
  await expect(page.locator('#tab-match .card-title').first()).toHaveText('Controllo Punteggio');
  await expect(page.locator('#posHome')).toHaveText('Servizio Casa');
  await expect(page.getByRole('button', { name: 'Azzera Partita' })).toBeVisible();
  // Dynamic texts rendered by JS
  await expect(page.locator('#pinStatus')).toHaveText('○ Nessun PIN');
  await expect(page.locator('#scoreHistoryList li').first()).toContainText('1 - 0');
  await expect(page.locator('#previousSetsContainer')).toHaveText('Nessun set completato.');
  await openTab(page, 'settings');
  await expect(page.locator('.shortcut-row .shortcut-label').first()).toHaveText('Casa +1 punto');
  await expect(page.locator('#newPin')).toHaveAttribute('placeholder', 'Nuovo PIN 4 cifre');

  // Toasts too
  await page.getByRole('button', { name: 'Applica Scorciatoie' }).click();
  await expect(page.locator('#toast-container')).toContainText('Scorciatoie salvate');

  // Every key used by the page exists in both dictionaries
  const missing = await page.evaluate(() => {
    const keys = new Set();
    document.querySelectorAll('[data-i18n]').forEach((el) => keys.add(el.getAttribute('data-i18n')));
    document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => keys.add(el.getAttribute('data-i18n-placeholder')));
    return [...keys].filter((k) => !TRANSLATIONS.it[k] || !TRANSLATIONS.en[k]);
  });
  expect(missing).toEqual([]);

  // Remembered after reload, and EN switches back
  await page.reload();
  await expect(page.locator('#connectionText')).toHaveText('Connesso');
  await expect(page.locator('#tab-match .card-title').first()).toHaveText('Controllo Punteggio');
  await page.getByRole('button', { name: 'EN', exact: true }).click();
  await expect(page.locator('#tab-match .card-title').first()).toHaveText('Score Controls');
  await expect(page.locator('#connectionText')).toHaveText('Connected');
});
