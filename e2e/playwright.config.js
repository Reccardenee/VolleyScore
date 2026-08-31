const { defineConfig } = require('@playwright/test');
const path = require('path');

const repoRoot = path.join(__dirname, '..');
const python =
  process.env.E2E_PYTHON ||
  (process.platform === 'win32'
    ? path.join(repoRoot, '.venv', 'Scripts', 'python.exe')
    : 'python3');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30000,
  retries: process.env.CI ? 2 : 1,
  workers: 1,
  reporter: [['list']],
  use: {
    baseURL: 'http://127.0.0.1:8130',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: {
    command: `"${python}" "${path.join(repoRoot, 'scorebug', 'server.py')}"`,
    url: 'http://127.0.0.1:8130/current',
    reuseExistingServer: !process.env.CI,
    timeout: 60000,
    env: {
      VOLLEYSCORE_PORT: '8130',
      VOLLEYSCORE_CONFIG: path.join(__dirname, '.tmp', 'config.json'),
      VOLLEYSCORE_LOG_DIR: path.join(__dirname, '.tmp', 'logs'),
    },
  },
});
