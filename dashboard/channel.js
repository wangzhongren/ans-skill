'use strict';
(() => {
  const base=document.querySelector('meta[name="ans-base-path"]').content;
  const match=location.pathname.slice(base.length).match(/^\/p\/([a-z0-9]+(?:-[a-z0-9]+)*)\/$/);
  if(!match)return;
  const path=base+'/p/'+match[1]+'/api/';
  const $=id=>document.getElementById(id);
  let identity=null,loading=false;
  function el(tag,value,cls){const node=document.createElement(tag);if(value!==undefined)node.textContent=String(value);if(cls)node.className=cls;return node}
  async function request(url,options={}){
    const response=await fetch(url,{cache:'no-store',credentials:'same-origin',...options});
    const value=await response.json();
    if(!response.ok)throw Error(value.error||'请求失败');
    return value;
  }
  async function post(url,value){return request(url,{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':identity.csrfToken},body:JSON.stringify(value)})}
  function clearOrEmpty(node,rows,label){node.replaceChildren();if(!rows.length)node.append(el('p',label,'small muted'))}
  function renderRequest(item){
    const card=el('article',undefined,'channelcard');
    const status={pending:'待处理',approved:'已批准',denied:'已拒绝',expired:'已过期',stale:'版本失效'}[item.status]||item.status;
    card.append(el('strong','#'+item.id+' · '+item.requester_role_id+' · '+status),
      el('p',item.reason),el('small',item.task_id+' / '+item.node_id+' · '+item.operation+' · '+item.worker_id),
      el('code',item.writeSet.join('\n')),
      el('small','计划 #'+item.plan_revision+' · 批次 #'+item.attempt_number+' · 需求 '+item.requirement_revision+' · 设计 '+item.design_revision+' · 边界 '+item.boundary_revision));
    if(item.decision)card.append(el('p',(item.decision==='approved'?'已批准':'已拒绝')+'：'+item.decision_reason+'（'+item.decided_by+'）'+(item.expires_at?' · 截止 '+item.expires_at:''),'small'));
    if(identity.role==='admin'&&item.status==='pending'){
      const controls=el('div',undefined,'channeldecision'),reason=el('input');reason.placeholder='审批理由（必填）';reason.maxLength=2000;
      for(const [choice,label] of [['approved','批准 1 小时'],['denied','拒绝']]){
        const button=el('button',label,'btn');button.type='button';button.onclick=async()=>{
          $('channelError').textContent='';
          try{if(!reason.value.trim())throw Error('请填写审批理由');button.disabled=true;
            await post(path+'permission-requests/'+item.id+'/decision',{decision:choice,reason:reason.value});await refresh();
          }catch(error){$('channelError').textContent=error.message;button.disabled=false}
        };controls.append(button);
      }
      controls.prepend(reason);card.append(controls);
    }
    return card;
  }
  function render(value){
    $('navChannelCount').textContent=value.requests.filter(item=>item.status==='pending').length;
    $('channelRequestCount').textContent=value.requests.filter(item=>item.status==='pending').length+' 待处理';
    clearOrEmpty($('channelRequests'),value.requests,'暂无权限申请。');
    for(const item of value.requests)$('channelRequests').append(renderRequest(item));
    clearOrEmpty($('channelMessages'),value.messages,'暂无角色消息。');
    for(const item of value.messages){const card=el('article',undefined,'channelcard');card.append(
      el('strong',item.sender_id+' → '+item.to_role_id+' · '+item.kind),
      el('p',item.body),el('small',item.task_id+' · 版本 '+item.revision+' · '+item.created_at));$('channelMessages').append(card)}
    clearOrEmpty($('channelEvents'),value.events,'暂无审计记录。');
    for(const item of value.events){const card=el('article',undefined,'channelcard');card.append(
      el('strong','#'+item.seq+' · '+item.kind),el('p',item.summary),
      el('small',item.actor_kind+':'+item.actor_id+' · '+item.at));$('channelEvents').append(card)}
    const select=$('channelToRole'),selected=select.value;select.replaceChildren();
    for(const role of value.roles){const option=el('option',role.name);option.value=role.id;select.append(option)}
    if(value.roles.some(role=>role.id===selected))select.value=selected;
  }
  async function refresh(){
    if(loading||$('channelView').hidden)return;
    loading=true;
    try{
      if(!identity){identity=await request(base+'/api/me');$('channelCompose').hidden=identity.role!=='admin'}
      render(await request(path+'channel'));$('channelError').textContent='';
    }catch(error){$('channelError').textContent='协作记录读取失败：'+error.message}
    finally{loading=false}
  }
  $('channelMessageForm').addEventListener('submit',async event=>{
    event.preventDefault();$('channelError').textContent='';
    try{await post(path+'messages',{toRoleId:$('channelToRole').value,taskId:$('channelTask').value,
      revision:$('channelRevision').value,kind:$('channelKind').value,body:$('channelBody').value,
      clientMessageId:crypto.randomUUID()});event.target.reset();await refresh()}
    catch(error){$('channelError').textContent='消息发送失败：'+error.message}
  });
  window.refreshChannel=refresh;
})();
