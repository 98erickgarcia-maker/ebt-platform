import {pathToFileURL} from 'node:url';
import {open, unlink} from 'node:fs/promises';

const conversation = /^https:\/\/chatgpt\.com\/c\/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/;
const secrets = /sk-[A-Za-z0-9_-]{12,}|PRIVATE KEY|Bearer\s+[A-Za-z0-9._-]{12,}|(?:password|senha|access_token|api_key)\s*[=:]\s*[^\s,]{8,}/i;
export function validateRequest(p) {
 if (!p || Object.keys(p).sort().join(',') !== 'action,text,url' || !conversation.test(p.url)
  || p.action !== 'send' || typeof p.text !== 'string' || !p.text.trim()
  || Buffer.byteLength(p.text)>48000 || secrets.test(p.text)) throw Error('invalid_request');
 return p;
}
export function guardComposer(s) {
 if (s.limitNotice) throw Error('workspace_limit_notice');
 if (s.busy) throw Error('chat_busy');
 if (s.draft?.trim()) throw Error('draft_present');
 if (!s.extraHigh) throw Error('select_extra_high');
 if (!s.composer) throw Error('composer_missing');
}
async function targets() {
 const r = await fetch('http://127.0.0.1:9222/json/list', {signal:AbortSignal.timeout(3000)});
 if (!r.ok) throw Error('browser_unavailable');
 return (await r.json()).filter(t => t.type==='page' && conversation.test(t.url));
}
async function connection(url) {
 if (!/^ws:\/\/127\.0\.0\.1:9222\/devtools\/page\/[a-zA-Z0-9-]+$/.test(url)) throw Error('browser_unavailable');
 const ws = new WebSocket(url);
 const awaiting = new Map(); let serial=0;
 ws.addEventListener('message', e => {
  let p; try {p=JSON.parse(e.data);} catch {return;}
  const a=awaiting.get(p.id); if (!a) return;
  awaiting.delete(p.id); clearTimeout(a.timer);
  p.error ? a.reject(Error('browser_command_failed')) : a.resolve(p.result);
 });
 await new Promise((resolve,reject) => {
  const timer=setTimeout(()=>{ws.close();reject(Error('browser_unavailable'));},3000);
  ws.addEventListener('open',()=>{clearTimeout(timer);resolve();},{once:true});
  ws.addEventListener('error',()=>{clearTimeout(timer);reject(Error('browser_unavailable'));},{once:true});
 });
 return {
  async call(method,params={}) {
   return new Promise((resolve,reject)=>{
    const id=++serial;
    const timer=setTimeout(()=>{awaiting.delete(id);reject(Error('browser_timeout'));},5000);
    awaiting.set(id,{resolve,reject,timer}); ws.send(JSON.stringify({id,method,params}));
   });
  }, close(){ws.close();}
 };
}
const editorExpression = `(() => {const matches=[...document.querySelectorAll('#prompt-textarea,[role="textbox"][contenteditable="true"],[role="textbox"][aria-label="Pergunte ao ChatGPT"],[role="textbox"][aria-label="Ask ChatGPT"]')].filter(e=>e.getClientRects().length);return matches.length===1?matches[0]:null;})()`;
const stateExpression = `(() => {
 const editor=${editorExpression};
 const buttons=[...document.querySelectorAll('button')];
 return {url:location.href, composer:!!editor,
  draft:editor?.innerText||editor?.value||'',
  busy:buttons.some(b=>b.dataset.testid==='stop-button'||/stop generating|parar|interromper resposta/i.test(b.getAttribute('aria-label')||'')),
  extraHigh:buttons.some(b=>/extra\\s*high|extra\\s*alto/i.test(b.innerText+' '+(b.getAttribute('aria-label')||''))),
  limitNotice:/um membro do workspace atingiu um limite|you have reached.*limit|you've reached.*limit/i.test(document.body.innerText),
  userMessages:document.querySelectorAll('[data-message-author-role="user"]').length};
})()`;
async function evaluate(c,expression) {
 const r=await c.call('Runtime.evaluate',{expression,returnByValue:true});
 if (r.exceptionDetails) throw Error('browser_command_failed');
 return r.result.value;
}
export async function run(p) {
 if (p?.action==='list' && Object.keys(p).length===1) {
  return {targets:(await targets()).map(t=>({url:t.url,title:String(t.title||'ChatGPT').slice(0,120)}))};
 }
 const inspectOnly=p?.action==='inspect' && Object.keys(p).sort().join(',')==='action,url' && conversation.test(p.url);
 if(!inspectOnly)validateRequest(p);
 const matches=(await targets()).filter(t=>t.url===p.url);
 if (matches.length!==1) throw Error('target_missing_or_ambiguous');
 let lock;
 if(!inspectOnly) {
  try {lock=await open('/tmp/ebt-chat-send.lock','wx',0o600);}
  catch {throw Error('send_locked');}
 }
 let c;
 try {
  c=await connection(matches[0].webSocketDebuggerUrl);
  const s=await evaluate(c,stateExpression);
  if(s.url!==p.url) throw Error('target_changed');
  if(inspectOnly)return {status:'inspected',composer:s.composer,busy:s.busy,draft_present:!!s.draft.trim(),extra_high:s.extraHigh,workspace_limit_notice:s.limitNotice,
   editor_shapes:await evaluate(c,`[...document.querySelectorAll('textarea,[contenteditable="true"],[role="textbox"]')].filter(e=>e.getClientRects().length).map(e=>({tag:e.tagName,id:e.id,role:e.getAttribute('role'),placeholder:e.getAttribute('placeholder'),ariaLabel:e.getAttribute('aria-label')}))`),
   button_shapes:await evaluate(c,`[...document.querySelectorAll('button')].filter(e=>e.getClientRects().length&&/enviar|send|stop|parar|interromper/i.test(e.getAttribute('aria-label')||'')).map(e=>({label:e.getAttribute('aria-label'),testid:e.dataset.testid}))`),
   message_shapes:await evaluate(c,`[...document.querySelectorAll('article,[data-message-author-role],[data-turn]')].slice(-6).map(e=>({tag:e.tagName,author:e.getAttribute('data-message-author-role'),turn:e.getAttribute('data-turn'),role:e.getAttribute('role'),keys:Object.keys(e.dataset)}))`)};
  guardComposer(s);
  await c.call('Page.bringToFront');
  await evaluate(c,`(${editorExpression}).focus()`);
  await c.call('Input.insertText',{text:p.text});
  // Allow the editor's mutation observer to reconcile, without issuing a model request.
  await new Promise(resolve=>setTimeout(resolve,180));
  const typed=await evaluate(c,stateExpression);
  if(typed.limitNotice) throw Error('workspace_limit_notice');
  if(typed.url!==p.url || typed.busy) throw Error('target_changed');
  if(typed.draft.trim()!==p.text.trim()) throw Error('insertion_unconfirmed_no_retry');
  const clicked=await evaluate(c,`(() => {
   if(location.href!==${JSON.stringify(p.url)}) return false;
   const editor=${editorExpression};
   if((editor?.innerText||editor?.value||'').trim()!==${JSON.stringify(p.text.trim())}) return false;
   const candidates=[...document.querySelectorAll('button')].filter(b=>b.getClientRects().length&&(b.dataset.testid==='send-button'||/^(enviar|send)( mensagem| message)?$/i.test(b.getAttribute('aria-label')||'')));
   const button=candidates.length===1?candidates[0]:null;
   if(!button||button.disabled) return false;
   button.click(); return true;
  })()`);
  if(!clicked) throw Error('send_unavailable');
  // Observe acceptance only. No polling for task completion, follow-up or retry.
  for(let attempt=0;attempt<12;attempt++) {
   const accepted=await evaluate(c,`(() => {
    const messages=[...document.querySelectorAll('[data-message-author-role="user"]')];
    const normalize=s=>s.replace(/\\s+/g,' ').trim();
    return messages.length>${s.userMessages} && normalize(messages.at(-1)?.innerText||'')===normalize(${JSON.stringify(p.text)});
   })()`);
   const after=await evaluate(c,stateExpression);
   if(accepted||(after.url===p.url&&after.composer&&!after.draft.trim()&&after.busy)) return {status:'submission_observed',task_completed:false,automatic_followup:false};
   await new Promise(resolve=>setTimeout(resolve,300));
  }
  throw Error('submission_unconfirmed_no_retry');
 } finally {
  c?.close();
  if(lock){await lock.close();await unlink('/tmp/ebt-chat-send.lock');}
 }
}
if (process.argv[1] && import.meta.url===pathToFileURL(process.argv[1]).href) {
 try {
  let data=''; for await(const chunk of process.stdin) {data+=chunk;if(data.length>60000)throw Error('invalid_request');}
  console.log(JSON.stringify(await run(JSON.parse(data))));
 } catch(e) {
  const allowed=['invalid_request','chat_busy','draft_present','select_extra_high','composer_missing',
   'target_missing_or_ambiguous','send_unavailable','submission_unconfirmed_no_retry',
   'insertion_unconfirmed_no_retry','target_changed','workspace_limit_notice','send_locked'];
  console.log(JSON.stringify({error:allowed.includes(e.message)?e.message:'browser_unavailable'}));process.exitCode=2;
 }
}
