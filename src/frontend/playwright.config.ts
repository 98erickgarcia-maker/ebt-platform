import { defineConfig } from "@playwright/test";
const qaPort = process.env.EBT_QA_PORT ?? "5186";
if (!/^\d+$/.test(qaPort) || Number(qaPort) < 1024 || Number(qaPort) > 65535)
  throw new Error("Porta localhost de QA inválida.");
const qaUrl = `http://127.0.0.1:${qaPort}`;
export default defineConfig({
  testDir: "./e2e",
  workers: 1,
  fullyParallel: false,
  timeout: 45000,
  webServer: {
    command: `${process.platform === "win32" ? "powershell" : "pwsh"} -NoProfile -File "../../scripts/Start-Local.ps1" -Port ${qaPort}`,
    url: `${qaUrl}/health/ready`,
    reuseExistingServer: true,
    timeout: 120000,
  },
  outputDir: "../../tmp/e2e/artifacts",
  reporter: [
    ["list"],
    ["json", { outputFile: "../../evidencias/testes_connect_browser.json" }],
  ],
  use: {
    baseURL: qaUrl,
    headless: true,
    timezoneId: "America/Sao_Paulo",
    viewport: { width: 1440, height: 1000 },
    trace: "off",
    screenshot: "only-on-failure",
  },
});
