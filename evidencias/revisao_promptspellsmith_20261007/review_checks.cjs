const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../..');
const { chromium, request } = require(path.join(root, 'src/frontend/node_modules/@playwright/test'));
const access = JSON.parse(fs.readFileSync(path.join(root, 'tmp/runtime/qa-access.json'), 'utf8').replace(/^\uFEFF/, ''));
const config = JSON.parse(fs.readFileSync(path.join(root, 'tmp/runtime/local-config.json'), 'utf8').replace(/^\uFEFF/, ''));
const baseURL = 'http://127.0.0.1:5191';
const prefix = '/api/connect/v1';
const run = crypto.randomUUID().slice(0, 8);
const results = [];
const artifacts = path.join(__dirname, 'evidencias');
fs.mkdirSync(artifacts, { recursive: true });

async function api(client, route, method = 'GET', data, headers = {}) {
  if (method !== 'GET') headers['X-CSRF-TOKEN'] = (await (await client.get('/api/security/csrf')).json()).token;
  const response = await client.fetch(route, { method, data, headers });
  const payload = response.status() === 204 ? null : await response.json().catch(() => null);
  return { status: response.status(), payload };
}
async function requireApi(client, route, method = 'GET', data, headers = {}) {
  const response = await api(client, route, method, data, headers);
  if (response.status >= 400) throw new Error(`${method} ${route}: ${response.status} ${response.payload?.code || ''}`);
  return response.payload;
}
async function client(email) {
  const c = await request.newContext({ baseURL });
  await requireApi(c, '/api/auth/login', 'POST', { email, password: access.password });
  return c;
}
async function inbound(phone, text) {
  const envelope = { object: 'whatsapp_business_account', entry: [{ id: 'qa-account', changes: [{ field: 'messages', value: { metadata: { phone_number_id: 'qa-phone-a' }, messages: [{ id: `qa.ps.${crypto.randomUUID()}`, from: phone, type: 'text', text: { body: text }, timestamp: String(Math.floor(Date.now() / 1000)) }] } }] }] };
  const body = Buffer.from(JSON.stringify(envelope));
  const signature = crypto.createHmac('sha256', config.Qa.AppSecret).update(body).digest('hex');
  const c = await request.newContext({ baseURL });
  try {
    const response = await c.post('/webhooks/connect/meta/qa-app', { data: body, headers: { 'Content-Type': 'application/json', 'X-Hub-Signature-256': `sha256=${signature}` } });
    if (response.status() !== 200) throw new Error(`QA webhook: ${response.status()}`);
  } finally { await c.dispose(); }
}
async function waitForConversation(c, id) {
  for (let i = 0; i < 50; i++) {
    const rows = await requireApi(c, `${prefix}/conversations?contactId=${id}`);
    if (rows.length) return rows[0];
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  throw new Error('Synthetic inbound was not processed.');
}

(async () => {
  let browser, page, releaseGate;
  const admin = await client('admin@ebt.example');
  try {
    await requireApi(admin, `/api/auth/context/${access.tenantA}`, 'POST');
    const me = await requireApi(admin, '/api/auth/me');
    const contacts = [];
    for (let i = 0; i < 2; i++) {
      const body = { name: `PS Review ${run} ${i === 0 ? 'A' : 'B'}`, email: '', phone: `55119${Date.now().toString().slice(-7)}${i}`, externalKey: `ps-${run}-${i}`, organizationId: null, ownerId: me.userId, portfolio: 'principal', stage: 'novo' };
      contacts.push(await requireApi(admin, `${prefix}/contacts`, 'POST', body, { 'Idempotency-Key': crypto.randomUUID() }));
    }
    const taskTitle = `Tarefa exclusiva A ${run}`;
    const task = await requireApi(admin, `${prefix}/contacts/${contacts[0].id}/tasks`, 'POST', { title: taskTitle, dueAt: '2026-10-12T15:00:00Z', ownerId: me.userId }, { 'Idempotency-Key': crypto.randomUUID() });
    const note = await requireApi(admin, `${prefix}/contacts/${contacts[0].id}/history`, 'POST', { content: `Nota exclusiva A ${run}`, occurredAt: null }, { 'Idempotency-Key': crypto.randomUUID() });
    for (let i = 0; i < contacts.length; i++) await inbound(contacts[i].phone, `Mensagem sintética ${i === 0 ? 'A' : 'B'} ${run}`);
    const conversationA = await waitForConversation(admin, contacts[0].id);
    const conversationB = await waitForConversation(admin, contacts[1].id);
    results.push({ case: 'Synthetic fixture and durable inbound A/B', passed: true, contactA: contacts[0].id, contactB: contacts[1].id, taskA: task.id, conversationA: conversationA.id, conversationB: conversationB.id, noteA: note.id });

    const tenantB = await client('admin@ebt.example');
    await requireApi(tenantB, `/api/auth/context/${access.tenantB}`, 'POST');
    const negative = await api(tenantB, `${prefix}/contacts/${contacts[0].id}`);
    results.push({ case: 'Tenant B cannot read direct contact ID from A', passed: negative.status === 404, status: negative.status });
    await tenantB.dispose();
    const reader = await client('consulta@ebt.example');
    const denied = await api(reader, `${prefix}/contacts`, 'POST', { name: 'PS review denied', email: '', phone: '' }, { 'Idempotency-Key': crypto.randomUUID() });
    results.push({ case: 'Reader cannot create contact', passed: denied.status === 403, status: denied.status });
    await reader.dispose();

    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ baseURL, timezoneId: 'America/Sao_Paulo', viewport: { width: 1440, height: 1000 }, storageState: await admin.storageState() });
    page = await context.newPage();
    await page.goto('/');
    await page.getByRole('heading', { name: 'Meu dia', exact: true }).waitFor();
    await page.getByRole('button', { name: 'Relacionamentos', exact: true }).click();
    await page.getByLabel('Buscar contatos').fill(`PS Review ${run}`);
    await page.getByRole('button', { name: `Abrir ${contacts[0].name}`, exact: true }).click();
    await page.getByText(taskTitle, { exact: true }).first().waitFor();
    await page.getByRole('button', { name: /Voltar aos relacionamentos/ }).click();
    await page.getByRole('button', { name: `Abrir ${contacts[1].name}`, exact: true }).waitFor();
    const gate = new Promise(resolve => { releaseGate = resolve; });
    let held = 0;
    await page.route('**/api/connect/v1/tasks?*', async route => {
      if (new URL(route.request().url()).searchParams.get('contactId') === contacts[1].id) { held++; await gate; }
      if (!page.isClosed()) await route.continue();
    });
    await page.getByRole('button', { name: `Abrir ${contacts[1].name}`, exact: true }).click();
    await page.getByRole('heading', { level: 1, name: contacts[1].name, exact: true }).waitFor();
    const foreignTaskVisible = await page.getByText(taskTitle, { exact: true }).first().isVisible();
    const foreignTaskAction = page.locator('article.task-row').filter({ hasText: taskTitle }).getByRole('button', { name: 'Encerrar', exact: true });
    const foreignTaskActionEnabled = foreignTaskVisible && await foreignTaskAction.isEnabled();
    await page.screenshot({ path: path.join(artifacts, 'contato-b-tarefa-a.png'), fullPage: true });
    console.log('CHECK R01 foreign task visible:', foreignTaskVisible, 'action enabled:', foreignTaskActionEnabled);
    if (foreignTaskActionEnabled) {
      await foreignTaskAction.click();
      const dialog = page.getByRole('dialog');
      await dialog.getByLabel('Descreva o resultado ou motivo').fill('Reprodução sintética: tarefa A encerrada com cabeçalho B.');
      await dialog.getByRole('button', { name: 'Confirmar resultado', exact: true }).click();
      await dialog.waitFor({ state: 'hidden' });
    }
    const taskAfter = (await requireApi(admin, `${prefix}/tasks?contactId=${contacts[0].id}`)).find(row => row.id === task.id);
    results.push({ case: 'R01 stale task remains actionable under another contact', reproduced: foreignTaskVisible && foreignTaskActionEnabled && taskAfter.state === 'done', foreignTaskVisible, foreignTaskActionEnabled, taskAState: taskAfter.state, throttledRequests: held, screenshot: 'contato-b-tarefa-a.png' });
    releaseGate();
    await page.unrouteAll({ behavior: 'wait' });
    await page.getByText(taskTitle, { exact: true }).waitFor({ state: 'hidden' });

    await page.getByRole('button', { name: 'Relacionamentos', exact: true }).click();
    await page.getByLabel('Buscar contatos').fill(contacts[0].name);
    await page.getByRole('button', { name: `Abrir ${contacts[0].name}`, exact: true }).waitFor();
    await page.getByRole('button', { name: 'Conversas', exact: true }).click();
    await page.locator('.conversation-list').getByText(contacts[0].name, { exact: true }).waitFor();
    const unnamed = await page.locator('.conversation-list').getByText('Contato vinculado', { exact: true }).count();
    const bNamed = await page.locator('.conversation-list').getByText(contacts[1].name, { exact: true }).count();
    await page.locator('.conversation-list button').filter({ hasText: 'Contato vinculado' }).first().click();
    await page.locator('.conversation-panel h2').waitFor();
    const conversationHeader = await page.locator('.conversation-panel h2').innerText();
    await page.screenshot({ path: path.join(artifacts, 'conversas-sem-identificacao.png'), fullPage: true });
    results.push({ case: 'R02 conversation identity depends on unrelated filtered contact page', reproduced: unnamed > 0 && bNamed === 0 && conversationHeader === 'Conversa', unnamedConversations: unnamed, nameBShown: bNamed > 0, conversationHeader, screenshot: 'conversas-sem-identificacao.png' });

    const beforeMove = await requireApi(admin, `${prefix}/contacts/${contacts[1].id}`);
    await requireApi(admin, `${prefix}/contacts/${beforeMove.id}`, 'PUT', { name: beforeMove.name, email: beforeMove.email, phone: beforeMove.phone, externalKey: beforeMove.externalKey, organizationId: null, ownerId: me.userId, portfolio: 'outra', stage: beforeMove.stage }, { 'If-Match': `"${beforeMove.version}"` });
    const textAfterMove = `Entrada após transferência ${run}`;
    await inbound(beforeMove.phone, textAfterMove);
    await new Promise(resolve => setTimeout(resolve, 3000));
    const messagesAfterMove = await requireApi(admin, `${prefix}/conversations/${conversationB.id}/messages`);
    results.push({ case: 'R03 moving contact portfolio prevents subsequent channel inbound', reproduced: !messagesAfterMove.items.some(row => row.content === textAfterMove), acceptedWebhook: true, inboundReachedConversation: messagesAfterMove.items.some(row => row.content === textAfterMove), transferredPortfolio: 'outra' });

    const key = await requireApi(admin, '/api/admin/api-keys', 'POST');
    const keyList = await api(admin, '/api/admin/api-keys');
    await requireApi(admin, `/api/admin/api-keys/${key.id}`, 'DELETE');
    results.push({ case: 'R04 issued keys cannot be enumerated for later revocation', reproduced: keyList.status === 405, listStatus: keyList.status, createdReviewKeyRevoked: true });

    await requireApi(admin, `/api/auth/context/${access.tenantB}`, 'POST');
    const invite = await requireApi(admin, '/api/admin/invitations', 'POST', { email: 'outra@ebt.example', role: 'operator', portfolio: 'principal' });
    const anonymous = await request.newContext({ baseURL });
    const activation = await api(anonymous, '/api/auth/activate', 'POST', { token: invite.activationToken, name: 'QA existing member', password: access.password });
    results.push({ case: 'R05 existing account invitation has no application linking path', reproduced: activation.status === 409 && activation.payload?.code === 'existing_user', activationStatus: activation.status, activationCode: activation.payload?.code });
    await anonymous.dispose();

    await page.setViewportSize({ width: 390, height: 844 });
    const mobileOverflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    await page.screenshot({ path: path.join(artifacts, 'mobile-conversas.png'), fullPage: true });
    results.push({ case: 'Mobile conversations have no horizontal overflow', passed: !mobileOverflow, screenshot: 'mobile-conversas.png' });
    const health = await requireApi(admin, '/health/ready');
    results.push({ case: 'Current reviewed runtime SQL health', passed: health.status === 'ready' });
  } catch (error) {
    results.push({ case: 'Review harness execution', passed: false, error: error.message });
    console.log('HARNESS ERROR:', error.message);
    process.exitCode = 1;
  } finally {
    releaseGate?.();
    fs.writeFileSync(path.join(artifacts, 'review_checks.json'), JSON.stringify({ generatedUtc: new Date().toISOString(), run, environment: 'Development; localhost:5191; EbtPlatformQa_20261007Migrated; only synthetic fixtures; no real provider send', results }, null, 2));
    for (const row of results) console.log(JSON.stringify(row));
    await page?.unrouteAll({ behavior: 'ignoreErrors' });
    await browser?.close();
    await admin.dispose();
  }
})();
