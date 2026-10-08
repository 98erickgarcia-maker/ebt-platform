const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const { chromium, request } = require(path.join(root, 'src/frontend/node_modules/@playwright/test'));
const access = JSON.parse(fs.readFileSync(path.join(root, 'tmp/runtime/qa-access.json'), 'utf8').replace(/^\uFEFF/, ''));
const reportPath = path.join(__dirname, 'evidencias/review_checks.json');
const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
(async () => {
  const baseURL = 'http://127.0.0.1:5191';
  const client = await request.newContext({ baseURL });
  const post = async (url, data) => {
    const token = (await (await client.get('/api/security/csrf')).json()).token;
    const response = await client.post(url, { data, headers: { 'X-CSRF-TOKEN': token } });
    if (!response.ok()) throw new Error(`Session setup: ${response.status()}`);
  };
  let browser;
  try {
    await post('/api/auth/login', { email: 'admin@ebt.example', password: access.password });
    await post(`/api/auth/context/${access.tenantA}`);
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ baseURL, storageState: await client.storageState(), timezoneId: 'America/Sao_Paulo', viewport: { width: 1440, height: 1000 } });
    const page = await context.newPage();
    await page.goto('/');
    await page.getByRole('button', { name: 'Relacionamentos', exact: true }).click();
    await page.getByLabel('Buscar contatos').fill(`PS Review ${report.run} A`);
    await page.getByRole('button', { name: `Abrir PS Review ${report.run} A`, exact: true }).waitFor();
    await page.getByRole('button', { name: 'Conversas', exact: true }).click();
    await page.locator('.conversation-list').getByText(`PS Review ${report.run} A`, { exact: true }).waitFor();
    await page.locator('.conversation-list button').filter({ hasText: 'Contato vinculado' }).first().click();
    await page.locator('.conversation-panel .message').first().waitFor();
    await page.getByLabel('Resposta para o contato').fill('Rascunho sintético para verificar o botão. Não enviado.');
    const confirmation = { conversationHeader: await page.locator('.conversation-panel h2').innerText(), responseButtonEnabled: await page.getByRole('button', { name: 'Confirmar resposta', exact: true }).isEnabled(), outgoingMessageSent: false };
    await page.screenshot({ path: path.join(__dirname, 'evidencias/conversas-sem-identificacao.png'), fullPage: true });
    report.results.find(row => row.case.startsWith('R02')).afterMessagesLoaded = confirmation;
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(JSON.stringify(confirmation));
  } finally { await browser?.close(); await client.dispose(); }
})();
