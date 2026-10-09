import { test, expect, type Page } from "@playwright/test";
import { reserveQaAuthOperation } from "./qa-auth-budget";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(process.cwd(), "../..");
const qa = JSON.parse(fs.readFileSync(path.join(root, "tmp/runtime/qa-access.json"), "utf8")) as {
  password: string; tenantA: string;
};
const evidence = path.join(root, "tmp/e2e/visual-review");

test.setTimeout(180_000);

async function enter(page: Page) {
  await page.goto("/");
  expect(["127.0.0.1", "localhost"]).toContain(new URL(page.url()).hostname);
  await page.getByLabel("E-mail", { exact: true }).fill("admin@ebt.example");
  await page.getByLabel("Senha", { exact: true }).fill(qa.password);
  await reserveQaAuthOperation();
  await page.getByRole("button", { name: "Entrar", exact: true }).click();
  await page.getByRole("button", { name: "Acessar Connect", exact: true }).click();
  await expect(page.locator(".flow-aura-daily")).toBeVisible();
  await expect(page.locator(".loading-bar")).not.toBeVisible();
  const me = await (await page.request.get("/api/auth/me")).json();
  if (me.tenantId !== qa.tenantA) {
    await page.getByLabel("Empresa", { exact: true }).selectOption(qa.tenantA);
    await expect(page.getByText("Empresa selecionada.", { exact: true })).toBeVisible();
    await expect(page.locator(".loading-bar")).not.toBeVisible();
  }
  fs.mkdirSync(evidence, { recursive: true });
}

async function capture(page: Page, name: string) {
  await page.screenshot({ path: path.join(evidence, "audit-" + name + ".png"), fullPage: true, animations: "disabled" });
}

async function clipping(page: Page) {
  return page.evaluate(() => {
    const findings: string[] = [];
    const selectors = [".page-heading h1", ".contact-card h2", ".next-action strong", ".task-row strong"];
    for (const selector of selectors) {
      document.querySelectorAll<HTMLElement>(selector).forEach((node, index) => {
        if (!node.getClientRects().length) return;
        const range = document.createRange();
        range.selectNodeContents(node);
        const text = range.getBoundingClientRect();
        let left = 0, right = document.documentElement.clientWidth;
        for (let parent: HTMLElement | null = node; parent; parent = parent.parentElement) {
          if (parent === node || /hidden|clip/.test(getComputedStyle(parent).overflowX)) {
            const box = parent.getBoundingClientRect();
            left = Math.max(left, box.left);
            right = Math.min(right, box.right);
          }
        }
        if (text.left < left - 1 || text.right > right + 1) {
          findings.push(`${selector}[${index}]: text ${Math.round(text.left)}..${Math.round(text.right)}, visible ${Math.round(left)}..${Math.round(right)}`);
        }
      });
    }
    if (document.documentElement.scrollWidth > window.innerWidth + 1) {
      findings.push(`document overflow ${document.documentElement.scrollWidth}/${window.innerWidth}`);
    }
    return findings;
  });
}

