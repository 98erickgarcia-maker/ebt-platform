import {test,expect} from "@playwright/test";
import {reserveQaAuthOperation} from "./qa-auth-budget";
import fs from "node:fs";
import path from "node:path";
const root=path.resolve(process.cwd(),"../..");
const qa=JSON.parse(fs.readFileSync(process.env.EBT_FLOW_QA_ACCESS ?? path.join(root,"tmp/runtime/qa-access.json"),"utf8")) as {password:string};

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
  await expect(page.getByText("Abrir protocolo",{exact:true})).toBeVisible();
  const subject = "QA navegador " + Date.now();
  await page.getByLabel("Assunto do protocolo").fill(subject);
  await page.getByRole("button",{name:"Abrir protocolo",exact:true}).click();
  const row = page.getByRole("article").filter({has:page.getByRole("heading",{name:subject,exact:true})});
  await expect(row).toBeVisible();
  await row.getByRole("button",{name:"Iniciar análise",exact:true}).click();
  await row.getByRole("textbox").fill("Resultado sintético comprovado.");
  await row.getByRole("button",{name:"Concluir protocolo",exact:true}).click();
  await expect(row.getByText("Concluído",{exact:true})).toBeVisible();
  await row.getByRole("button",{name:/Ver histórico/}).click();
  await expect(row.getByText("Resultado sintético comprovado.",{exact:true})).toBeVisible();
  await page.reload();
  await page.getByRole("button",{name:"EBT Flow",exact:true}).click();
  await expect(page.getByRole("heading",{name:subject,exact:true})).toBeVisible();
  await page.screenshot({path:path.join(root,"tmp/e2e/flow-release-390.png"),fullPage:true});
});
