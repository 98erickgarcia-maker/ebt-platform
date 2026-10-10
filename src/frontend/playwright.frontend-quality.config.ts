import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './e2e', testMatch: 'frontend-quality.spec.ts', workers: 1,
  timeout: 15000, reporter: 'list', outputDir: '../../tmp/frontend-quality',
  webServer: {command: 'node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5187 --strictPort', url:'http://127.0.0.1:5187', reuseExistingServer:false, timeout:20000},
  use: {baseURL:'http://127.0.0.1:5187', headless:true, viewport:{width:1440,height:900}},
});
