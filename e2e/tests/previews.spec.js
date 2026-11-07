const { test, expect } = require('@playwright/test');
const { openPanel, openTab } = require('./helpers');

// Content selectors inside each preview iframe (1920px layout space)
const PREVIEWS = [
  ['#preview-scoreboard', '.containervolley', 'match'],
  ['#preview-sets', '.containervolley', 'match'],
  ['#preview-timer', '.timer-container', 'match'],
  ['#preview-timeouts', '.timeout-container', 'match'],
  ['#preview-history', '.history-container', 'match'],
  ['#preview-formation', '.dual-wrapper', 'teams'],
];

for (const [frameId, selector, tab] of PREVIEWS) {
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

    // Scaled content fills the visible box (no blowout, no tiny thumbnail),
    // whatever the panel width - the box tracks the container's dimensions
    expect(box.width).toBeGreaterThanOrEqual(containerBox.width * 0.95);
    expect(box.height).toBeGreaterThanOrEqual(containerBox.height * 0.8);
    // Content is anchored at the container's origin, not shifted off-screen
    expect(box.x).toBeGreaterThanOrEqual(containerBox.x - 5);
    expect(box.y).toBeGreaterThanOrEqual(containerBox.y - 5);
  });
}