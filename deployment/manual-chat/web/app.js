'use strict';
const $=id=>document.getElementById(id);
let pending=null, expiryTimer=null, sending=false;
const messages={workspace_limit_notice:'Há um aviso de limite no workspace. Confira sua conta antes de aprovar outro envio. O painel não ativa recarga nem contorna a cota.',
 chat_busy:'O ChatGPT ainda está respondendo. Aguarde e prepare uma nova prévia.',
 draft_present:'Há um rascunho no chat. Preserve ou finalize esse rascunho antes de tentar novamente.',
 select_extra_high:'Selecione Extra High no ChatGPT do Linux e prepare uma nova prévia.',
 composer_missing:'Abra a conversa e termine a autenticação no ChatGPT do Linux.',
 target_missing_or_ambiguous:'O chat escolhido foi fechado ou está duplicado. Atualize a lista.',
 send_unavailable:'O texto pode estar no rascunho, mas o envio não foi confirmado. Confira a tela; não repita às cegas.',
 submission_unconfirmed_no_retry:'O clique ocorreu, mas não foi possível confirmar a mensagem. Confira o chat antes de repetir.',
 insertion_unconfirmed_no_retry:'Não foi possível confirmar a colagem. Confira o rascunho antes de repetir.',
 approval_expired_or_source_changed:'A aprovação expirou ou o estado mudou. Revise uma nova prévia.',
 approval_missing_or_consumed:'Esta aprovação já foi usada ou substituída. Prepare uma nova prévia.',
 browser_unavailable:'A conexão com o Chrome Linux não está disponível. Confira a tela e o serviço.',
 manual_desk_unavailable:'O painel não conseguiu consultar os serviços. Confira a VPS.',
 target_changed:'O chat mudou durante a ação. Confira a tela antes de uma nova tentativa.'};
async function api(path,body){
 const r=await fetch(path,body?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:{});
 const data=await r.json();if(!r.ok)throw Error(messages[data.error]||'A ação foi bloqueada. Confira o painel e gere uma nova prévia.');return data;
}
function invalidate(){pending=null;clearTimeout(expiryTimer);$('consent').checked=false;$('consent').disabled=true;$('approve').disabled=true;$('fingerprint').textContent='Nenhuma aprovação pendente.';}
async function refresh(){
 invalidate();const data=await api('/api/targets');$('target').replaceChildren();
 const placeholder=new Option(data.targets.length?'Selecione a conversa':'Abra uma conversa no Chrome Linux e atualize','');$('target').add(placeholder);
 for(const t of data.targets)$('target').add(new Option(t.title+' — '+t.url,t.url));
 if(data.targets.length===1)$('target').value=data.targets[0].url;
}
$('refresh').addEventListener('click',async()=>{try{await refresh();$('status').textContent='Lista atualizada. Revise uma nova prévia.';}catch(e){$('status').textContent=e.message;}});
for(const id of ['target','task'])$(id).addEventListener('change',invalidate);
$('consent').addEventListener('change',()=>{$('approve').disabled=!pending||!$('consent').checked||sending;});
$('preview').addEventListener('click',async e=>{
 if(!e.isTrusted||sending)return;invalidate();$('preview').disabled=true;
 try{pending=await api('/api/preview',{url:$('target').value,task_id:$('task').value});$('text').value=pending.text;$('consent').disabled=false;
  $('fingerprint').textContent='SHA-256 do texto: '+pending.sha256+' | destino: '+pending.url;
  $('status').textContent='Prévia pronta. Leia o texto e confira o destino. Nenhuma mensagem foi enviada.';
  expiryTimer=setTimeout(()=>{invalidate();$('status').textContent='A prévia expirou. Prepare e revise novamente.';},pending.expires_in_seconds*1000);
 }catch(err){$('status').textContent=err.message;}finally{$('preview').disabled=false;}
});
$('approve').addEventListener('click',async e=>{
 if(!e.isTrusted||!pending||!$('consent').checked||sending)return;
 const approved=pending;invalidate();sending=true;$('preview').disabled=true;$('refresh').disabled=true;$('target').disabled=true;$('task').disabled=true;
 $('status').textContent='Executando somente a mensagem aprovada na VPS…';
 try{const result=await api('/api/approve',{approval_id:approved.approval_id,sha256:approved.sha256,approved:true,action:'send'});
  $('status').textContent=result.status==='submission_observed'?'Mensagem observada no ChatGPT. Aguarde a resposta e confira as evidências. Nenhum próximo bloco foi agendado.':'Resultado não confirmado. Confira a tela antes de repetir.';
 }catch(err){$('status').textContent=err.message;}finally{sending=false;for(const id of ['preview','refresh','target','task'])$(id).disabled=false;}
});
(async()=>{try{const data=await api('/api/tasks');for(const t of data.tasks)$('task').add(new Option(t.id+' — '+t.role,t.id));
 $('runner').textContent='Runner separado: '+(data.runner_status||'desconhecido')+' | bloco registrado: '+(data.current_task||'desconhecido')+'. Escolher um papel aqui não altera sua conclusão.';
 await refresh();
 const s=await api('/api/schedule');
 $('schedule').textContent='Rotina CONTINUE: '+(s.timer_active?'timer ativo':'timer inativo')+' | a cada '+s.interval_minutes+' minutos | estado: '+s.status+' | envios observados: '+s.observed_count+'. Limite ou erro pausa os envios. Isso não comprova programação concluída.';
 }catch(e){$('status').textContent=e.message;}})();
