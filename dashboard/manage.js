'use strict';
const $=id=>document.getElementById(id);
let csrfToken='';
function message(value){$('message').textContent=value}
function row(...parts){const item=document.createElement('div');item.className='row';for(const part of parts){const span=document.createElement('span');span.textContent=String(part);item.append(span)}return item}
async function api(path,options={}){
  const response=await fetch(path,{credentials:'same-origin',cache:'no-store',...options});
  const result=await response.json();
  if(!response.ok)throw Error(result.error||'请求失败');
  return result;
}
async function post(path,value){return api(path,{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrfToken},body:JSON.stringify(value)})}
async function refresh(){
  const [projects,users,keys]=await Promise.all([api('/api/admin/projects'),api('/api/admin/users'),api('/api/admin/keys')]);
  $('projects').replaceChildren(...projects.projects.map(project=>{const item=row(project.id,project.name,project.receivedAt?'已同步 '+project.receivedAt:'尚未同步');const link=document.createElement('a');link.href=project.url;link.textContent='打开';item.append(link);return item}));
  $('users').replaceChildren(...users.users.map(user=>{const item=row(user.username,user.role,user.active?'已启用':'已停用',user.projects.join('、')||'无项目');if(user.active){const button=document.createElement('button');button.type='button';button.className='secondary';button.textContent='停用';button.onclick=async()=>{try{await post('/api/admin/users/disable',{username:user.username});await refresh();message('已停用 '+user.username)}catch(error){message(error.message)}};item.append(button)}return item}));
  $('keys').replaceChildren(...keys.keys.map(key=>{const item=row('#'+key.id,key.projectId,key.label,key.revokedAt?'已撤销':'有效');if(!key.revokedAt){const button=document.createElement('button');button.type='button';button.className='secondary';button.textContent='撤销';button.onclick=async()=>{try{await post('/api/admin/keys/revoke',{id:key.id});await refresh();message('已撤销 Key #'+key.id)}catch(error){message(error.message)}};item.append(button)}return item}));
}
function attach(formId,path,values,done){$(formId).addEventListener('submit',async event=>{event.preventDefault();message('');try{const result=await post(path,values());event.target.reset();if(done)done(result);await refresh();if(!done)message('已保存')}catch(error){message(error.message)}})}
async function init(){
  try{
    const me=await api('/api/me');if(me.role!=='admin'){location.assign('/');return}csrfToken=me.csrfToken;
    attach('projectForm','/api/admin/projects',()=>({id:$('projectId').value,title:$('projectTitle').value}));
    attach('userForm','/api/admin/users',()=>({username:$('newUsername').value,password:$('newPassword').value,role:$('userRole').value}));
    attach('grantForm','/api/admin/grants',()=>({username:$('grantUsername').value,projectId:$('grantProject').value}));
    attach('keyForm','/api/admin/keys',()=>({projectId:$('keyProject').value,label:$('keyLabel').value}),result=>{$('issuedKey').textContent=result.key;$('keyResult').hidden=false;message('Key 已创建，仅显示这一次')});
    $('logout').onclick=async()=>{try{await post('/api/logout',{});location.assign('/login')}catch(error){message(error.message)}};
    await refresh();
  }catch(error){message(error.message);if(error.message==='Login required')location.assign('/login')}
}
init();
