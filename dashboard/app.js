'use strict';
const projectMatch=location.pathname.match(/^\/p\/([a-z0-9]+(?:-[a-z0-9]+)*)\/$/);
const currentProjectId=projectMatch?.[1]||null;
const apiPath=path=>currentProjectId?'/p/'+currentProjectId+path:path;
const $=id=>document.getElementById(id);let data=null,view='overview',loading=false,lastSuccess=null,refreshTimer=null,lastDataSignature=null,contextRoleId=null,contextPage={category:'flows',topicId:null},contextDetail=null;const contextRelatedCache=new Map(),contextCategoryCache=new Map();
const statuses={pending:'待执行',ready:'已就绪',running:'执行中','awaiting-verification':'待验收',verified:'已完成（已验收）',blocked:'阻塞',failed:'失败',cancelled:'已取消',unreported:'未上报',inconsistent:'记录待核对'};
const eventNames={initialized:'任务初始化','check-passed':'检查通过','report-rejected':'反馈已拒绝',stopped:'旧批次已停止',assigned:'任务派发',started:'开始执行',progress:'进度反馈','issue-reported':'发现问题','implementation-reported':'实现反馈','verification-passed':'验收通过','verification-failed':'验收失败','requirement-change-proposed':'需求变更提议','requirement-change-accepted':'需求变更接受','design-revised':'设计修订','revision-acknowledged':'新版本已确认','evidence-invalidated':'证据失效',resumed:'恢复执行',cancelled:'任务取消'};
const attention=s=>['blocked','failed','inconsistent'].includes(s);
function str(x){return x==null?'—':typeof x==='object'?JSON.stringify(x):String(x)}
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=str(text);if(cls)n.className=cls;return n}
function when(s){const d=new Date(s);return s&&!Number.isNaN(d.getTime())?d.toLocaleString('zh-CN',{hour12:false}):'时间未记录'}
function summaryRole(r){const rows=data.tasks.filter(t=>t.roleId===r.id);for(const s of ['inconsistent','failed','blocked','running','awaiting-verification','ready','pending','unreported'])if(rows.some(t=>t.status===s))return s;return rows.length?(rows.every(t=>t.status==='cancelled')?'cancelled':'verified'):'unreported'}
function pill(s){return el('span',statuses[s]||s,'pill '+s)}
function empty(title,desc,compact=false){const n=el('div',undefined,'empty'+(compact?' compact':''));n.append(el('div','◌','emptyicon'),el('strong',title),el('p',desc));return n}
function showDialog(title){$('detailTitle').textContent=title;$('detailBody').replaceChildren();if(!$('detail').open)$('detail').showModal();return $('detailBody')}
function roleDetail(r){
  const body=showDialog(r.name),rows=data.tasks.filter(task=>task.roleId===r.id);
  body.append(el('p',r.description||'暂无职责说明','muted'),el('h3','角色记录'),rows.length?table(rows):empty('尚无执行反馈','该角色还没有阶段状态。',true));
  if(!Object.keys(r.documents||{}).length){body.append(el('p','云端只同步角色摘要和边界路径；完整文档仍在项目本地。','small muted'));return}
  const names={'role-card.md':'角色卡','boundary.md':'修改边界','api-spec.md':'实现报告','functional-description.md':'职责说明','changelog.md':'变更记录'};
  const buttons=el('div',undefined,'docbuttons'),content=el('pre','选择文档查看内容。');
  for(const [name,path] of Object.entries(r.documents)){
    const button=el('button',names[name]||name,'btn');
    button.onclick=async()=>{content.textContent='正在读取…';try{const response=await fetch(apiPath('/api/document?path='+encodeURIComponent(path)),{cache:'no-store'});const result=await response.json();if(!response.ok)throw Error(result.error);content.textContent=result.text;}catch(error){content.textContent='读取失败：'+error.message}};
    buttons.append(button);
  }
  body.append(el('h3','只读文档'),buttons,content);
}
const contextLabels={flows:['流程总览','该角色参与的工作路径'],data:['数据总览','输入、输出与数据归属'],interfaces:['接口总览','公开能力与调用关系'],definitions:['定义总览','术语与职责边界']};
function openContext(roleId){contextRoleId=roleId;contextPage={category:'flows',topicId:null};contextDetail=null;setView('context')}
function contextGo(category,topicId=null){contextPage={category,topicId};contextDetail=null;renderContext();window.scrollTo({top:0})}
function contextCard(title,description,meta,action){const card=el('button',undefined,'contextcard');card.append(el('span',meta,'count'),el('strong',title),el('p',description||'暂无摘要'),el('span','查看详情 →','arrow'));card.onclick=action;return card}
function fieldTable(fields){
  const wrap=el('div',undefined,'fieldsbox'),table=el('table',undefined,'fieldtable'),head=el('tr');
  for(const label of ['字段','类型','是否必填','含义'])head.append(el('th',label));table.append(head);
  for(const field of fields){const row=el('tr');for(const value of [field.name,field.type,field.required?'必填':'可选',field.description||'—'])row.append(el('td',value));table.append(row)}
  wrap.append(table);return wrap;
}
function structuredFields(host,record){
  if(record.category==='data'){
    if(!record.data){host.append(el('p','字段待补充。'));return}
    host.append(el('p','归属：'+record.data.owner),fieldTable(record.data.fields));
  }
  if(record.category==='interfaces'){
    if(!record.interface){host.append(el('p','接口字段待补充。'));return}
    const spec=record.interface,network=spec.kind==='network';
    host.append(el('p',network?'类型：网络接口 · '+(spec.protocol||'Network'):'类型：内部接口'),el('p','入口：'+spec.entry));
    if(network&&spec.requestUrl){const url=el('div',undefined,'requesturl');url.append(el('b',spec.method||spec.protocol),el('code',spec.requestUrl));host.append(url)}
    if(record.interface.inputs?.length)host.append(el('strong','输入字段'),fieldTable(record.interface.inputs));
    if(record.interface.outputs?.length)host.append(el('strong','输出字段'),fieldTable(record.interface.outputs));
  }
}
function contextRelated(ids,topics,roleId){
  const related=el('div',undefined,'contextrelated');
  for(const id of ids||[]){
    const target=topics.find(topic=>topic.topic_id===id);if(!target)continue;
    const card=el('article',undefined,'contextrelatedcard'),details=el('div');
    card.append(el('span',contextLabels[target.category]?.[0]||target.category,'kind'),el('strong',target.title),el('p',target.summary),details);related.append(card);
    const key=roleId+'/'+id+'/'+target.revision;
    function show(record){
      if(!card.isConnected)return;
      details.replaceChildren();
      details.append(el('p',record.details||'暂无详细说明'));
      structuredFields(details,record);
      if(record.refs?.length)details.append(el('small',record.refs.join(' · ')));
    }
    if(contextRelatedCache.has(key)){queueMicrotask(()=>show(contextRelatedCache.get(key)));continue}
    details.append(el('p','正在读取详情…'));
    fetch(apiPath('/api/context?role='+encodeURIComponent(roleId)+'&topic='+encodeURIComponent(id)),{cache:'no-store'}).then(async response=>{const record=await response.json();if(!response.ok)throw Error(record.error);if(contextRelatedCache.size>100)contextRelatedCache.clear();contextRelatedCache.set(key,record);show(record)}).catch(error=>{if(card.isConnected)details.textContent='详情暂不可用：'+error.message});
  }
  return related;
}
function renderContext(){
  if(!data)return;
  const select=$('contextRole');select.replaceChildren();
  for(const role of data.roles){const option=el('option',role.name);option.value=role.id;select.append(option)}
  if(!data.roles.some(role=>role.id===contextRoleId))contextRoleId=data.roles[0]?.id||null;
  if(contextRoleId)select.value=contextRoleId;
  const role=data.roles.find(item=>item.id===contextRoleId),trail=$('contextTrail'),info=$('contextRoleInfo'),tabs=$('contextTabs'),body=$('contextBody');
  trail.replaceChildren();info.replaceChildren();tabs.replaceChildren();body.replaceChildren();
  if(!role){body.append(empty('还没有项目角色','建立角色卡后，这里可以按角色浏览项目理解。'));return}
  const purpose=el('div'),boundary=el('div'),chips=el('div',undefined,'boundarychips');purpose.append(el('strong','角色职责'),el('p',role.description||'职责尚未填写。'));
  boundary.append(el('strong','修改边界'));
  for(const path of role.boundaryPaths||[])chips.append(el('code',path));
  if(!chips.childElementCount)chips.append(el('p','边界文档暂无可识别的路径条目。'));
  boundary.append(chips);if(role.documents?.['boundary.md']){const boundaryButton=el('button','查看完整边界 →');boundaryButton.onclick=()=>roleDetail(role);boundary.append(boundaryButton)}info.append(purpose,boundary);
  const context=role.projectContext,category=contextPage.category||'flows',topicId=contextPage.topicId;
  trail.append(el('strong',role.name),el('span','/'));
  if(topicId){const back=el('button',contextLabels[category]?.[0]||category);back.onclick=()=>contextGo(category);trail.append(back,el('span','/'));const topic=context?.topics.find(item=>item.topic_id===topicId);trail.append(el('strong',topic?.title||'主题'))}
  else trail.append(el('strong',contextLabels[category]?.[0]||category));
  for(const [name,[label]] of Object.entries(contextLabels)){const tab=el('button',label);tab.classList.toggle('active',name===category);tab.setAttribute('aria-current',name===category?'page':'false');tab.onclick=()=>contextGo(name);tabs.append(tab)}
  if(!context){body.append(empty('还没有项目理解','该角色尚未建立项目理解。'));return}
  if(!topicId){
    const topics=context.topics.filter(item=>item.category===category),summary=context.categorySummaries?.[category]?.summary||(category==='flows'?context.overview.summary:contextLabels[category]?.[1]||'');
    const hero=el('div',undefined,'contexthero');hero.append(el('span',role.name+' · '+topics.length+' 个主题','contextkicker'),el('h2',contextLabels[category][0]),el('p',summary));
    if(category==='flows'){const actions=el('div',undefined,'contextactions'),records=el('button','角色记录','btn');records.onclick=()=>roleDetail(role);actions.append(records);hero.append(actions)}
    body.append(hero);
    if((category==='data'||category==='interfaces')&&topics.length){
      const key=role.id+'/'+category+'/'+topics.map(item=>item.topic_id+':'+item.revision).join(',')+'/'+(context.categorySummaries?.[category]?.revision||0),cached=contextCategoryCache.get(key);
      if(!cached){
        body.append(empty('正在读取字段','只读取当前角色的'+contextLabels[category][0]+'。'));
        const expectedRole=role.id,expectedCategory=category;
        fetch(apiPath('/api/context?role='+encodeURIComponent(expectedRole)+'&category='+encodeURIComponent(expectedCategory)),{cache:'no-store'}).then(async response=>{const result=await response.json();if(!response.ok)throw Error(result.error);if(contextCategoryCache.size>50)contextCategoryCache.clear();contextCategoryCache.set(key,result);if(view==='context'&&contextRoleId===expectedRole&&contextPage.category===expectedCategory&&!contextPage.topicId)renderContext()}).catch(error=>{if(contextRoleId===expectedRole&&contextPage.category===expectedCategory&&!contextPage.topicId)body.replaceChildren(empty('字段读取失败',error.message))});return;
      }
      function topicCard(topic){const card=el('article',undefined,'contextschema'),button=el('button','查看完整说明 →','btn');card.append(el('h3',topic.title),el('p',topic.summary));structuredFields(card,topic);button.onclick=()=>contextGo(category,topic.topic_id);card.append(button);return card}
      if(category==='interfaces'){
        for(const [kind,label] of [['network','网络接口'],['internal','内部接口']]){
          const group=cached.topics.filter(topic=>(topic.interface?.kind||'internal')===kind),section=el('section',undefined,'contextsection');section.append(el('h3',label+' · '+group.length));
          if(group.length)for(const topic of group)section.append(topicCard(topic));
          else section.append(el('p','暂无'+label+'。','small muted'));
          body.append(section);
        }
      }else for(const topic of cached.topics)body.append(topicCard(topic));
      return;
    }
    const grid=el('div',undefined,'contextgrid');for(const topic of topics)grid.append(contextCard(topic.title,topic.summary,'版本 '+topic.revision,()=>contextGo(category,topic.topic_id)));
    body.append(topics.length?grid:empty('暂无主题','该总览已有汇总，尚未录入具体主题。'));return;
  }
  const topicMeta=context.topics.find(item=>item.topic_id===topicId&&item.category===category);
  if(!topicMeta){body.append(empty('主题已变化','返回总览后重新选择。'));return}
  if(!contextDetail||contextDetail.roleId!==role.id||contextDetail.topic_id!==topicId||contextDetail.revision!==topicMeta.revision){
    body.append(empty('正在读取详情','只读取所选角色的主题。'));
    const expectedRole=role.id,expectedCategory=category,expectedTopic=topicId;
    fetch(apiPath('/api/context?role='+encodeURIComponent(expectedRole)+'&topic='+encodeURIComponent(expectedTopic)),{cache:'no-store'}).then(async response=>{const result=await response.json();if(!response.ok)throw Error(result.error);if(view==='context'&&contextRoleId===expectedRole&&contextPage.category===expectedCategory&&contextPage.topicId===expectedTopic){contextDetail={...result,roleId:expectedRole};renderContext()}}).catch(error=>{if(contextRoleId===expectedRole&&contextPage.topicId===expectedTopic)body.replaceChildren(empty('详情读取失败',error.message))});return;
  }
  const topic=contextDetail,hero=el('div',undefined,'contexthero');hero.append(el('span',role.name+' · '+contextLabels[category][0]+' · 版本 '+topic.revision,'contextkicker'),el('h2',topic.title),el('p',topic.summary));body.append(hero);
  function relatedSection(title,ids){const related=contextRelated(ids,context.topics,role.id);if(!related.childElementCount)return;const section=el('section',undefined,'contextsection');section.append(el('h3',title),related);body.append(section)}
  if(category==='flows'){
    const flow=topic.flow;
    if(flow){
      if(flow.triggers?.length){const section=el('section',undefined,'contextsection'),list=el('div',undefined,'contextrelated');section.append(el('h3','触发条件'));for(const trigger of flow.triggers){const card=el('article',undefined,'contextrelatedcard');card.append(el('strong',trigger.when));if(trigger.sourceFlow){const source=context.topics.find(item=>item.topic_id===trigger.sourceFlow);card.append(el('p','来自流程：'+(source?.title||trigger.sourceFlow)))}if(trigger.ref)card.append(el('small',trigger.ref));list.append(card)}section.append(list);body.append(section)}
      if(flow.steps?.length){const section=el('section',undefined,'contextsection'),steps=el('div',undefined,'contextflow');section.append(el('h3','流程步骤'));for(const [index,step] of flow.steps.entries()){const card=el('article',undefined,'contextstep');card.append(el('b',String(index+1).padStart(2,'0')),el('strong',step.title),el('p',step.description));if(step.ref)card.append(el('small',step.ref));steps.append(card)}section.append(steps);body.append(section)}
      relatedSection('输入数据',flow.inputs);relatedSection('输出数据',flow.outputs);relatedSection('相关接口',flow.interfaces);
    }else body.append(empty('流程结构待补充','请补充触发条件、执行步骤、输入和输出数据。'));
  }
  if(category==='data'||category==='interfaces'){const section=el('section',undefined,'contextsection'),fields=el('div',undefined,'contextbody');section.append(el('h3',category==='data'?'数据字段':'接口字段'));structuredFields(fields,topic);section.append(fields);body.append(section)}
  if(topic.details){const section=el('section',undefined,'contextsection'),detail=el('div',undefined,'contextbody');section.append(el('h3','说明'));for(const paragraph of topic.details.split(/\n+/).filter(Boolean))detail.append(el('p',paragraph));section.append(detail);body.append(section)}
  if(topic.refs?.length){const section=el('section',undefined,'contextsection'),items=el('div',undefined,'contextrefs');section.append(el('h3','依据与位置'));for(const ref of topic.refs)items.append(el('code',ref));section.append(items);body.append(section)}
}
function taskDetail(t){const body=showDialog(str(t.title));body.append(pill(t.status),el('p',t.taskId+' / '+t.nodeId,'small muted'),el('h3','版本与执行记录'),el('pre',JSON.stringify(t,null,2)))}
function table(rows){if(!rows.length)return empty('还没有阶段任务','项目角色写入 plan.json 和 state.json 后，这里会展示实际进度。');const wrap=el('div',undefined,'tablewrap'),t=el('table'),head=el('thead'),hr=el('tr');for(const label of ['任务 / 角色','状态','需求 / 设计','最新反馈 / 下一步'])hr.append(el('th',label));head.append(hr);t.append(head);const b=el('tbody');for(const row of rows){const tr=el('tr',undefined,'taskrow');tr.tabIndex=0;tr.setAttribute('aria-label','查看任务 '+str(row.title));tr.onclick=()=>taskDetail(row);tr.onkeydown=e=>{if(e.key==='Enter')taskDetail(row)};const title=el('td');title.append(el('strong',row.title),el('small',str(row.roleId)+' · '+str(row.stage)));const status=el('td');status.append(pill(row.status));const versions=el('td');versions.append(el('span',str(row.assignedRevisions?.requirement)+' / '+str(row.assignedRevisions?.design)),el('small','状态版本 '+str(row.stateRevision)));const feedback=el('td');feedback.append(el('span',row.latestReport?.summary||row.reason||'暂无反馈'),el('small',(row.nextAction?.responsibleRole?str(row.nextAction.responsibleRole)+' · ':'')+(row.nextAction?.summary||row.nextAction?.action||'—')));tr.append(title,status,versions,feedback);b.append(tr)}t.append(b);wrap.append(t);return wrap}
function events(node,rows){node.replaceChildren();if(!rows.length){node.append(empty('等待第一条事件','角色反馈、需求变更和设计修订都会记录在这里。',true));return}for(const e of rows){const n=el('article',undefined,'event');n.append(el('time',when(e.at)),el('p',e.summary||eventNames[e.kind]||e.kind),el('small',(eventNames[e.kind]||e.kind)+' · '+e.taskId+' · #'+e.seq+(e.consistent?'':' · 记录待核对')));node.append(n)}}
function renderRoles(){const q=$('roleSearch').value.toLowerCase(),f=$('roleFilter').value;const rows=data.roles.filter(r=>{const s=summaryRole(r);return(r.name+' '+r.description).toLowerCase().includes(q)&&(f==='all'||(f==='blocked'?attention(s):s===f))});$('roleGrid').replaceChildren();if(!rows.length){const n=empty('没有匹配角色',data.roles.length?'调整搜索或筛选条件。':'请指定包含角色卡的项目目录；页面不会自动创建角色。');n.style.gridColumn='1/-1';$('roleGrid').append(n);return}rows.forEach(r=>{const card=el('button',undefined,'rolecard');card.setAttribute('aria-label','查看角色 '+r.name);card.onclick=()=>openContext(r.id);const top=el('div',undefined,'rolerow');top.append(el('span',r.name.slice(0,1),'avatar'),el('strong',r.name),pill(summaryRole(r)));const foot=el('div',undefined,'rolefoot');const tasks=data.tasks.filter(t=>t.roleId===r.id);const boundary=currentProjectId?(r.boundaryPaths?.length?'已列出边界':'边界待补充'):(r.documents?.['boundary.md']?'有边界文档':'缺少边界');foot.append(el('span',tasks.length+' 个阶段 · '+boundary),el('span','查看理解 ↗'));card.append(top,el('p',r.description||'暂无职责说明','desc'),foot);$('roleGrid').append(card)})}
function render(){const unreported=data.roles.filter(r=>!data.tasks.some(t=>t.roleId===r.id)).length;$('project').textContent=data.project;$('roleCount').textContent=data.roles.length;$('roleHint').textContent=unreported+' 个角色尚无执行记录';$('roleTotal').textContent=data.roles.length+' 个角色';$('runningCount').textContent=data.tasks.filter(t=>t.status==='running').length;$('reviewCount').textContent=data.tasks.filter(t=>t.status==='awaiting-verification').length;$('attentionCount').textContent=data.tasks.filter(t=>attention(t.status)).length;$('navTasks').textContent=data.tasks.length;$('navEvents').textContent=data.events.length;renderRoles();$('taskPreview').replaceChildren(table(data.tasks.slice(0,5)));renderTasks();events($('eventPreview'),data.events.slice(0,8));events($('eventFull'),data.events);if(view==='context')renderContext();$('notice').hidden=!data.issues.length;$('noticeText').textContent=data.issues.length+' 项记录需要核对，受影响状态不会显示为已验收。';$('lastUpdated').textContent='最近读取 '+when(data.sampledAt)}
function renderTasks(){const q=$('taskSearch').value.toLowerCase();$('taskTable').replaceChildren(table(data.tasks.filter(t=>JSON.stringify([t.title,t.nodeId,t.roleId,t.latestReport]).toLowerCase().includes(q))))}
function setView(v){
  view=v;document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===v));
  $('overview').hidden=v!=='overview';$('contextView').hidden=v!=='context';$('tasksView').hidden=v!=='tasks';$('eventsView').hidden=v!=='events';$('metrics').hidden=v==='context';
  $('pageTitle').textContent={overview:'每个角色，进展清晰。',context:'按角色查看项目理解。',tasks:'从阶段任务，看到交付。',events:'每一次变化，都有记录。'}[v];
  $('pageSubtitle').textContent=v==='context'?'角色职责、边界和流程、数据、接口一页可查。':'角色、阶段与设计版本，在一个视图中保持同步。';
  if(v==='context')renderContext();
}
async function loadProjects(){
  if(!currentProjectId)return;
  try{
    $('workspaceMode').textContent='SHARED DASHBOARD';$('workspaceHint').textContent='只同步展示快照';$('footerHint').textContent='展示最近同步的项目快照 · 不代表代理进程在线 · 不自动验收';
    const response=await fetch('/api/projects',{cache:'no-store'});
    if(response.status===401){location.assign('/login?next='+encodeURIComponent(location.pathname));return}
    if(!response.ok)return;
    const result=await response.json(),selector=$('projectSelect');selector.replaceChildren();
    for(const project of result.projects){const option=el('option',project.name);option.value=project.id;selector.append(option)}
    selector.value=currentProjectId;selector.hidden=result.projects.length<2;
    selector.onchange=()=>location.assign('/p/'+encodeURIComponent(selector.value)+'/');
    const me=await fetch('/api/me',{cache:'no-store'}).then(result=>result.json());$('manageLink').hidden=me.role!=='admin';$('logout').hidden=false;
    $('logout').onclick=async()=>{await fetch('/api/logout',{method:'POST',headers:{'X-CSRF-Token':me.csrfToken},credentials:'same-origin'});location.assign('/login')};
  }catch(_error){/* The current project remains usable if the project list is temporarily unavailable. */}
}
async function refresh(){
  if(loading)return;
  clearTimeout(refreshTimer);loading=true;$('refresh').disabled=true;
  try{
    const response=await fetch(apiPath('/api/snapshot'),{cache:'no-store',signal:AbortSignal.timeout(8000)});
    if(response.status===401){location.assign('/login?next='+encodeURIComponent(location.pathname));return}
    if(!response.ok)throw Error('HTTP '+response.status);
    const next=await response.json(),signature=JSON.stringify({...next,sampledAt:null});
    data=next;lastSuccess=next.sampledAt;
    if(signature!==lastDataSignature){render();lastDataSignature=signature}
    else $('lastUpdated').textContent='最近读取 '+when(next.sampledAt);
    $('notice').hidden=!next.issues.length;
    if(next.issues.length)$('noticeText').textContent=next.issues.length+' 项记录需要核对，受影响状态不会显示为已验收。';
    $('connection').classList.remove('failed');
    $('connectionText').textContent=currentProjectId?(next.receivedAt?'上次同步 '+when(next.receivedAt):'项目尚未同步'):'记录已连接 · 2s 刷新';
  }catch(error){
    $('connection').classList.add('failed');$('connectionText').textContent='连接中断';$('notice').hidden=false;
    $('noticeText').textContent='无法刷新：'+error.message+(lastSuccess?'。当前展示 '+when(lastSuccess)+' 的旧快照。':'。请检查服务是否启动。');
  }finally{loading=false;$('refresh').disabled=false;refreshTimer=setTimeout(refresh,2000)}
}
function help(){const body=showDialog('让角色信息持续同步');body.append(el('p',currentProjectId?'本地同步器只发送角色摘要、边界路径、项目理解和任务快照，云端不需要业务源码。页面显示最近同步的数据，不监测代理进程，也不自动验收。':'页面只读，每 2 秒重新读取磁盘。项目角色更新记录后即可看到变化；它不会监测代理进程，也不会把“报告完成”自动验收。','muted'),el('h3','本地记录目录'),el('pre','项目根目录/\n  角色卡/<角色>/role-card.md\n  角色卡/<角色>/boundary.md\n  project-context/context.sqlite3  # 按 role_id 筛选\n  docs/scheduling/<任务>/\n    plan.json\n    state.json\n    events.jsonl'),el('h3','字段约定'),el('p','plan 和 state 使用 schemaVersion: 1、相同 taskId 和 planRevision。nodes 可为数组或按 nodeId 索引的对象。roleId 对应角色文件夹名。'),el('pre','节点状态字段示例（不是实际执行记录）：\n'+JSON.stringify({nodeId:'export-impl',roleId:'导出',attemptId:'attempt-1',status:'running',assignedRevisions:{requirement:'R2',design:'D3'},acknowledgedRevisions:{requirement:'R2',design:'D3'},latestReport:{reportId:'report-1',summary:'正在实现导出'},nextAction:{summary:'完成契约测试',responsibleRole:'导出'}},null,2)),el('p','state 顶层需有 stateRevision、lastEventSeq、updatedAt。事件按 seq 从 1 连续递增，带 eventId、taskId、kind、summary 和时间。记录缺失或版本不一致会明确提示。','small muted'))}
$('help').onclick=$('helpInline').onclick=help;$('refresh').onclick=refresh;$('closeDetail').onclick=()=>$('detail').close();$('detail').onclick=e=>{if(e.target===$('detail'))$('detail').close()};$('issuesButton').onclick=()=>{const b=showDialog('记录检查');b.append(el('pre',JSON.stringify(data?.issues||[],null,2)))};$('allTasks').onclick=()=>setView('tasks');document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>setView(b.dataset.view));$('contextRole').onchange=e=>openContext(e.target.value);$('roleSearch').oninput=$('roleFilter').onchange=()=>{if(data)renderRoles()};$('taskSearch').oninput=()=>{if(data)renderTasks()};loadProjects();refresh();
