const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './e2e',
  timeout: 120000,
  retries: 1,
  use: {
    baseURL: 'http://127.0.0.1:8080',
    headless: true,
    trace: 'on-first-retry',
  },
  webServer: [
    {
      command: '.\\.venv\\Scripts\\python app.py',
      cwd: '../backend',
      url: 'http://127.0.0.1:5000/api/models',
      reuseExistingServer: true,
      timeout: 120000,
      env: {
        FLASK_DEBUG: 'False',
        FLASK_PORT: '5000',
      },
    },
    {
      command: 'npm run serve -- --port 8080',
      cwd: '.',
      url: 'http://127.0.0.1:8080',
      reuseExistingServer: true,
      timeout: 120000,
    },
  ],
});
