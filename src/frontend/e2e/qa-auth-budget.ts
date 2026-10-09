import { test } from "@playwright/test";

// QA has 15 auth operations/minute for the shared loopback address.
// Pace synthetic callers instead of weakening the product's rate limiter.
const operations: number[] = [];
export async function reserveQaAuthOperation() {
  test.setTimeout(90000);
  const cutoff = Date.now() - 61000;
  while (operations.length && operations[0] <= cutoff) operations.shift();
  if (operations.length >= 15) {
    const wait = operations[0] + 61000 - Date.now();
    if (wait > 0) await new Promise((resolve) => setTimeout(resolve, wait));
    return reserveQaAuthOperation();
  }
  operations.push(Date.now());
}
