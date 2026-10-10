import { test, expect, type Page } from '@playwright/test';

// Isolated synthetic API fixtures validate presentation; they do not prove backend integration.
async function openWorkspace(page:Page) {
  await page.route('**/api/**', async request => {
    const path = new URL(request.request().url()).pathname;
    let data:unknown = [];
    if(path==='/api/auth/me') data={name:'Operador QA',email:'qa@ebt.example',userId:'qa-user',tenantId:'qa-tenant',role:'admin',portfolio:'QA',tenants:[{id:'qa-tenant',name:'Empresa de teste EBT',product:'connect',role:'admin'}]};
    else if(path==='/api/platform/v1/applications') data={platform:'EBT Enterprise',applications:[
      {code:'connect',name:'EBT Connect',description:'Relacionamentos, próximas ações e comunicação comercial.',available:true,state:'available'},
      {code:'flow',name:'EBT Flow',description:'Protocolos fixos e acompanhamento de atividades.',available:true,state:'available'},
      {code:'portal',name:'EBT Portal',description:'Acesso externo na evolução da plataforma.',available:false,state:'planned'}]};
    else if(path.endsWith('/summary')) data={contacts:0,openTasks:0,overdue:0,withoutNextAction:0,stages:[]};
    else if(['/contacts','/tasks','/organizations'].some(end=>path.endsWith(end))) data={items:[],total:0};
    await request.fulfill({status:200,contentType:'application/json',body:JSON.stringify(data)});
  });
  await page.goto('/');
  await expect(page.getByRole('heading',{name:'Aplicativos',exact:true})).toBeVisible();
}

test('Keyboard can bypass navigation and reach the labelled main region',async({page})=>{
  await openWorkspace(page);
  await page.keyboard.press('Tab');
  const skip=page.getByRole('link',{name:'Ir para o conteúdo principal'});
  await expect(skip).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('main',{name:'Aplicativos',exact:true})).toBeFocused();
});

test('Short mobile navigation keeps all pages reachable and can close from inside',async({page})=>{
  await page.setViewportSize({width:390,height:420});
  await openWorkspace(page);
  await page.getByRole('button',{name:'Abrir navegação',exact:true}).click();
  const close=page.getByRole('button',{name:'Fechar menu',exact:true});
  await expect(close).toBeVisible();
  const settings=page.getByRole('navigation').getByRole('button',{name:'Configurações',exact:true});
  await settings.scrollIntoViewIfNeeded();
  const rect=await settings.boundingBox();
  expect(rect!.y).toBeGreaterThanOrEqual(0);
  expect(rect!.y+rect!.height).toBeLessThanOrEqual(420);
  await close.click();
  await expect(page.getByRole('button',{name:'Abrir navegação',exact:true})).toBeFocused();
});

test('Responsive catalog and daily dashboard fit 320, 768 and 1440 pixels',async({page})=>{
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  for(const width of [320,768,1440]) {
    await page.setViewportSize({width,height:900});
    await openWorkspace(page);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
    await page.getByRole('button',{name:'Acessar Connect',exact:true}).click();
    await expect(page.getByRole('heading',{name:'Meu dia',exact:true})).toBeVisible();
    await expect(page.locator('.loading-bar')).not.toBeVisible();
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
    const refresh=page.getByRole('button',{name:'Atualizar',exact:true});
    const size=await refresh.boundingBox();expect(size!.height).toBeGreaterThanOrEqual(44);
    await page.screenshot({path:`../../tmp/frontend-quality/daily-${width}.png`,fullPage:true});
  }
  expect(errors).toEqual([]);
});

test('Mobile drawer receives keyboard focus, wraps Tab and restores Escape focus',async({page})=>{
  await page.setViewportSize({width:390,height:700});
  await openWorkspace(page);
  const trigger=page.getByRole('button',{name:'Abrir navegação',exact:true});
  await trigger.click();
  await expect(page.getByRole('button',{name:'Fechar menu',exact:true})).toBeFocused();
  await page.getByRole('button',{name:'Sair',exact:true}).focus();
  await page.keyboard.press('Tab');
  await expect(page.locator('.sidebar .brand')).toBeFocused();
  await page.keyboard.press('Shift+Tab');
  await expect(page.getByRole('button',{name:'Sair',exact:true})).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(trigger).toBeFocused();
  await expect(page.getByRole('navigation')).not.toBeVisible();
});
