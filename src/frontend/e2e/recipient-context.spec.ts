import { reserveQaAuthOperation } from "./qa-auth-budget";
import { test, expect, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(process.cwd(), "../..");
const qa = JSON.parse(
  fs.readFileSync(path.join(root, "tmp/runtime/qa-access.json"), "utf8"),
) as { password: string; tenantA: string };

async function login(page: Page) {
  await page.goto("/");
  await page.getByLabel("E-mail", { exact: true }).fill("operador@ebt.example");
  await page.getByLabel("Senha", { exact: true }).fill(qa.password);
  await reserveQaAuthOperation();
  await page.getByRole("button", { name: "Entrar", exact: true }).click();
  await page.getByRole("button", { name: "Acessar Connect", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Meu dia", exact: true }),
  ).toBeVisible({ timeout: 20000 });
  await expect(page.getByText("Atualizando dados…")).not.toBeVisible();
  const me = await (await page.request.get("/api/auth/me")).json();
  if (me.tenantId !== qa.tenantA) {
    await page.getByLabel("Empresa", { exact: true }).selectOption(qa.tenantA);
    await expect(page.getByLabel("Empresa", { exact: true })).toHaveValue(
      qa.tenantA,
    );
    await expect(
      page.getByText("Empresa selecionada.", { exact: true }),
    ).toBeVisible();
    await expect(page.locator(".loading-bar")).not.toBeVisible();
  }
}

test("R02: inbox identifies actual channel recipient independently of paged contacts", async ({
  page,
}) => {
  await login(page);
  await page.getByRole("button", { name: "Conversas", exact: true }).click();
  const inbox = page.locator(".inbox");
  await expect(inbox.getByText("Contato Exemplo A")).toBeVisible();
  await expect(inbox.getByText(/\+5511999990001/).first()).toBeVisible();
  await inbox.getByRole("button", { name: /Contato Exemplo A/ }).click();
  await expect(
    page.getByRole("heading", { name: "Contato Exemplo A", exact: true }),
  ).toBeVisible();
  await expect(page.getByText("Destinatário: +5511999990001")).toBeVisible();
  await expect(
    page.getByRole("button", { name: /Confirmar resposta/ }),
  ).toBeDisabled();
});

test("R01: switching contacts does not display previous contact notes or tasks", async ({
  page,
}) => {
  await login(page);
  await page
    .getByRole("button", { name: "Relacionamentos", exact: true })
    .click();
  await page.getByLabel("Buscar contatos").fill("Contato Exemplo A");
  await page
    .getByRole("button", { name: /Contato Exemplo A contato@cliente.example/ })
    .click();
  await expect(
    page.getByRole("heading", { name: "Contato Exemplo A", level: 1 }),
  ).toBeVisible();
  await expect(page.getByText("Apresentar o EBT Connect")).toBeVisible();
  await page
    .getByRole("button", { name: /Voltar aos relacionamentos/ })
    .click();
  await page.getByLabel("Buscar contatos").fill("R01 QA");
  await page.getByRole("button", { name: "Novo contato", exact: true }).click();
  const dialog = page.getByRole("dialog");
  const name = "R01 QA " + Date.now();
  await dialog.getByLabel("Nome", { exact: true }).fill(name);
  await dialog
    .getByLabel("E-mail", { exact: true })
    .fill("r01-qa@client.example");
  await dialog.getByRole("button", { name: "Salvar", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await page.getByLabel("Buscar contatos").fill(name);
  await page
    .getByRole("button", { name: "Abrir " + name, exact: true })
    .click();
  await expect(page.getByRole("heading", { name, level: 1 })).toBeVisible();
  await expect(page.getByText("Apresentar o EBT Connect")).not.toBeVisible();
});

async function post(page: Page, url: string, body: unknown) {
  const csrf = await (await page.request.get("/api/security/csrf")).json();
  const response = await page.request.post(url, {
    data: body,
    headers: {
      "X-CSRF-TOKEN": csrf.token,
      "Idempotency-Key": crypto.randomUUID(),
    },
  });
  expect(response.ok()).toBeTruthy();
  return response.json();
}

for (const failure of [false, true]) {
  test(`R01: previous resources stay absent during ${failure ? "failed" : "delayed"} contact load`, async ({
    page,
  }) => {
    await login(page);
    const marker = crypto.randomUUID().slice(0, 8);
    const a = await post(page, "/api/connect/v1/contacts", {
      name: "Slow A " + marker,
    });
    const b = await post(page, "/api/connect/v1/contacts", {
      name: "Slow B " + marker,
    });
    const task = await post(page, `/api/connect/v1/contacts/${a.id}/tasks`, {
      title: "Only A " + marker,
      dueAt: "2026-12-12T15:00:00Z",
    });
    await post(page, `/api/connect/v1/contacts/${a.id}/history`, {
      content: "Note A " + marker,
    });
    await page
      .getByRole("button", { name: "Relacionamentos", exact: true })
      .click();
    await page.getByLabel("Buscar contatos").fill(a.name);
    await page
      .getByRole("button", { name: "Abrir " + a.name, exact: true })
      .click();
    await expect(page.getByText(task.title, { exact: true })).toHaveCount(2);
    await expect(
      page.getByText("Note A " + marker, { exact: true }),
    ).toBeVisible();
    await page
      .getByRole("button", { name: /Voltar aos relacionamentos/ })
      .click();
    await page.getByLabel("Buscar contatos").fill(b.name);
    let release!: () => void;
    let started!: () => void;
    const held = new Promise<void>((resolve) => {
      release = resolve;
    });
    const intercepted = new Promise<void>((resolve) => {
      started = resolve;
    });
    await page.route(
      url => url.pathname === "/api/connect/v1/tasks" && url.searchParams.get("contactId") === b.id,
      async (route) => {
        started();
        await held;
        if (failure)
          await route.fulfill({
            status: 503,
            json: { title: "Synthetic contact load failure" },
          });
        else await route.continue();
      },
    );
    try {
      await page
        .getByRole("button", { name: "Abrir " + b.name, exact: true })
        .click();
      await intercepted;
      await expect(
        page.getByRole("heading", { name: b.name, level: 1 }),
      ).toBeVisible();
      await expect(page.getByText(task.title, { exact: true })).toHaveCount(0);
      await expect(
        page.getByText("Note A " + marker, { exact: true }),
      ).toHaveCount(0);
      await expect(
        page.getByRole("button", { name: "Encerrar", exact: true }),
      ).toHaveCount(0);
      release();
      await expect(page.locator(".loading-bar")).not.toBeVisible();
      if (failure)
        await expect(page.getByRole("alert")).toContainText(
          "Synthetic contact load failure",
        );
      await expect(page.getByText(task.title, { exact: true })).toHaveCount(0);
      const tasks = await (
        await page.request.get(`/api/connect/v1/tasks?contactId=${a.id}`)
      ).json();
      expect(
        tasks.find((item: { id: string }) => item.id === task.id).state,
      ).toBe("open");
    } finally {
      release();
    }
  });
}

test("R02: filtered page and 26 newer contacts do not hide the immutable reply destination", async ({
  page,
}) => {
  await login(page);
  const prefix = "Paged " + crypto.randomUUID().slice(0, 8);
  for (let i = 0; i < 26; i++)
    await post(page, "/api/connect/v1/contacts", { name: `${prefix} ${i}` });
  await page
    .getByRole("button", { name: "Relacionamentos", exact: true })
    .click();
  await page.getByLabel("Buscar contatos").fill(prefix);
  await expect(page.locator(".loading-bar")).not.toBeVisible();
  await expect(
    page.getByRole("button", { name: /Abrir Contato Exemplo A/ }),
  ).toHaveCount(0);
  await page.getByRole("button", { name: "Conversas", exact: true }).click();
  await page
    .locator(".inbox")
    .getByRole("button", { name: /Contato Exemplo A/ })
    .click();
  await expect(page.getByText("Destinatário: +5511999990001")).toBeVisible();
  await page
    .getByLabel("Resposta para Contato Exemplo A")
    .fill("Synthetic draft, not sent");
  await expect(
    page.getByRole("button", { name: /Confirmar resposta/ }),
  ).toBeEnabled();
});

test("R02: an unidentified recipient cannot be confirmed even with a draft", async ({
  page,
}) => {
  await login(page);
  await page.route("**/api/connect/v1/conversations", async (route) => {
    const response = await route.fetch();
    const rows = await response.json();
    await route.fulfill({
      response,
      json: rows.map((item: object) => ({
        ...item,
        contactName: "",
        recipient: "",
      })),
    });
  });
  await page.getByRole("button", { name: "Conversas", exact: true }).click();
  await page.locator(".inbox").getByRole("button").first().click();
  await page
    .getByLabel("Resposta para destinatário não identificado")
    .fill("Synthetic draft, not sent");
  await expect(
    page.getByRole("button", { name: /Confirmar resposta/ }),
  ).toBeDisabled();
});

test("R02: late reply acknowledgement cannot replace another conversation's draft or version", async ({
  page,
}) => {
  await login(page);
  const rows = await (
    await page.request.get("/api/connect/v1/conversations")
  ).json();
  const a = rows.find(
    (item: { contactName: string }) => item.contactName === "Contato Exemplo A",
  );
  const b = rows.find((item: { id: string }) => item.id !== a.id);
  expect(b).toBeTruthy();
  let release!: () => void;
  let started!: () => void;
  const held = new Promise<void>((resolve) => {
    release = resolve;
  });
  const intercepted = new Promise<void>((resolve) => {
    started = resolve;
  });
  await page.route(
    `**/api/connect/v1/conversations/${a.id}/messages`,
    async (route) => {
      if (route.request().method() !== "POST") return route.continue();
      started();
      await held;
      // Intercept before the backend: this test must not enqueue or send a message.
      await route.fulfill({
        status: 202,
        json: { status: "queued", version: '"777"' },
      });
    },
  );
  try {
    await page.getByRole("button", { name: "Conversas", exact: true }).click();
    await page
      .locator(".inbox button")
      .filter({ hasText: a.contactName })
      .first()
      .click();
    await page
      .getByLabel("Resposta para " + a.contactName)
      .fill("Synthetic A draft");
    await page.getByRole("button", { name: /Confirmar resposta/ }).click();
    await intercepted;
    await page
      .locator(".inbox button")
      .filter({ hasText: b.contactName })
      .first()
      .click();
    const draft = page.getByLabel("Resposta para " + b.contactName);
    await draft.fill("Synthetic B retained draft");
    const acknowledged = page.waitForResponse(
      (response) =>
        response.url().endsWith(`/conversations/${a.id}/messages`) &&
        response.request().method() === "POST",
    );
    release();
    await acknowledged;
    await expect(draft).toHaveValue("Synthetic B retained draft");
    await expect(
      page.getByRole("button", { name: /Confirmar resposta/ }),
    ).toBeEnabled();
    await expect(
      page.getByText(
        "Resposta registrada na fila. A entrega depende da confirmação do canal.",
        { exact: true },
      ),
    ).toHaveCount(0);
  } finally {
    release();
  }
});
