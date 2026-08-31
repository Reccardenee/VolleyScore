const { expect } = require('@playwright/test');

async function resetState(requestContext) {
  const res = await requestContext.post('/reset_config');
  if (res.status() !== 200) {
    throw new Error(`reset_config failed: ${res.status()}`);
  }
}

async function getState(requestContext) {
  const res = await requestContext.get('/current');
  if (res.status() !== 200) {
    throw new Error(`/current failed: ${res.status()}`);
  }
  return res.json();
}
// WARNING: never write `(await req.get(...)).json().field` - json() is async
// and `.field` would be read off the pending Promise (always undefined).

async function expectState(requestContext, matcher) {
  await expect
    .poll(() => getState(requestContext), { timeout: 5000, intervals: [250] })
    .toMatchObject(matcher);
}

async function openPanel(page) {
  await page.goto('/control_panel');
  await page.locator('#connectionText').filter({ hasText: 'Connected' }).waitFor({
    state: 'visible',
    timeout: 10000,
  });
}

async function openTab(page, tabName) {
  await page.locator(`.tab-btn[data-tab="${tabName}"]`).click();
}

function pointsRow(page, team) {
  return page
    .locator(`.team-score-control.${team} .score-row`)
    .filter({ hasText: 'Points' });
}

function setsRow(page, team) {
  return page
    .locator(`.team-score-control.${team} .score-row`)
    .filter({ hasText: 'Sets' });
}

async function clickPlus(page, team, times) {
  const plus = pointsRow(page, team).getByRole('button', { name: '+', exact: true });
  for (let i = 0; i < times; i++) {
    await plus.click();
  }
}

async function parseTimerSeconds(text) {
  const m = /(\d+):(\d+)/.exec(text || '');
  return m ? parseInt(m[1], 10) * 60 + parseInt(m[2], 10) : NaN;
}

module.exports = {
  resetState,
  getState,
  expectState,
  openPanel,
  openTab,
  pointsRow,
  setsRow,
  clickPlus,
  parseTimerSeconds,
};
