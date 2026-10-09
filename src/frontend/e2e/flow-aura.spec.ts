import { test, expect } from "@playwright/test";
import { reserveQaAuthOperation } from "./qa-auth-budget";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(process.cwd(), "../..");
const qa = JSON.parse(
  fs.readFileSync(path.join(root, "tmp/runtime/qa-access.json"), "utf8"),
) as { password: string };

test("FLOW + AURA mantém navegação, Contato 360 e reflow 320/390/768/1366", async ({ page }) => {
  await page.setViewportSize({ width: 1366, height: 900 });
  await page.goto("/");
  await page.getByLabel("E-mail", { exact: true }).fill("admin@ebt.example");
  await page.getByLabel("Senha", { exact: true }).fill(qa.password);
  await reserveQaAuthOperation();
  await page.getByRole("button", { name: "Entrar", exact: true }).click();
  await page.getByRole("button", { name: "Acessar Connect", exact: true }).click();

  await expect(page.locator(".flow-aura-daily")).toBeVisible();
  await expect(page.locator(".flow-aura-daily .metrics > button")).toHaveCount(4);
  await expect(page.getByRole("button", { name: /Ver minha agenda/ })).toBeVisible();
  for (const width of [320, 390, 768, 1366]) {
    await page.setViewportSize({ width, height: 900 });
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
      "Meu dia sem rolagem horizontal global em " + width + "px",
    ).toBe(true);
  }

  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator(".flow-aura-daily .metrics > button").first().click();
  await expect(page.getByRole("heading", { name: "Relacionamentos", exact: true })).toBeVisible();
  await page.getByLabel("Buscar contatos").fill("Contato Exemplo A");
  await page.getByRole("button", { name: /Contato Exemplo A contato@cliente.example/ }).click();
  await expect(page.getByRole("heading", { name: "Contato Exemplo A", level: 1 })).toBeVisible();
  await expect(page.getByRole("region", { name: "Panorama do contato" })).toBeVisible();
  await expect(page.locator(".detail-grid.flow-contact-360")).toBeVisible();

  for (const width of [320, 390, 768, 1366]) {
    await page.setViewportSize({ width, height: 900 });
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
      "Contato 360 sem rolagem horizontal global em " + width + "px",
    ).toBe(true);
  }

  await page.getByRole("button", { name: /Voltar aos relacionamentos/ }).click();
  await expect(page.getByLabel("Buscar contatos")).toHaveValue("Contato Exemplo A");
});
