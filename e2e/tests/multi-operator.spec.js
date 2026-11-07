const { test, expect } = require('@playwright/test');
const { openPanel, openTab, clickPlus, expectState } = require('./helpers');

test('a point scored by another operator does not wipe unsaved edits', async ({ browser, request }) => {
  await request.post('/reset_config');
  const ctxA = await browser.newContext();
  const ctxB = await browser.newContext();
  const a = await ctxA.newPage();
  const b = await ctxB.newPage();
  await openPanel(a);
  await openPanel(b);

  // Operator A edits team settings and remaps a shortcut, without saving
  await openTab(a, 'teams');
  await a.locator('#homeName').fill('Draft Name');
  await a.locator('#homeP1').fill('Rossi');
  await a.locator('#homeColorPrimary').evaluate((el) => {
    el.value = '#123456';
    el.dispatchEvent(new Event('input', { bubbles: true }));
  });
  await a.locator('#homeP2').focus(); // A is still typing
  await openTab(a, 'settings');
  await a.locator('.shortcut-bind[data-action="timer_toggle"]').click();
  await a.keyboard.press('q');
  await expect(a.locator('.shortcut-bind[data-action="timer_toggle"]')).toHaveText('Q');
  await openTab(a, 'teams');

  // Operator B scores: A receives the live update...
  await clickPlus(b, 'home', 1);
  await expect(a.locator('#summaryHomeScore')).toHaveText('1');

  // ...but A's unsaved edits survive
  await expect(a.locator('#homeName')).toHaveValue('Draft Name');
  await expect(a.locator('#homeP1')).toHaveValue('Rossi');
  await expect(a.locator('#homeColorPrimary')).toHaveValue('#123456');
  await expect(a.locator('.shortcut-bind[data-action="timer_toggle"]')).toHaveText('Q');

  // Once A saves, the server has A's values and B sees them
  await a.getByRole('button', { name: 'Save Team Settings' }).click();
  await expectState(request, { homeName: 'Draft Name', homePlayers: ['Rossi', '', '', '', '', ''] });
  await openTab(b, 'teams');
  await expect(b.locator('#homeName')).toHaveValue('Draft Name');

  // After saving, A follows server updates again
  await request.post('/update', { form: { homeName: 'From B' } });
  await expect(a.locator('#homeName')).toHaveValue('From B');

  await ctxA.close();
  await ctxB.close();
});

test('a score being typed survives a remote update, then the server wins', async ({ browser, request }) => {
  await request.post('/reset_config');
  const ctxA = await browser.newContext();
  const a = await ctxA.newPage();
  await openPanel(a);

  // A is typing 12 for home (not yet sent: 350 ms debounce) when another
  // operator scores for away: neither value may be lost
  await a.locator('#homeScore').fill('12');
  await request.post('/update', { form: { awayScore: '5' } });
  await expectState(request, { homeScore: 12, awayScore: 5 });
  await expect(a.locator('#awayScore')).toHaveValue('5');

  // Once sent, the (still focused) input follows the server again
  await request.post('/update', { form: { homeScore: '13' } });
  await expect(a.locator('#homeScore')).toHaveValue('13');
  await ctxA.close();
});