test("FLOW AURA audit: persisted long text, spacing and 200 percent text resize", async ({ page }) => {
  const runtimeErrors: string[] = [];
  page.on("pageerror", error => runtimeErrors.push(error.message));
  await page.setViewportSize({ width: 1366, height: 900 });
  await enter(page);
  await page.locator(".flow-aura-daily .metrics > button").first().click();
  const marker = Date.now().toString();
  const name = "Ana " + "Relacionamento".repeat(6) + marker;
  const task = "Acompanhar".repeat(9) + marker;
  await page.getByRole("button", { name: "Novo contato", exact: true }).click();
  let dialog = page.getByRole("dialog");
  await dialog.getByLabel("Nome", { exact: true }).fill(name);
  await dialog.getByLabel("E-mail", { exact: true }).fill("audit-" + marker + "@ebt.example");
  await dialog.getByRole("button", { name: "Salvar", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await page.getByLabel("Buscar contatos").fill(name);
  await page.getByRole("button", { name: "Abrir " + name, exact: true }).click();
  await expect(page.getByRole("heading", { name, level: 1 })).toBeVisible();
  const contactId = await page.locator(".contact-card dd.mono").innerText();
  await page.getByRole("button", { name: "Registrar nota", exact: true }).click();
  dialog = page.getByRole("dialog");
  await dialog.getByLabel("Conteúdo da nota").fill("Nota sintética: " + "Rastreabilidade".repeat(15));
  await dialog.getByRole("button", { name: "Salvar", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await page.getByRole("button", { name: "Nova tarefa", exact: true }).click();
  dialog = page.getByRole("dialog");
  await dialog.getByLabel("Próximo passo", { exact: true }).fill(task);
  await dialog.getByLabel("Prazo", { exact: true }).fill("2026-10-12T10:00");
  await dialog.getByRole("button", { name: "Salvar", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await expect(page.locator(".contact-card dd.mono")).toHaveText(contactId);
  await expect(page.locator(".contact-360-facts")).toContainText("Previsto para");

  for (const width of [320, 390, 768, 1366]) {
    await page.setViewportSize({ width, height: 900 });
    const found = await clipping(page);
    console.log(JSON.stringify({ scenario: "long-persisted-text", width, found }));
    await capture(page, "long-contact-" + width);
    expect.soft(found, "Contact text must not be clipped at " + width + "px").toEqual([]);
  }
  await page.setViewportSize({ width: 390, height: 844 });
  const spacing = await page.addStyleTag({ content: "main * { line-height:1.5 !important; letter-spacing:.12em !important; word-spacing:.16em !important; } main p { margin-bottom:2em !important; }" });
  const spaced = await clipping(page);
  console.log(JSON.stringify({ scenario: "text-spacing", found: spaced }));
  await capture(page, "text-spacing-390");
  expect.soft(spaced, "User text spacing must not clip information").toEqual([]);
  await spacing.evaluate(node => node.remove());

  // Text-only enlargement, deliberately NOT labelled native browser zoom.
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.evaluate(() => {
    const nodes = Array.from(document.querySelectorAll<HTMLElement>("main *"));
    const sizes = nodes.map(node => parseFloat(getComputedStyle(node).fontSize));
    nodes.forEach((node, index) => node.style.setProperty("font-size", sizes[index] * 2 + "px", "important"));
  });
  const enlarged = await clipping(page);
  console.log(JSON.stringify({ scenario: "text-only-200-percent", found: enlarged }));
  await capture(page, "text-200-percent");
  expect.soft(enlarged, "200 percent text must not clip information").toEqual([]);
  expect.soft(runtimeErrors, "No uncaught application errors").toEqual([]);
});

test("FLOW AURA audit: forward keyboard menu and printable operational values", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await enter(page);
  const open = page.getByRole("button", { name: "Abrir navegação", exact: true });
  await open.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("navigation", { name: "Navegação principal" })).toBeVisible();
  const focusedInNav = () => page.evaluate(() => !!document.activeElement?.closest("#ebt-sidebar-navigation nav"));
  let reached = await focusedInNav();
  const sequence: string[] = [];
  for (let step = 0; step < 3 && !reached; step++) {
    await page.keyboard.press("Tab");
    sequence.push(await page.evaluate(() => document.activeElement?.getAttribute("aria-label") || document.activeElement?.textContent?.trim() || "unknown"));
    reached = await focusedInNav();
  }
  console.log(JSON.stringify({ scenario: "mobile-forward-tab", reached, sequence }));
  await capture(page, "mobile-keyboard-focus");
  expect.soft(reached, "Opening navigation should reach its items without traversing unrelated main content").toBe(true);
  await page.keyboard.press("Escape");
  await expect(open).toBeFocused();
  await expect(page.locator("#ebt-sidebar-navigation")).toBeHidden();

  await page.setViewportSize({ width: 1366, height: 900 });
  const metrics = page.locator(".flow-aura-daily .metrics > button");
  await expect(metrics).toHaveCount(4);
  await page.emulateMedia({ media: "print" });
  for (let index = 0; index < 4; index++) {
    expect.soft(await metrics.nth(index).isVisible(), "Printed operational metric " + index + " must remain visible").toBe(true);
  }
  await capture(page, "daily-print");
  await page.emulateMedia({ media: "screen" });
});
