import { test, expect, chromium, type Page } from "@playwright/test";
import { reserveQaAuthOperation } from "./qa-auth-budget";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const root = path.resolve(process.cwd(), "../..");
const qa = JSON.parse(fs.readFileSync(path.join(root, "tmp/runtime/qa-access.json"), "utf8")) as { password: string };
const evidence = path.join(root, "tmp/e2e/visual-review");

async function readable(page: Page) {
  return page.evaluate(() => {
    const failures: string[] = [];
    for (const selector of [".page-heading h1", ".contact-card h2", ".next-action strong", ".task-row strong"]) {
      for (const node of document.querySelectorAll<HTMLElement>(selector)) {
        if (!node.getClientRects().length) continue;
        const range = document.createRange();
        range.selectNodeContents(node);
        const text = range.getBoundingClientRect();
        let left = 0, right = document.documentElement.clientWidth;
        for (let parent: HTMLElement | null = node; parent; parent = parent.parentElement) {
          if (parent === node || /hidden|clip/.test(getComputedStyle(parent).overflowX)) {
            const box = parent.getBoundingClientRect();
            left = Math.max(left, box.left); right = Math.min(right, box.right);
          }
        }
        if (text.left < left - 1 || text.right > right + 1) failures.push(selector);
      }
    }
    if (document.documentElement.scrollWidth > innerWidth + 1) failures.push("document overflow");
    return failures;
  });
}

