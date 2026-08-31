const { test, expect } = require('@playwright/test');
const { openPanel, openTab, expectState } = require('./helpers');

test('keyboard drives points, possession and the timer', async ({ page, request }) => {
  await page.request.post('/reset_config');
  await openPanel(page);

  // Home +1 / Away +1
  await page.keyboard.press('1');
  await page.keyboard.press('2');
  await expectState(request, { homeScore: 1, awayScore: 1 });

  // Scoring auto-sets possession; Space cycles none -> home -> away -> none
  await expectState(request, { possession: 'away' });
  await page.keyboard.press(' ');
  await expectState(request, { possession: 'none' });
  await page.keyboard.press(' ');
  await expectState(request, { possession: 'home' });

  // Shift+1 / Shift+2 undo points
  await page.keyboard.press('Shift+2');
  await expectState(request, { awayScore: 0 });

  // T starts the timer, Shift+T resets it
  await page.keyboard.press('t');
  await expectState(request, { timerStarted: true });
  await page.keyboard.press('Shift+t');
  await expectState(request, { timerStarted: false });
});

test('overlay toggles work from the keyboard and paint their buttons', async ({ page, request }) => {
  await page.request.post('/reset_config');
  await openPanel(page);

  await page.keyboard.press('Control+1');
  await expectState(request, { overlayVisibility: { scorebug_sets: true } });
  await expect(page.locator('#overlayToggleSets')).toHaveClass(/btn-primary/);

  await page.keyboard.press('Control+1');
  await expectState(request, { overlayVisibility: { scorebug_sets: false } });

  await page.keyboard.press('Control+2');
  await expectState(request, { overlayVisibility: { timer: true } });
  await page.keyboard.press('Control+2');
  await expectState(request, { overlayVisibility: { timer: false } });
});

test('shortcuts can be remapped in Settings and the new key works', async ({ page, request }) => {
  await page.request.post('/reset_config');
  await openPanel(page);

  await openTab(page, 'settings');
  const bind = page.locator('.shortcut-bind[data-action="away_point_plus"]');
  await bind.click();
  await page.keyboard.press('9');
  await expect(bind).toHaveText('9');
  await page.getByRole('button', { name: 'Apply Shortcuts' }).click();

  // The remapped key now scores for away
  await openTab(page, 'match');
  await page.keyboard.press('9');
  await expectState(request, { awayScore: 1 });

  // The original key no longer scores for away
  await page.keyboard.press('2');
  await expectState(request, { awayScore: 1 });
});

test('duplicate combos are rejected when remapping', async ({ page }) => {
  await page.request.post('/reset_config');
  await openPanel(page);

  await openTab(page, 'settings');
  const home = page.locator('.shortcut-bind[data-action="home_point_plus"]');
  await home.click();
  await page.keyboard.press('2'); // away_point_plus already uses "2"
  await expect(page.locator('#toast-container')).toContainText('Key already used by');
  await expect(home).toHaveText('1');
});

test('shortcuts are ignored while typing in an input', async ({ page, request }) => {
  await page.request.post('/reset_config');
  await openPanel(page);

  await openTab(page, 'teams');
  await page.locator('#homeName').fill('X');
  await page.getByRole('button', { name: 'Save Team Settings' }).click();
  await expectState(request, { homeName: 'X' });

  // Focus stays in the input: "1" must type into the field, not score a point
  await page.locator('#homeName').focus();
  await page.keyboard.type('Y');
  await expect(page.locator('#homeName')).toHaveValue('XY');
  await page.keyboard.press('1');
  await expect(page.locator('#homeName')).toHaveValue('XY1');
  await expectState(request, { homeScore: 0, homeName: 'X' });
});