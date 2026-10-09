import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  workers: 1,
  fullyParallel: false,
  timeout: 45000,
  webServer: {
    command:
      process.platform === "win32"
        ? 'powershell -NoProfile -File "../../scripts/Start-Local.ps1"'
        : "dotnet run --no-build -c Release --project ../../src/backend/Ebt.Platform.Api --urls http://127.0.0.1:5186",
    url: "http://127.0.0.1:5186/health/ready",
    reuseExistingServer: true,
    timeout: 120000,
  },
  outputDir: "../../tmp/e2e/artifacts",
  reporter: [
    ["list"],
    ["json", { outputFile: "../../evidencias/testes_connect_browser.json" }],
  ],
  use: {
    baseURL: "http://127.0.0.1:5186",
    headless: true,
    timezoneId: "America/Sao_Paulo",
    viewport: { width: 1440, height: 1000 },
    trace: "off",
    screenshot: "only-on-failure",
  },
});
