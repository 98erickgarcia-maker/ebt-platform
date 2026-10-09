import { test, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { api, download, resetContext, setAccess } from "../tmp/unit/api.js";

const identity = (userId) => ({
  userId,
  tenantId: "tenant-a",
  role: "operator",
  portfolio: "principal",
});
const deferred = () => {
  let resolve;
  const promise = new Promise((r) => {
    resolve = r;
  });
  return { promise, resolve };
};
const changed = (error) => error.code === "context_changed";
beforeEach(() => {
  globalThis.window = Object.assign(new EventTarget(), {
    location: { origin: "https://ebt.example" },
  });
  resetContext();
  setAccess(identity("user-a"));
});

test("JSON arriving after context change is discarded", async () => {
  const body = deferred(),
    started = deferred();
  globalThis.fetch = async () => ({
    ok: true,
    status: 200,
    headers: new Headers(),
    json: () => {
      started.resolve();
      return body.promise;
    },
  });
  const pending = api("/api/connect/v1/contacts");
  await started.promise;
  resetContext();
  body.resolve([{ id: "old-private-record" }]);
  await assert.rejects(pending, changed);
});

test("Changing user within the same tenant and role discards previous data", async () => {
  const body = deferred(),
    started = deferred();
  globalThis.fetch = async () => ({
    ok: true,
    status: 200,
    headers: new Headers(),
    json: () => {
      started.resolve();
      return body.promise;
    },
  });
  const pending = api("/api/connect/v1/contacts");
  await started.promise;
  setAccess(identity("user-b"));
  body.resolve([{ id: "old-private-record" }]);
  await assert.rejects(pending, changed);
});

test("Blob arriving after logout never triggers a download", async () => {
  const body = deferred(),
    started = deferred();
  let clicks = 0;
  globalThis.document = {
    createElement: () => ({
      click: () => {
        clicks++;
      },
    }),
  };
  window.document = globalThis.document;
  globalThis.fetch = async () => ({
    ok: true,
    status: 200,
    headers: new Headers(),
    blob: () => {
      started.resolve();
      return body.promise;
    },
  });
  const pending = download("/api/connect/v1/documents/test/download/1");
  await started.promise;
  resetContext();
  body.resolve(new Blob(["private-old-file"]));
  await assert.rejects(pending, changed);
  assert.equal(clicks, 0);
});

test("Download rejects external destinations before any request", async () => {
  let requests = 0;
  globalThis.fetch = async () => {
    requests++;
    throw new Error("Unexpected request");
  };
  await assert.rejects(
    download("https://other.example/api/file"),
    /Destino de API inválido/,
  );
  assert.equal(requests, 0);
});

test("CSRF from an old context cannot poison a subsequent mutation", async () => {
  const token = deferred(),
    started = deferred();
  let issued = 0;
  let sent = "";
  globalThis.fetch = async (path, init) => {
    if (path === "/api/security/csrf") {
      issued++;
      if (issued === 1) {
        started.resolve();
        return { ok: true, json: () => token.promise };
      }
      return { ok: true, json: async () => ({ token: "new-token" }) };
    }
    sent = init.headers["X-CSRF-TOKEN"];
    return { ok: true, status: 204, headers: new Headers() };
  };
  const pending = api("/api/connect/v1/contacts", "POST", {});
  await started.promise;
  resetContext();
  token.resolve({ token: "old-token" });
  await assert.rejects(pending, changed);
  await api("/api/connect/v1/contacts", "POST", {});
  assert.equal(issued, 2);
  assert.equal(sent, "new-token");
});

test("Old 401 body cannot clear a newer session", async () => {
  const body = deferred(),
    started = deferred();
  let invalidated = 0;
  window.addEventListener("ebt:unauthorized", () => {
    invalidated++;
  });
  globalThis.fetch = async () => ({
    ok: false,
    status: 401,
    headers: new Headers(),
    json: () => {
      started.resolve();
      return body.promise;
    },
  });
  const pending = api("/api/connect/v1/contacts");
  await started.promise;
  resetContext();
  setAccess(identity("user-b"));
  body.resolve({ title: "expired" });
  await assert.rejects(pending, changed);
  assert.equal(invalidated, 0);
});

test("Current successful request returns its data and requires no CSRF for GET", async () => {
  let called = 0;
  globalThis.fetch = async (_path, options) => {
    called++;
    assert.equal(options.credentials, "same-origin");
    return Response.json({ id: "current-record" });
  };
  assert.deepEqual(await api("/api/connect/v1/contacts"), {
    id: "current-record",
  });
  assert.equal(called, 1);
});

test("Current authorized download clicks once and releases its temporary URL", async () => {
  const originalCreate = URL.createObjectURL;
  const originalRevoke = URL.revokeObjectURL;
  let clicks = 0;
  let released = "";
  const link = { download: "", href: "", click: () => { clicks++; } };
  window.document = { createElement: () => link };
  URL.createObjectURL = () => "blob:synthetic-current";
  URL.revokeObjectURL = (url) => { released = url; };
  globalThis.fetch = async () => new Response(new Blob(["Synthetic document"]), {
    headers: { "Content-Disposition": 'attachment; filename="synthetic.txt"' },
  });
  try {
    await download("/api/connect/v1/documents/current/download/1");
    assert.equal(clicks, 1);
    assert.equal(link.download, "synthetic.txt");
    assert.equal(released, "blob:synthetic-current");
  } finally { URL.createObjectURL = originalCreate; URL.revokeObjectURL = originalRevoke; }
});

test("Concurrent mutations share current CSRF without modifying caller headers", async () => {
  const token = deferred();
  const started = deferred();
  const headers = { "Idempotency-Key": "synthetic-operation" };
  let issued = 0;
  const sent = [];
  globalThis.fetch = async (path, init) => {
    if (path === "/api/security/csrf") {
      issued++; started.resolve();
      return { ok: true, json: () => token.promise };
    }
    sent.push(init.headers["X-CSRF-TOKEN"]);
    return { ok: true, status: 204, headers: new Headers() };
  };
  const first = api("/api/connect/v1/contacts", "POST", {}, headers);
  await started.promise;
  const second = api("/api/connect/v1/contacts", "POST", {}, headers);
  token.resolve({ token: "synthetic-current-csrf" });
  await Promise.all([first, second]);
  assert.equal(issued, 1);
  assert.deepEqual(sent, ["synthetic-current-csrf", "synthetic-current-csrf"]);
  assert.deepEqual(headers, { "Idempotency-Key": "synthetic-operation" });
});
