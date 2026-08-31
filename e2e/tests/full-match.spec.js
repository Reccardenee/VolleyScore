const { test, expect } = require('@playwright/test');
const { expectState, getState, openPanel, clickPlus } = require('./helpers');

test('plays a full match and syncs all overlays', async ({ page, request }) => {
  await page.request.post('/reset_config');
  await openPanel(page);

  await expect(page.locator('#summaryHomeName')).toHaveText('Home');
  await expect(page.locator('#summarySet')).toHaveText('1');

  // Set 1: home wins 25-20. Alternate rallies (home serve, away answer) so
  // the set completes exactly on the last point with no leftover clicks.
  for (let i = 0; i < 20; i++) {
    await clickPlus(page, 'home', 1);
    await clickPlus(page, 'away', 1);
  }
  await clickPlus(page, 'home', 5);

  // The server is authoritative: the set completes and both scores reset.
  // (The input box can briefly echo clicks still in flight, so we poll the API.)
  await expectState(request, { homeScore: 0, awayScore: 0, homeSets: 1, awaySets: 0, currentSet: 2 });
  await expect(page.locator('#summarySet')).toHaveText('2');
  await expect(page.locator('#posHome')).toHaveClass(/active/);

  // Set 2: home wins 25-18
  for (let i = 0; i < 18; i++) {
    await clickPlus(page, 'home', 1);
    await clickPlus(page, 'away', 1);
  }
  await clickPlus(page, 'home', 7);
  await expect(page.locator('#homeSets')).toHaveValue('2');
  await expect(page.locator('#summarySet')).toHaveText('3');

  // Set 3: home wins 25-16 by typing the scores directly. One input event
  // commits both values through the debounced sender (typing both fields
  // quickly can fire two sends, and the stale second send could regress the
  // set counters server-side).
  await page.locator('#homeScore').evaluate((el) => {
    el.value = '25';
    document.getElementById('awayScore').value = '16';
    el.dispatchEvent(new Event('input'));
  });
  await page.waitForTimeout(600);
  await expect(page.locator('#homeSets')).toHaveValue('3');
  await expect(page.locator('#summarySet')).toHaveText('4');

  // The live scoreboard overlay reflects the match state
  const overlay = await page.context().newPage();
  await overlay.goto('/');
  await expect(overlay.locator('#points_1')).toHaveText('0');
  await expect(overlay.locator('#points_2')).toHaveText('0');
  await expect(overlay.locator('#set_1')).toHaveText('3');
  await expect(overlay.locator('#set_2')).toHaveText('0');
  await overlay.close();

  // The All Sets overlay records every set
  const sets = await page.context().newPage();
  await sets.goto('/scorebug_sets');
  await expect(sets.locator('#home_set_1')).toHaveText('25');
  await expect(sets.locator('#away_set_1')).toHaveText('20');
  await expect(sets.locator('#home_set_2')).toHaveText('25');
  await expect(sets.locator('#away_set_2')).toHaveText('18');
  await expect(sets.locator('#home_set_3')).toHaveText('25');
  await expect(sets.locator('#away_set_3')).toHaveText('16');
  await sets.close();

  // Full point-by-point history records every posted point: set 1 (25+20)
  // + set 2 (25+18) clicked points = 88 entries, plus the single typed
  // commit that finished set 3 (25-16) = 89. Typed score jumps only
  // record the committed state, not the skipped intermediate points.
  await expect
    .poll(async () => (await getState(page.request)).scoreHistory.length, {
      timeout: 5000,
    })
    .toBe(89);
});
