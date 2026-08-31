const { test, expect } = require('@playwright/test');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { openPanel, clickPlus } = require('./helpers');

test('export match downloads valid JSON and CSV with the match data', async ({ page }) => {
  await page.request.post('/reset_config');
  await openPanel(page);

  await clickPlus(page, 'home', 2);
  await expect(page.locator('#summaryHomeScore')).toHaveText('2');

  await page.goto('/export_match');

  const jsonDownload = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Download as JSON' }).click();
  const jsonFile = await jsonDownload;
  const jsonPath = path.join(os.tmpdir(), 'volleyscore-e2e-export.json');
  await jsonFile.saveAs(jsonPath);
  const data = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
  expect(data.homeTeam).toBe('Home');
  expect(data.awayTeam).toBe('Away');
  expect(data.finalScore).toEqual({ homeSets: 0, awaySets: 0, homePoints: 2, awayPoints: 0 });
  expect(data.scoreHistory.length).toBe(2);

  const csvDownload = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Download as CSV' }).click();
  const csvFile = await csvDownload;
  const csvPath = path.join(os.tmpdir(), 'volleyscore-e2e-export.csv');
  await csvFile.saveAs(csvPath);
  const csv = fs.readFileSync(csvPath, 'utf8').trim().split('\n');
  expect(csv.length).toBe(3);
  expect(csv[0]).toBe('Point,Home Score,Away Score,Scoring Team');
  expect(csv[2]).toContain('2,2,0');
});
