'use strict';
const form=document.getElementById('loginForm'),message=document.getElementById('message');
form.addEventListener('submit',async event=>{
  event.preventDefault();message.textContent='';const button=form.querySelector('button');button.disabled=true;
  try{
    const response=await fetch('/api/login',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:document.getElementById('username').value,password:document.getElementById('password').value})});
    const result=await response.json();if(!response.ok)throw Error(result.error||'登录失败');
    const requested=new URLSearchParams(location.search).get('next');
    const next=requested&&/^\/p\/[a-z0-9]+(?:-[a-z0-9]+)*\/$/.test(requested)?requested:'/';
    location.assign(next);
  }catch(error){message.textContent=error.message;document.getElementById('password').value='';button.disabled=false}
});
