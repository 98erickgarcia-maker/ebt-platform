import { test, expect } from "@playwright/test";
import { reserveQaAuthOperation } from "./qa-auth-budget";
import fs from "node:fs";
import path from "node:path";
const root = path.resolve(process.cwd(), "../..");
const qa = JSON.parse(fs.readFileSync(path.join(root, "tmp/runtime/qa-access.json"), "utf8"));

async function enter(page: import("@playwright/test").Page) {
  await page.goto("/");
  await page.getByLabel("E-mail", { exact: true }).fill("admin@ebt.example");
  await page.getByLabel("Senha", { exact: true }).fill(qa.password);
  await reserveQaAuthOperation();
  await page.getByRole("button", { name: "Entrar", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Aplicativos", exact: true })).toBeVisible({ timeout:20000 });
  await expect(page.getByRole("button", { name: "Acessar Connect", exact: true })).toBeVisible();
}
test("Platform groups Connect and planned apps; reload and tenant switch preserve authorized catalog", async ({page}) => {
  const errors: string[] = []; page.on("pageerror", e => errors.push(e.message));
  await enter(page);
  await expect(page.locator(".application-card")).toHaveCount(9);
  await expect(page.locator('[data-application="flow"]')).toContainText("Planejado");
  await expect(page.locator('[data-application="flow"] button')).toHaveCount(0);
  await page.getByRole("button", { name:"Acessar Connect", exact:true }).click();
  await expect(page.getByRole("heading", {name:"Meu dia", exact:true})).toBeVisible();
  await page.getByRole("button", {name:"Aplicativos",exact:true}).click();
  await page.reload();
  await expect(page.locator(".application-card")).toHaveCount(9);
  const current = await (await page.request.get("/api/auth/me")).json();
  const target = current.tenantId === qa.tenantA ? qa.tenantB : qa.tenantA;
  await page.getByLabel("Empresa", {exact:true}).selectOption(target);
  await expect(page.getByText("Empresa selecionada.", {exact:true})).toBeVisible();
  await expect(page.locator(".application-card")).toHaveCount(9);
  const catalog = await (await page.request.get("/api/platform/v1/applications")).json();
  expect(catalog.tenantId).toBe(target);
  expect(errors).toEqual([]);
  await page.screenshot({path:path.join(root,"tmp/platform-release/platform-desktop.png"),fullPage:true});
});
test("Platform is usable on mobile without horizontal overflow", async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  await enter(page);
  await expect(page.locator('[data-application="connect"]')).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({path:path.join(root,"tmp/platform-release/platform-mobile.png"),fullPage:true});
  await page.getByRole("button", {name:"Acessar Connect",exact:true}).click();
  await expect(page.getByRole("heading", {name:"Meu dia",exact:true})).toBeVisible();
});
test("Catalog error exposes retry; successful retry restores real applications", async ({page}) => {
  let failed = true;
  await page.route("**/api/platform/v1/applications", async r => failed ? r.fulfill({status:503,contentType:"application/problem+json",body:JSON.stringify({code:"service_unavailable",title:"Falha simulada do catalogo"})}) : r.continue());
  await page.goto("/");await page.getByLabel("E-mail",{exact:true}).fill("admin@ebt.example");await page.getByLabel("Senha",{exact:true}).fill(qa.password);
  await reserveQaAuthOperation();await page.getByRole("button",{name:"Entrar",exact:true}).click();
  await expect(page.getByRole("alert")).toContainText("Falha simulada");
  failed=false;await page.getByRole("button",{name:"Tentar novamente",exact:true}).click();
  await expect(page.locator(".application-card")).toHaveCount(9);
});

test("Platform navigation stays accessible across breakpoints and mobile menu state", async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  await enter(page);

  for (const width of [320, 390, 768, 1366]) {
    await page.setViewportSize({width,height:844});
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
      "No document-wide horizontal overflow at " + width + "px"
    ).toBe(true);
  }

  await page.setViewportSize({width:390,height:844});
  const sidebar = page.locator("#ebt-sidebar-navigation");
  const open = page.getByRole("button", {name:"Abrir navegação"});
  await expect(open).toHaveAttribute("aria-expanded", "false");
  await expect(open).toHaveAttribute("aria-controls", "ebt-sidebar-navigation");
  await expect(sidebar).toBeHidden();

  await open.click();
  const close = page.getByRole("button", {name:"Fechar navegação"});
  await expect(close).toHaveAttribute("aria-expanded", "true");
  const nav = page.getByRole("navigation", {name:"Navegação principal"});
  await expect(nav).toBeVisible();

  await page.keyboard.press("Escape");
  await expect(sidebar).toBeHidden();
  await expect(open).toBeFocused();
  await expect(open).toHaveAttribute("aria-expanded", "false");

  await open.click();
  await nav.getByRole("button", {name:"Meu dia",exact:true}).click();
  await expect(page.getByRole("heading", {name:"Meu dia",exact:true})).toBeVisible();
  await expect(sidebar).toBeHidden();
  await expect(open).toBeFocused();

  await open.click();
  await nav.getByRole("button", {name:"Aplicativos",exact:true}).click();
  await expect(page.getByRole("heading", {name:"Aplicativos",exact:true})).toBeVisible();
  await expect(page.getByRole("button", {name:"Acessar Connect",exact:true})).toBeVisible();
});
