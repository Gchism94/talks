(()=>{'use strict';
// Keep the six main paths visible; detail pages belong to Supplement.
const requestedPage=location.pathname.split('/').pop();
function openLegacySlide(){
 if((!requestedPage||requestedPage==='index.html')&&/^#[1-5]$/.test(location.hash)){
  const talk=new URL('talk.html',location.href);talk.search=location.search;talk.hash=location.hash;location.replace(talk.href);return true;
 }
 return false;
}
if(openLegacySlide())return;
addEventListener('hashchange',openLegacySlide);
const currentPage=!requestedPage||requestedPage==='program.html'?'index.html':requestedPage;
const primaryPages=new Set(['index.html','program.html','inventory.html','primers.html','needs.html','report.html','supplemental.html']);
for(const link of document.querySelectorAll('.md-tabs__link,.md-nav--primary a.md-nav__link')){
 const target=new URL(link.href,location.href).pathname.split('/').pop();
 if(target===currentPage)link.setAttribute('aria-current','page');
 else if(target==='supplemental.html'&&!primaryPages.has(currentPage)&&currentPage!=='404.html')link.dataset.currentSection='true';
}
for(const group of document.querySelectorAll('[data-directory]')){
const search=group.querySelector('input[type=search]'),select=group.querySelector('select'),level=group.querySelector('[data-level-filter]'),items=[...group.querySelectorAll('[data-resource]')],count=group.querySelector('[role=status]');
function update(){const q=(search?.value||'').trim().toLowerCase(),c=select?.value||'all',l=level?.value||'all';let n=0;for(const item of items){const text=(item.textContent+' '+(item.dataset.category||'')).toLowerCase(),match=!q||(q.length<=3?text.split(/[^\p{L}\p{N}]+/u).some(word=>word.startsWith(q)):text.includes(q));const show=match&&(c==='all'||item.dataset.category===c)&&(l==='all'||item.dataset.level===l);item.hidden=!show;if(show)n++;}count.textContent=n+' of '+items.length+' resources shown.';}search?.addEventListener('input',update);select?.addEventListener('change',update);level?.addEventListener('change',update);update();}
// Open the mobile menu at its root, so users can see every workstream immediately.
for(const label of document.querySelectorAll('label[for^="__nav_"]')){const input=document.getElementById(label.htmlFor);if(!input)continue;label.tabIndex=0;label.setAttribute('role','button');if(label.classList.contains('md-nav__title'))label.setAttribute('aria-label','Back to navigation');const sync=()=>label.setAttribute('aria-expanded',String(input.checked));sync();input.addEventListener('change',sync);label.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();e.stopPropagation();label.click()}});}
// Align non-heading hash targets below the complete sticky header; the theme handles headings.
const header=document.querySelector('.md-header');
if(header){const offset=()=>document.documentElement.style.setProperty('--guide-sticky-offset',(header.getBoundingClientRect().height+16)+'px');offset();new ResizeObserver(offset).observe(header);}
const drawer=document.getElementById('__drawer'),menu=document.querySelector('header label[for=__drawer]');
if(drawer&&menu){menu.tabIndex=0;menu.setAttribute('role','button');menu.setAttribute('aria-label','Open navigation');const state=()=>{menu.setAttribute('aria-expanded',String(drawer.checked));menu.setAttribute('aria-label',drawer.checked?'Close navigation':'Open navigation');if(drawer.checked&&matchMedia('(max-width: 1219px)').matches){document.querySelectorAll('input.md-nav__toggle').forEach(x=>x.checked=false);document.querySelectorAll('label[for^="__nav_"]').forEach(x=>x.setAttribute('aria-expanded','false'))}};drawer.addEventListener('change',state);menu.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();e.stopPropagation();menu.click()}});document.addEventListener('keydown',e=>{if(e.key==='Escape'&&drawer.checked){drawer.checked=false;state();menu.focus()}});state();}
let states=[];addEventListener('beforeprint',()=>{states=[...document.querySelectorAll('details')].map(x=>x.open);document.querySelectorAll('details').forEach(x=>x.open=true)});addEventListener('afterprint',()=>document.querySelectorAll('details').forEach((x,i)=>x.open=states[i]||false));
})();

function revealSource(){if(location.hash){const el=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(el){const d=el.querySelector('details');if(d)d.open=true;el.scrollIntoView();}}}addEventListener('hashchange',revealSource);revealSource();
