const { test, expect } = require('@playwright/test');
const { openPanel, clickPlus } = require('./helpers');

test('set 5 completed at 15-13 shows the final score in the All Sets overlay', async ({ page }) => {
  await page.request.post('/reset_config');
  await openPanel(page);

  // Reach a 3-3 set count so the match goes to the tie-break set 5
  await page.locator('#homeSets').fill('3');
  await page.locator('#homeSets').blur();
  await expect(page.locator('#summarySet')).toHaveText('4');

  await page.locator('#awaySets').fill('3');
  await page.locator('#awaySets').blur();
  await expect(page.locator('#summarySet')).toHaveText('5');

  // Play set 5: home wins 15-13 with the + buttons (alternate, end exactly at 15)
  for (let i = 0; i < 13; i++) {
    await clickPlus(page, 'home', 1);
    await clickPlus(page, 'away', 1);
  }
  await clickPlus(page, 'home', 2);

  await expect(page.locator('#homeScore')).toHaveValue('0');
  await expect(page.locator('#awayScore')).toHaveValue('0');
  await expect(page.locator('#homeSets')).toHaveValue('4');
  await expect(page.locator('#awaySets')).toHaveValue('3');

  // Regression: the completed set 5 must display 15-13, not 0-0
  const sets = await page.context().newPage();
  await sets.goto('/scorebug_sets');
  await expect(sets.locator('#home_set_5')).toHaveText('15');
  await expect(sets.locator('#away_set_5')).toHaveText('13');
  await expect(sets.locator('#home_set_4')).toHaveText('0');
  await expect(sets.locator('#away_set_4')).toHaveText('0');
  await sets.close();

  // The match ends with the tie-break; the current set stays at 5
  const overlay = await page.context().newPage();
  await overlay.goto('/');
  await expect(overlay.locator('#set_1')).toHaveText('4');
  await expect(overlay.locator('#set_2')).toHaveText('3');
  await expect(overlay.locator('#points_1')).toHaveText('0');
  await overlay.close();
});
