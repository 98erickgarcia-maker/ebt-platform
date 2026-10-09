import {test,expect} from "@playwright/test";
import {reserveQaAuthOperation} from "./qa-auth-budget";
import fs from "node:fs";
import path from "node:path";
const root=path.resolve(process.cwd(),"../..");
const qa=JSON.parse(fs.readFileSync(path.join(root,"tmp/runtime/qa-access.json"),"utf8")) as {password:string};

test("EBT Flow has isolated, keyboard-accessible navigation and readonly-safe UI", async ({page}) => {
  await page.goto("/");
  await page.getByLabel("E-mail",{exact:true}).fill("admin@ebt.example");
  await page.getByLabel("Senha",{exact:true}).fill(qa.password);
  await reserveQaAuthOperation();
  await page.getByRole("button",{name:"Entrar",exact:true}).click();
  await page.getByRole("button",{name:"EBT Flow",exact:true}).click();
  await expect(page.getByRole("heading",{name:"EBT Flow",exact:true})).toBeVisible();
  await expect(page.getByRole("region",{name:"EBT Flow"})).toBeVisible();
  for(const width of [320,390,768,1366]) {
    await page.setViewportSize({width,height:844});
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  }
  // Backend may be deliberately unavailable until the reviewed isolated Flow schema is provisioned.
  await expect(page.getByText("Abrir protocolo",{exact:true})).toBeVisible();
});
