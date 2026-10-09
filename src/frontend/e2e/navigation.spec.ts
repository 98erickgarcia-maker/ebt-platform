import { reserveQaAuthOperation } from "./qa-auth-budget";
import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(process.cwd(), "../..");
const qa = JSON.parse(
  fs.readFileSync(path.join(root, "tmp/runtime/qa-access.json"), "utf8"),
) as { password: string };

test("Current page navigation during loading completes the replacement request", async ({
  page,
}) => {
  let release!: () => void;
  let markStarted!: () => void;
  const held = new Promise<void>((resolve) => {
    release = resolve;
  });
  const started = new Promise<void>((resolve) => {
    markStarted = resolve;
  });
  let first = true;
  await page.route("**/api/connect/v1/summary", async (request) => {
    if (first) {
      first = false;
      markStarted();
      await held;
    }
    await request.continue();
  });
  try {
    await page.goto("/");
    await page
      .getByLabel("E-mail", { exact: true })
      .fill("operador@ebt.example");
    await page.getByLabel("Senha", { exact: true }).fill(qa.password);
    await reserveQaAuthOperation();
    await page.getByRole("button", { name: "Entrar", exact: true }).click();
  await page.getByRole("button", { name: "Acessar Connect", exact: true }).click();
    await started;
    await expect(page.locator(".loading-bar")).toBeVisible();
    await page
      .getByRole("navigation", { name: "Navegação principal" })
      .getByRole("button", { name: "Meu dia", exact: true })
      .click();
    release();
    await expect(page.locator(".loading-bar")).not.toBeVisible({
      timeout: 4000,
    });
    await expect(
      page.getByRole("button", { name: "Atualizar", exact: true }),
    ).toBeEnabled();
    await expect(
      page.getByRole("heading", { name: "Meu dia", exact: true }),
    ).toBeVisible();
  } finally {
    release();
  }
});
