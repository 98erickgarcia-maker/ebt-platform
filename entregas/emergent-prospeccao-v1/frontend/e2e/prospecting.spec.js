import { test, expect } from "@playwright/test";

test("salva automação e prepara e-mail do contato sintético", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByRole("button", { name: "Prospecção automática", exact: true })
    .click();
  await page.getByLabel("Nome da automação").fill("TI SP");
  await page.getByLabel("UF", { exact: true }).fill("SP");
  await page.getByRole("button", { name: "Salvar automação" }).click();
  await expect(page.getByText("TI SP", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Contatos", exact: true }).click();
  await page.getByRole("button", { name: /Empresa Exemplo A/ }).click();
  await expect(
    page.getByRole("heading", { name: "Empresa Exemplo A" }),
  ).toBeVisible();
  await page.getByLabel("Seu nome para assinatura").fill("Erick");
  await page.getByRole("button", { name: "Preparar e-mail" }).click();
  await expect(
    page.getByText("Para: comercial-a@example.com", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Agendar rascunho no Outlook" }),
  ).toBeVisible();
});

test("template WhatsApp manual abre texto aprovado e registra preparação", async ({
  page,
  context,
}) => {
  await context.route("https://wa.me/**", (route) =>
    route.fulfill({
      contentType: "text/html",
      body: "<p>WhatsApp simulado: sem envio</p>",
    }),
  );
  await page.goto("/");
  await page.getByRole("button", { name: "Contatos", exact: true }).click();
  await page.getByRole("button", { name: /Empresa Exemplo A/ }).click();
  await page.getByLabel("Seu nome para assinatura").fill("Erick");
  await page
    .getByLabel("Template", { exact: true })
    .selectOption("whatsapp_intro");
  await page
    .getByRole("button", { name: "Preparar template WhatsApp" })
    .click();
  await expect(
    page.getByRole("button", { name: "Agendar rascunho no Outlook" }),
  ).not.toBeVisible();
  const popupPromise = page.waitForEvent("popup");
  await page
    .getByRole("button", { name: "Enviar template manual no WhatsApp ↗" })
    .click();
  const popup = await popupPromise;
  await popup.waitForURL("https://wa.me/**");
  expect(new URL(popup.url()).searchParams.get("text")).toContain(
    "Erick, da EBT Enterprise",
  );
  await expect(
    page.getByText(
      "Template manual preparado para abrir a conversa; envio não confirmado.",
      { exact: true },
    ),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Baixar histórico JSON" }),
  ).toBeVisible();
});

test("trocar contato limpa a prévia anterior mesmo com resposta atrasada", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Contatos", exact: true }).click();
  await page.getByRole("button", { name: /Empresa Exemplo A/ }).click();
  await page.getByLabel("Seu nome para assinatura").fill("Erick");
  await page.getByRole("button", { name: "Preparar e-mail" }).click();
  await expect(
    page.getByText("Para: comercial-a@example.com", { exact: true }),
  ).toBeVisible();
  await page.route("**/contacts/*", async (route) => {
    if (
      route.request().method() === "GET" &&
      !route.request().url().endsWith("history")
    )
      await new Promise((r) => setTimeout(r, 500));
    await route.continue();
  });
  await page.getByRole("button", { name: /Empresa Exemplo B/ }).click();
  await expect(
    page.getByText("Para: comercial-a@example.com", { exact: true }),
  ).not.toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Empresa Exemplo B" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Agendar rascunho no Outlook" }),
  ).not.toBeVisible();
});

test("mobile mantém conteúdo e ações dentro da tela", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: "Contatos", exact: true }).click();
  await page.getByRole("button", { name: /Empresa Exemplo A/ }).click();
  await expect(
    page.getByRole("heading", { name: "Empresa Exemplo A" }),
  ).toBeVisible();
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > innerWidth + 1,
  );
  expect(overflow).toBe(false);
  await page.screenshot({ path: "../evidence/mobile.png", fullPage: true });
});

test("WhatsApp oficial mantém a aprovação após resposta incerta", async ({
  page,
}) => {
  const requests = [];
  await page.route("**/whatsapp/status", (route) =>
    route.fulfill({ json: { configured: true, send_enabled: true } }),
  );
  await page.route("**/contacts/*/whatsapp-template", (route) => {
    const body = route.request().postDataJSON();
    requests.push(body);
    const contact_id = new URL(route.request().url()).pathname
      .split("/")
      .at(-2);
    return route.fulfill({
      json: {
        ...body,
        id: body.operation_id,
        contact_id,
        status: "unknown",
        phone: body.confirmation_phone,
        at: "2026-10-07T12:00:00",
      },
    });
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Contatos", exact: true }).click();
  await page.getByRole("button", { name: /Empresa Exemplo A/ }).click();
  await page
    .getByText("Solicitar template oficial WhatsApp", { exact: true })
    .click();
  await page.getByLabel("Nome aprovado do template").fill("approved_template");
  await page
    .getByLabel("Evidência do opt-in")
    .fill("Consentimento sintético registrado");
  await page
    .getByLabel("Digite o telefone para confirmar")
    .fill("5511999999999");
  await page
    .getByRole("button", { name: "Confirmar template oficial" })
    .click();
  await expect(
    page.getByText("WhatsApp: Resultado não confirmado", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Confirmar template oficial" })
    .click();
  await expect.poll(() => requests.length).toBe(2);
  expect(requests[0].operation_id).toBe(requests[1].operation_id);
  await expect(
    page.getByRole("link", { name: "Consultar operação WhatsApp JSON" }),
  ).toBeVisible();
});
