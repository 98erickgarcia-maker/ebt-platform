export default {
  testDir: "e2e",
  workers: 1,
  reporter: [
    ["list"],
    ["json", { outputFile: "../evidence/browser-results.json" }],
  ],
  use: { baseURL: "http://127.0.0.1:5197", headless: true },
  webServer: {
    command: "npm run dev",
    url: "http://127.0.0.1:5197",
    reuseExistingServer: true,
  },
};
