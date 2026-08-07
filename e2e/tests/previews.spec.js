const { test, expect } = require('@playwright/test');
const { openPanel, openTab } = require('./helpers');

const PREVIEWS = [
  ['#preview-scoreboard', '.containervolley', 500, 100, 'match'],
  ['#preview-sets', '.containervolley', 500, 150, 'match'],
  ['#preview-timer', '.timer-container', 200, 80, 'timer'],
  ['#preview-timeouts', '.timeout-container', 300, 100, 'timer'],
  ['#preview-history', '.history-container', 300, 150, 'timer'],
  ['#preview-formation', '.dual-wrapper', 500, 80, 'teams'],
];

for (const [frameId, selector, minW, minH, tab] of PREVIEWS) {
  test(`${frameId} preview renders the overlay scaled into the visible box`, async ({ page }) => {
    await page.request.post('/reset_config');
    await openPanel(page);

    // Previews on hidden tabs are re-measured when their tab is shown
    await openTab(page, tab);
    await page.waitForTimeout(1400);

    const frame = page.frameLocator(frameId);
    const content = frame.locator(selector).first();
    await content.waitFor({ state: 'visible', timeout: 10000 });

    const container = page.locator(frameId + '-container');
    const containerBox = await container.boundingBox();
    const box = await content.boundingBox();

    expect(box.width).toBeGreaterThanOrEqual(minW);
    expect(box.height).toBeGreaterThanOrEqual(minH);
    // Content is anchored at the container's origin, not shifted off-screen
    expect(box.x).toBeGreaterThanOrEqual(containerBox.x - 5);
    expect(box.y).toBeGreaterThanOrEqual(containerBox.y - 5);
  });
}