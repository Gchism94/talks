(()=>{'use strict';
for(const group of document.querySelectorAll('[data-directory]')){
const search=group.querySelector('input[type=search]'),select=group.querySelector('select'),items=[...group.querySelectorAll('[data-resource]')],count=group.querySelector('[role=status]');
function update(){const q=(search?.value||'').trim().toLowerCase(),c=select?.value||'all';let n=0;for(const item of items){const show=item.textContent.toLowerCase().includes(q)&&(c==='all'||item.dataset.category===c);item.hidden=!show;if(show)n++;}count.textContent=n+' of '+items.length+' resources shown.';}search?.addEventListener('input',update);select?.addEventListener('change',update);update();}
let states=[];addEventListener('beforeprint',()=>{states=[...document.querySelectorAll('details')].map(x=>x.open);document.querySelectorAll('details').forEach(x=>x.open=true)});addEventListener('afterprint',()=>document.querySelectorAll('details').forEach((x,i)=>x.open=states[i]||false));
})();
