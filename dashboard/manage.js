'use strict';
const basePath=document.querySelector('meta[name="ans-base-path"]').content;
const $=id=>document.getElementById(id);
let csrfToken='',currentAdmin='';

function element(tag,value,className){
  const node=document.createElement(tag);
  if(value!==undefined)node.textContent=String(value);
  if(className)node.className=className;
  return node;
}
function notice(value,tone='ok'){
  $('message').textContent=value;
  $('message').className='message '+(value?(tone==='error'?'error':'ok'):'');
}
function badge(label,tone){return element('span',label,'tag '+tone)}
function record(initial,title,subtitle,badges,action){
  const card=element('article',undefined,'record');
  const avatar=element('span',initial,'record-avatar');
  const main=element('div',undefined,'record-main');
  const heading=element('div',undefined,'record-title');
  heading.append(element('span',title),...badges);
  main.append(heading,element('div',subtitle,'record-subtitle'));
  card.append(avatar,main);
  if(action){const slot=element('div',undefined,'record-action');slot.append(action);card.append(slot)}
  return card;
}
function fill(id,items,emptyText){
  const container=$(id);
  container.replaceChildren(...(items.length?items:[element('p',emptyText,'empty-record')]));
}
function actionButton(label,onClick,danger=false){
  const button=element('button',label,danger?'danger':'');
  button.type='button';button.onclick=onClick;
  return button;
}
function date(value){return value?new Date(value).toLocaleString('zh-CN',{hour12:false}):'未记录'}
async function api(path,options={}){
  const response=await fetch(basePath+path,{credentials:'same-origin',cache:'no-store',...options});
  const result=await response.json();
  if(!response.ok)throw Error(result.error||'请求失败');
  return result;
}
async function post(path,value){
  return api(path,{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrfToken},body:JSON.stringify(value)});
}
async function refresh(){
  const [projects,users,keys]=await Promise.all([
    api('/api/admin/projects'),api('/api/admin/users'),api('/api/admin/keys')
  ]);
  const projectRows=projects.projects,userRows=users.users,keyRows=keys.keys;
  $('projectCount').textContent=projectRows.length;
  $('userCount').textContent=userRows.filter(user=>user.active).length;
  $('keyCount').textContent=keyRows.filter(key=>!key.revokedAt).length;
  $('projectsTotal').textContent=projectRows.length+' 个项目';
  $('usersTotal').textContent=userRows.length+' 个账号';

  fill('projects',projectRows.map(project=>{
    const link=element('a','打开 ↗');link.href=project.url;
    return record((project.name||project.id).slice(0,1).toUpperCase(),project.name,
      '/p/'+project.id+'/ · '+(project.receivedAt?'最近同步 '+date(project.receivedAt):'等待首次同步'),
      [badge(project.receivedAt?'已同步':'待同步',project.receivedAt?'good':'warn')],link);
  }),'尚未创建项目。');

  fill('users',userRows.map(user=>{
    const labels=[badge(user.role==='admin'?'管理员':'查看者',user.role==='admin'?'good':'')];
    if(!user.active)labels.push(badge('已停用','off'));
    const subtitle=user.role==='admin'?'查看全部项目 · 可管理与审批':'查看全部项目';
    const disable=user.active&&user.username!==currentAdmin?actionButton('停用',async()=>{
      try{await post('/api/admin/users/disable',{username:user.username});await refresh();notice('已停用 '+user.username)}
      catch(error){notice(error.message,'error')}
    },true):null;
    return record(user.username.slice(0,1).toUpperCase(),user.username,subtitle,labels,disable);
  }),'尚未添加其他成员。');

  fill('keys',keyRows.map(key=>{
    const revoke=!key.revokedAt?actionButton('撤销',async()=>{
      try{await post('/api/admin/keys/revoke',{id:key.id});await refresh();notice('已撤销 Key #'+key.id)}
      catch(error){notice(error.message,'error')}
    },true):null;
    return record('K',key.label,'项目 '+key.projectId+' · 创建于 '+date(key.createdAt),
      [badge(key.revokedAt?'已撤销':'有效',key.revokedAt?'off':'good')],revoke);
  }),'尚未创建项目 Key。');
}
function attach(formId,path,values,afterSave){
  $(formId).addEventListener('submit',async event=>{
    event.preventDefault();notice('');
    const button=event.target.querySelector('button[type="submit"]');button.disabled=true;
    try{
      const result=await post(path,values());
      event.target.reset();
      if(afterSave)afterSave(result);
      await refresh();
      if(!afterSave)notice('已保存');
    }catch(error){notice(error.message,'error')}
    finally{button.disabled=false}
  });
}
async function init(){
  try{
    const me=await api('/api/me');
    if(me.role!=='admin'){location.assign(basePath+'/');return}
    currentAdmin=me.username;csrfToken=me.csrfToken;
    $('adminName').textContent=me.username;
    attach('projectForm','/api/admin/projects',()=>({id:$('projectId').value,title:$('projectTitle').value}));
    attach('userForm','/api/admin/users',()=>({username:$('newUsername').value,password:$('newPassword').value,role:$('userRole').value}));
    attach('keyForm','/api/admin/keys',()=>({projectId:$('keyProject').value,label:$('keyLabel').value}),result=>{
      $('issuedKey').textContent=result.key;$('keyResult').hidden=false;
      notice('项目 Key 已创建，仅显示这一次');
    });
    $('logout').onclick=async()=>{
      try{await post('/api/logout',{});location.assign(basePath+'/login')}
      catch(error){notice(error.message,'error')}
    };
    await refresh();
  }catch(error){
    notice(error.message,'error');
    if(error.message==='Login required')location.assign(basePath+'/login');
  }
}
init();