test("FLOW AURA native browser zoom 200/400 percent, not CSS or viewport emulation", async () => {
  test.setTimeout(180_000);
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "ebt-native-zoom-"));
  const extension = path.join(temporary, "extension");
  fs.mkdirSync(extension);
  fs.mkdirSync(evidence, { recursive: true });
  // Test-only extension controls the browser's native zoom. No page code or CSP is changed.
  fs.writeFileSync(path.join(extension, "manifest.json"), JSON.stringify({
    manifest_version: 3, name: "EBT local QA zoom controller", version: "1.0.0",
    permissions: ["tabs"], host_permissions: ["http://127.0.0.1/*"],
    background: { service_worker: "worker.js" },
  }));
  fs.writeFileSync(path.join(extension, "worker.js"), "chrome.runtime.onInstalled.addListener(() => {});\n");
  const context = await chromium.launchPersistentContext(path.join(temporary, "profile"), {
    channel: "chromium", headless: true, viewport: null,
    timezoneId: "America/Sao_Paulo", locale: "pt-BR",
    args: ["--window-size=1280,1024", "--disable-extensions-except=" + extension, "--load-extension=" + extension],
  });
  try {
    const worker = context.serviceWorkers()[0] ?? await context.waitForEvent("serviceworker");
    const page = context.pages()[0] ?? await context.newPage();
    const errors: string[] = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.goto("http://127.0.0.1:5186/");
    expect(new URL(page.url()).hostname).toBe("127.0.0.1");
    await page.getByLabel("E-mail", { exact: true }).fill("admin@ebt.example");
    await page.getByLabel("Senha", { exact: true }).fill(qa.password);
    await reserveQaAuthOperation();
    await page.getByRole("button", { name: "Entrar", exact: true }).click();
    await page.getByRole("button", { name: "Acessar Connect", exact: true }).click();
    await expect(page.locator(".flow-aura-daily")).toBeVisible();
    await expect(page.locator(".loading-bar")).not.toBeVisible();
    const original = await page.evaluate(() => ({ width: innerWidth, dpr: devicePixelRatio }));
    const zoom = async (factor: number) => {
      const actual = await worker.evaluate(`(async () => {
        const tabs = await chrome.tabs.query({ url: 'http://127.0.0.1:5186/*' });
        if (tabs.length !== 1) throw new Error('Expected exactly one isolated QA tab');
        await chrome.tabs.setZoomSettings(tabs[0].id, {mode: 'automatic', scope: 'per-tab'});
        await chrome.tabs.setZoom(tabs[0].id, ${factor});
        return await chrome.tabs.getZoom(tabs[0].id);
      })()`);
      // Chromium represents 400 percent as 3.9999999999999996.
      expect(actual).toBeCloseTo(factor, 10);
      await expect.poll(() => page.evaluate(() => devicePixelRatio)).toBeCloseTo(original.dpr * factor, 1);
      const measured = await page.evaluate(() => ({ width: innerWidth, height: innerHeight, dpr: devicePixelRatio }));
      expect(Math.abs(measured.width - original.width / factor)).toBeLessThanOrEqual(2);
      console.log(JSON.stringify({ scenario: "native-browser-zoom", factor, actual, original, measured }));
    };
    for (const factor of [2, 4]) {
      await zoom(factor);
      expect.soft(await readable(page), "Daily native zoom " + factor).toEqual([]);
      await page.screenshot({ path: path.join(evidence, `audit-native-daily-${factor * 100}.png`), fullPage: true, animations: "disabled" });
    }
    await zoom(1);
    await page.locator(".flow-aura-daily .metrics > button").first().click();
    const marker = Date.now().toString();
    const name = "Zoom " + "Relacionamento".repeat(6) + marker;
    await page.getByRole("button", { name: "Novo contato", exact: true }).click();
    const dialog = page.getByRole("dialog");
    await dialog.getByLabel("Nome", { exact: true }).fill(name);
    await dialog.getByLabel("E-mail", { exact: true }).fill("zoom-" + marker + "@ebt.example");
    await dialog.getByRole("button", { name: "Salvar", exact: true }).click();
    await expect(dialog).not.toBeVisible();
    await page.getByLabel("Buscar contatos").fill(name);
    await page.getByRole("button", { name: "Abrir " + name, exact: true }).click();
    await expect(page.locator(".flow-contact-360")).toBeVisible();
    await expect(page.locator(".loading-bar")).not.toBeVisible();
    for (const factor of [2, 4]) {
      await zoom(factor);
      expect.soft(await readable(page), "Contact native zoom " + factor).toEqual([]);
      await page.screenshot({ path: path.join(evidence, `audit-native-contact-${factor * 100}.png`), fullPage: true, animations: "disabled" });
    }
    const opener = page.getByRole("button", { name: "Abrir navegação", exact: true });
    await opener.focus(); await page.keyboard.press("Enter");
    const nav = page.getByRole("navigation", { name: "Navegação principal" });
    await expect(nav.locator('[aria-current="page"]')).toBeFocused();
    const focusedBox = await nav.locator('[aria-current="page"]').evaluate(node => {
      const box = node.getBoundingClientRect();
      return { top: box.top, bottom: box.bottom, height: innerHeight };
    });
    console.log(JSON.stringify({ scenario: "native-400-focus-geometry", ...focusedBox }));
    await page.screenshot({ path: path.join(evidence, "audit-native-menu-focus-400.png"), animations: "disabled" });
    expect(focusedBox.top >= 0 && focusedBox.bottom <= focusedBox.height,
      "Focused navigation remains visible at native 400 percent zoom").toBe(true);
    await page.keyboard.press("Shift+Tab");
    await page.keyboard.press("Tab");
    await expect(nav.locator('[aria-current="page"]')).toBeFocused();
    await page.keyboard.press("Escape");
    await expect(opener).toBeFocused();
    await expect(page.locator("#ebt-sidebar-navigation")).toBeHidden();
    await page.keyboard.press("Enter");
    for (let n = 0; n < 12 && await page.locator("#ebt-sidebar-navigation").isVisible(); n++) {
      await page.keyboard.press("Tab");
      const returnedToTrigger = await page.locator(".mobile-menu").evaluate(node => node === document.activeElement);
      if (returnedToTrigger) {
        await expect(page.locator("#ebt-sidebar-navigation"), "Tab must not leave the trigger focused behind the open panel").toBeHidden();
        await expect(opener).toBeFocused();
      }
    }
    await expect(page.locator("#ebt-sidebar-navigation")).toBeHidden();
    expect.soft(errors, "No uncaught application errors").toEqual([]);
  } finally {
    await context.close();
    fs.rmSync(temporary, { recursive: true, force: true });
  }
});
