import { test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

// QA has 15 auth operations/minute for the shared loopback address.
// Pace synthetic callers instead of weakening the product's rate limiter.
// Playwright isolates spec modules. Share timestamps across files and worker restarts.
// The suite uses exactly one worker; this file contains no accounts or credentials.
const ledger = path.resolve(
  process.cwd(),
  "../../tmp/runtime/qa-auth-operations.json",
);
export async function reserveQaAuthOperation() {
  test.setTimeout(90000);
  const cutoff = Date.now() - 61000;
  const operations: number[] = fs.existsSync(ledger)
    ? JSON.parse(fs.readFileSync(ledger, "utf8")).filter(
        (at: number) => at > cutoff,
      )
    : [];
  if (operations.length >= 12) {
    const wait = operations[0] + 61000 - Date.now();
    if (wait > 0) await new Promise((resolve) => setTimeout(resolve, wait));
    return reserveQaAuthOperation();
  }
  operations.push(Date.now());
  fs.mkdirSync(path.dirname(ledger), { recursive: true });
  fs.writeFileSync(ledger, JSON.stringify(operations));
}
