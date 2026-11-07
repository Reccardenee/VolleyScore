const { test, expect } = require('@playwright/test');
const { getState, openPanel, openTab, clickPlus, pointsRow } = require('./helpers');

test('team settings reach the overlays; formation shows the saved players', async ({ page }) => {
  await page.request.post('/reset_config');
  await openPanel(page);

  // Rename teams and set a player in the Teams tab
  await openTab(page, 'teams');
  await page.locator('#homeName').fill('Ribera');
  await page.locator('#awayName').fill('Sciacca');
  await page.locator('#homeP1').fill('John');
  await page.locator('#awayP1').fill('Marco');
  await page.getByRole('button', { name: 'Save Team Settings' }).click();

  await expect
    .poll(async () => (await getState(page.request)).homeName, { timeout: 5000 })
    .toBe('Ribera');
  await expect
    .poll(async () => (await getState(page.request)).homePlayers[0], { timeout: 5000 })
    .toBe('John');

  // The scoreboard overlay shows the new names
  const scoreboard = await page.context().newPage();
  await scoreboard.goto('/');
  await expect(scoreboard.locator('#team_1')).toHaveText('Ribera');
  await expect(scoreboard.locator('#team_2')).toHaveText('Sciacca');
  await scoreboard.close();

  // The dual formation overlay shows the saved players
  const formation = await page.context().newPage();
  await formation.goto('/dual_formation');
  await expect(formation.locator('body')).toContainText('John');
  await expect(formation.locator('body')).toContainText('Marco');
  await formation.close();
});

test('score history, timeouts and game reset work from the panel', async ({ page }) => {
  await page.request.post('/reset_config');
  await openPanel(page);

  // Four home points => four history rows (newest first)
  await clickPlus(page, 'home', 4);
  await expect(page.locator('#scoreHistoryList li')).toHaveCount(4);
  await expect(page.locator('#scoreHistoryList li').first()).toContainText('Home 4 - 0');

  // Timeouts decrement on the Match tab
  await page
    .locator('.timeout-team.home .timeout-btns')
    .getByRole('button', { name: '−', exact: true })
    .click();
  await expect(page.locator('#homeTimeoutCount')).toHaveText('(1/2)');
  await expect(page.locator('#homeTimeoutDots')).toHaveText('●○');
  await page.getByRole('button', { name: 'Reset Game' }).click();
  await page.getByRole('button', { name: 'Yes, Reset' }).click();
  await expect(page.locator('#summaryHomeScore')).toHaveText('0');
  await expect(page.locator('#summaryAwayScore')).toHaveText('0');
  await expect(page.locator('#summarySet')).toHaveText('1');
  await expect(page.locator('#scoreHistoryList li')).toContainText('No points scored yet');
});
